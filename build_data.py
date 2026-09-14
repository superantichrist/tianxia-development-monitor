"""Build a curated public snapshot. Never copy project documents or private links.

Run from any directory: python project_monitor/build_data.py
Only writes monitor-data.json and monitor-data.js beside this script.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUBLIC_REFERENCE_URLS = frozenset({
    "https://www.youtube.com/watch?v=EhPbt8CLEFo",
    "https://www.youtube.com/watch?v=Qp-6yLLrPzI",
})
REVIEWED_H_PCK_SHA256 = "c23dbc83e0a80b94ba0a306f508648038576928407a74162a9e2510911c7308c"
REVIEWED_H_MODEL_SHA256 = "502ac2f3e2b39e619be15eafc22ac86f5a8bf23f2afae186f12057ce2d886595"


def read_json(relative: str) -> dict:
    path = ROOT / relative
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}


def number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def card(key, title, domain, status, milestone, summary, evidence, next_step, priority="normal"):
    return dict(id=key, title=title, domain=domain, status=status, milestone=milestone,
                summary=summary, evidence=evidence, next=next_step, priority=priority)


def current_development_evidence() -> dict:
    """Select reviewed counts, without publishing raw reports or local paths."""
    gallery = read_json("artifacts/hero-gallery-tests.json")
    heroes = gallery.get("heroes", [])
    if (gallery.get("failures") != [] or not number(gallery.get("passed")) or len(heroes) != 4
            or {hero.get("hero") for hero in heroes} != {"lubu", "guanyu", "zhangfei", "machao"}
            or not all(hero.get("authored") is True for hero in heroes)):
        raise ValueError("Four-hero gallery evidence is missing or failed")
    lubu = next(hero for hero in heroes if hero["hero"] == "lubu")
    if lubu.get("model_sha256") != REVIEWED_H_MODEL_SHA256:
        raise ValueError("The gallery model changed after the reviewed H snapshot; review and update the public scope before regeneration")
    build = read_json("build/Tianxia/build-manifest.json")
    pck_hash = build.get("packaged_sha256", {}).get("Tianxia.pck")
    if (build.get("source_unchanged_during_export_and_validation") is not True
            or not re.fullmatch(r"[0-9a-f]{64}", str(pck_hash))):
        raise ValueError("Reviewed portable build provenance is missing")
    if pck_hash != REVIEWED_H_PCK_SHA256:
        raise ValueError("The packaged build changed after the reviewed H snapshot; review and update the public scope before regeneration")
    portable = {}
    for mode in ("menu", "duel", "heroes"):
        result = read_json("artifacts/portable-validation-" + mode + ".json")
        recorded = build.get("headless_checks", {}).get(mode, {})
        if (result.get("failures") != [] or recorded.get("failures") != []
                or result.get("launch_mode") != mode or result.get("pck_sha256") != pck_hash
                or not number(result.get("passed")) or recorded.get("passed") != result["passed"]
                or result.get("version") != recorded.get("version")):
            raise ValueError("Portable launch-mode evidence differs from its reviewed build: " + mode)
        portable[mode] = int(result["passed"])
    viewer = read_json("artifacts/references/yoho/viewer-ui-validation.json")
    checks = viewer.get("checks", [])
    if viewer.get("failures") != [] or not checks or any(check.get("result") != "pass" for check in checks):
        raise ValueError("Reference viewer UI evidence is missing or failed")
    # The reviewed segments list has already checked every source and PNG hash.
    # Bind the UI attestation to that exact list, without copying its URLs/paths.
    segments_path = ROOT / "artifacts/references/yoho/segments.json"
    hashes = {name.replace("\\", "/"): value for name, value in viewer.get("files", {}).items()}
    if hashlib.sha256(segments_path.read_bytes()).hexdigest() != hashes.get("artifacts/references/yoho/segments.json"):
        raise ValueError("Reference viewer segment list changed after UI review")
    segments = read_json("artifacts/references/yoho/segments.json")
    references, ours = segments.get("references", []), segments.get("ours", [])
    if (len(references) != 2 or {item.get("source_url") for item in references} != PUBLIC_REFERENCE_URLS
            or len(ours) != 1 or not all(item.get("frames") for item in references + ours)):
        raise ValueError("Reviewed viewer requires the two public references and one H comparison")
    return {"galleryChecks": int(gallery["passed"]), "galleryHeroes": len(heroes),
            "portableByMode": portable, "portablePckSha256": pck_hash,
            "referenceVideos": len(references), "referenceFrames": sum(len(item["frames"]) for item in references),
            "comparisonFrames": len(ours[0]["frames"]), "referenceViewerUiChecks": len(checks),
            "scope": "검토된 H 중간 빌드·감상 도구·참고 영상 분석의 범위입니다. 새 공방과 발목 후보의 완료 또는 전체 프레임 시각 검수를 뜻하지 않습니다."}


def _completion_evidence(milestone: dict, milestone_id: str) -> dict:
    """Require the reviewed local movie and private-upload record before completion.

    Only booleans leave this function. Paths, account data and private video IDs
    stay in the local ledger. Pending milestones do not read a recording in flight.
    """
    proof = {"localVideoHashVerified": False, "captureEvidenceVerified": False,
             "privateUploadVerified": False}
    if milestone.get("status") != "complete":
        return proof
    if not isinstance(milestone.get("version"), str) or not milestone["version"].strip():
        raise ValueError("M05 completion requires an explicit verified milestone version")
    video, youtube = milestone.get("video"), milestone.get("youtube")
    if not isinstance(video, dict) or not isinstance(youtube, dict):
        raise ValueError("M05 completion requires actual video and private-upload evidence")
    video_path = (ROOT / str(video.get("file", ""))).resolve()
    if not within(video_path, (ROOT / "artifacts/videos").resolve()) or not video_path.is_file():
        raise ValueError("M05 completed video must exist in the local video artifact directory")
    expected_hash = video.get("sha256", "")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
        raise ValueError("M05 completion requires the reviewed video SHA-256")
    digest = hashlib.sha256()
    with video_path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_hash = digest.hexdigest()
    if actual_hash != expected_hash.lower():
        raise ValueError("M05 completed video bytes differ from the reviewed SHA-256")
    if (video.get("width"), video.get("height"), video.get("fps")) != (1920, 1080, 30):
        raise ValueError("M05 completion requires reviewed 1080p30 media")
    max_seconds = 135 if milestone_id == "M05.1" else 90
    if not number(video.get("seconds")) or not 60 <= video["seconds"] <= max_seconds:
        raise ValueError(f"{milestone_id} completion requires the validated 60–{max_seconds} second movie")
    if not isinstance(video.get("visual_qa_seconds"), list) or len(video["visual_qa_seconds"]) < 3:
        raise ValueError("M05 completion requires campaign, battle and duel visual review timestamps")
    if any(number(value) is None or not 0 <= value < video["seconds"] for value in video["visual_qa_seconds"]):
        raise ValueError("M05 visual review timestamps must lie inside the reviewed movie")
    capture_name = video.get("capture_report", f"artifacts/{milestone_id}-capture.json")
    capture_path = (ROOT / str(capture_name)).resolve()
    if not within(capture_path, (ROOT / "artifacts").resolve()) or not capture_path.is_file():
        raise ValueError("M05 completion requires its local gameplay capture report")
    capture = json.loads(capture_path.read_text(encoding="utf-8-sig"))
    if (capture.get("milestone") != milestone_id or capture.get("failures") != []
            or capture.get("performance_benchmark") is not False):
        raise ValueError("M05 gameplay capture evidence is incomplete or failed")
    screens = {chapter.get("screen") for chapter in capture.get("chapters", [])}
    if not {"campaign", "battle", "duel"}.issubset(screens):
        raise ValueError("M05 completion requires campaign, battle and duel gameplay chapters")
    campaign, battle, duel = (capture.get(key, {}) for key in ("campaign", "battle", "duel"))
    if (campaign.get("travel_distance", 0) <= 1 or battle.get("observed_hit_intents", 0) <= 0
            or sum(battle.get("casualties", [])) <= 0 or duel.get("combatants") != 2
            or len(duel.get("selected_models", [])) != 4
            or not all(model.get("authored") is True for model in duel["selected_models"])):
        raise ValueError("M05 completion requires recorded army movement, individual combat and four authored duel heroes")
    if milestone_id == "M05":
        if not duel.get("exchanges"):
            raise ValueError("M05 completion requires recorded duel exchanges")
    else:
        _validate_m051_capture(capture, video, milestone["version"])
    if (youtube.get("status") != "complete" or youtube.get("privacy") != "private"
            or not youtube.get("verified_date") or not youtube.get("verification")
            or not re.fullmatch(r"[A-Za-z0-9_-]{11}", str(youtube.get("video_id", "")))):
        raise ValueError("M05 completion requires a verified private YouTube upload record")
    return {key: True for key in proof}


def m05_completion_evidence(milestone: dict) -> dict:
    # Preserve the original M05 contract and its recorded telemetry limitation.
    return _completion_evidence(milestone, "M05")


def m051_completion_evidence(milestone: dict) -> dict:
    return _completion_evidence(milestone, "M05.1")


def _validate_m051_capture(capture: dict, video: dict, version: str) -> None:
    """Verify the stronger animation movie contract; return no private fields.

    This validates recorded coverage and review attestations, not aesthetic
    naturalness, exact weapon collision, media decoding or YouTube itself.
    """
    heroes = {"lubu", "guanyu", "zhangfei", "machao"}
    if (capture.get("version") != version or capture.get("capture_fps") != 30
            or capture.get("fixed_timestep") is not True or capture.get("automated_commands") is not True
            or video.get("fixed_timestep") is not True or video.get("automated_commands") is not True
            or video.get("performance_benchmark") is not False):
        raise ValueError("M05.1 version, fixed-timestep and automated-command disclosures must match")
    reviews = video["visual_qa_seconds"]
    if len(set(reviews)) < 6:
        raise ValueError("M05.1 requires separate visual review of campaign, battle and each of four attacking heroes")
    chapters = capture.get("chapters", [])
    for screen in ("campaign", "battle"):
        intervals = [(chapter.get("seconds"), chapters[i+1].get("seconds") if i+1 < len(chapters) else video["seconds"])
                     for i, chapter in enumerate(chapters) if chapter.get("screen") == screen]
        if not any(number(start) is not None and number(end) is not None and any(start <= moment < end for moment in reviews)
                   for start, end in intervals):
            raise ValueError("M05.1 visual review must include " + screen)
    source_hashes = capture.get("source_animation_sha256", {})
    if not isinstance(source_hashes, dict) or len(source_hashes) < 7 or not all(re.fullmatch(r"[0-9a-fA-F]{64}", str(value)) for value in source_hashes.values()):
        raise ValueError("M05.1 requires recorded animation source hashes")
    battle = capture["battle"]
    samples = battle.get("contact_samples", [])
    if not isinstance(samples, list) or not samples or battle.get("conservation") != [True, True]:
        raise ValueError("M05.1 requires contact samples and conserved soldier counts")
    def vector(value, length):
        return isinstance(value, list) and len(value) == length and all(number(v) is not None for v in value)
    pair_found = False
    for sample in samples:
        agents = sample.get("agents", [])
        if sample.get("contact_agents", 0) <= 0 or len(agents) != 2:
            continue
        if agents[0].get("id") == agents[1].get("id") or not all(agent.get("alive") == 1 for agent in agents):
            continue
        if not all(vector(agent.get("position"), 2) and vector(agent.get("velocity"), 2)
                   and all(number(agent.get(key)) is not None for key in ("facing", "attack_phase", "readiness", "movement_phase", "health"))
                   and agent.get("kind") for agent in agents):
            continue
        if any(agent.get("target_id") == agents[1-i].get("id") for i, agent in enumerate(agents)):
            pair_found = True
            break
    if not pair_found:
        raise ValueError("M05.1 requires a live sampled target pair with animation state")
    duel = capture["duel"]
    if {model.get("hero") for model in duel["selected_models"]} != heroes:
        raise ValueError("M05.1 requires four distinct authored heroes")
    bouts = duel.get("bouts", [])
    if len(bouts) != 4 or {bout.get("hero") for bout in bouts} != heroes:
        raise ValueError("M05.1 requires an actual bout for each of the four heroes")
    for bout in bouts:
        # tests/m051_capture.gd places the named hero on side 0 in every bout.
        if not any(exchange.get("source") == 0 and exchange.get("target") == 1
                   and number(exchange.get("damage")) is not None and exchange["damage"] > 0
                   for exchange in bout.get("exchanges", [])):
            raise ValueError("M05.1 lacks a damaging attack from " + bout["hero"])
        poses = [pose for pose in bout.get("samples", []) if pose.get("attacking_side") == 0]
        if not {"windup", "impact"}.issubset({pose.get("phase") for pose in poses}):
            raise ValueError("M05.1 lacks windup and contact poses for " + bout["hero"])
        for key in ("torso", "right_leg", "left_leg", "weapon_up"):
            if not poses or not all(vector(pose.get(key), 3) for pose in poses) or len({tuple(pose[key]) for pose in poses}) < 2:
                raise ValueError("M05.1 lacks changing full-body pose evidence: " + bout["hero"] + "/" + key)
        frames = [pose.get("frame") for pose in poses]
        if not all(number(frame) is not None for frame in frames) or not any(min(frames)/30 <= moment <= max(frames)/30 for moment in reviews):
            raise ValueError("M05.1 requires visual review inside the attacking bout of " + bout["hero"])


def build() -> dict:
    if not (ROOT / "docs/milestones.json").is_file():
        raise FileNotFoundError("Run this generator in the complete development workspace; published snapshots do not contain private source records")
    source = read_json("docs/milestones.json")
    milestones = {m.get("id"): m for m in source.get("milestones", [])}
    m03 = milestones.get("M03", {})
    m031 = milestones.get("M03.1", {})
    m05 = milestones.get("M05", {})
    m051 = milestones.get("M05.1", {})
    m05_proof = m05_completion_evidence(m05)
    m051_proof = m051_completion_evidence(m051)
    m05_complete = all(m05_proof.values())
    m051_complete = all(m051_proof.values())
    development = current_development_evidence()
    m05_state = "complete" if m05_complete else "in_progress"
    m051_state = "complete" if m051_complete else "in_progress"
    movie_progress = "통합 보고 영상과 비공개 업로드를 검증했습니다." if m05_complete else "통합 보고 영상과 비공개 업로드는 검증 대기 중입니다."
    complete03 = "complete" if m03.get("status") == "complete" else "in_progress"
    complete031 = "complete" if m031.get("status") == "complete" else "in_progress"
    latest_verified = m051["version"] if m051_complete else m05["version"] if m05_complete else "0.3.1" if complete031 == "complete" else "0.3.0"
    physics = read_json("artifacts/soldier-dynamics-tests.json")
    # Functional regressions can run under mixed load. Do not silently replace
    # the reviewed M05 module timing with today's concurrent test execution.
    physics_archive = read_json("artifacts/milestones/M05/evidence/soldier-dynamics-tests.json")
    if not physics_archive or physics_archive.get("failures"):
        raise ValueError("Preserved M05 module timing evidence is missing or failed")
    raw_bench = physics_archive.get("benchmark", {})
    physics_metrics = {k: number(raw_bench.get(k)) for k in (
        "agents", "contact_median_ms", "contact_p99_ms", "idle_median_ms",
        "maximum_active_agents", "maximum_pair_checks", "measured_steps", "dt")}
    physics_metrics.update({"checks": number(physics.get("passed")),
                            "contact_hits": number(physics_archive.get("contact_hits")),
                            "contact_deaths": number(physics_archive.get("contact_deaths")),
                            "timingMilestone": "M05", "timingPreserved": True,
                            "timingScope": "보존된 M05 모듈 측정. 새 병렬 회귀 실행의 시간과 구별하며 통합 FPS로 주장하지 않습니다."})
    individual_render = read_json("artifacts/individual-render-headless-tests.json")
    gpu_render = read_json("artifacts/individual-render-gpu-tests.json")
    pose = read_json("artifacts/hero-pose-tests.json")
    portable = [read_json("artifacts/portable-validation-" + mode + ".json") for mode in ("menu", "duel", "heroes")]
    ui = read_json("artifacts/ui-results.json")
    duel_sources = [read_json("artifacts/" + name) for name in (
        "duel-director-tests.json", "duel-matchups-tests.json",
        "duel-arena-tests.json", "battle-duel-ui-tests.json")]
    for result in [physics, individual_render, gpu_render, pose, ui, *portable, *duel_sources]:
        if not result or result.get("failures"):
            raise ValueError("Required current check evidence is missing or contains failures")
    physics_checks = int(physics["passed"])
    render_checks = int(individual_render["passed"])
    gpu_checks = int(gpu_render["passed"])
    gpu_verified = gpu_render.get("gpu_buffer_readback") is True
    pose_checks, pose_samples = int(pose["passed"]), int(pose["pose_samples"])
    portable_checks = sum(int(result["passed"]) for result in portable)
    ui_checks = int(ui["passed"])
    duel_checks = sum(int(result["passed"]) for result in duel_sources)
    hero_animation = read_json("artifacts/hero-animation-tests.json")
    soldier_animation = read_json("artifacts/soldier-animation-tests.json")
    for result in (hero_animation, soldier_animation):
        if not result or result.get("failures") or not number(result.get("passed")):
            raise ValueError("M05.1 animation functional evidence is missing or failed")
    hero_animation_checks = int(hero_animation["passed"])
    soldier_animation_checks = int(soldier_animation["passed"])
    soldier_pose_samples = int(soldier_animation["pose_samples"])
    roster = read_json("assets/data/officers.json")
    officers = roster.get("officers", [])
    if not officers or len({row.get("id") for row in officers}) != len(officers):
        raise ValueError("Officer catalog requires distinct reference IDs")
    roster_metrics = {"referenceEntries": len(officers), "illustrations": sum(bool(row.get("portrait")) for row in officers),
                      "models": sum(row.get("model_status") != "not_created" for row in officers),
                      "duelPlayable": sum(row.get("duel_playable") is True for row in officers),
                      "koreanNames": sum(bool(row.get("name_ko")) for row in officers)}
    if (roster.get("count") != roster_metrics["referenceEntries"] or roster.get("illustrated") != roster_metrics["illustrations"]
            or roster.get("duel_playable") != roster_metrics["duelPlayable"] or roster.get("name_ko_count") != roster_metrics["koreanNames"]):
        raise ValueError("Officer catalog count mismatch")
    roster_count, portrait_count, model_count, duel_count = (roster_metrics[key] for key in ("referenceEntries", "illustrations", "models", "duelPlayable"))
    original = read_json("tools/modding/evidence/2026-09-10-runtime/summary.json")
    original_metrics = {key: number(original.get("csv_metrics", {}).get(key)) for key in (
        "frame_count", "total_frame_time_seconds", "average_fps", "mean_frame_time_ms", "p99_frame_time_ms")}
    original_public = {
        "milestone": "M04", "runDate": "2026-09-09", "collectionDate": "2026-09-10",
        "metrics": original_metrics, "resolution": [1920, 1080],
        "controlledComparison": False, "engineTxtSummaryRecovered": False,
        "campaignObservation": "9월 10일 신규 유비 캠페인 지도·3D 군대를 조작해 초기 황건적 전투를 플레이하고 결정적 승리·캠페인 복귀를 확인했습니다. 장비 일기토 시작과 두 장수 HP는 확인했으나 개별 일기토 결과·정확한 근접 무기 동작은 미확인입니다.",
        "scope": "원작 내장 전투 CSV 전체 행의 재계산입니다. 개발 작업 일부가 겹쳤으며 장면·해상도·병력이 다른 Godot 성능과 비교하지 않습니다. 실제 캠페인 저장 생성·재실행, 리플레이 재생, 전체 모드 호환성과 품질 후보 비교는 아직 검증 중입니다.",
    }
    bench = m031.get("benchmark_near", {})
    wide = m031.get("benchmark_wide", {})
    cards = [
        card("individual", "개별 병사 전투 첫 통합", "battle", m05_state, "M05", "영속 ID·실제 위치·속도·개인 HP와 생존 목록을 전투에 연결했습니다.", f"모듈 {physics_checks}개·전투 통합 15개 검사. 렌더 연결 headless {render_checks}개와 실제 GPU {gpu_checks}개 검사를 통과했습니다. 개별 사망 후 ID 재배치·보간·LOD·그림자·행동 데이터를 GPU에서 읽어 확인했습니다. {movie_progress}", "개별 동작·전선 접촉과 대규모 플레이 품질 개선", "focus"),
        card("contact", "전선 접촉과 개별 타격", "battle", "in_progress", "M05", "접근 → 공격 준비 → 타격 → 회복. 공간 격자로 개인 접촉을 계산합니다.", "첫 분리 모델은 제한된 후보와 위치 보정을 사용합니다. 완전한 비관통 물리가 아닙니다.", "전선 후보 축소, 아군 교차, 표적 점유와 좁은 통로 검증", "focus"),
        card("terrain", "연속된 3D 캠페인 지형", "campaign", m05_state, "M05", "도시와 길이 연결된 캠페인을 높낮이가 있는 연속 지형으로 확장했습니다.", f"캠페인 지형·군대 210개 검사와 GPU 화면 확인. 실제 GPU에서 전체 UI 흐름 {ui_checks}개 검사도 통과했습니다. {movie_progress}", "캠페인 조작·지형·군대 이동의 그래픽과 플레이 품질 확장", "focus"),
        card("campaign_armies", "지도 위 3D 군대와 장수", "campaign", m05_state, "M05", "군대의 장수 모델·깃발·선택 표시를 지도에 배치하고 이동 명령에 연결했습니다.", "3D 배치·색상·선택·행군·제거를 포함한 캠페인 검사와 GPU 화면 확인. " + movie_progress, "군대 행군 동작·지형 상호작용과 전략 지도 콘텐츠 확장", "focus"),
        card("duel_mode", "별도로 실행하는 일기토 모드", "battle", m05_state, "M05", "장수 선택·두 명의 독립 교전·태세 전환·타이밍 방어·승패와 재대결을 연결했습니다.", f"일기토 합계 {duel_checks}개 headless 검사. 이후 H 개선 빌드의 메뉴 {development['portableByMode']['menu']}개·일기토 {development['portableByMode']['duel']}개·장수 감상 {development['portableByMode']['heroes']}개, 합계 {portable_checks}개 휴대 실행 검사를 통과했습니다. M05 완료 영상은 이전 빌드의 기록이며 M05.1 완료를 뜻하지 않습니다. {movie_progress}", "장수별 무기 접촉·전용 동작과 연출 확장", "focus"),
        card("hero_models", "여포 H 중간 개선과 네 장수 모델", "graphics", "in_progress", "M05.1", "여포의 머리 비례·갈라진 허벅지 갑주·얼굴과 손 재질을 보정한 H 모델을 현재 검증 빌드에 채택했습니다. 관우·장비·마초와 원화의 개성을 3D로 맞추는 작업은 계속됩니다.", f"실제 H 화면 검수와 네 모델의 포즈 {pose_checks}개 검사 / {pose_samples:,}개 표본을 확인했습니다. 손의 큰 자기 몸 관통은 개선됐으나 상대 몸통에서의 회수·얼굴 횡단·갑주와 피부의 미술 격차가 남습니다. 독립 발목 I는 제작 중인 별도 후보입니다.", "장수의 위용·얼굴 식별·재질을 원화와 맞추고 발목 후보와 가중 스키닝 검수", "focus"),
        card("hero_gallery", "네 장수의 원화·3D 동작 감상", "graphics", "complete", "M05.1 · 감상 도구", "여포·관우·장비·마초 원화와 실제 3D 모델을 나란히 보고 회전·확대·전신·얼굴·대기·공격·방어를 선택하는 별도 감상 모드를 연결했습니다.", f"감상 기능 {development['galleryChecks']}개 검사와 실제 화면 검수. 동작별 카메라 맞춤, 얼굴 보기의 무기 숨김·복구, 수동 회전·확대를 확인했습니다. 네 장수 3D 품질이나 실제 일기토 공방을 완료한 판정은 아닙니다.", "모델·클립 개선 때 얼굴·전신 구도와 동작 감상 재검수"),
        card("models", "인물·기병·말 모델 개선", "graphics", complete03, "M03", "인체 기반 얼굴, 피부 색상·노멀 재질과 병사·기병·말 8종을 개선했습니다.", "모델·재질 검사, 확대 GPU 화면, 실행 빌드와 마일스톤 영상 확인.", "골격 리깅, 보행·공격·피격 동작과 재질 품질 확장"),
        card("lod", "근접 공간 분할과 그림자 LOD", "performance", complete031, "M03.1", "가까운 공간 구역만 상세 모델로 표현해 근접 렌더 비용을 줄였습니다.", "GPU 354검사, 병사 수 보존, 동일 조건 근접·원거리 측정.", "새 개별 전투 통합 후 같은 조건에서 다시 측정"),
        card("campaign_base", "캠페인 기본 운영", "campaign", "complete", "기반", "8세력·30도시, 계절·세금·식량·민심·도시 건설·군대 운용을 연결했습니다.", "현재 기능 범위 문서에 기록된 실행 가능한 기본 시스템.", "세력별 구조·정치·경제·지도 콘텐츠를 확장"),
        card("controls", "전투 명령과 전술 기본", "battle", "complete", "기반", "배치·드래그 선택·집단 명령·진형·사기·패주·병종 상성을 구현했습니다.", "기존 부대 단위 전투 경로의 기능. 개별 병사 물리 완료를 뜻하지 않습니다.", "개인 접촉 모델과 전술 규칙의 일치 확인"),
        card("mod_tools", "모드 제작 도구와 정적 진단", "modding", "complete", "M04 · 도구", "공식 RPFM·스키마·의존성 캐시와 읽기 전용 진단 경로를 구성했습니다.", "설치 팩별 분리 진단과 복구 가능한 튜닝 후보를 준비했습니다.", "실제 원작 캠페인·전투에서 조합과 호환성 검증"),
        card("mod_runtime", "원작 모드·튜닝 플레이 비교", "modding", "in_progress", "M04", "기존 모드 구성의 내장 전투와 새 유비 캠페인에서 군대 이동·초기 전투·결정적 승리·캠페인 복귀를 실제 확인했습니다.", f"9월 9일 내장 전투 CSV {original_metrics['frame_count']:,}프레임 / {original_metrics['total_frame_time_seconds']:.3f}초, 전체 행 평균 {original_metrics['average_fps']:.3f} FPS. 9월 10일 1,263 대 721명 초기 전투와 장비 일기토 시작 확인. 일기토 개별 결과는 미확인이며 이 원작 FPS를 Godot와 비교하지 않습니다.", "실제 저장·재실행·리플레이 재생·근접 일기토·같은 조건의 품질 후보·패치 효과 확인"),
        card("soldier_animation", "상대를 향한 병사 무기와 관절 동작", "graphics", m051_state, "M05.1", "창을 교전 상대 앞으로 낮추고 칼·방패·활·쇠뇌의 서로 다른 동작을 실제 개인 공격·이동 위상에 연결했습니다.", f"Blender v4 자산 7종 × 3 LOD. {soldier_animation_checks}개 검사 / {soldier_pose_samples:,}개 자세에서 무기 길이·팔 관절·방향을 확인했습니다. GPU {gpu_checks}개 렌더 검사와 근접 화면 검수를 수행했습니다. 고정 프레임 검수는 실시간 FPS가 아닙니다.", "무기 궤적 충돌·지형 발 접지·기병과 말 동작 품질 확장", "focus"),
        card("hero_animation", "장수마다 다른 전신 공격", "graphics", m051_state, "M05.1", "Blender의 28개 컨트롤 Action을 일기토에 연결해 여포 횡베기·관우 중량 베기·장비와 마초의 찌르기에 몸통 회전과 앞발 이동을 넣었습니다.", f"장수 동작 {hero_animation_checks}개 검사, 장수마다 569프레임의 베이크와 실제 GPU 준비·타격·피격·받아치기 검수. {('통합 영상과 비공개 업로드를 확인했습니다.' if m051_complete else 'M05.1 통합 영상과 비공개 업로드는 아직 검증 중입니다.')}", "서로 맞물리는 무기 접촉·타격 후 빼기·다방향 연속기·전신 스키닝", "focus"),
        card("paired_motion", "두 장수가 맞물리는 공방과 발 접지", "battle", "in_progress", "M05.1", "진입·위협·접촉·상대 반응·무기 회수·간격 회복을 하나의 시간축과 두 인물의 이동 곡선으로 연결하는 작업을 진행합니다.", "H 첫 공격 58프레임 비교에서 몸통에 겹친 채 회복, 얼굴을 가로지르는 무기, 큰 자세 변화, HP·반응 시차와 약한 발 접지를 확인했습니다. 현재 H 빌드에는 새 맞춤 공방과 독립 발목 I 후보가 통합 완료되지 않았습니다.", "Blender 두 인물 제작 장면·접촉 표식·발목과 발바닥 앵커를 게임 재생에 연결하고 실제 근접 화면 검수", "focus"),
        card("reference_viewer", "원작·제작본 프레임 비교 도구", "tooling", "complete", "M05.1 · 참고 분석", f"공개 원작 영상 {development['referenceVideos']}개의 추출 {development['referenceFrames']}프레임과 H 첫 공격 {development['comparisonFrames']}프레임을 독립적으로 이동·재생·확대하는 로컬 비교 도구를 검증했습니다.", f"원본 PTS와 29.97·25FPS, H의 30FPS를 구분했습니다. 실제 브라우저 조작 {development['referenceViewerUiChecks']}건 통과. 주력 구간은 연속 64프레임의 잘라낸 장면표·전체 해상도 1장·간격을 둔 개요 17개를 확인했으며 전체 439장을 모두 시각 검수한 것은 아닙니다.", "두 장수의 공통 시간축·회피·낮아짐·거리 회복을 새 공방 제작과 비교 검수에 적용"),
        card("animation", "병사·말 스키닝과 지면 접지", "graphics", "planned", "후속", "현재 강체 관절과 GPU 해석 동작을 넘어 가중치 스키닝·지형 발 IK·말 골격과 발굽 접지를 확장합니다.", "M05.1의 관절 동작이 자연스러운 전신 스키닝과 접지까지 완성했다는 뜻은 아닙니다.", "발 미끄러짐과 관절 경계가 보이는 근접 장면부터 개선", "focus"),
        card("officer_roster", "가능한 많은 유니크 장수 명부", "campaign", "in_progress", "콘텐츠 확장", f"삼국지 14 공식 이름 목록 {roster_count:,}개 ID를 등록했습니다. 다른 작품의 추가 인물도 신원·출처를 확인해 확장하며 인원 상한을 두지 않습니다.", f"한글 이름 {roster_metrics['koreanNames']}명. 동명이인은 ID를 분리했습니다. 원화 {portrait_count}명·3D 모델 {model_count}명·독립 일기토 {duel_count}명이며, {roster_count:,}명이 플레이 가능하다는 뜻은 아닙니다.", "남은 한글 이름·연의와 정사 출전·중복 신원 검토 후 장수 데이터와 플레이 통합", "focus"),
        card("officer_portraits", "연의 특징을 살린 독자 장수 원화", "graphics", "in_progress", "콘텐츠 확장", f"여포·관우·장비·마초·조운·황충·전위·조조·유비·손권·제갈량·주유, 첫 {portrait_count}명의 그림을 개별 생성했습니다.", f"12개 서로 다른 1,024×1,536 PNG를 직접 검토하고 원본·게임 리소스·갤러리 사본의 SHA-256 일치를 확인했습니다. 공개 장수 명부에서 그림과 제작 상태를 볼 수 있습니다.", "다음 장수 묶음의 얼굴·복식·무기·연령을 개별 설계하고 추가 제작", "focus"),
        card("cavalry", "기병 충격과 창병 저지", "battle", "planned", "후속", "질량·속도·방향·대형을 고려한 접촉 충격과 저지 반응을 만듭니다.", "물리 설계 문서에 제안. 연속 충돌·넘어짐은 미구현 범위.", "기병 돌파와 창병 방어의 반복 가능한 충돌 장면"),
        card("siege", "공성 통로와 성벽 위 교전", "battle", "planned", "후속", "문·벽·사다리의 통로 용량과 높이 층을 전투 경로에 반영합니다.", "현재 성문·내구도·투석 규칙은 기본 구현. 성벽 위 이동은 확장 대상.", "좁은 문 통과, 열린 문·파괴된 벽 경로 변경 검사"),
        card("diplomacy", "장수·정치·외교 확장", "campaign", "planned", "M07", "인물 관계·장비·조정·복합 협상·수행 부대 구조를 확장합니다.", "기본 장수·외교·개혁은 존재하며 원작 전체 구조는 아직 없습니다.", "관계·직위·협상 기능의 플레이 시나리오 설계"),
        card("native", "시뮬레이션 병목 개선", "performance", "in_progress", "병행", "C++ 접촉 계산을 연결하고 기능·그래픽 작업과 병행해 비용을 줄였습니다.", f"{physics_checks}개 기능 검사 통과. 보존된 M05의 25,664명 상태 모듈 접촉 중앙값 {physics_metrics['contact_median_ms']:.3f}ms / p99 {physics_metrics['contact_p99_ms']:.3f}ms. 새 병렬 회귀 실행이나 통합 전투 FPS와 다른 측정입니다.", "같은 알고리즘·병력·장면의 통합 렌더 비용과 기능 결과 비교"),
        card("engine", "엔진·도구·모드 선택 재검토", "tooling", "in_progress", "매 단계", "검증된 Godot 실행을 유지하며 Blender 두 인물 제작·공유 클립 도구를 선택했습니다. Unreal·Unity·전용 엔진과 원작 모드 경로도 마일스톤마다 검토합니다.", "현재 그래픽과 공방의 격차를 다른 엔진 이전이 실제로 해소했다는 비교 증거는 없습니다. 참고 목록의 TPU모드 표기는 보존하지만 원작 무모드·단일 모드의 통제 A/B 비교는 아직 미검증입니다.", "동일 장수·동작·조명 장면의 표현과 제작 비용, 모드 호환·품질 효과를 확인"),
        card("replay", "재현 가능한 전투·리플레이", "battle", "planned", "후속", "고정 틱·명령 기록·개별 상태 저장으로 같은 전투를 재현합니다.", "동일 장비의 첫 모듈 재현 검사와 완성된 리플레이 제품을 구분합니다.", "상태 해시와 저장·복원 후 결과 일치 확인"),
    ]
    parity = [
        {"area":"캠페인·경제", "domain":"campaign", "current":"8세력·30도시, 세금·식량·민심·건설·계절, 연속 3D 지형", "gap":"전체 지도·시작 연도·세력 콘텐츠, 복잡한 자원·인구 계층", "next":"3D 지형·도시 표현과 전략 콘텐츠 확장", "level":"기반 구현"},
        {"area":"군대·장수", "domain":"campaign", "current":"복수 군대, 모병·보충·행군, 캠페인 장수 26명 데이터, 지도 위 3D 군대·장수·깃발", "gap":"수행 부대, 관계·가족·장비·직위·세밀한 보급", "next":"군대 행군 동작과 지도 상호작용 확장", "level":"기반 구현"},
        {"area":"외교·개혁", "domain":"campaign", "current":"전쟁·화친·선물·교역·동맹·통행, 개혁 8개", "gap":"복합 거래·영토 교환·속국·연합 정치·전체 개혁 트리", "next":"캠페인 구조 확장", "level":"기반 구현"},
        {"area":"개별 병사 전투", "domain":"battle", "current":"개인 위치·속도·HP·접촉·공격 모듈의 전투 연결, 상대 방향의 무기와 관절 동작", "gap":"전선 점유·아군 비관통·정교한 무기 접촉·규모 성능", "next":"개별 접촉·회수·발 접지의 실제 화면 품질 개선", "level":"M05 기반 완료 · 동작 개선 중"},
        {"area":"전술·AI", "domain":"battle", "current":"진형·상성·측후방·돌격·사기·패주, 기본 AI", "gap":"장기 작전·협공·포위·증원·세밀한 시야와 은폐", "next":"개인 접촉과 전술 규칙 결합", "level":"기반 구현"},
        {"area":"공성·물리", "domain":"battle", "current":"성문·성벽 내구도·투석·화공·중앙 진입 경로", "gap":"성벽 위 전투·사다리·공성탑·복합 도시 길 찾기", "next":"장애물과 통로 용량 모델", "level":"기반 구현"},
        {"area":"모델·재질·표현", "domain":"graphics", "current":"독자 3D 모델·2K 피부 재질·3단계 LOD·여포 H 비례와 갑주 개선·네 장수 원화/3D 감상", "gap":"원화와 3D의 미술 격차·가중 스키닝·지형 접지·말 골격·의상 품질", "next":"독립 발목 후보 검수, 장수의 위용·얼굴·갑옷 재질 개선", "level":"H 중간 개선 · 품질 제작 중"},
        {"area":"사운드·제품 완성도", "domain":"graphics", "current":"합성 배경음·북소리, 한국어 UI, 캠페인 저장", "gap":"장수 음성·전체 효과음·멀티플레이·튜토리얼·접근성", "next":"핵심 기능 검증 후 범위별 확장", "level":"기반 구현"},
        {"area":"장군 일기토", "domain":"battle", "current":"독립 모드·4장수·양손 IK·Blender 전신 동작·피격·받아치기·실제 HP와 결과, 원본/H 프레임 비교", "gap":"맞물리는 공방·상대 몸통에서의 무기 회수·얼굴 횡단·자세 전환·발 접지·가중 스키닝", "next":"공통 시간축과 두 인물 이동·접촉·반응·거리 회복을 실제 교전에 연결", "level":"M05 기반 완료 · M05.1 개선 중"},
        {"area":"유니크 장수·원화", "domain":"graphics", "current":f"공식 참고 명부 {roster_count:,}개 ID · 독자 원화 {portrait_count}명 · 3D 모델 {model_count}명 · 독립 일기토 {duel_count}명", "gap":"명부 전체 플레이 통합·추가 일러스트·한글 이름·연의와 정사 구분·다른 작품 추가 인물", "next":"인물별 출처·특징을 확인하며 원화와 장수 콘텐츠 확대", "level":"첫 제작 묶음"},
        {"area":"원작 모드·튜닝", "domain":"modding", "current":"공식 도구·내장 전투 CSV·신규 캠페인 초기 전투 승리와 지도 복귀·장비 일기토 시작", "gap":"실제 저장·재실행·리플레이 재생·근접 동작과 모드 호환성·패치 효과", "next":"같은 조건의 반복·품질 후보 비교", "level":"실행 검증 진행"},
    ]
    public_milestones = []
    for key, title, state, description in [
        ("M03", "인체 기반 모델·재질", complete03, "인물·기병·말 개선, 실행 빌드와 영상 검증"),
        ("M03.1", "근접 렌더링 개선", complete031, "25,664명 표현 유지, 공간 분할·그림자 LOD"),
        ("M04", "원작 모드·튜닝 비교", "in_progress", "내장 전투 CSV, 신규 유비 캠페인 초기 전투 승리·장비 일기토 시작·지도 복귀 확인 · 저장·품질·호환성 비교 진행"),
        ("M05", "개별 전투·3D 캠페인·4장수 일기토", m05_state, "개인 이동·접촉, 연속 지형·3D 군대, 여포·관우·장비·마초와 별도 일기토 모드"),
        ("M05.1", "병사 무기 자세·장수 전신 동작", m051_state, "여포 H 중간 개선·4장수 감상·원본 439/H 58프레임 비교 도구 확인 · 맞물리는 공방·독립 발목·가중 스키닝은 제작 중, 새 통합 영상·업로드 미완료"),
        ("후속", "접촉·공성·장수 콘텐츠·정치", "planned", "스키닝·기병 충격·성벽 경로·장수 원화와 플레이 통합·외교 확장"),
    ]:
        raw = milestones.get(key, {})
        checks = raw.get("checks", {})
        public_milestones.append(dict(id=key, title=title, status=state, description=description,
            checks={name:number(checks.get(name)) for name in ("assets", "rules", "ui", "render_lod_gpu") if number(checks.get(name)) is not None},
            videoVerified=m051_complete if key == "M05.1" else m05_complete if key == "M05" else raw.get("youtube", {}).get("privacy") == "private" and raw.get("status") == "complete" if isinstance(raw.get("youtube"), dict) else False))
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    return {
        "schemaVersion":1,
        "updatedAt":now,
        "project": {"name":"천하", "englishName":"TIANXIA", "edition":"개발 관측소", "latestVerified":latest_verified,
                    "currentMilestone":"M05.1", "currentVersion":m051.get("version", "0.4.1-dev"), "currentMilestoneTitle":"병사 무기 자세·장수 전신 동작", "goal":"캠페인부터 전장까지, 삼국지 토탈워와 동등한 수준을 최대한 추구합니다.",
                    "policy":"기능·그래픽 확장을 우선하고, 최적화를 병행합니다.",
                    "boundary":"현재는 독립 개발 중인 전략 게임입니다. 항목별 구현과 검증을 기록하며 전체 동등성이나 완성률을 주장하지 않습니다."},
        "statuses":[{"id":"in_progress", "label":"진행 중", "description":"현재 제작·통합·검증 중"}, {"id":"complete", "label":"검증 완료", "description":"카드에 적힌 범위의 근거 확인"}, {"id":"planned", "label":"다음 계획", "description":"아직 완성되지 않은 기능"}, {"id":"external", "label":"외부 검증 대기", "description":"원작 실행 등 외부 환경 확인 필요"}],
        "domains":[{"id":"battle","label":"전투·물리"},{"id":"campaign","label":"캠페인"},{"id":"graphics","label":"그래픽·동작"},{"id":"performance","label":"최적화"},{"id":"modding","label":"모드·튜닝"},{"id":"tooling","label":"엔진·도구"}],
        "cards":cards, "parity":parity, "milestones":public_milestones,
        "renderBenchmark":{"milestone":"M03.1", "nearFps":number(bench.get("average_fps")), "beforeNearFps":number(m03.get("benchmark_near", {}).get("average_fps")), "wideFps":number(wide.get("average_fps")), "nearP99Ms":number(bench.get("p99_process_frame_ms")), "initialSoldiers":number(bench.get("initial_soldiers")), "gpuChecks":number(m031.get("checks", {}).get("render_lod_gpu")), "conditions":"RTX 2080 Ti · 1600×900 · 최고 품질 · VSync 해제 · 시점별 약 10초 1회", "scope":"개별 병사 물리 통합 전 렌더 측정입니다. 모든 장면의 FPS 보장이 아닙니다. 30FPS 고정 녹화는 성능 측정과 별개입니다."},
        "physicsBenchmark":physics_metrics,
        "originalGameRuntime":original_public,
        "integrationChecks":{"individualRenderHeadless":render_checks,"individualRenderGpu":gpu_checks,"individualRenderGpuVerified":gpu_verified,"duelHeadless":duel_checks,"portableHeadless":portable_checks,"heroPoseChecks":pose_checks,"heroPoseSamples":pose_samples,"uiGpu":ui_checks,"rigidJointTwoHandIkImplemented":True,"currentMilestoneVideoVerified":m051_complete},
        "animationChecks":{"soldierChecks":soldier_animation_checks,"soldierPoseSamples":soldier_pose_samples,"heroChecks":hero_animation_checks,"scope":"기하·동작 재생 검사. 피부·관절·접지의 자연스러움과 실제 무기 충돌을 입증하는 점수는 아닙니다."},
        "developmentEvidence":development,
        "officerCatalog":{**roster_metrics, "page":"officers.html", "scope":"공식 이름 목록의 참고 ID 수이며 현재 플레이 가능한 장수 수나 전 시리즈 최대 수가 아닙니다."},
        "milestoneCompletion":{"M05":m05_proof, "M05.1":m051_proof},
        "evidencePolicy":["완료는 각 카드가 명시한 범위에만 적용합니다. 보드 카드 비율은 원작 대비 완성도가 아닙니다.", f"M05의 보존된 완료 영상과 M05.1의 새 애니메이션 작업을 구분합니다. 최신 검증 완료 버전은 {latest_verified}입니다.", "애니메이션의 관절·무기 길이 검사와 화면의 자연스러움은 다릅니다. 손·무기 관통, 접지와 실제 접촉을 영상으로 확인합니다.", "참고 프레임 추출·뷰어 검증과 실제 시각 검수 범위는 별도입니다. 두 원작 영상과 H의 FPS를 통일하거나 보간하지 않습니다.", "원작 내장 벤치마크와 독립 개발판은 장면·해상도·병력이 다릅니다. 두 FPS의 우열이나 비율을 비교하지 않습니다.", "원작 모드의 정적 경고 수를 실제 오류 수로 단정하지 않습니다. TPU 등 모드 표기 참고 자료와 무모드·단일 모드의 통제 비교를 구분합니다.", "마일스톤 영상은 비공개로 보관합니다. 확인한 공개 참고 영상 두 개만 출처에 연결하며 개인 영상·계정·로컬 원본 파일을 공개하지 않습니다."],
        "sources":[{"label":"마일스톤 상태", "source":"milestones.json의 선택된 필드", "scope":"M03·M03.1 기록, M05·M05.1의 로컬 영상·실제 캡처·비공개 업로드 근거 확인"}, {"label":"기능 범위", "source":"FEATURES.md의 수동 검토 요약", "scope":"현재 기능과 생략·단순화된 범위를 분리"}, {"label":"물리 알고리즘", "source":"BATTLE_PHYSICS.md + 보존된 M05 측정과 새 기능 검사", "scope":"첫 모듈 시간과 새 병렬 회귀 시간·통합 FPS를 구별"}, {"label":"장수와 애니메이션", "source":"OFFICER_ROSTER.md / HERO_ANIMATION.md / SOLDIER_ANIMATION.md", "scope":"명부·원화·모델·플레이 가능 수와 관절 동작·품질 차이를 구별"}, {"label":"엔진·모드 경로", "source":"ENGINE_DECISIONS.md / ORIGINAL_GAME.md 요약", "scope":"도구 준비와 실제 원작 검증을 분리"},
                   {"label":"공개 원작 참고 · YOHO요호", "source":"오호대장군 VS 전위 일기토 대전:삼국지 토탈워", "url":"https://www.youtube.com/watch?v=EhPbt8CLEFo", "scope":"199–207초 239프레임 추출. 연속 64프레임의 두 인물 진입·도약·낮아짐·거리 회복 관찰. 해당 구간 인물 이름·정확한 충돌 결과는 미확정"},
                   {"label":"공개 원작 참고 · YOHO요호", "source":"1.3.0 패치 추가 전설장수 황개 vs 여포: 일기토대전", "url":"https://www.youtube.com/watch?v=Qp-6yLLrPzI", "scope":"40–48초 200프레임 추출, 원본 25FPS 보존. 추출·뷰어 확인을 전 프레임 동작 분석 완료로 표시하지 않음"}],
        "snapshotNote":"자동 실시간 상태가 아닌 검토된 공개 스냅샷입니다. 기능 카드 분류는 담당자가 갱신하고 생성기가 허용된 수치만 추출합니다.",
    }


def validate(data: dict) -> None:
    export_check = json.loads(json.dumps(data, ensure_ascii=False))
    for source in export_check.get("sources", []):
        if "url" in source:
            if source["url"] not in PUBLIC_REFERENCE_URLS:
                raise ValueError("Only the two reviewed public reference URLs may be exported")
            source["url"] = "reviewed-public-reference"
    text = json.dumps(export_check, ensure_ascii=False)
    forbidden = [r"https?://(?:[A-Za-z0-9-]+\.)?(?:youtu\.be|youtube\.com)", r"[A-Za-z]:[\\/]", r"file://", r"https?://(?:127\.0\.0\.1|localhost)", r"artifacts[/\\]references", r"res://", r"\bUC[A-Za-z0-9_-]{22}\b", r"\b3k_[A-Za-z0-9_]+\b"]
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
    for milestone_id in ("M05", "M05.1"):
        if any(m["id"] == milestone_id and m["status"] == "complete" for m in data["milestones"]):
            proof = data.get("milestoneCompletion", {}).get(milestone_id, {})
            if not all(proof.get(key) is True for key in (
                    "localVideoHashVerified", "captureEvidenceVerified", "privateUploadVerified")):
                raise ValueError(milestone_id + " public completion requires all local-media, gameplay and private-upload attestations")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate existing snapshot without changing it")
    args = parser.parse_args()
    if args.check:
        data = json.loads((HERE / "monitor-data.json").read_text(encoding="utf-8"))
        validate(data)
        for milestone_id, verifier in (("M05", m05_completion_evidence), ("M05.1", m051_completion_evidence)):
            if any(m["id"] == milestone_id and m["status"] == "complete" for m in data["milestones"]) and (ROOT / "docs/milestones.json").is_file():
                local = next((m for m in read_json("docs/milestones.json").get("milestones", []) if m.get("id") == milestone_id), {})
                if not all(verifier(local).values()):
                    raise ValueError("Published " + milestone_id + " completion does not match verified local milestone evidence")
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
