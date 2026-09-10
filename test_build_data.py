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


if __name__ == "__main__":
    unittest.main()
