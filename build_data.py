"""Build a curated public snapshot. Never copy project documents or private links.

Run from any directory: python project_monitor/build_data.py
Only writes monitor-data.json and monitor-data.js beside this script.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def read_json(relative: str) -> dict:
    path = ROOT / relative
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def card(key, title, domain, status, milestone, summary, evidence, next_step, priority="normal"):
    return dict(id=key, title=title, domain=domain, status=status, milestone=milestone,
                summary=summary, evidence=evidence, next=next_step, priority=priority)


def build() -> dict:
    if not (ROOT / "docs/milestones.json").is_file():
        raise FileNotFoundError("Run this generator in the complete development workspace; published snapshots do not contain private source records")
    source = read_json("docs/milestones.json")
    milestones = {m.get("id"): m for m in source.get("milestones", [])}
    m03 = milestones.get("M03", {})
    m031 = milestones.get("M03.1", {})
    complete03 = "complete" if m03.get("status") == "complete" else "in_progress"
    complete031 = "complete" if m031.get("status") == "complete" else "in_progress"
    physics = read_json("artifacts/soldier-dynamics-tests.json")
    raw_bench = physics.get("benchmark", {})
    physics_metrics = {k: number(raw_bench.get(k)) for k in (
        "agents", "contact_median_ms", "contact_p99_ms", "idle_median_ms",
        "maximum_active_agents", "maximum_pair_checks", "measured_steps", "dt")}
    physics_metrics.update({"checks": number(physics.get("passed")),
                            "contact_hits": number(physics.get("contact_hits")),
                            "contact_deaths": number(physics.get("contact_deaths"))})
    bench = m031.get("benchmark_near", {})
    wide = m031.get("benchmark_wide", {})
    cards = [
        card("individual", "병사마다 움직이는 전투", "battle", "in_progress", "M05", "영속 ID·실제 위치·속도·개인 HP와 생존 목록을 전투에 연결합니다.", "모듈 266개·전투 통합 15개 검사, 1,344명 실제 화면을 확인했습니다. 최대 규모의 통합 성능·완료 영상은 별도입니다.", "최대 병력의 렌더 ID·사망 위치·접촉 비용·전투 품질 확인", "focus"),
        card("contact", "전선 접촉과 개별 타격", "battle", "in_progress", "M05", "접근 → 공격 준비 → 타격 → 회복. 공간 격자로 개인 접촉을 계산합니다.", "첫 분리 모델은 제한된 후보와 위치 보정을 사용합니다. 완전한 비관통 물리가 아닙니다.", "전선 후보 축소, 아군 교차, 표적 점유와 좁은 통로 검증", "focus"),
        card("terrain", "연속된 3D 캠페인 지형", "campaign", "in_progress", "M05", "도시와 길이 연결된 캠페인을 높낮이가 있는 연속 지형으로 확장합니다.", "캠페인 지형·군대 210개 검사와 GPU 화면 확인. M05 통합 빌드·완료 영상은 준비 중입니다.", "통합 캠페인 조작과 지형 그래픽 품질 확인", "focus"),
        card("campaign_armies", "지도 위 3D 군대와 장수", "campaign", "in_progress", "M05", "군대의 장수 모델·깃발·선택 표시를 지도에 배치하고 이동 명령에 연결합니다.", "3D 배치·색상·선택·행군·제거를 포함한 캠페인 검사와 GPU 화면 확인. 완료 영상은 별도입니다.", "군대 선택·경로 이동·턴 전환의 통합 플레이 확인", "focus"),
        card("duel_mode", "별도로 실행하는 일기토 모드", "battle", "planned", "다음 우선", "장수 두 명의 접근·공격·방어·피격을 집중해서 플레이하는 독립 모드를 만듭니다.", "새 요청으로 범위를 정한 우선 기능. 기존 전투의 일기토 신청과 구분합니다.", "장수 선택·결투 시작·전투 조작·승패 흐름과 개인 무기 접촉 구현", "focus"),
        card("hero_models", "여포·관우·장비·마초 모델", "graphics", "planned", "다음 우선", "네 장수의 체형·얼굴·갑옷·무기를 구분하는 독자 모델을 우선 제작합니다.", "새 제작 과제. 기존 일반 장수 모델이나 인물 데이터가 이 네 모델의 완성을 뜻하지 않습니다.", "각 장수의 실루엣·무장·얼굴 제작, 리깅과 일기토 화면 연결", "focus"),
        card("models", "인물·기병·말 모델 개선", "graphics", complete03, "M03", "인체 기반 얼굴, 피부 색상·노멀 재질과 병사·기병·말 8종을 개선했습니다.", "모델·재질 검사, 확대 GPU 화면, 실행 빌드와 마일스톤 영상 확인.", "골격 리깅, 보행·공격·피격 동작과 재질 품질 확장"),
        card("lod", "근접 공간 분할과 그림자 LOD", "performance", complete031, "M03.1", "가까운 공간 구역만 상세 모델로 표현해 근접 렌더 비용을 줄였습니다.", "GPU 354검사, 병사 수 보존, 동일 조건 근접·원거리 측정.", "새 개별 전투 통합 후 같은 조건에서 다시 측정"),
        card("campaign_base", "캠페인 기본 운영", "campaign", "complete", "기반", "8세력·30도시, 계절·세금·식량·민심·도시 건설·군대 운용을 연결했습니다.", "현재 기능 범위 문서에 기록된 실행 가능한 기본 시스템.", "세력별 구조·정치·경제·지도 콘텐츠를 확장"),
        card("controls", "전투 명령과 전술 기본", "battle", "complete", "기반", "배치·드래그 선택·집단 명령·진형·사기·패주·병종 상성을 구현했습니다.", "기존 부대 단위 전투 경로의 기능. 개별 병사 물리 완료를 뜻하지 않습니다.", "개인 접촉 모델과 전술 규칙의 일치 확인"),
        card("mod_tools", "모드 제작 도구와 정적 진단", "modding", "complete", "M04 · 도구", "공식 RPFM·스키마·의존성 캐시와 읽기 전용 진단 경로를 구성했습니다.", "설치 팩별 분리 진단과 복구 가능한 튜닝 후보를 준비했습니다.", "실제 원작 캠페인·전투에서 조합과 호환성 검증"),
        card("mod_runtime", "원작 모드·튜닝 플레이 비교", "modding", "external", "M04", "원작에서 현재 모드 구성과 그래픽·병력 규모 후보를 같은 장면으로 비교합니다.", "정적 진단 완료. 실제 원작 실행을 통한 비교는 미완료입니다.", "원작 실행 접근 후 기준 장면·프레임·세이브 호환성 확인"),
        card("animation", "병사·말 골격 애니메이션", "graphics", "planned", "후속", "리깅과 보행·공격·피격·사망 상태를 개인 전투 위상에 연결합니다.", "현재 GPU 변형 동작과 구분되는 제작 과제.", "보병·말 각 1종의 골격 동작을 먼저 전투에 연결", "focus"),
        card("cavalry", "기병 충격과 창병 저지", "battle", "planned", "후속", "질량·속도·방향·대형을 고려한 접촉 충격과 저지 반응을 만듭니다.", "물리 설계 문서에 제안. 연속 충돌·넘어짐은 미구현 범위.", "기병 돌파와 창병 방어의 반복 가능한 충돌 장면"),
        card("siege", "공성 통로와 성벽 위 교전", "battle", "planned", "후속", "문·벽·사다리의 통로 용량과 높이 층을 전투 경로에 반영합니다.", "현재 성문·내구도·투석 규칙은 기본 구현. 성벽 위 이동은 확장 대상.", "좁은 문 통과, 열린 문·파괴된 벽 경로 변경 검사"),
        card("diplomacy", "장수·정치·외교 확장", "campaign", "planned", "M07", "인물 관계·장비·조정·복합 협상·수행 부대 구조를 확장합니다.", "기본 장수·외교·개혁은 존재하며 원작 전체 구조는 아직 없습니다.", "관계·직위·협상 기능의 플레이 시나리오 설계"),
        card("native", "시뮬레이션 병목 개선", "performance", "in_progress", "M05 병행", "접촉 후보와 데이터 배치를 개선하고 C++ 모듈의 비용을 비교합니다.", "첫 측정의 병목을 개선 중이며 최신 모듈 CPU 수치를 검증 탭에 공개합니다. 통합 전투 FPS와 구분합니다.", "같은 알고리즘·병력·장면으로 비용과 기능 결과 비교"),
        card("engine", "엔진·도구·모드 선택 재검토", "tooling", "in_progress", "매 단계", "Godot 개선, 다른 엔진, 전용 모듈, 원작 모드 경로를 단계마다 비교합니다.", "현재 경로는 Godot와 Blender. 다른 엔진의 우위를 아직 측정하지 않았습니다.", "기능·그래픽 효과, 제작 비용, 호환성과 성능을 함께 판단"),
        card("replay", "재현 가능한 전투·리플레이", "battle", "planned", "후속", "고정 틱·명령 기록·개별 상태 저장으로 같은 전투를 재현합니다.", "동일 장비의 첫 모듈 재현 검사와 완성된 리플레이 제품을 구분합니다.", "상태 해시와 저장·복원 후 결과 일치 확인"),
    ]
    parity = [
        {"area":"캠페인·경제", "domain":"campaign", "current":"8세력·30도시, 세금·식량·민심·건설·계절", "gap":"전체 지도·시작 연도·세력 콘텐츠, 복잡한 자원·인구 계층", "next":"연속 3D 지형과 군대 표시", "level":"기반 구현"},
        {"area":"군대·장수", "domain":"campaign", "current":"복수 군대, 모병·보충·행군, 장수 26명 데이터", "gap":"수행 부대, 관계·가족·장비·직위·세밀한 보급", "next":"지도 위 장수·깃발과 군대 이동", "level":"기반 구현"},
        {"area":"외교·개혁", "domain":"campaign", "current":"전쟁·화친·선물·교역·동맹·통행, 개혁 8개", "gap":"복합 거래·영토 교환·속국·연합 정치·전체 개혁 트리", "next":"캠페인 구조 확장", "level":"기반 구현"},
        {"area":"개별 병사 전투", "domain":"battle", "current":"개인 위치·속도·HP·접촉·공격 모듈과 통합 작업", "gap":"전선 점유·아군 비관통·정교한 무기 접촉·규모 성능", "next":"실제 전투 연결과 수치·영상 검증", "level":"개발 중"},
        {"area":"전술·AI", "domain":"battle", "current":"진형·상성·측후방·돌격·사기·패주, 기본 AI", "gap":"장기 작전·협공·포위·증원·세밀한 시야와 은폐", "next":"개인 접촉과 전술 규칙 결합", "level":"기반 구현"},
        {"area":"공성·물리", "domain":"battle", "current":"성문·성벽 내구도·투석·화공·중앙 진입 경로", "gap":"성벽 위 전투·사다리·공성탑·복합 도시 길 찾기", "next":"장애물과 통로 용량 모델", "level":"기반 구현"},
        {"area":"모델·재질·표현", "domain":"graphics", "current":"독자 3D 모델·2K 피부 재질·3단계 LOD·조명·환경", "gap":"AAA 수준 스캔·의상 세트·모션 캡처·골격 동작", "next":"리깅·개인 동작·지형 그래픽 확장", "level":"개선 진행"},
        {"area":"사운드·제품 완성도", "domain":"graphics", "current":"합성 배경음·북소리, 한국어 UI, 캠페인 저장", "gap":"장수 음성·전체 효과음·멀티플레이·튜토리얼·접근성", "next":"핵심 기능 검증 후 범위별 확장", "level":"기반 구현"},
        {"area":"원작 모드·튜닝", "domain":"modding", "current":"공식 도구·경로·스키마·분리 진단·후보 프로필", "gap":"실제 원작 플레이·세이브·모드 조합 호환성 확인", "next":"동일 장면 기준 비교", "level":"외부 검증 대기"},
    ]
    public_milestones = []
    for key, title, state, description in [
        ("M03", "인체 기반 모델·재질", complete03, "인물·기병·말 개선, 실행 빌드와 영상 검증"),
        ("M03.1", "근접 렌더링 개선", complete031, "25,664명 표현 유지, 공간 분할·그림자 LOD"),
        ("M04", "원작 모드·튜닝 비교", "external", "도구와 정적 진단 완료 · 원작 플레이 확인 대기"),
        ("M05", "개별 교전 + 3D 캠페인", "in_progress", "개인 이동·접촉·타격, 지형과 지도 위 군대"),
        ("후속", "애니메이션·공성·정치", "planned", "리깅·기병 충격·성벽 경로·장수·외교 확장"),
    ]:
        raw = milestones.get(key, {})
        checks = raw.get("checks", {})
        public_milestones.append(dict(id=key, title=title, status=state, description=description,
            checks={name:number(checks.get(name)) for name in ("assets", "rules", "ui", "render_lod_gpu") if number(checks.get(name)) is not None},
            videoVerified=raw.get("youtube", {}).get("privacy") == "private" and raw.get("status") == "complete" if isinstance(raw.get("youtube"), dict) else False))
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    return {
        "schemaVersion":1,
        "updatedAt":now,
        "project": {"name":"천하", "englishName":"TIANXIA", "edition":"개발 관측소", "latestVerified":"0.3.1" if complete031 == "complete" else "0.3.0",
                    "currentMilestone":"M05", "goal":"캠페인부터 전장까지, 삼국지 토탈워와 동등한 수준을 최대한 추구합니다.",
                    "policy":"기능·그래픽 확장을 우선하고, 최적화를 병행합니다.",
                    "boundary":"현재는 독립 개발 중인 전략 게임입니다. 항목별 구현과 검증을 기록하며 전체 동등성이나 완성률을 주장하지 않습니다."},
        "statuses":[{"id":"in_progress", "label":"진행 중", "description":"현재 제작·통합·검증 중"}, {"id":"complete", "label":"검증 완료", "description":"카드에 적힌 범위의 근거 확인"}, {"id":"planned", "label":"다음 계획", "description":"아직 완성되지 않은 기능"}, {"id":"external", "label":"외부 검증 대기", "description":"원작 실행 등 외부 환경 확인 필요"}],
        "domains":[{"id":"battle","label":"전투·물리"},{"id":"campaign","label":"캠페인"},{"id":"graphics","label":"그래픽·동작"},{"id":"performance","label":"최적화"},{"id":"modding","label":"모드·튜닝"},{"id":"tooling","label":"엔진·도구"}],
        "cards":cards, "parity":parity, "milestones":public_milestones,
        "renderBenchmark":{"milestone":"M03.1", "nearFps":number(bench.get("average_fps")), "beforeNearFps":number(m03.get("benchmark_near", {}).get("average_fps")), "wideFps":number(wide.get("average_fps")), "nearP99Ms":number(bench.get("p99_process_frame_ms")), "initialSoldiers":number(bench.get("initial_soldiers")), "gpuChecks":number(m031.get("checks", {}).get("render_lod_gpu")), "conditions":"RTX 2080 Ti · 1600×900 · 최고 품질 · VSync 해제 · 시점별 약 10초 1회", "scope":"개별 병사 물리 통합 전 렌더 측정입니다. 모든 장면의 FPS 보장이 아닙니다. 30FPS 고정 녹화는 성능 측정과 별개입니다."},
        "physicsBenchmark":physics_metrics,
        "evidencePolicy":["완료는 각 카드가 명시한 범위에만 적용합니다. 보드 카드 비율은 원작 대비 완성도가 아닙니다.", "M05는 첫 모듈 검사와 통합·규모 성능·플레이 검증을 구분합니다.", "원작 모드의 정적 경고 수를 실제 오류 수로 단정하지 않습니다.", "마일스톤 영상은 비공개로 보관합니다. 이 공개 페이지에는 영상 링크나 계정 정보를 싣지 않습니다."],
        "sources":[{"label":"마일스톤 상태", "source":"milestones.json의 선택된 필드", "scope":"M03·M03.1 상태와 수치만 자동 추출; 다음 기능은 명시적으로 분류"}, {"label":"기능 범위", "source":"FEATURES.md의 수동 검토 요약", "scope":"현재 기능과 생략·단순화된 범위를 분리"}, {"label":"물리 알고리즘", "source":"BATTLE_PHYSICS.md + 모듈 검사 결과", "scope":"설계, 첫 모듈 검사, 미구현·성능 한계 구분"}, {"label":"엔진·모드 경로", "source":"ENGINE_DECISIONS.md / ORIGINAL_GAME.md 요약", "scope":"도구 준비와 실제 원작 검증을 분리"}],
        "snapshotNote":"자동 실시간 상태가 아닌 검토된 공개 스냅샷입니다. 기능 카드 분류는 담당자가 갱신하고 생성기가 허용된 수치만 추출합니다.",
    }


def validate(data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False)
    forbidden = [r"https?://(?:www\.)?(?:youtu\.be|youtube\.com)", r"[A-Za-z]:[\\/]", r"file://", r"\bUC[A-Za-z0-9_-]{22}\b", r"\b3k_[A-Za-z0-9_]+\b"]
    for expression in forbidden:
        if re.search(expression, text, re.IGNORECASE):
            raise ValueError("Public export rejected: forbidden private/local content")
    states = {s["id"] for s in data["statuses"]}
    domains = {d["id"] for d in data["domains"]}
    ids = [c["id"] for c in data["cards"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate card ID")
    for item in data["cards"]:
        if item["status"] not in states or item["domain"] not in domains:
            raise ValueError("Unknown card status or domain")
    if any(m["id"] == "M05" and m["status"] == "complete" for m in data["milestones"]):
        raise ValueError("M05 completion requires a reviewed scope update")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate existing snapshot without changing it")
    args = parser.parse_args()
    if args.check:
        data = json.loads((HERE / "monitor-data.json").read_text(encoding="utf-8"))
        validate(data)
        expected = "window.MONITOR_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
        if (HERE / "monitor-data.js").read_text(encoding="utf-8") != expected:
            raise ValueError("JSON / JS snapshot mismatch")
        print(f"Public snapshot OK: {len(data['cards'])} cards, {len(data['parity'])} feature areas; JSON / JS match")
        return
    data = build()
    validate(data)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    (HERE / "monitor-data.json").write_text(content + "\n", encoding="utf-8")
    (HERE / "monitor-data.js").write_text("window.MONITOR_DATA = " + content + ";\n", encoding="utf-8")
    print(f"Built curated public snapshot: {len(data['cards'])} cards, {len(data['parity'])} feature areas")


if __name__ == "__main__":
    main()
