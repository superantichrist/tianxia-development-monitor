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


if __name__ == "__main__":
    unittest.main()
