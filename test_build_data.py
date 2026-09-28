"""Check the completion-evidence contract using synthetic local fixtures.

This does not decode movies or replace human visual/private-upload verification.
"""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_data


class CompletionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.root_patch = patch.object(build_data, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        (self.root / "artifacts/videos").mkdir(parents=True)
        movie = b"synthetic file: validates provenance checks, not a playable video"
        (self.root / "artifacts/videos/M05.mp4").write_bytes(movie)
        self.capture = {
            "milestone": "M05", "failures": [], "performance_benchmark": False,
            "chapters": [{"screen": screen} for screen in ("campaign", "battle", "duel")],
            "campaign": {"travel_distance": 30},
            "battle": {"observed_hit_intents": 20, "casualties": [2, 3]},
            "duel": {"combatants": 2, "exchanges": [{"damage": 8}],
                     "selected_models": [{"authored": True} for _ in range(4)]},
        }
        self.write_capture()
        self.record = {
            "id": "M05", "status": "complete", "version": "fixture-version",
            "video": {"file": "artifacts/videos/M05.mp4", "sha256": hashlib.sha256(movie).hexdigest(),
                      "width": 1920, "height": 1080, "fps": 30, "seconds": 80,
                      "visual_qa_seconds": [4, 30, 65]},
            "youtube": {"status": "complete", "privacy": "private", "video_id": "fixture0001",
                        "verified_date": "2026-09-10", "verification": "Synthetic reviewed fixture"},
        }

    def write_capture(self):
        (self.root / "artifacts/M05-capture.json").write_text(json.dumps(self.capture), encoding="utf-8")

    def test_pending_never_requires_recording_in_flight(self):
        proof = build_data.m05_completion_evidence({"status": "in_progress"})
        self.assertTrue(proof)
        self.assertFalse(any(proof.values()))

    def test_reviewed_contract_returns_only_public_booleans(self):
        proof = build_data.m05_completion_evidence(self.record)
        self.assertEqual(set(proof.values()), {True})
        self.assertNotIn("fixture0001", json.dumps(proof))

    def test_missing_or_nonprivate_upload_cannot_complete(self):
        for privacy in (None, "public", "unlisted"):
            record = copy.deepcopy(self.record)
            record["youtube"]["privacy"] = privacy
            with self.subTest(privacy=privacy), self.assertRaises(ValueError):
                build_data.m05_completion_evidence(record)

    def test_completed_video_must_exist_and_match_reviewed_bytes(self):
        (self.root / "artifacts/videos/M05.mp4").write_bytes(b"different bytes")
        with self.assertRaises(ValueError):
            build_data.m05_completion_evidence(self.record)
        (self.root / "artifacts/videos/M05.mp4").unlink()
        with self.assertRaises(ValueError):
            build_data.m05_completion_evidence(self.record)

    def test_gameplay_report_must_cover_all_three_modes(self):
        self.capture["chapters"] = [{"screen": "campaign"}, {"screen": "battle"}]
        self.write_capture()
        with self.assertRaises(ValueError):
            build_data.m05_completion_evidence(self.record)

    def test_no_contact_or_fallback_hero_rejects_completion(self):
        self.capture["battle"]["observed_hit_intents"] = 0
        self.write_capture()
        with self.assertRaises(ValueError):
            build_data.m05_completion_evidence(self.record)
        self.capture["battle"]["observed_hit_intents"] = 20
        self.capture["duel"]["selected_models"][0]["authored"] = False
        self.write_capture()
        with self.assertRaises(ValueError):
            build_data.m05_completion_evidence(self.record)

    def test_review_times_must_be_inside_movie(self):
        for times in ([1, 2], [-1, 2, 3], [1, 2, 100]):
            record = copy.deepcopy(self.record)
            record["video"]["visual_qa_seconds"] = times
            with self.subTest(times=times), self.assertRaises(ValueError):
                build_data.m05_completion_evidence(record)


class AnimationCompletionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.root_patch = patch.object(build_data, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        (self.root / "artifacts/videos").mkdir(parents=True)
        movie = b"synthetic M05.1 media bytes, not a playable video"
        (self.root / "artifacts/videos/M05.1-r2.mp4").write_bytes(movie)
        heroes = ("lubu", "guanyu", "zhangfei", "machao")
        self.capture = {
            "milestone": "M05.1", "version": "fixture-animation", "failures": [],
            "performance_benchmark": False, "capture_fps": 30,
            "fixed_timestep": True, "automated_commands": True,
            "source_animation_sha256": {f"source-{i}": "a" * 64 for i in range(7)},
            "chapters": [{"screen": "campaign", "seconds": 0}, {"screen": "battle", "seconds": 15},
                         {"screen": "duel", "seconds": 35}],
            "campaign": {"travel_distance": 30},
            "battle": {"observed_hit_intents": 20, "casualties": [2, 3], "conservation": [True, True],
                       "contact_samples": [{"contact_agents": 2, "agents": [
                           {"id": i, "alive": 1, "target_id": 1-i, "position": [i, 0], "velocity": [0.1, 0],
                            "facing": 0.2, "attack_phase": 0.45, "readiness": 1, "movement_phase": 2,
                            "health": 85, "kind": "spear"} for i in range(2)]}]},
            "duel": {"combatants": 2, "selected_models": [{"hero": hero, "authored": True} for hero in heroes],
                     "bouts": []},
        }
        for i, hero in enumerate(heroes):
            self.capture["duel"]["bouts"].append({
                "hero": hero, "exchanges": [{"source": 0, "target": 1, "damage": 9.5}],
                "samples": [{"frame": (40 + 20*i + j*2)*30, "phase": phase, "attacking_side": 0,
                             "torso": [0, j*.2, 0], "right_leg": [j*.3, 0, 0], "left_leg": [j*.1, 0, 0],
                             "weapon_up": [j*.2, 0, -1]} for j, phase in enumerate(("windup", "impact"))],
            })
        self.record = {
            "id": "M05.1", "status": "complete", "version": "fixture-animation",
            "video": {"file": "artifacts/videos/M05.1-r2.mp4", "capture_report": "artifacts/M05.1-r2-capture.json",
                      "sha256": hashlib.sha256(movie).hexdigest(), "width": 1920, "height": 1080, "fps": 30,
                      "seconds": 120, "visual_qa_seconds": [4, 22, 41, 61, 81, 101],
                      "fixed_timestep": True, "automated_commands": True, "performance_benchmark": False},
            "youtube": {"status": "complete", "privacy": "private", "video_id": "fixture0002",
                        "verified_date": "2026-09-14", "verification": "Synthetic reviewed fixture"},
        }
        self.write_capture()

    def write_capture(self):
        (self.root / "artifacts/M05.1-r2-capture.json").write_text(json.dumps(self.capture), encoding="utf-8")

    def reject(self):
        self.write_capture()
        with self.assertRaises(ValueError):
            build_data.m051_completion_evidence(self.record)

    def test_pending_does_not_require_or_read_the_recording(self):
        self.assertFalse(any(build_data.m051_completion_evidence({"status": "in_progress"}).values()))

    def test_reviewed_retake_uses_its_explicit_capture_report(self):
        proof = build_data.m051_completion_evidence(self.record)
        self.assertEqual(set(proof.values()), {True})
        self.assertNotIn("fixture0002", json.dumps(proof))
        self.assertFalse((self.root / "artifacts/M05.1-capture.json").exists())

    def test_original_m05_report_cannot_verify_new_animation(self):
        self.capture["milestone"] = "M05"
        self.reject()

    def test_duplicate_hero_or_missing_bout_rejects_all_four_claim(self):
        self.capture["duel"]["bouts"][3]["hero"] = "lubu"
        self.reject()
        self.capture["duel"]["bouts"].pop()
        self.reject()

    def test_same_model_repeated_four_times_is_not_four_heroes(self):
        self.capture["duel"]["selected_models"][3]["hero"] = "lubu"
        self.reject()

    def test_opponent_only_or_zero_damage_is_not_named_hero_attack(self):
        exchange = self.capture["duel"]["bouts"][0]["exchanges"][0]
        exchange.update(source=1, target=0)
        self.reject()
        exchange.update(source=0, target=1, damage=0)
        self.reject()

    def test_without_contact_pose_does_not_prove_strike_animation(self):
        self.capture["duel"]["bouts"][0]["samples"][1]["phase"] = "recover"
        self.reject()

    def test_unchanging_or_nonfinite_body_pose_rejects_motion_claim(self):
        self.capture["duel"]["bouts"][0]["samples"][1]["torso"] = [0, 0, 0]
        self.reject()
        self.capture["duel"]["bouts"][0]["samples"][1]["torso"] = [0, float("nan"), 0]
        self.reject()

    def test_missing_contact_sample_cannot_repeat_m05_telemetry_gap(self):
        self.capture["battle"]["contact_samples"] = []
        self.reject()

    def test_dead_or_unrelated_soldiers_do_not_prove_live_target_pair(self):
        agents = self.capture["battle"]["contact_samples"][0]["agents"]
        agents[0]["alive"] = 0
        self.reject()
        agents[0]["alive"] = 1
        for agent in agents:
            agent["target_id"] = -1
        self.reject()

    def test_missing_animation_state_in_contact_pair_rejects_completion(self):
        del self.capture["battle"]["contact_samples"][0]["agents"][0]["readiness"]
        self.reject()

    def test_each_hero_bout_requires_an_in_range_review_timestamp(self):
        self.record["video"]["visual_qa_seconds"][-1] = 110
        self.reject()

    def test_both_campaign_and_battle_need_visual_review(self):
        self.record["video"]["visual_qa_seconds"][1] = 14
        self.reject()

    def test_capture_version_and_disclosures_must_match(self):
        self.capture["version"] = "old-version"
        self.reject()
        self.capture["version"] = self.record["version"]
        self.capture["automated_commands"] = False
        self.reject()

    def test_animation_provenance_and_count_conservation_required(self):
        self.capture["source_animation_sha256"] = {}
        self.reject()
        self.capture["source_animation_sha256"] = {f"source-{i}": "a" * 64 for i in range(7)}
        self.capture["battle"]["conservation"] = [True, False]
        self.reject()

    def test_changed_movie_and_nonprivate_upload_reject_completion(self):
        self.record["youtube"]["privacy"] = "unlisted"
        self.reject()
        self.record["youtube"]["privacy"] = "private"
        (self.root / "artifacts/videos/M05.1-r2.mp4").write_bytes(b"changed")
        self.reject()


class PublicReferenceExportTests(unittest.TestCase):
    def snapshot(self):
        return {"sources": [], "statuses": [], "domains": [], "cards": [], "milestones": []}

    def test_only_exact_public_urls_in_source_slots_are_allowed(self):
        data = self.snapshot()
        data["sources"] = [{"url": url} for url in build_data.PUBLIC_REFERENCE_URLS]
        build_data.validate(data)
        for url in ("https://www.youtube.com/watch?v=fixture0002", "https://youtu.be/EhPbt8CLEFo",
                    "https://www.youtube.com/watch?v=EhPbt8CLEFo&account=private", "javascript:alert(1)"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                build_data.validate({**data, "sources": [{"url": url}]})
        data["note"] = next(iter(build_data.PUBLIC_REFERENCE_URLS))
        with self.assertRaises(ValueError):
            build_data.validate(data)

    def test_public_link_exception_does_not_allow_local_or_private_content(self):
        for value in ("http://127.0.0.1:8771/", "http://localhost:8771/", "C:/private/video.mp4",
                      "artifacts/references/yoho/source.json", "res://assets/model.glb",
                      "https://studio.youtube.com/channel/private", "UC" + "x" * 22):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_data.validate({**self.snapshot(), "note": value})


class DevelopmentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        root_patch = patch.object(build_data, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        models = {}
        for hero, (name, _) in build_data.REVIEWED_MODELS.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((hero + " synthetic model").encode())
            models[hero] = (name, hashlib.sha256(path.read_bytes()).hexdigest())
        curve = self.root / "assets/animations/duel-exchanges.json"
        curve.parent.mkdir(parents=True)
        curve.write_bytes(b"synthetic reviewed curve bytes")
        curve_hash = hashlib.sha256(curve.read_bytes()).hexdigest()
        pck = self.root / "build/Tianxia/Tianxia.pck"
        pck.parent.mkdir(parents=True)
        pck.write_bytes(b"synthetic reviewed PCK bytes")
        self.pck_hash = hashlib.sha256(pck.read_bytes()).hexdigest()
        catalog=self.root/"assets/data/officers.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_bytes(b"synthetic reviewed 16-portrait catalog")
        catalog_hash=hashlib.sha256(catalog.read_bytes()).hexdigest()
        for key,value in (("REVIEWED_MODELS",models),("REVIEWED_CURVE_SHA256",curve_hash),
                          ("REVIEWED_PCK_SHA256",self.pck_hash),("REVIEWED_CATALOG_SHA256",catalog_hash),
                          ("REVIEWED_REPORTS",copy.deepcopy(build_data.REVIEWED_REPORTS))):
            current_patch=patch.object(build_data,key,value)
            current_patch.start();self.addCleanup(current_patch.stop)
        source_hashes = {path: value for path,value in models.values()}
        source_hashes["assets/animations/duel-exchanges.json"] = curve_hash
        source_hashes["assets/data/officers.json"] = catalog_hash
        self.art_report={"passed":95,"failures":[],"pck_sha256":self.pck_hash,"catalog_sha256":catalog_hash,
                         "portrait_count":16,"model_count":4,"playable_count":4,"private_note":"private-art-note",
                         "portraits":[{"path":"res://assets/portraits/romance_v1/fixture"+str(i)+".png"} for i in range(12)]
                           +[{"path":"res://assets/portraits/romance_v2/"+hero+".png"} for hero in ("sunce","zhangliao","diaochan","lumeng")],
                         "excluded_prototype_resources":[{"source":"res://private/pelvis_fixture/"+str(i)} for i in range(20)]}
        art_name="artifacts/romance-v2-pack-validation-r2.json"
        art_path=self.write(art_name,self.art_report)
        art_patch=patch.object(build_data,"REVIEWED_ART_PACKAGE",(art_name,hashlib.sha256(art_path.read_bytes()).hexdigest()))
        art_patch.start();self.addCleanup(art_patch.stop)
        runtime_sources = {"res://"+key:value for key,value in source_hashes.items()}
        base={"failures":[],"source_hashes":runtime_sources,"after_hashes":runtime_sources}
        gallery={**base,"passed":127,"private_note":"private-gallery-path",
                 "heroes":[{"hero":hero,"authored":True,"model":"res://"+path,"model_sha256":value}
                           for hero,(path,value) in models.items()]}
        self.write_report("gallery",gallery)
        for key,count in (("grounding",43),("approach",40)):
            self.write_report(key,{**base,"passed":count})
        self.pairs=[]
        hero_ids=list(models)
        for attacker in range(4):
            for defender in range(4):
                if attacker==defender:continue
                entries=[]
                for index in (attacker,defender):
                    hero=hero_ids[index];path,value=models[hero]
                    before={"model_sha256":value,"private_note":"private-account"}
                    entries.append({"hero":hero,"model_path":"res://"+path,
                                    "provenance":{"before_load":before,"after_trace":before}})
                self.pairs.append({"attacker":attacker,"defender":defender,"models":entries,
                                   "frames":[{}]*1716,"summary":{outcome:{"head_frames":[],"precontact_torso_frames":[],
                                     "torso_frames":[184] if outcome=="hit" else []} for outcome in ("hit","blocked","parried","miss")}})
        self.write_report("opponent",{**base,"passed":169,"fps":240,"total_actor_pair_frames":20592,
                                      "candidate_curve":"","zero_baseline_control":False,"pairs":self.pairs})
        for key,count,poses,heroes in (("paired_arms",33,600,hero_ids),("generic_arms",22,2901,hero_ids[1:])):
            self.write_report(key,{**base,"passed":count,"poses":poses,"full_unique_vertices":True,
                                   "heroes":[{"hero":hero,"after":{"model_sha256":models[hero][1]}} for hero in heroes]})
        self.build = {"source_unchanged_during_export_and_validation": True,
                      "packaged_sha256": {"Tianxia.pck": self.pck_hash}, "headless_checks": {},"source_sha256":source_hashes}
        for mode in ("menu", "duel", "heroes"):
            checks = {"passed": 76, "version": "fixture-build", "failures": []}
            self.build["headless_checks"][mode] = checks
            self.write("artifacts/portable-validation-" + mode + ".json", {
                **checks, "launch_mode": mode, "pck_sha256": self.pck_hash,
                "executable": "C:/private/game.exe", "account": "private-account"})
        self.write("build/Tianxia/build-manifest.json", self.build)
        self.segments = {"references": [{"source_url": url, "frames": [{"src": "private-source-path"}]} for url in build_data.PUBLIC_REFERENCE_URLS],
                         "ours": [{"frames": [{"src": "private-comparison-path"}]}]}
        self.segments_path = self.write("artifacts/references/yoho/segments.json", self.segments)
        self.write("artifacts/references/yoho/viewer-ui-validation.json", {
            "failures": [], "checks": [{"result": "pass"}] * 11, "url": "http://127.0.0.1:8771/",
            "files": {"artifacts\\references\\yoho\\segments.json": hashlib.sha256(self.segments_path.read_bytes()).hexdigest()}})

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def write_report(self,key,data):
        name,_,count=build_data.REVIEWED_REPORTS[key]
        path=self.write(name,data)
        build_data.REVIEWED_REPORTS[key]=(name,hashlib.sha256(path.read_bytes()).hexdigest(),count)

    def test_selects_counts_without_serializing_raw_evidence(self):
        public = build_data.current_development_evidence()
        self.assertEqual(public["portableByMode"], {"menu": 76, "duel": 76, "heroes": 76})
        self.assertEqual((public["galleryChecks"], public["referenceFrames"], public["referenceViewerUiChecks"]), (127, 2, 11))
        self.assertEqual((public["groundingChecks"],public["approachChecks"],public["pairedOpponentChecks"]),(43,40,169))
        self.assertEqual((public["pairedArmChecks"],public["genericArmChecks"],public["pairedMatchups"],public["pairedSampleHz"]),(33,22,12,240))
        self.assertEqual((public["artPackageChecks"],public["packedPortraits"]),(95,16))
        self.assertFalse(public["experimentalPelvisAssetsPackaged"])
        for hidden in ("private-account", "private-art-note", "private-source-path", "private-comparison-path", "res://", "127.0.0.1"):
            self.assertNotIn(hidden, json.dumps(public))

    def test_missing_third_mode_cannot_claim_three_mode_validation(self):
        (self.root / "artifacts/portable-validation-heroes.json").unlink()
        with self.assertRaises(ValueError):
            build_data.current_development_evidence()

    def test_mixed_packaged_builds_cannot_share_validation(self):
        path = self.root / "artifacts/portable-validation-duel.json"
        result = json.loads(path.read_text())
        result["pck_sha256"] = "b" * 64
        path.write_text(json.dumps(result), encoding="utf-8")
        with self.assertRaises(ValueError):
            build_data.current_development_evidence()

    def test_changed_viewer_list_cannot_reuse_old_ui_review(self):
        self.segments["references"][0]["frames"].append({"src": "added-frame"})
        self.segments_path.write_text(json.dumps(self.segments), encoding="utf-8")
        with self.assertRaises(ValueError):
            build_data.current_development_evidence()

    def test_same_check_counts_cannot_relabel_new_model_or_build_as_reviewed_snapshot(self):
        gallery_path = self.root / build_data.REVIEWED_REPORTS["gallery"][0]
        gallery = json.loads(gallery_path.read_text(encoding="utf-8"))
        gallery["heroes"][0]["model_sha256"] = "d" * 64
        self.write_report("gallery",gallery)
        with self.assertRaisesRegex(ValueError, "gallery model changed"):
            build_data.current_development_evidence()
        gallery["heroes"][0]["model_sha256"] = build_data.REVIEWED_MODELS["lubu"][1]
        self.write_report("gallery",gallery)
        new_pck = "e" * 64
        self.build["packaged_sha256"]["Tianxia.pck"] = new_pck
        self.write("build/Tianxia/build-manifest.json", self.build)
        for mode in ("menu", "duel", "heroes"):
            path = self.root / ("artifacts/portable-validation-" + mode + ".json")
            result = json.loads(path.read_text(encoding="utf-8"))
            result["pck_sha256"] = new_pck
            path.write_text(json.dumps(result), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "packaged build changed"):
            build_data.current_development_evidence()

    def test_changed_report_bytes_cannot_reuse_same_green_count(self):
        path=self.root/build_data.REVIEWED_REPORTS["grounding"][0]
        report=json.loads(path.read_text());report["new_unreviewed_scope"]=True
        path.write_text(json.dumps(report),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"report bytes changed"):
            build_data.current_development_evidence()

    def test_live_model_curve_or_package_bytes_cannot_diverge_from_pins(self):
        for name in (build_data.REVIEWED_MODELS["guanyu"][0],"assets/animations/duel-exchanges.json","build/Tianxia/Tianxia.pck","assets/data/officers.json"):
            path=self.root/name;original=path.read_bytes();path.write_bytes(b"unreviewed new bytes")
            with self.subTest(path=name),self.assertRaises(ValueError):build_data.current_development_evidence()
            path.write_bytes(original)

    def test_subset_matchups_or_missing_contact_cannot_support_all_pair_claim(self):
        path=self.root/build_data.REVIEWED_REPORTS["opponent"][0]
        original=json.loads(path.read_text())
        for defect in ("missing_pair","miss_has_contact","hit_has_no_contact","lower_rate"):
            report=copy.deepcopy(original)
            if defect=="missing_pair":report["pairs"].pop()
            elif defect=="miss_has_contact":report["pairs"][0]["summary"]["miss"]["torso_frames"]=[184]
            elif defect=="hit_has_no_contact":report["pairs"][0]["summary"]["hit"]["torso_frames"]=[]
            else:report["fps"]=60
            self.write_report("opponent",report)
            with self.subTest(defect=defect),self.assertRaises(ValueError):build_data.current_development_evidence()

    def test_partial_arm_sampling_or_unstable_report_inputs_reject(self):
        path=self.root/build_data.REVIEWED_REPORTS["paired_arms"][0]
        original=json.loads(path.read_text())
        report=copy.deepcopy(original);report["full_unique_vertices"]=False
        self.write_report("paired_arms",report)
        with self.assertRaisesRegex(ValueError,"full-mesh"):build_data.current_development_evidence()
        report=copy.deepcopy(original);report["after_hashes"]={"changed":"d"*64}
        self.write_report("paired_arms",report)
        with self.assertRaisesRegex(ValueError,"stable inputs"):build_data.current_development_evidence()

    def test_existing_public_snapshot_cannot_inflate_current_counts(self):
        public=build_data.current_development_evidence()
        snapshot={"sources":[],"statuses":[],"domains":[],"cards":[],"milestones":[],"developmentEvidence":public}
        build_data.validate(snapshot)
        public["pairedMatchups"]=16
        with self.assertRaisesRegex(ValueError,"snapshot contract"):build_data.validate(snapshot)

    def test_art_counts_and_exact_new_set_cannot_be_relabelled_even_with_reviewed_report_pin(self):
        for change in ("portrait_count","playable_count","model_count","missing_new_portrait","missing_exclusion"):
            report=copy.deepcopy(self.art_report)
            if change=="portrait_count":report[change]=12
            elif change in ("playable_count","model_count"):report[change]=16
            elif change=="missing_new_portrait":report["portraits"][-1]["path"]="res://assets/portraits/romance_v1/other.png"
            else:report["excluded_prototype_resources"].pop()
            name=build_data.REVIEWED_ART_PACKAGE[0];path=self.write(name,report)
            with patch.object(build_data,"REVIEWED_ART_PACKAGE",(name,hashlib.sha256(path.read_bytes()).hexdigest())):
                with self.subTest(change=change),self.assertRaisesRegex(ValueError,"Packed-art scope"):
                    build_data.current_development_evidence()

    def test_public_catalog_cannot_turn_new_portraits_into_playable_officers(self):
        snapshot={"sources":[],"statuses":[],"domains":[],"cards":[],"milestones":[],
                  "developmentEvidence":build_data.current_development_evidence(),
                  "officerCatalog":{"referenceEntries":1000,"illustrations":16,"models":4,"duelPlayable":4}}
        build_data.validate(snapshot)
        snapshot["officerCatalog"]["duelPlayable"]=16
        with self.assertRaisesRegex(ValueError,"Public catalog must distinguish"):
            build_data.validate(snapshot)


if __name__ == "__main__":
    unittest.main()
