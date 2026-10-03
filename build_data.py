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
import field_review
import battle_review

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUBLIC_REFERENCE_URLS = frozenset({
    "https://www.youtube.com/watch?v=EhPbt8CLEFo",
    "https://www.youtube.com/watch?v=Qp-6yLLrPzI",
})
REVIEWED_PCK_SHA256 = "9fd7a747b7e6da7abc155170f7e4ff3f7ba43dfbcd6c114ba99e808079adc4db"
REVIEWED_CATALOG_SHA256 = "37e6dc3f81db2c4c5319cdc5df4e7d8f3085ec5bf273a71f9d2cde494e259c4a"
REVIEWED_ART_PACKAGE = ("artifacts/romance-v2-pack-validation-r2.json", "446ef927f112ab2ad69a7bf6809e8d1e3c42bbffe0dd407d5863be8efa61dda3")
REVIEWED_CURVE_SHA256 = "8eaa7adafc86b44a925f438aeed53124607c6385aa4174427ba172136f80855c"
REVIEWED_MODELS = {
    "lubu": ("assets/models/heroes/r3/lubu-i.glb", "9a5ca5628553fc95ea358a4f078c0faffcdcd7346a120c789aaa85c9fc7f1cfb"),
    "guanyu": ("assets/models/heroes/arm_v3/guanyu.glb", "53d7d92dfba7d3a40afa2fc41118d5c1233d176d1355329b1a5a64d14af7e708"),
    "zhangfei": ("assets/models/heroes/arm_v3/zhangfei.glb", "08a14d403c09da4d43bd3794257f043c9d9e9252150c8e57d5ba2a9e01056592"),
    "machao": ("assets/models/heroes/arm_v3/machao.glb", "73f44e4bfaae268721088d403735b335aa1720e340daabaaa26a9e060ef3e6ec"),
}
# Pins bind the selected counts to the reviewed report bytes, not just a green
# count from any later revision. No report object is serialized to the site.
REVIEWED_REPORTS = {
    "gallery": ("artifacts/hero-gallery-arm-v3-r1.json", "b57091fb8ab9198275190b69b195b775629c659daa1bf5eac65917232895d0d8", 127),
    "grounding": ("artifacts/hero-grounding-runtime-armv3-v4-r1.json", "7448374cbb7ea13c89d7fe332f9b3e08cd73bfe5f2694439ae4ddb242de3e3f4", 43),
    "approach": ("artifacts/duel-approach-runtime-armv3-v4-r1.json", "e9e7027063bf6bcf306a4c0821aeb25cc469f2ab8b1f84873a9714ba2cde118f", 40),
    "opponent": ("artifacts/duel-exchange-opponent-all-armv3-v4-r1.json", "86a1c89417a1a524d98205292b3af472654affe0442354344fcd61e38f7749b9", 169),
    "paired_arms": ("artifacts/hero-arms-arm-v3-paired-v4-fullmesh.json", "6ea9830b650255bb06a04c4518c148e3ffcd9516c3094881223d53dbdee1eb08", 33),
    "generic_arms": ("artifacts/hero-arms-arm-v3-generic-fullmesh.json", "21be1c393118b1e43af6c2004c44b8be0c845765350590ce7a96970ba744883c", 22),
}


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reviewed_fullbody_prototype() -> dict:
    path = ROOT / "artifacts/lubu-fullbody-prototype-release-r1.json"
    if not path.exists():
        return {}
    if file_sha256(path) != "003b0faf3af9dd0fed3a121c5cc938e9eb79ca2cb16e3c356cfc541a30ac78d5":
        raise ValueError("Reviewed full-body prototype release changed")
    doc = read_json("artifacts/lubu-fullbody-prototype-release-r1.json")
    if (doc.get("production_adopted") is not False or doc.get("paired_fight") is not False
            or doc.get("deform_bones") != 64 or doc.get("skinned_meshes") != 17
            or doc.get("range_frames") != 240 or doc.get("bone_matrix_observations") != 384
            or doc.get("registered_skin_cpu_bake_checks") != 102):
        raise ValueError("Full-body prototype scope differs from reviewed evidence")
    model = ROOT / "artifacts/rig-prototypes/fullbody-v3/lubu.glb"
    if file_sha256(model) != doc.get("model_sha256"):
        raise ValueError("Reviewed full-body model changed")
    for relative, expected in doc["sources"].items():
        source = (ROOT / relative).resolve()
        source.relative_to(ROOT.resolve())
        if file_sha256(source) != expected:
            raise ValueError("Full-body prototype evidence changed")
    return {"deformBones":64,"skinnedMeshes":17,"rangeFrames":240,"boneMatrices":384,
            "registeredCpuBakes":102,"productionAdopted":False,"pairedFight":False}


def reviewed_paired_authoring() -> dict:
    latest = ROOT / "artifacts/paired-fullbody-authoring-release-r2.json"
    if latest.exists():
        if file_sha256(latest) != "7b3786d1c00568a6d947080ca142eb6680ff01eeb935171f3dbd27a0b935b025":
            raise ValueError("Reviewed corrected paired authoring release changed")
        doc = read_json("artifacts/paired-fullbody-authoring-release-r2.json")
        expected = {"status":"targeted_authoring_constraints_verified","revision":"zl_phrase_v14",
                    "production_adopted":False,"naturalness_accepted":False,"battle_outcomes_integrated":False,
                    "deform_bones":128,"skinned_meshes":32,"authored_frames":480,
                    "bone_matrix_observations":1024,"registered_skin_cpu_bakes":256,
                    "finite_mesh_review_frames":480,"finite_mesh_review_passed":True,"paired_pole_observations":3840}
        if any(doc.get(key) != value for key,value in expected.items()):
            raise ValueError("Corrected paired authoring exceeds its reviewed scope")
        for name,digest in doc["sources"].items():
            source = (ROOT/name).resolve()
            source.relative_to(ROOT.resolve())
            if file_sha256(source) != digest:
                raise ValueError("Corrected paired authoring evidence changed")
        mesh = read_json("artifacts/zl-phrase-mesh-r6.json")
        poles = read_json("artifacts/zl-phrase-poles-r2.json")
        gpu = read_json("artifacts/zl-phrase-gpu-r9.json")
        if (mesh.get("failures") != [] or mesh.get("checked_frames") != 480
                or mesh.get("weapon_pairs_with_crossing_frames") or mesh.get("forearm_pairs_with_crossing_frames")
                or mesh.get("source_unchanged") is not True or poles.get("failures") != []
                or len(poles.get("observations",[])) != 3840 or gpu.get("failures") != []
                or len(gpu.get("registered_skin_cpu_bakes",[])) != 256):
            raise ValueError("Corrected paired authoring does not match actual reviewed results")
        return {"deformBones":128,"skins":32,"frames":480,"productionAdopted":False,"clearancePassed":True}
    relative = "artifacts/paired-fullbody-authoring-release-r1.json"
    path = ROOT / relative
    if not path.exists():
        return {}
    if file_sha256(path) != "987f3c45bfb936028018207a20203e31b7a31b5b9d9bf7abe8ea81f77d6c5e34":
        raise ValueError("Reviewed paired authoring release changed")
    doc = read_json(relative)
    expected = {"status":"rejected_clearance_candidate_preserved", "revision":"zl_phrase_v11",
                "production_adopted":False,"naturalness_accepted":False,"battle_outcomes_integrated":False,
                "deform_bones":128,"skinned_meshes":32,"authored_frames":480,
                "bone_matrix_observations":1024,"registered_skin_cpu_bakes":256,
                "finite_mesh_review_frames":480,"finite_mesh_review_passed":False,
                "independent_triangle_crossing_confirmations":30,"rest_forearm_body_overlap_detected":True}
    if any(doc.get(key) != value for key,value in expected.items()):
        raise ValueError("Paired authoring scope differs from reviewed failed candidate")
    for name,digest in doc["sources"].items():
        source = (ROOT / name).resolve()
        source.relative_to(ROOT.resolve())
        if file_sha256(source) != digest:
            raise ValueError("Paired authoring evidence changed")
    gpu = read_json("artifacts/zl-phrase-gpu-r6.json")
    mesh = read_json("artifacts/zl-phrase-mesh-r3.json")
    if (gpu.get("failures") != [] or gpu.get("source_unchanged") is not True
            or len(gpu.get("registered_skin_cpu_bakes",[])) != 256
            or mesh.get("checked_frames") != 480 or not mesh.get("failures")
            or mesh.get("source_unchanged") is not True):
        raise ValueError("Paired authoring must distinguish import passes and clearance failures")
    return {"deformBones":128,"skins":32,"frames":480,"productionAdopted":False,"clearancePassed":False}


def reviewed_contact_window_research() -> dict:
    relative = "artifacts/duel-phrase-contact-research-r1.json"
    path = ROOT / relative
    if not path.exists():
        return {}
    if file_sha256(path) != "9adcee1fad8a5b9afe7e3b463d6f1ab76f6c54ea656d75ddda7ba6266a009c2c":
        raise ValueError("Reviewed contact/transition research changed")
    doc = read_json(relative)
    expected = {"status":"actual_contact_window_verified_response_and_transitions_unfinished",
                "production_adopted":False,"naturalness_accepted":False,"reaction_accepted":False,
                "playable_input_branches_integrated":False,"original_quality_achieved":False,
                "geometry_assets":3,"geometry_poses_per_asset":67,"actual_window_cases":12,
                "sample_rate":60,"first_observed_blade_frame":100,"first_observed_blade_seconds":1.65,
                "weapon_body_crossing_frames":33,"legacy_all_weapon_clearance_gate_passed":False,
                "prefix_common_last_frame":76,"prefix_first_different_frame":77,
                "gpu_bone_observations":1024,"registered_engine_cpu_skin_bakes":256,
                "gpu_vertex_buffer_readback":False}
    if any(doc.get(key) != value for key,value in expected.items()):
        raise ValueError("Contact-window research exceeds reviewed scope")
    for name,digest in doc["sources"].items():
        source = (ROOT/name).resolve()
        source.relative_to(ROOT.resolve())
        if file_sha256(source) != digest:
            raise ValueError("Contact-window evidence changed")
    mesh = read_json("artifacts/zl-phrase-open-mesh-r4.json")
    windows = read_json("artifacts/duel-phrase-window-probe-r1.json")
    transition = read_json("artifacts/duel-phrase-transition-audit-r1.json")
    if (mesh.get("source_unchanged") is not True or mesh.get("forearm_pairs_with_crossing_frames") != {}
            or mesh.get("weapon_pairs_with_crossing_frames") != {"A_WeaponMesh -> B_TorsoMesh":list(range(100,133))}
            or mesh.get("failures") != ["Actual weapon/head-or-torso surface crossings in authored candidate"]
            or windows.get("failures") != [] or len(windows.get("runs",[])) != 12
            or windows.get("sources_before") != windows.get("sources_after")
            or transition.get("first_different_frame",{}).get("frame") != 77):
        raise ValueError("Contact research must preserve remaining crossings and transition gaps")
    for run in windows["runs"]:
        hit = "zl_phrase_open_v8" in run["model"]
        history = run.get("history",[])
        if len(history) != 1:
            raise ValueError("Contact window resolves once")
        result = history[0]["result"]
        if (result.get("accepted") is not True or result.get("outcome") != ("hit" if hit else "miss")
                or result.get("time") != (1.65 if hit else 2.5)
                or run.get("hero_hp") != ([100.0,88.0] if hit else [100.0,100.0])):
            raise ValueError("Contact window does not match actual geometry-gated HP")
    return {"cases":12,"sampleHz":60,"bodyCrossingFrames":33,"productionAdopted":False}


def reviewed_reactive_first_strike() -> dict:
    relative = "artifacts/duel-reactive-first-strike-release-r1.json"
    path = ROOT / relative
    if not path.exists():
        return {}
    if file_sha256(path) != "9855d7b55f729b39a0db58b7911f18922b1c0b4481dfcca47c198044e0be9931":
        raise ValueError("Reviewed first-strike release changed")
    doc = read_json(relative)
    expected = {"status":"first_body_reaction_reviewed_flat_stage","revision":"zl_phrase_hit_v4",
                "production_adopted":False,"naturalness_accepted":False,"full_battle_integrated":False,
                "later_damage_windows_integrated":False,"next_phrase_graph_integrated":False,
                "first_body_window_integrated":True,"paired_reaction_contract_verified":True,
                "deform_bones":128,"skin_meshes":32,"authoring_frames":480,
                "finite_self_forearm_crossings_detected":False,"expected_weapon_body_crossing_frames":6,
                "legacy_all_weapon_clearance_gate_passed":False,"shared_response_prefix_last_frame":100,
                "contract_checks":183,"intent_dt_cases":15,"rendered_engine_input_events":4,
                "rendered_skin_cpu_bakes":288,"asset_gpu_bone_observations":1024,
                "asset_registered_skin_cpu_bakes":256,"paired_pole_observations":3840,
                "compiled_skin_comparisons":288,"compiled_skin_maximum_reference_error_m":0.0}
    if any(doc.get(key) != value for key,value in expected.items()):
        raise ValueError("First-strike prototype exceeds reviewed scope")
    for name,digest in doc["sources"].items():
        source=(ROOT/name).resolve();source.relative_to(ROOT.resolve())
        if file_sha256(source) != digest:
            raise ValueError("First-strike evidence changed")
    mesh=read_json("artifacts/zl-hit-recoil-mesh-r4.json")
    contract=read_json("artifacts/duel-phrase-reactive-contract-r3.json")
    gpu=read_json("artifacts/duel-reactive-gpu-r3.json")
    if (mesh.get("checked_frames") != 480 or mesh.get("source_unchanged") is not True
            or mesh.get("forearm_pairs_with_crossing_frames") != {}
            or mesh.get("weapon_pairs_with_crossing_frames") != {"A_WeaponMesh -> B_TorsoMesh":list(range(100,106))}
            or mesh.get("failures") != ["Actual weapon/head-or-torso surface crossings in authored candidate"]
            or contract.get("passed") != 183 or contract.get("failures") != []
            or len(contract.get("cases",[])) != 15 or gpu.get("failures") != []
            or gpu.get("hero_hp") != [100.0,88.0] or len(gpu.get("registered_skin_cpu_bakes",[])) != 288):
        raise ValueError("First-strike data does not match actual prototype results")
    return {"cases":15,"checks":183,"productionAdopted":False,"naturalnessAccepted":False}


def reviewed_three_exchanges() -> dict:
    relative="artifacts/duel-phrase-three-exchanges-release-r1.json"
    path=ROOT/relative
    if not path.exists():return {}
    if file_sha256(path)!="194f96a0e6597c8b402239caa05442211b3fc36441e7cd5d00682a73dc1e5c88":
        raise ValueError("Reviewed three-window release changed")
    doc=read_json(relative)
    expected={"status":"three_contact_windows_reviewed_flat_stage","production_adopted":False,
              "naturalness_accepted":False,"normal_battle_integrated":False,
              "later_weapon_windows_integrated":True,"later_body_reactions_integrated":False,
              "next_phrase_graph_integrated":False,"actual_contact_windows":3,"contract_checks":144,
              "intent_dt_cases":15,"actual_contour_pose_observations":212,
              "independent_segment_oracle_cases":105,"total_registered_skin_cpu_bakes":864,
              "total_rendered_engine_key_events":12}
    if any(doc.get(k)!=v for k,v in expected.items()):raise ValueError("Three-window scope exceeds actual prototype")
    for name,digest in doc["sources"].items():
        source=(ROOT/name).resolve();source.relative_to(ROOT.resolve())
        if file_sha256(source)!=digest:raise ValueError("Three-window evidence changed")
    contract=read_json("artifacts/duel-phrase-exchange-contract-r2.json")
    if contract.get("failures")!=[] or contract.get("passed")!=144 or len(contract.get("cases",[]))!=15:
        raise ValueError("Three-window contract does not match actual cases")
    for name,outcomes in {"threat":["hit","parried","parried"],"guard":["parried"]*3,"miss":["miss","parried","parried"]}.items():
        gpu=read_json(f"artifacts/duel-exchange-{name}-gpu-r2.json")
        if (gpu.get("failures")!=[] or [r["result"]["outcome"] for r in gpu.get("history",[])]!=outcomes
                or len(gpu.get("registered_skin_cpu_bakes",[]))!=288 or len(gpu.get("input_events",[]))!=4
                or gpu.get("hero_hp")!=([100.0,88.0] if name=="threat" else [100.0,100.0])):
            raise ValueError("Three rendered choices disagree with reviewed contacts")
    return {"windows":3,"checks":144,"productionAdopted":False}


def reviewed_report(key: str) -> dict:
    name, expected, count = REVIEWED_REPORTS[key]
    path = ROOT / name
    if not path.is_file() or file_sha256(path) != expected:
        raise ValueError("Reviewed report bytes changed: " + key)
    report = read_json(name)
    if report.get("passed") != count or report.get("failures") != []:
        raise ValueError("Reviewed report count or failures changed: " + key)
    for before, after in (("sources_before", "sources_after"), ("sources", "after"), ("source_hashes", "after_hashes")):
        if before in report and (not report[before] or report[before] != report.get(after)):
            raise ValueError("Report does not attest stable inputs: " + key)
    return report


def current_art_package(pck_hash: str) -> dict:
    name, expected = REVIEWED_ART_PACKAGE
    path = ROOT / name
    if not path.is_file() or file_sha256(path) != expected:
        raise ValueError("Packed-art report changed after review")
    report = read_json(name)
    new_paths = {"res://assets/portraits/romance_v2/"+hero+".png" for hero in ("sunce","zhangliao","diaochan","lumeng")}
    actual_new = {row.get("path") for row in report.get("portraits",[]) if "/romance_v2/" in row.get("path","")}
    if (report.get("passed") != 95 or report.get("failures") != [] or report.get("pck_sha256") != pck_hash
            or report.get("catalog_sha256") != REVIEWED_CATALOG_SHA256 or report.get("portrait_count") != 16
            or report.get("playable_count") != 4 or report.get("model_count") != 4
            or len(report.get("portraits",[])) != 16 or actual_new != new_paths
            or len(report.get("excluded_prototype_resources",[])) != 20):
        raise ValueError("Packed-art scope must remain 16 portraits, four playable/models, and excluded prototypes")
    if not (ROOT / "assets/data/officers.json").is_file() or file_sha256(ROOT / "assets/data/officers.json") != REVIEWED_CATALOG_SHA256:
        raise ValueError("Officer catalog changed after the reviewed art package")
    return {"artPackageChecks":95,"packedPortraits":16,"catalogSha256":REVIEWED_CATALOG_SHA256,
            "artRevision":"romance_v2", "experimentalPelvisAssetsPackaged":False,
            "artCaptureScope":"손책·장료·초선·여몽 원화는 기존 M05.1 영상 촬영 이후 추가했습니다. 새 네 장수의 3D 모델·플레이 통합은 미완료입니다."}


def current_development_evidence() -> dict:
    """Select reviewed counts, without publishing raw reports or local paths."""
    manifest = read_json("build/Tianxia-flow/build-manifest.json") if (ROOT/"build/Tianxia-flow/build-manifest.json").exists() else read_json("build/Tianxia/build-manifest.json")
    if manifest.get("packaged_sha256", {}).get("Tianxia.pck") == field_review.PCK:
        return field_review.read(ROOT)
    reports = {key: reviewed_report(key) for key in REVIEWED_REPORTS}
    gallery = reports["gallery"]
    heroes = gallery.get("heroes", [])
    if (gallery.get("failures") != [] or not number(gallery.get("passed")) or len(heroes) != 4
            or {hero.get("hero") for hero in heroes} != {"lubu", "guanyu", "zhangfei", "machao"}
            or not all(hero.get("authored") is True for hero in heroes)):
        raise ValueError("Four-hero gallery evidence is missing or failed")
    for hero in heroes:
        path, expected = REVIEWED_MODELS[hero["hero"]]
        if (hero.get("model_sha256") != expected or hero.get("model") != "res://" + path
                or not (ROOT / path).is_file() or file_sha256(ROOT / path) != expected):
            raise ValueError("The gallery model changed after the reviewed I/arm_v3 snapshot")
    build = read_json("build/Tianxia/build-manifest.json")
    pck_hash = build.get("packaged_sha256", {}).get("Tianxia.pck")
    if (build.get("source_unchanged_during_export_and_validation") is not True
            or not re.fullmatch(r"[0-9a-f]{64}", str(pck_hash))):
        raise ValueError("Reviewed portable build provenance is missing")
    if pck_hash != REVIEWED_PCK_SHA256 or file_sha256(ROOT / "build/Tianxia/Tianxia.pck") != pck_hash:
        raise ValueError("The packaged build changed after the reviewed I/arm_v3/v4 snapshot")
    art = current_art_package(pck_hash)
    build_sources = build.get("source_sha256", {})
    for name, expected in build_sources.items():
        path = (ROOT / name).resolve()
        if not within(path, ROOT.resolve()) or not path.is_file() or file_sha256(path) != expected:
            raise ValueError("Current source differs from the reviewed build: " + name)
    for path, expected in [*REVIEWED_MODELS.values(), ("assets/animations/duel-exchanges.json", REVIEWED_CURVE_SHA256)]:
        if build_sources.get(path) != expected:
            raise ValueError("Reviewed model/curve is missing from the build source identity")
    portable = {}
    for mode in ("menu", "duel", "heroes"):
        result = read_json("artifacts/portable-validation-" + mode + ".json")
        recorded = build.get("headless_checks", {}).get(mode, {})
        if (result.get("failures") != [] or recorded.get("failures") != []
                or result.get("launch_mode") != mode or result.get("pck_sha256") != pck_hash
                or result.get("passed") != 76 or recorded.get("passed") != result["passed"]
                or result.get("version") != recorded.get("version")):
            raise ValueError("Portable launch-mode evidence differs from its reviewed build: " + mode)
        portable[mode] = int(result["passed"])
    opponent = reports["opponent"]
    pairs = opponent.get("pairs", [])
    expected_pairs = {(a, b) for a in range(4) for b in range(4) if a != b}
    if (len(pairs) != 12 or {(p.get("attacker"), p.get("defender")) for p in pairs} != expected_pairs
            or opponent.get("fps") != 240 or opponent.get("total_actor_pair_frames") != 20592
            or opponent.get("candidate_curve") != "" or opponent.get("zero_baseline_control") is not False
            or opponent.get("source_hashes", {}).get("res://assets/animations/duel-exchanges.json") != REVIEWED_CURVE_SHA256):
        raise ValueError("Opponent evidence must cover the actual adopted roster, all 12 directions at 240Hz")
    for pair in pairs:
        if len(pair.get("frames", [])) != 1716 or set(pair.get("summary", {})) != {"hit", "blocked", "parried", "miss"}:
            raise ValueError("Opponent evidence lacks all four full sampled outcomes")
        for outcome, values in pair["summary"].items():
            if values.get("head_frames") != [] or values.get("precontact_torso_frames") != []:
                raise ValueError("Opponent evidence contains sampled head or early-body overlap")
            if (outcome == "hit") != bool(values.get("torso_frames")):
                raise ValueError("Opponent body results differ from the reviewed hit/defense contract")
        for model in pair.get("models", []):
            path, expected = REVIEWED_MODELS[model["hero"]]
            provenance = model.get("provenance", {})
            before = provenance.get("before_load", {})
            if (model.get("model_path") != "res://" + path or before.get("model_sha256") != expected
                    or before != provenance.get("after_trace")):
                raise ValueError("Opponent model differs from adopted model evidence")
    for key, expected_heroes, poses in (("paired_arms", set(REVIEWED_MODELS), 600),
                                      ("generic_arms", set(REVIEWED_MODELS) - {"lubu"}, 2901)):
        report = reports[key]
        if (report.get("full_unique_vertices") is not True or report.get("poses") != poses
                or {h.get("hero") for h in report.get("heroes", [])} != expected_heroes):
            raise ValueError("Arm evidence does not cover the reviewed full-mesh pose set")
        for hero in report["heroes"]:
            if hero.get("after", {}).get("model_sha256") != REVIEWED_MODELS[hero["hero"]][1]:
                raise ValueError("Arm audit model differs from current adopted model")
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
    return {**art, "galleryChecks": int(gallery["passed"]), "galleryHeroes": len(heroes),
            "portableByMode": portable, "portablePckSha256": pck_hash,
            "modelRevisions": {"lubu":"I", "guanyu":"arm_v3", "zhangfei":"arm_v3", "machao":"arm_v3"},
            "modelSha256": {hero: entry[1] for hero, entry in REVIEWED_MODELS.items()},
            "pairedCurveRevision":"v4", "pairedCurveSha256":REVIEWED_CURVE_SHA256,
            "groundingChecks":reports["grounding"]["passed"], "approachChecks":reports["approach"]["passed"],
            "pairedOpponentChecks":opponent["passed"], "pairedMatchups":len(pairs), "pairedSampleHz":240,
            "pairedActorPairPoses":opponent["total_actor_pair_frames"],
            "pairedArmChecks":reports["paired_arms"]["passed"], "genericArmChecks":reports["generic_arms"]["passed"],
            "referenceVideos": len(references), "referenceFrames": sum(len(item["frames"]) for item in references),
            "comparisonFrames": len(ours[0]["frames"]), "referenceViewerUiChecks": len(checks),
            "referenceSnapshot":"과거 H 첫 공격 비교 도구의 검증 기록",
            "scope": "현재 I/arm_v3 모델·v4 공방과 원화 16장을 포함한 휴대 실행본입니다. 기존 여섯 동작/형상 보고서의 코드·곡선·모델은 동일합니다. 한 축 envelope와 어깨 접합부 제외 조건이 있으며 연속 충돌·자연스러움·M05.1 완료를 뜻하지 않습니다. 새 네 원화는 기존 영상 이후 추가됐고 pelvis/짝 공방 실험 후보는 배포하지 않았습니다. 참고 뷰어는 과거 H 스냅샷입니다."}


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
        "duel-field-arena-flow-r3.json" if development.get("currentRevision")=="field-v4" else "duel-arena-tests.json", "battle-duel-ui-tests.json")]
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
        card("duel_mode", "별도로 실행하는 일기토 모드", "battle", m05_state, "M05", "장수 선택·두 명의 독립 교전·태세 전환·타이밍 방어·승패와 재대결을 연결했습니다.", f"현재 I/arm_v3·v4 빌드의 메뉴 {development['portableByMode']['menu']}개·일기토 {development['portableByMode']['duel']}개·장수 감상 {development['portableByMode']['heroes']}개, 합계 {portable_checks}개 휴대 실행 검사를 통과했습니다. M05 완료 영상은 이전 빌드의 기록이며 M05.1 완료를 뜻하지 않습니다.", "장수별 무기 접촉·전용 동작과 연출 확장", "focus"),
        card("hero_models", "여포 I와 세 장수의 상완·발목 개선", "graphics", "in_progress", "M05.1", "여포 I와 관우·장비·마초 arm_v3를 실제 명단과 새 실행본에 채택했습니다. 독립 발목을 유지하면서 어깨·상완 연결을 수정했습니다.", f"현재 모델의 모든 팔 정점 표본 검사: 공방 {development['pairedArmChecks']}개·일반 동작 {development['genericArmChecks']}개 통과. 한 축 몸통 envelope이며 어깨 접합부 상단 30%는 제외합니다. 원화와 3D의 얼굴·갑주·피부 격차, 강체 관절과 가중 스키닝 과제는 남습니다.", "장수의 위용·얼굴 식별·재질을 원화와 맞추고 골반·흉곽·옷의 변형 개선", "focus"),
        card("hero_gallery", "네 장수의 원화·3D 동작 감상", "graphics", "complete", "M05.1 · 감상 도구", "여포·관우·장비·마초 원화와 실제 3D 모델을 나란히 보고 회전·확대·전신·얼굴·대기·공격·방어를 선택하는 별도 감상 모드를 연결했습니다.", f"현재 네 모델로 감상 기능 {development['galleryChecks']}개 headless 검사 통과. 동작별 구도, 얼굴 보기 무기 숨김·복구와 수동 조작 보존을 검사했습니다. 모델 품질이나 실제 일기토의 자연스러움 완료 판정은 아닙니다.", "모델·클립 개선 때 얼굴·전신 구도와 실제 화면 동작 감상 재검수"),
        card("models", "인물·기병·말 모델 개선", "graphics", complete03, "M03", "인체 기반 얼굴, 피부 색상·노멀 재질과 병사·기병·말 8종을 개선했습니다.", "모델·재질 검사, 확대 GPU 화면, 실행 빌드와 마일스톤 영상 확인.", "골격 리깅, 보행·공격·피격 동작과 재질 품질 확장"),
        card("lod", "근접 공간 분할과 그림자 LOD", "performance", complete031, "M03.1", "가까운 공간 구역만 상세 모델로 표현해 근접 렌더 비용을 줄였습니다.", "GPU 354검사, 병사 수 보존, 동일 조건 근접·원거리 측정.", "새 개별 전투 통합 후 같은 조건에서 다시 측정"),
        card("campaign_base", "캠페인 기본 운영", "campaign", "complete", "기반", "8세력·30도시, 계절·세금·식량·민심·도시 건설·군대 운용을 연결했습니다.", "현재 기능 범위 문서에 기록된 실행 가능한 기본 시스템.", "세력별 구조·정치·경제·지도 콘텐츠를 확장"),
        card("controls", "전투 명령과 전술 기본", "battle", "complete", "기반", "배치·드래그 선택·집단 명령·진형·사기·패주·병종 상성을 구현했습니다.", "기존 부대 단위 전투 경로의 기능. 개별 병사 물리 완료를 뜻하지 않습니다.", "개인 접촉 모델과 전술 규칙의 일치 확인"),
        card("mod_tools", "모드 제작 도구와 정적 진단", "modding", "complete", "M04 · 도구", "공식 RPFM·스키마·의존성 캐시와 읽기 전용 진단 경로를 구성했습니다.", "설치 팩별 분리 진단과 복구 가능한 튜닝 후보를 준비했습니다.", "실제 원작 캠페인·전투에서 조합과 호환성 검증"),
        card("mod_runtime", "원작 모드·튜닝 플레이 비교", "modding", "in_progress", "M04", "기존 모드 구성의 내장 전투와 새 유비 캠페인에서 군대 이동·초기 전투·결정적 승리·캠페인 복귀를 실제 확인했습니다.", f"9월 9일 내장 전투 CSV {original_metrics['frame_count']:,}프레임 / {original_metrics['total_frame_time_seconds']:.3f}초, 전체 행 평균 {original_metrics['average_fps']:.3f} FPS. 9월 10일 1,263 대 721명 초기 전투와 장비 일기토 시작 확인. 일기토 개별 결과는 미확인이며 이 원작 FPS를 Godot와 비교하지 않습니다.", "실제 저장·재실행·리플레이 재생·근접 일기토·같은 조건의 품질 후보·패치 효과 확인"),
        card("soldier_animation", "상대를 향한 병사 무기와 관절 동작", "graphics", m051_state, "M05.1", "창을 교전 상대 앞으로 낮추고 칼·방패·활·쇠뇌의 서로 다른 동작을 실제 개인 공격·이동 위상에 연결했습니다.", f"Blender v4 자산 7종 × 3 LOD. {soldier_animation_checks}개 검사 / {soldier_pose_samples:,}개 자세에서 무기 길이·팔 관절·방향을 확인했습니다. GPU {gpu_checks}개 렌더 검사와 근접 화면 검수를 수행했습니다. 고정 프레임 검수는 실시간 FPS가 아닙니다.", "무기 궤적 충돌·지형 발 접지·기병과 말 동작 품질 확장", "focus"),
        card("hero_animation", "장수마다 다른 전신 공격", "graphics", m051_state, "M05.1", "장수별 공격과 양손 IK를 유지하며 v4 공방에서 장비·마초의 바깥 진입, 관우·장비의 낮은 후속 궤적을 연결했습니다.", "실제 GPU 구간을 프레임 단위로 비교했습니다. 준비·회수의 긴 멈춤, 단단한 허리 회전과 약한 반발·체중 전달은 아직 보입니다. " + ("통합 영상과 비공개 업로드를 확인했습니다." if m051_complete else "M05.1 통합 영상의 로컬 검수는 완료했고 비공개 업로드를 기다립니다. 새 네 장수 원화는 이 영상 촬영 이후 추가했습니다."), "두 무기가 실제 맞닿는 저작 접점, 받아내는 체중과 연속적인 회수 동작", "focus"),
        card("paired_motion", "두 장수의 v4 공방과 실제 바닥 접지", "battle", "in_progress", "M05.1", "두 장수의 공통 시간축, 접근→준비 자세 연결과 모델별 실제 밑창 높이를 경기장 바닥에 맞췄습니다. 장병기의 이른 몸통 진입과 방어 후 회수 경로를 수정했습니다.", f"현 명단 {development['pairedMatchups']}개 공격 방향 × 4결과, {development['pairedSampleHz']}Hz·{development['pairedActorPairPoses']:,}개 두 배우 자세에서 상대 검사 {development['pairedOpponentChecks']}개 통과. 실제 접지 {development['groundingChecks']}개·접근 연결 {development['approachChecks']}개 통과. 유한 표본과 한 축 envelope 검사이며 연속 무관통·정확한 충돌 시각·자연스러운 전투의 보장은 아닙니다.", "접점과 양쪽 반응을 함께 저작하고 경직된 허리·회수 멈춤·체중 이동 개선", "focus"),
        card("reference_viewer", "원작·제작본 프레임 비교 도구", "tooling", "complete", "M05.1 · 과거 참고 분석", f"공개 원작 영상 {development['referenceVideos']}개의 추출 {development['referenceFrames']}프레임과 당시 H 첫 공격 {development['comparisonFrames']}프레임을 독립적으로 이동·재생·확대하는 로컬 도구의 검증 기록입니다. H는 현재 모델이 아닙니다.", f"이 과거 스냅샷은 원본 PTS와 29.97·25FPS, H의 30FPS를 구분했고 브라우저 조작 {development['referenceViewerUiChecks']}건을 통과했습니다. 주력 연속 64프레임의 장면표·전체 해상도 1장·개요 17개를 확인했으며 추출 439장 전체 시각 검수를 뜻하지 않습니다.", "최신 제작본은 별도 촬영·검수하고 과거 참고 분석과 구별"),
        card("animation", "병사·말 스키닝과 지면 접지", "graphics", "planned", "후속", "현재 강체 관절과 GPU 해석 동작을 넘어 가중치 스키닝·지형 발 IK·말 골격과 발굽 접지를 확장합니다.", "M05.1의 관절 동작이 자연스러운 전신 스키닝과 접지까지 완성했다는 뜻은 아닙니다.", "발 미끄러짐과 관절 경계가 보이는 근접 장면부터 개선", "focus"),
        card("officer_roster", "가능한 많은 유니크 장수 명부", "campaign", "in_progress", "콘텐츠 확장", f"삼국지 14 공식 이름 목록 {roster_count:,}개 ID를 등록했습니다. 다른 작품의 추가 인물도 신원·출처를 확인해 확장하며 인원 상한을 두지 않습니다.", f"한글 이름 {roster_metrics['koreanNames']}명. 동명이인은 ID를 분리했습니다. 원화 {portrait_count}명·3D 모델 {model_count}명·독립 일기토 {duel_count}명이며, {roster_count:,}명이 플레이 가능하다는 뜻은 아닙니다.", "남은 한글 이름·연의와 정사 출전·중복 신원 검토 후 장수 데이터와 플레이 통합", "focus"),
        card("officer_portraits", "연의 특징을 살린 독자 장수 원화", "graphics", "in_progress", "콘텐츠 확장", f"여포·관우·장비·마초·조운·황충·전위·조조·유비·손권·제갈량·주유에 손책·장료·초선·여몽을 더해 {portrait_count}명의 독자 원화를 제작했습니다.", f"{portrait_count}개 서로 다른 1,024×1,536 PNG를 검토하고 원본·게임·공개 갤러리의 동일성을 확인했습니다. 새 실행본에서 원화 {portrait_count}장 로딩과 실험 자산 제외를 {development['artPackageChecks']}개 조건으로 확인했습니다. 새 네 그림은 기존 M05.1 영상에 없으며 3D 모델·플레이 가능 수는 여전히 {model_count}명·{duel_count}명입니다.", "새 장수의 3D·플레이 통합과 다음 원화 묶음 제작", "focus"),
        card("cavalry", "기병 충격과 창병 저지", "battle", "planned", "후속", "질량·속도·방향·대형을 고려한 접촉 충격과 저지 반응을 만듭니다.", "물리 설계 문서에 제안. 연속 충돌·넘어짐은 미구현 범위.", "기병 돌파와 창병 방어의 반복 가능한 충돌 장면"),
        card("siege", "공성 통로와 성벽 위 교전", "battle", "planned", "후속", "문·벽·사다리의 통로 용량과 높이 층을 전투 경로에 반영합니다.", "현재 성문·내구도·투석 규칙은 기본 구현. 성벽 위 이동은 확장 대상.", "좁은 문 통과, 열린 문·파괴된 벽 경로 변경 검사"),
        card("diplomacy", "장수·정치·외교 확장", "campaign", "planned", "M07", "인물 관계·장비·조정·복합 협상·수행 부대 구조를 확장합니다.", "기본 장수·외교·개혁은 존재하며 원작 전체 구조는 아직 없습니다.", "관계·직위·협상 기능의 플레이 시나리오 설계"),
        card("native", "시뮬레이션 병목 개선", "performance", "in_progress", "병행", "C++ 접촉 계산을 연결하고 기능·그래픽 작업과 병행해 비용을 줄였습니다.", f"{physics_checks}개 기능 검사 통과. 보존된 M05의 25,664명 상태 모듈 접촉 중앙값 {physics_metrics['contact_median_ms']:.3f}ms / p99 {physics_metrics['contact_p99_ms']:.3f}ms. 새 병렬 회귀 실행이나 통합 전투 FPS와 다른 측정입니다.", "같은 알고리즘·병력·장면의 통합 렌더 비용과 기능 결과 비교"),
        card("engine", "엔진·도구·모드 선택 재검토", "tooling", "in_progress", "매 단계", "검증된 Godot 실행을 유지하며 Blender 두 인물 제작·공유 클립 도구를 선택했습니다. Unreal·Unity·전용 엔진과 원작 모드 경로도 마일스톤마다 검토합니다.", "현재 그래픽과 공방의 격차를 다른 엔진 이전이 실제로 해소했다는 비교 증거는 없습니다. 참고 목록의 TPU모드 표기는 보존하지만 원작 무모드·단일 모드의 통제 A/B 비교는 아직 미검증입니다.", "동일 장수·동작·조명 장면의 표현과 제작 비용, 모드 호환·품질 효과를 확인"),
        card("replay", "재현 가능한 전투·리플레이", "battle", "planned", "후속", "고정 틱·명령 기록·개별 상태 저장으로 같은 전투를 재현합니다.", "동일 장비의 첫 모듈 재현 검사와 완성된 리플레이 제품을 구분합니다.", "상태 해시와 저장·복원 후 결과 일치 확인"),
    ]
    battlefield_prototype = None
    if development.get("currentRevision")=="field-v4":
        battlefield_prototype = battle_review.read(ROOT)
        cards.append(card("battlefield_duel", "실제 병사 전장과 상세 일기토 시제품", "battle", "in_progress", "M05.1 · 전장 연결", "320명의 실제 전투와 같은 장군 ID·HP를 쓰며, 주변 병사와 보급 수레를 고려해 경로를 선택하고 전장 지면에 발을 딛습니다.", "네 장수12대진과 입력을 포함한20경기221개 검사, 실제 GPU의 원래 표시 슬롯12개·스킨18개 읽기, 실제 지형256점 비교. 흰 기둥처럼 쌓이던 화살 표시 시계를 고쳤습니다. 보존된 시제품의 근거이며 이후 일반 전투 연결은 별도 카드에서 기록합니다. 고밀도·공성·돌발 장애물 검증은 미완료입니다.", "일반 전투 메뉴 연결과 밀도·공성·막힌 경로, 상체 동작/병력 미술 품질 검수", "focus"))
    if development.get("currentRevision")=="field-v4":
        cards.append(card("normal_battle_duel", "일반 전투의 상세 장수 일기토 연결", "battle", "in_progress", "M05.1 · 전투 통합", "사용자 지정 전투에서 네 장수를 선택하고 일반 일기토 버튼으로 상세 모델·지면 접지·이동 공방을 시작합니다. 받아치기/회피/태세와 움직이는 카메라를 전투 HUD에 연결했습니다.", "새 독립 패키지의 실제 일반 전투에서5,184명 병사를 유지한 두 장비–여포 배치18개 검사와 GPU 표시 슬롯6개를 확인했습니다. 승부 뒤 전투는 계속되고 원래 표시를 복구합니다. 모든 대진·밀도·공성의 통합 검증이나 원작 수준의 동작 품질 완료는 아닙니다.", "일반 전투의 전 대진·입력·공성·고밀도·모델 전환과 상체/병사/말 품질 검수", "focus"))
    fullbody_prototype = reviewed_fullbody_prototype()
    if fullbody_prototype:
        cards.append(card("fullbody_rig", "여포 전신 가중 리그 제작", "graphics", "in_progress", "M05.1 · 리그 후보", "척추·쇄골·팔 비틀림·손목·손가락·다리·발목·발끝과 망토의64개 변형 뼈를 만들고17개 몸/의상 메시를 스키닝했습니다. 기본 게임과 별도로 실행하는 리그 후보입니다.", "저장 파일240프레임의 실제 IK 끝점과 뼈 길이, 엔진6시점의 전체384개 뼈 자세와102개 등록 Skin CPU bake를 대조했습니다. GPU 렌더 화면은 확인했지만 실제 GPU 정점 버퍼 읽기나 전체 형상 충돌 검사는 아닙니다. 8초 자료는 한 인물의 동작 범위이며 두 장수 공방·원작 품질 완료가 아닙니다.", "상대의 전신 리그·양손 무기 앵커·여러 사건/반격 분기를 가진 공방, 실제 변형된 자기 몸/상대 형상과 전장 지지 검수", "focus"))
    paired_authoring = reviewed_paired_authoring()
    if paired_authoring and paired_authoring["clearancePassed"]:
        cards.append(card("paired_fullbody_authoring", "장비·여포 전신 공방 제작과 관통 검수", "graphics", "in_progress", "M05.1 · 제작 후보", "팔 기준 형상과 실제 팔꿈치·무릎 굽힘 방향을 고쳐 새 두 장수 리그를 만들었습니다. 준비 자세와 여포의 회수·물러남·반격 진입을 같은8초 공방에서 함께 저작했습니다.", "480프레임에서 무기는 자기·상대의 머리/몸통, 전완/손은 자기 머리/몸통과의 표면 교차가 검출되지 않았습니다. 지지 발·그립,3,840굽힘 방향과 실제 엔진8시점1,024뼈/256등록 CPU Skin bake도 확인했습니다. 유한 표면 교차 검사이며 완전 포함·연속 충돌·다른 신체/옷·원작 수준 전체 동작·실전 피해/승패 통합은 아직 검수 중입니다. 기본 게임에 채택한 결과가 아닙니다.", "공방 전체의 자연스러움·추가 신체/의상과 연속 충돌, 반응 분기·입출구·실제 전장 연결을 검수", "focus"))
    elif paired_authoring:
        cards.append(card("paired_fullbody_authoring", "장비·여포 전신 공방 제작과 관통 검수", "graphics", "in_progress", "M05.1 · 제작 후보", "장비의64개 변형 뼈/15개 Skin을 추가하고, 두 장수128개 뼈/32개 Skin·개별 루트/무기·8초480프레임 공통 클립과 별도 프레임 뷰어를 제작했습니다.", "재로딩480프레임과 엔진8시점의1,024개 뼈 자세·256개 등록 CPU Skin bake는 통과했지만 실제 무기·전완/손과 머리/몸통의 형상 검수는 실패했습니다. 선택한 교차30건을 별도 삼각형 계산으로 확인했고 새 리그의 기준 메시 겹침도 찾았습니다. 실패 후보를 보존하며 기본 게임에 채택하지 않았습니다.", "기준 자세·가중치/갑주와 실제 형상 제약부터 수정한 뒤, 공방 전체·반응 분기·전장 연결을 검수", "focus"))
    contact_research = reviewed_contact_window_research()
    if contact_research and paired_authoring:
        item = next(c for c in cards if c["id"] == "paired_fullbody_authoring")
        item["summary"] += " 첫 공격의 방어·빗나감·창날 접촉 후보와 실제 장군 체력의 접촉 창을 별도 검증했습니다."
        item["evidence"] += " 실제 자산3개/각67자세와144·60·30Hz/긴 프레임의12조합에서 창날 접촉만 같은 시각에 한 번 피해를 적용했습니다. 새 명중 후보는 접촉 뒤33표본 교차가 남고, 발의 조기 분기와 공방 끝/시작 불일치도 확인했습니다. 자연스러운 피격·회수·연결과 실전 입력 통합은 미완료입니다."
        item["next"] = "실제 접점에서의 피격·무기 회수, 공유 착지 입구와 다음 공방 디딤/거리 회복을 함께 저작하고 실제 플레이로 검수"
    reactive = reviewed_reactive_first_strike()
    if reactive and paired_authoring:
        item = next(c for c in cards if c["id"] == "paired_fullbody_authoring")
        item["summary"] = "두 전신 리그의 실제 창날 접촉에서 장군 HP와 피격·무기 회수로 이어지는 별도 조작 시제품을 만들었습니다. 진입 선택·정지·재개와 늦은 선택 거부를 연결했습니다."
        item["evidence"] = "세 진입과 시간 간격15조합·183검사, 실제 키 입력/렌더9시점의288등록 CPU Skin bake를 확인했습니다. 접촉 시 두 루트·무기·128뼈를 유지합니다. 전체480저장 자세에서 지정 자기 전완 교차는 검출되지 않았고 창날/몸통 교차는 접촉 직후6표본으로 줄었습니다. 자산8시점1,024뼈/256bake와3,840굽힘 방향도 확인했습니다. 유한 표면 검사이며 완전 충돌·후속 피해·전장/지형·원작 자연스러움과 미술 품질은 미완료입니다. 기본 게임에 채택한 결과가 아닙니다."
        item["next"] = "후속 방어/반격 피해 창과 다음 공방 디딤/출구, 실제 지형·주변 병사의 전투 표시와 전신 리그·미술 품질을 연결"
    exchanges=reviewed_three_exchanges()
    if exchanges and paired_authoring:
        item=next(c for c in cards if c["id"]=="paired_fullbody_authoring")
        item["summary"]="첫 타격의 피격·방어·빗나감 뒤 장비의 후속 공세와 여포의 반격을 실제 무기 단면 접촉 창에 연결했습니다. 별도 조작 시제품에서 접촉 시각과 공격·방어 장수가 표시됩니다."
        item["evidence"]="세 창·15시간 조합의144검사와 세 선택의 실제 키 입력/렌더864등록 CPU Skin bake를 확인했습니다. 실제 윤곽212자세·독립 거리105사례를 대조했고, 무기를 분리한 경우에는 세 창 모두 빗나감으로 피해가 없었습니다. 정지·개입·전사 후 남은 공방도 중단됩니다. 지정 단면의 유한 근접 판정이며 전체 무기 충돌/힘·후속 몸통 피격·다음 공방 그래프·실전 전장/지형과 원작 자연스러움은 미완료입니다. 기본 게임 채택은 아닙니다."
        item["next"]="반격의 몸통 명중/피격 자료, 다음 공방 디딤/출구와 실제 지형·주변 병사 연결, 얼굴/갑주/옷과 긴 도약·낙법·재기 품질을 확장"
    parity = [
        {"area":"캠페인·경제", "domain":"campaign", "current":"8세력·30도시, 세금·식량·민심·건설·계절, 연속 3D 지형", "gap":"전체 지도·시작 연도·세력 콘텐츠, 복잡한 자원·인구 계층", "next":"3D 지형·도시 표현과 전략 콘텐츠 확장", "level":"기반 구현"},
        {"area":"군대·장수", "domain":"campaign", "current":"복수 군대, 모병·보충·행군, 캠페인 장수 26명 데이터, 지도 위 3D 군대·장수·깃발", "gap":"수행 부대, 관계·가족·장비·직위·세밀한 보급", "next":"군대 행군 동작과 지도 상호작용 확장", "level":"기반 구현"},
        {"area":"외교·개혁", "domain":"campaign", "current":"전쟁·화친·선물·교역·동맹·통행, 개혁 8개", "gap":"복합 거래·영토 교환·속국·연합 정치·전체 개혁 트리", "next":"캠페인 구조 확장", "level":"기반 구현"},
        {"area":"개별 병사 전투", "domain":"battle", "current":"개인 위치·속도·HP·접촉·공격 모듈의 전투 연결, 상대 방향의 무기와 관절 동작", "gap":"전선 점유·아군 비관통·정교한 무기 접촉·규모 성능", "next":"개별 접촉·회수·발 접지의 실제 화면 품질 개선", "level":"M05 기반 완료 · 동작 개선 중"},
        {"area":"전술·AI", "domain":"battle", "current":"진형·상성·측후방·돌격·사기·패주, 기본 AI", "gap":"장기 작전·협공·포위·증원·세밀한 시야와 은폐", "next":"개인 접촉과 전술 규칙 결합", "level":"기반 구현"},
        {"area":"공성·물리", "domain":"battle", "current":"성문·성벽 내구도·투석·화공·중앙 진입 경로", "gap":"성벽 위 전투·사다리·공성탑·복합 도시 길 찾기", "next":"장애물과 통로 용량 모델", "level":"기반 구현"},
        {"area":"모델·재질·표현", "domain":"graphics", "current":"여포 I·관우/장비/마초 arm_v3 채택, 독립 발목과 상완 연결 개선·네 장수 원화/3D 감상", "gap":"원화와 3D의 미술 격차·가중 스키닝·경사 지형 접지·말 골격·의상 품질", "next":"장수의 위용·얼굴·갑옷 재질과 골반/흉곽 변형 개선", "level":"현재 모델 통합 · 품질 제작 중"},
        {"area":"사운드·제품 완성도", "domain":"graphics", "current":"합성 배경음·북소리, 한국어 UI, 캠페인 저장", "gap":"장수 음성·전체 효과음·멀티플레이·튜토리얼·접근성", "next":"핵심 기능 검증 후 범위별 확장", "level":"기반 구현"},
        {"area":"장군 일기토", "domain":"battle", "current":"독립 4장수 모드·양손 IK·v4 두 인물 공방·접근 연결·실제 평면 접지·HP와 결과", "gap":"실제 무기끼리 접점·체중과 반발·경직된 허리·회수 멈춤·연속 충돌·가중 스키닝", "next":"맞닿는 두 무기와 양쪽이 힘을 받는 공방, 연속적인 회수 저작", "level":"M05 기반 완료 · M05.1 개선 중"},
        {"area":"유니크 장수·원화", "domain":"graphics", "current":f"공식 참고 명부 {roster_count:,}개 ID · 독자 원화 {portrait_count}명 · 3D 모델 {model_count}명 · 독립 일기토 {duel_count}명", "gap":"새 네 원화 장수의 3D·플레이 통합, 명부 전체 통합·한글 이름·연의와 정사 구분", "next":"인물별 출처·특징을 확인하며 원화와 장수 콘텐츠 확대", "level":"두 번째 원화 묶음 추가"},
        {"area":"원작 모드·튜닝", "domain":"modding", "current":"공식 도구·내장 전투 CSV·신규 캠페인 초기 전투 승리와 지도 복귀·장비 일기토 시작", "gap":"실제 저장·재실행·리플레이 재생·근접 동작과 모드 호환성·패치 효과", "next":"같은 조건의 반복·품질 후보 비교", "level":"실행 검증 진행"},
    ]
    public_milestones = []
    for key, title, state, description in [
        ("M03", "인체 기반 모델·재질", complete03, "인물·기병·말 개선, 실행 빌드와 영상 검증"),
        ("M03.1", "근접 렌더링 개선", complete031, "25,664명 표현 유지, 공간 분할·그림자 LOD"),
        ("M04", "원작 모드·튜닝 비교", "in_progress", "내장 전투 CSV, 신규 유비 캠페인 초기 전투 승리·장비 일기토 시작·지도 복귀 확인 · 저장·품질·호환성 비교 진행"),
        ("M05", "개별 전투·3D 캠페인·4장수 일기토", m05_state, "개인 이동·접촉, 연속 지형·3D 군대, 여포·관우·장비·마초와 별도 일기토 모드"),
        ("M05.1", "병사 무기 자세·장수 전신 동작", m051_state, "여포 I·세 장수 arm_v3·v4 공방·접지 검증 · 경직된 허리·회수 반응·가중 스키닝 개선 중. 통합 영상 로컬 검수 완료·비공개 업로드 대기. 새 네 원화는 해당 영상 이후 추가"),
        ("후속", "접촉·공성·장수 콘텐츠·정치", "planned", "스키닝·기병 충격·성벽 경로·장수 원화와 플레이 통합·외교 확장"),
    ]:
        raw = milestones.get(key, {})
        checks = raw.get("checks", {})
        public_milestones.append(dict(id=key, title=title, status=state, description=description,
            checks={name:number(checks.get(name)) for name in ("assets", "rules", "ui", "render_lod_gpu") if number(checks.get(name)) is not None},
            videoVerified=m051_complete if key == "M05.1" else m05_complete if key == "M05" else raw.get("youtube", {}).get("privacy") == "private" and raw.get("status") == "complete" if isinstance(raw.get("youtube"), dict) else False))
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if development.get("currentRevision")=="field-v4":
        for row in parity:
            if row["area"]=="모델·재질·표현":
                row.update(current="여포 field/v1f의 가중 허리·망토, 세 장수 arm_v3·원화/3D 감상",gap="원화와 3D의 미술 격차·다른 장수 의상 스키닝·지형 접지·말 골격",next="얼굴·갑옷·의상의 품질과 몸통 체중 반응 개선")
            elif row["area"]=="장군 일기토":
                row.update(current="기본4장수 이동 전장 일기토·세계 지지 발·HP/자연 승부·장비→여포 변형 표면 타격",gap="다른 방향 정밀 타격·더 다양한 공방·몸통 경직·연속 충돌·전장 지형/병사 회피",next="공격 준비/회수 멈춤과 공방 교대 리듬 개선")
        for row in public_milestones:
            if row["id"]=="M05.1":row["description"]="이동하는 기본 일기토·여포 가중 허리/망토·실제 변형 복부 타격과 새 실행본 검증. 긴 버팀 자세·다른 방향 충돌·의상 품질 제작 중. 보존 통합 영상의 비공개 업로드는 대기 중이며 새 실행본과 촬영 시점을 구분합니다."
    return {
        "schemaVersion":1,
        "updatedAt":now,
        "project": {"name":"천하", "englishName":"TIANXIA", "edition":"개발 관측소", "latestVerified":latest_verified,
                    "currentMilestone":"M05.1", "currentVersion":m051.get("version", "0.4.1-dev"), "currentMilestoneTitle":"병사 무기 자세·장수 전신 동작", "goal":"캠페인부터 전장까지, 삼국지 토탈워와 동등한 수준을 최대한 추구합니다.",
                    "policy":"기능·그래픽 확장을 우선하고, 최적화를 병행합니다.",
                    "boundary":"현재는 독립 개발 중인 전략 게임입니다. 항목별 구현과 검증을 기록하며 전체 동등성이나 완성률을 주장하지 않습니다."},
        "statuses":[{"id":"in_progress", "label":"진행 중", "description":"현재 제작·통합·검증 중"}, {"id":"complete", "label":"검증 완료", "description":"카드에 적힌 범위의 근거 확인"}, {"id":"planned", "label":"다음 계획", "description":"아직 완성되지 않은 기능"}, {"id":"external", "label":"외부 검증 대기", "description":"원작 실행 등 외부 환경 확인 필요"}],
        "domains":[{"id":"battle","label":"전투·물리"},{"id":"campaign","label":"캠페인"},{"id":"graphics","label":"그래픽·동작"},{"id":"performance","label":"최적화"},{"id":"modding","label":"모드·튜닝"},{"id":"tooling","label":"엔진·도구"}],
        "battlefieldPrototype":battlefield_prototype,
        "cards":field_review.update_cards(cards) if development.get("currentRevision")=="field-v4" else cards, "parity":parity, "milestones":public_milestones,
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
    if data.get("battlefieldPrototype") is not None: battle_review.validate_public(data["battlefieldPrototype"])
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
    development = data.get("developmentEvidence")
    if development is not None:
        expected = {"portablePckSha256":REVIEWED_PCK_SHA256, "pairedCurveSha256":REVIEWED_CURVE_SHA256,
                    "modelSha256":{hero:entry[1] for hero,entry in REVIEWED_MODELS.items()},
                    "portableByMode":{"menu":76,"duel":76,"heroes":76}, "galleryChecks":127,
                    "groundingChecks":43,"approachChecks":40,"pairedOpponentChecks":169,
                    "pairedMatchups":12,"pairedSampleHz":240,"pairedActorPairPoses":20592,
                    "pairedArmChecks":33,"genericArmChecks":22,"artPackageChecks":95,"packedPortraits":16,
                    "catalogSha256":REVIEWED_CATALOG_SHA256,"experimentalPelvisAssetsPackaged":False}
        if development.get("currentRevision") == "field-v4":
            field_review.validate_public(development)
        elif any(development.get(key) != value for key,value in expected.items()):
            raise ValueError("Public development fields differ from the reviewed snapshot contract")
        catalog = data.get("officerCatalog")
        if catalog is not None and (catalog.get("illustrations") != 16 or catalog.get("models") != 4
                                    or catalog.get("duelPlayable") != 4 or catalog.get("referenceEntries") != 1000):
            raise ValueError("Public catalog must distinguish 16 portraits, four playable/models, and 1,000 reference IDs")
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
