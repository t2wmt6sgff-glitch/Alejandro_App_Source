import argparse
import copy
import unittest

from scripts.update_manual_app import add_version


def args(**overrides):
    values = {
        "bundle_id": "com.example.youtube",
        "version": "21.11.0",
        "build_version": "123789",
        "download_url": "https://example.com/youtube.ipa",
        "date": "2026-11-11",
        "size": 123456,
        "min_os_version": "16.0",
        "description": None,
        "platform": "iOS",
        "is_beta": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def sample():
    return {
        "apps": [{
            "name": "YouTube",
            "bundleIdentifier": "com.example.youtube",
            "appPermissions": {"entitlements": ["get-task-allow"]},
            "versions": [{
                "version": "21.10.1",
                "buildVersion": "123456",
                "downloadURL": "https://example.com/old.ipa",
            }],
        }]
    }


class ManualUpdateTests(unittest.TestCase):
    def test_adds_version_to_existing_app_and_preserves_metadata(self):
        data = sample()
        old_app = copy.deepcopy(data["apps"][0])
        added = add_version(data, args())
        app = data["apps"][0]
        self.assertEqual(added["version"], "21.11.0")
        self.assertEqual(len(data["apps"]), 1)
        self.assertEqual(app["bundleIdentifier"], old_app["bundleIdentifier"])
        self.assertEqual(app["appPermissions"], old_app["appPermissions"])
        self.assertEqual(app["name"], old_app["name"])
        self.assertEqual(app["versions"][1], old_app["versions"][0])
        self.assertEqual(app["versions"][0]["size"], 123456)

    def test_unknown_bundle_id_does_not_create_app(self):
        data = sample()
        with self.assertRaisesRegex(ValueError, "nunca crea fichas nuevas"):
            add_version(data, args(bundle_id="com.unknown.app"))
        self.assertEqual(len(data["apps"]), 1)

    def test_duplicate_version_is_rejected(self):
        data = sample()
        add_version(data, args())
        with self.assertRaisesRegex(ValueError, "ya está registrada"):
            add_version(data, args())
        self.assertEqual(len(data["apps"][0]["versions"]), 2)

    def test_non_https_url_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            add_version(sample(), args(download_url="http://example.com/app.ipa"))

    def test_invalid_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "fecha"):
            add_version(sample(), args(date="2026-02-31"))


if __name__ == "__main__":
    unittest.main()
