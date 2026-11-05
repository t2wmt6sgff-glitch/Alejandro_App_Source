import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import update_app_details


class UpdateAppDetailsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.source_path = Path(self.temp.name) / "source.json"
        self.original = {
            "name": "Test",
            "apps": [{
                "name": "Old",
                "bundleIdentifier": "com.example.stable",
                "localizedDescription": "Old description",
                "versions": [{"version": "1"}],
            }],
            "news": [],
        }
        self.source_path.write_text(json.dumps(self.original), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_editor(self, *args):
        with patch.object(update_app_details, "SOURCE", self.source_path), patch.object(sys, "argv", ["editor", *args]):
            update_app_details.main()

    def test_updates_only_display_fields_and_preserves_identifier(self):
        self.run_editor("Old", "New", "Descripción nueva")
        updated = json.loads(self.source_path.read_text(encoding="utf-8"))
        self.assertEqual(updated["apps"][0]["name"], "New")
        self.assertEqual(updated["apps"][0]["localizedDescription"], "Descripción nueva")
        self.assertEqual(updated["apps"][0]["bundleIdentifier"], "com.example.stable")
        self.assertEqual(updated["apps"][0]["versions"], [{"version": "1"}])

    def test_unknown_name_leaves_catalog_unchanged(self):
        before = self.source_path.read_bytes()
        with self.assertRaises(SystemExit):
            self.run_editor("Missing", "New", "Description")
        self.assertEqual(self.source_path.read_bytes(), before)

    def test_duplicate_name_leaves_catalog_unchanged(self):
        data = json.loads(self.source_path.read_text(encoding="utf-8"))
        data["apps"].append({**data["apps"][0], "bundleIdentifier": "com.example.other"})
        self.source_path.write_text(json.dumps(data), encoding="utf-8")
        before = self.source_path.read_bytes()
        with self.assertRaises(SystemExit):
            self.run_editor("Old", "New", "Description")
        self.assertEqual(self.source_path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
