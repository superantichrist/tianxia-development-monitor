/* Curated snapshot UI. No frameworks, analytics, network calls, or account data. */
(() => {
  "use strict";
  const data = window.MONITOR_DATA;
  if (!data) return;
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  const numeric = (value, decimals = 0) => typeof value === "number" && Number.isFinite(value) ? value.toLocaleString("ko-KR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : "—";
  const withUnit = (value, unit, decimals = 0) => value == null ? "미측정" : `${numeric(value, decimals)} ${unit}`;
  const state = { view: "board", domain: "all", query: "" };
  const openCards = new Set();
  const domainLabel = (id) => data.domains.find((domain) => domain.id === id)?.label ?? id;
  const statusLabel = (id) => data.statuses.find((status) => status.id === id)?.label ?? id;
  const copy = {
    board: ["WORK IN VIEW", "무엇을 만들고 있나요", "진행 중인 기능부터 완료 근거와 다음 단계까지."],
    parity: ["FEATURE PARITY", "현재 구현과 남은 격차", "범위를 넓히고, 실제 플레이로 하나씩 확인합니다."],
    evidence: ["EVIDENCE & MILESTONES", "변화의 근거를 남깁니다", "완료 기록, 측정 조건, 그리고 아직 확인하지 못한 것."],
  };

  function setText(selector, value) {
    const element = $(selector);
    if (element) element.textContent = value;
  }

  function matches(item) {
    const sameDomain = state.domain === "all" || item.domain === state.domain;
    const searchText = Object.values(item).join(" ").toLocaleLowerCase();
    return sameDomain && (!state.query || searchText.includes(state.query.toLocaleLowerCase()));
  }

  function renderCard(item, index) {
    return `<details class="task-card" data-card-id="${escape(item.id)}"${openCards.has(item.id) ? " open" : ""}>
      <summary><div class="task-meta"><span class="domain-label">${escape(domainLabel(item.domain))}</span><span class="milestone-label">${escape(item.milestone)}</span></div>
      <h4 class="task-title">${escape(item.title)}</h4><p class="task-summary">${escape(item.summary)}</p>
      <div class="task-bottom">${item.priority === "focus" ? '<span class="priority-chip">기능·그래픽 우선</span>' : '<span>근거와 다음 단계</span>'}<span class="task-id">TX–${String(index + 1).padStart(3, "0")}</span><span class="expand-icon" aria-hidden="true">+</span></div></summary>
      <div class="task-detail"><h4>확인한 근거와 범위</h4><p>${escape(item.evidence)}</p><h4>다음 단계</h4><p>${escape(item.next)}</p></div></details>`;
  }

  function renderBoard() {
    const items = data.cards.filter(matches);
    $("#kanban-board").innerHTML = data.statuses.map((status) => {
      const members = items.filter((item) => item.status === status.id);
      return `<section class="kanban-column ${escape(status.id)}" aria-label="${escape(status.label)}">
        <div class="column-heading"><span class="column-dot" aria-hidden="true"></span><h3>${escape(status.label)}</h3><span class="count">${members.length}</span></div>
        <p class="column-description">${escape(status.description)}</p><div class="card-stack">${members.map((item) => renderCard(item, data.cards.indexOf(item))).join("") || '<div class="column-empty">조건에 맞는 카드가 없습니다</div>'}</div></section>`;
    }).join("");
    $$(".task-card").forEach((details) => details.addEventListener("toggle", () => {
      if (details.open) openCards.add(details.dataset.cardId); else openCards.delete(details.dataset.cardId);
    }));
    setText("#result-count", `${items.length}개 카드 / 전체 ${data.cards.length}개`);
  }

  function renderParity() {
    const rows = data.parity.filter(matches);
    $("#parity-body").innerHTML = rows.map((row) => `<tr><td>${escape(row.area)}<span class="parity-level">${escape(row.level)}</span></td><td>${escape(row.current)}</td><td>${escape(row.gap)}</td><td>${escape(row.next)}</td></tr>`).join("");
    $("#parity-empty").hidden = rows.length > 0;
    setText("#result-count", `${rows.length}개 분야 / 전체 ${data.parity.length}개`);
  }

  function render() {
    if (state.view === "board") renderBoard();
    if (state.view === "parity") renderParity();
    $$("[data-domain]").forEach((button) => {
      const active = button.dataset.domain === state.domain;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    $("#reset-filters").hidden = state.domain === "all" && !state.query;
  }

  function changeView(view, updateHash = true) {
    if (!copy[view]) view = "board";
    state.view = view;
    $$(".view-panel").forEach((panel) => { panel.hidden = panel.id !== `${view}-view`; });
    $$(".view-nav [data-view]").forEach((button) => {
      const active = button.dataset.view === view;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    setText("#section-eyebrow", copy[view][0]);
    setText("#workspace-title", copy[view][1]);
    setText("#section-description", copy[view][2]);
    $("#toolbar").hidden = view === "evidence";
    $("#results-bar").hidden = view === "evidence";
    if (updateHash && location.hash !== `#${view}`) history.replaceState(null, "", `#${view}`);
    render();
  }

  function renderEvidence() {
    $("#milestone-timeline").innerHTML = data.milestones.map((item) => {
      const total = Object.values(item.checks).filter((n) => typeof n === "number").reduce((a, b) => a + b, 0);
      const evidence = [total ? `${numeric(total)}개 검사 기록` : null, item.videoVerified ? "비공개 보고 영상 확인" : null].filter(Boolean).join(" · ");
      return `<article class="timeline-item"><div class="timeline-meta"><span class="timeline-id">${escape(item.id)}</span><span class="badge ${escape(item.status)}">${escape(statusLabel(item.status))}</span></div><h3>${escape(item.title)}</h3><p>${escape(item.description)}</p>${evidence ? `<p class="timeline-evidence">${escape(evidence)}</p>` : ""}</article>`;
    }).join("");
    const render = data.renderBenchmark;
    setText("#fps-before", numeric(render.beforeNearFps, 2));
    setText("#fps-after", numeric(render.nearFps, 2));
    setText("#fps-wide", withUnit(render.wideFps, "FPS", 2));
    setText("#render-p99", withUnit(render.nearP99Ms, "ms", 2));
    setText("#gpu-checks", withUnit(render.gpuChecks, "개"));
    setText("#render-conditions", render.conditions);
    setText("#render-scope", render.scope);
    const physics = data.physicsBenchmark;
    setText("#physics-checks", withUnit(physics.checks, "개"));
    setText("#physics-hits", withUnit(physics.contact_hits, "개"));
    setText("#physics-deaths", withUnit(physics.contact_deaths, "명"));
    setText("#physics-median", withUnit(physics.contact_median_ms, "ms", 2));
    setText("#physics-p99", `p99 ${withUnit(physics.contact_p99_ms, "ms", 2)}`);
    const tickBudget = physics.dt == null ? null : physics.dt * 1000;
    const withinBudget = tickBudget !== null && physics.contact_p99_ms != null && physics.contact_p99_ms <= tickBudget;
    setText("#physics-budget", tickBudget === null ? "목표 주기 검증 대기" : withinBudget ? `${numeric(1 / physics.dt)}Hz 틱 한도 ${numeric(tickBudget)}ms 이내인 이번 모듈 측정. 통합 프레임 성능은 별도 확인합니다.` : `목표 ${numeric(1 / physics.dt)}Hz / 틱 한도 ${numeric(tickBudget)}ms · 현재 대규모 접촉은 목표 미달`);
    setText("#physics-conditions", `${numeric(physics.agents)}명 영속 상태 · 최대 활성 ${numeric(physics.maximum_active_agents)}명 · ${numeric(physics.measured_steps)}스텝 측정 · 비접촉 휴면 중앙값 ${withUnit(physics.idle_median_ms, "ms", 3)}`);
    $("#evidence-policy").innerHTML = data.evidencePolicy.map((text) => `<li>${escape(text)}</li>`).join("");
    $("#evidence-sources").innerHTML = data.sources.map((source) => `<div class="evidence-source"><strong>${escape(source.label)}</strong><div><p>${source.url ? `<a href="${escape(source.url)}" target="_blank" rel="noopener noreferrer">${escape(source.source)} ↗</a>` : escape(source.source)}</p><small>${escape(source.scope)}</small></div></div>`).join("");
  }

  function initialize() {
    setText("#hero-version", `v${data.project.latestVerified}`);
    setText("#current-milestone", data.project.currentMilestone);
    setText("#current-milestone-title", data.project.currentMilestoneTitle || "개별 전투·3D 캠페인·일기토");
    setText("#count-active", data.cards.filter((item) => item.status === "in_progress").length);
    setText("#count-complete", data.cards.filter((item) => item.status === "complete").length);
    const date = new Date(data.updatedAt);
    const time = $("#updated-time");
    time.dateTime = data.updatedAt;
    time.textContent = date.toLocaleDateString("ko-KR", { timeZone: "Asia/Seoul", year: "numeric", month: "2-digit", day: "2-digit" });
    time.title = `${date.toLocaleString("ko-KR", { timeZone: "Asia/Seoul" })} KST`;
    setText("#snapshot-note", data.snapshotNote);
    $("#domain-filters").innerHTML = [{ id: "all", label: "전체" }, ...data.domains].map((domain) => `<button type="button" data-domain="${escape(domain.id)}" aria-pressed="false">${escape(domain.label)}</button>`).join("");
    $$("[data-domain]").forEach((button) => button.addEventListener("click", () => { state.domain = button.dataset.domain; render(); }));
    $$("[data-view]").forEach((button) => button.addEventListener("click", () => { changeView(button.dataset.view); }));
    $("#search").addEventListener("input", (event) => { state.query = event.target.value.trim(); render(); });
    $("#reset-filters").addEventListener("click", () => { state.domain = "all"; state.query = ""; $("#search").value = ""; render(); });
    document.addEventListener("keydown", (event) => {
      if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName) && state.view !== "evidence") { event.preventDefault(); $("#search").focus(); }
    });
    window.addEventListener("hashchange", () => changeView(location.hash.slice(1), false));
    renderEvidence();
    changeView(location.hash.slice(1), false);
  }
  initialize();
})();
