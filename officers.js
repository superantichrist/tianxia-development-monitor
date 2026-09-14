/* Public production catalog. Stable reference IDs, never names, identify records. */
(() => {
  'use strict';
  const PAGE_SIZE = 24;
  const $ = id => document.getElementById(id);
  const number = n => n.toLocaleString('ko-KR');
  const normalize = value => String(value || '').normalize('NFKC').toLocaleLowerCase('ko-KR');
  const state = { display: 'gallery', filter: 'all', query: '', page: 1, rows: [], byId: new Map(), loading: false };
  const filters = {
    all: () => true,
    illustrated: row => !!row.portrait,
    queued: row => !row.portrait,
    model: row => row.model_status !== 'not_created',
    duel: row => row.duel_playable,
    untranslated: row => !row.name_ko,
    homonym: row => row.homonym_group_size > 1
  };

  function node(tag, className, text) {
    const result = document.createElement(tag);
    if (className) result.className = className;
    if (text !== undefined) result.textContent = text;
    return result;
  }
  function name(row) { return row.name_ko || row.name_han; }
  function imagePath(row) {
    // Only catalog-owned PNGs in this static site's portrait directory are loaded.
    const path = row.portrait?.public_path;
    return typeof path === 'string' && /^portraits\/[a-z0-9_-]+\.png$/.test(path) ? path : null;
  }
  function chip(text, kind = '') { return node('span', 'officer-chip ' + kind, text); }
  function status(row) {
    const group = node('div', 'portrait-status');
    group.append(chip(row.model_status === 'not_created' ? '3D 모델 미제작' : '3D 모델 있음', row.model_status === 'not_created' ? '' : 'ready'));
    group.append(chip(row.duel_playable ? '일기토 가능' : '일기토 미구현', row.duel_playable ? 'duel' : ''));
    return group;
  }
  function placeholder(row, failed = false) {
    const box = node('div', 'portrait-placeholder' + (failed ? ' portrait-load-error' : ''));
    box.append(node('span', '', row.name_han), node('strong', '', failed ? '그림을 불러오지 못했습니다' : '일러스트 미제작'));
    box.append(node('small', '', failed ? '명부의 파일 경로를 확인해주세요' : '등록된 인물 · 원화 제작 대기'));
    return box;
  }
  function openPortrait(id) {
    const row = state.byId.get(id);
    if (!row || !imagePath(row)) return;
    const picture = $('portrait-full');
    picture.src = imagePath(row);
    picture.alt = name(row) + ' 독자 일러스트 — ' + row.art_direction;
    $('portrait-title').textContent = name(row);
    $('portrait-han').textContent = row.name_ko ? row.name_han : '한글 이름 검토 대기';
    $('portrait-direction').textContent = row.art_direction || '인물별 시각적 특징 검토 중';
    $('portrait-status').replaceChildren(...status(row).childNodes);
    $('portrait-reference').textContent = row.id;
    $('portrait-size').textContent = `${number(row.portrait.width)} × ${number(row.portrait.height)} PNG · 독자 생성 원화`;
    $('portrait-original').href = imagePath(row);
    $('portrait-dialog').showModal();
  }
  function portraitCard(row) {
    const card = node('article', 'portrait-card');
    card.dataset.officerId = row.id;
    if (imagePath(row)) {
      const button = node('button', 'portrait-button');
      button.type = 'button';
      button.setAttribute('aria-label', name(row) + ' 일러스트 크게 보기');
      const img = node('img');
      img.src = imagePath(row);
      img.alt = name(row) + ' — ' + (row.art_direction || '독자 일러스트');
      img.width = row.portrait.width;
      img.height = row.portrait.height;
      img.loading = 'lazy';
      img.decoding = 'async';
      img.addEventListener('error', () => button.replaceWith(placeholder(row, true)), { once: true });
      button.append(img, node('span', 'portrait-zoom', '크게 보기 ↗'));
      button.addEventListener('click', () => openPortrait(row.id));
      card.append(button);
    } else card.append(placeholder(row));
    const label = node('div', 'portrait-label');
    const title = node('div', 'portrait-name-row');
    title.append(node('h3', '', name(row)));
    if (row.name_ko) title.append(node('span', '', row.name_han));
    label.append(title, node('p', '', row.art_direction || (row.name_ko ? '인물별 특징 · 연의 출전 검토 대기' : '한글 이름 · 인물별 특징 검토 대기')), status(row));
    label.append(node('div', 'portrait-reference', row.id));
    card.append(label);
    return card;
  }
  function rosterRow(row) {
    const tr = node('tr');
    tr.dataset.officerId = row.id;
    const identity = node('td');
    const identityBox = node('div', 'roster-name');
    if (imagePath(row)) {
      const img = node('img', 'roster-thumb');
      img.src = imagePath(row); img.alt = ''; img.loading = 'lazy'; img.width = 40; img.height = 54;
      img.addEventListener('error', () => img.replaceWith(node('span', 'roster-thumb roster-thumb-placeholder', '—')), { once: true });
      identityBox.append(img);
    } else identityBox.append(node('span', 'roster-thumb roster-thumb-placeholder', row.name_han.slice(0, 1)));
    const names = node('div');
    names.append(node('strong', '', name(row)), node('small', '', row.name_ko ? row.name_han : '한글 이름 검토 대기'), node('code', '', row.id));
    identityBox.append(names); identity.append(identityBox); tr.append(identity);
    const artCell = node('td');
    if (imagePath(row)) {
      const link = node('button', 'roster-portrait-link', '그림 보기 ↗');
      link.type = 'button'; link.setAttribute('aria-label', name(row) + ' 일러스트 크게 보기');
      link.addEventListener('click', () => openPortrait(row.id)); artCell.append(link);
    } else artCell.append(chip('미제작'));
    const modelCell = node('td');
    modelCell.append(chip(row.model_status === 'not_created' ? '미제작' : '관절 모델 있음', row.model_status === 'not_created' ? '' : 'ready'));
    const duelCell = node('td'); duelCell.append(chip(row.duel_playable ? '선택 · 대결 가능' : '미구현', row.duel_playable ? 'duel' : ''));
    const review = node('td', 'review-note');
    if (row.homonym_group_size > 1) review.append(chip(`동일 이름 ${row.homonym_group_size}개 ID`, 'review'), node('br'));
    review.append(document.createTextNode('연의·정사 구분 검토 중'));
    tr.append(artCell, modelCell, duelCell, review);
    return tr;
  }
  function filtered() {
    const terms = normalize(state.query).split(/\s+/).filter(Boolean);
    return state.rows.filter(row => {
      // The default gallery contains produced art; explicit filters can expose queued cards.
      if (state.display === 'gallery' && state.filter === 'all' && !row.portrait) return false;
      return filters[state.filter](row) && terms.every(term => row.searchText.includes(term));
    }).sort((a, b) => state.display === 'gallery' ? a.production_priority - b.production_priority || a.reference_index - b.reference_index : a.reference_index - b.reference_index);
  }
  function render() {
    const rows = filtered();
    const pages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
    state.page = Math.max(1, Math.min(state.page, pages));
    const start = (state.page - 1) * PAGE_SIZE;
    const visible = rows.slice(start, start + PAGE_SIZE);
    const gallery = state.display === 'gallery';
    $('portrait-grid').hidden = !gallery;
    $('roster-wrap').hidden = gallery || rows.length === 0;
    $('portrait-grid').replaceChildren(...(gallery ? visible.map(portraitCard) : []));
    $('roster-body').replaceChildren(...(!gallery ? visible.map(rosterRow) : []));
    $('officer-empty').hidden = rows.length !== 0;
    $('officer-results').textContent = rows.length ? `${number(rows.length)}명 중 ${number(start + 1)}–${number(start + visible.length)}명` : '검색 결과 0명';
    $('display-note').textContent = gallery && state.filter === 'all' ? '그림이 제작된 장수만 표시합니다. 전체 명부에서 모든 인물을 찾을 수 있습니다.' : '같은 이름의 인물도 참고 ID를 따로 표시합니다.';
    $('officer-pagination').hidden = pages <= 1;
    $('page-indicator').textContent = `${state.page} / ${pages}`;
    $('page-first').disabled = $('page-prev').disabled = state.page === 1;
    $('page-last').disabled = $('page-next').disabled = state.page === pages;
    $('officer-reset').hidden = !state.query && state.filter === 'all';
    document.querySelectorAll('[data-display]').forEach(button => {
      const active = button.dataset.display === state.display;
      button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active));
    });
  }
  async function load() {
    if (state.loading) return;
    state.loading = true; $('catalog-error').hidden = true;
    try {
      const response = await fetch('officers.json');
      if (!response.ok) throw new Error('Catalog HTTP ' + response.status);
      const data = await response.json();
      if (data.schema_version !== 1 || !Array.isArray(data.officers)) throw new Error('Unknown catalog schema');
      const ids = new Set();
      for (const row of data.officers) {
        if (!/^rtk14-ref-\d{4}$/.test(row.id) || ids.has(row.id) || typeof row.name_han !== 'string') throw new Error('Invalid or duplicate reference ID');
        if (row.portrait && !imagePath(row)) throw new Error('Invalid portrait path');
        ids.add(row.id);
      }
      const artCount = data.officers.filter(row => row.portrait).length;
      const duelCount = data.officers.filter(row => row.duel_playable).length;
      const translated = data.officers.filter(row => row.name_ko).length;
      if (data.count !== ids.size || data.illustrated !== artCount || data.duel_playable !== duelCount || data.name_ko_count !== translated) throw new Error('Catalog count mismatch');
      state.rows = data.officers.map(row => ({ ...row, searchText: normalize([row.name_han, row.name_ko, row.alias, row.id, row.art_direction].join(' ')) }));
      state.byId = new Map(state.rows.map(row => [row.id, row]));
      $('roster-total').textContent = number(ids.size);
      $('portrait-total').textContent = number(artCount);
      $('model-total').textContent = number(state.rows.filter(row => row.model_status !== 'not_created').length);
      $('duel-total').textContent = number(duelCount);
      $('translation-note').textContent = `한글 이름 ${number(translated)}명 등록 · ${number(ids.size - translated)}명 표기 검토 대기`;
      const stamp = new Date(data.generated_utc);
      $('catalog-date').textContent = Number.isNaN(stamp.getTime()) ? '공개 제작 명부 스냅샷' : `명부 생성 ${stamp.toLocaleDateString('ko-KR')} · 이후 검토 및 확장 중`;
      render();
    } catch (error) {
      $('catalog-error').hidden = false;
      $('officer-results').textContent = '불러오기 실패';
      console.error('Officer catalog:', error.message);
    } finally { state.loading = false; }
  }
  document.querySelectorAll('[data-display]').forEach(button => button.addEventListener('click', () => {
    state.display = button.dataset.display; state.page = 1; render();
  }));
  $('officer-search').addEventListener('input', event => { state.query = event.target.value; state.page = 1; render(); });
  $('officer-filter').addEventListener('change', event => { state.filter = event.target.value; state.page = 1; render(); });
  $('officer-reset').addEventListener('click', () => {
    state.query = ''; state.filter = 'all'; state.page = 1;
    $('officer-search').value = ''; $('officer-filter').value = 'all'; render();
  });
  function go(page) { state.page = page; render(); $('officer-workspace').scrollIntoView({ block: 'start' }); }
  $('page-first').addEventListener('click', () => go(1));
  $('page-prev').addEventListener('click', () => go(state.page - 1));
  $('page-next').addEventListener('click', () => go(state.page + 1));
  $('page-last').addEventListener('click', () => go(Math.ceil(filtered().length / PAGE_SIZE)));
  $('portrait-close').addEventListener('click', () => $('portrait-dialog').close());
  $('portrait-dialog').addEventListener('click', event => { if (event.target === $('portrait-dialog')) $('portrait-dialog').close(); });
  $('portrait-dialog').addEventListener('close', () => { $('portrait-full').removeAttribute('src'); });
  $('catalog-retry').addEventListener('click', load);
  load();
})();
