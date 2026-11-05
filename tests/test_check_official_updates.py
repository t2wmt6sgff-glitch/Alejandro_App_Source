import unittest
from unittest.mock import patch

from scripts import check_official_updates


class ResolveLatestTests(unittest.TestCase):
    def test_delta_uses_official_altstore_source(self):
        payload = {
            "apps": [{
                "bundleIdentifier": "com.rileytestut.Delta",
                "versions": [{
                    "version": "1.8",
                    "date": "2026-10-01",
                    "downloadURL": "https://cdn.altstore.io/file/delta.ipa",
                    "size": 123,
                }],
            }],
        }
        with patch.object(check_official_updates, "fetch_json", return_value=payload):
            result = check_official_updates.resolve_latest("Delta")
        self.assertEqual(result["label"], "1.8")
        self.assertEqual(result["size"], 123)
        self.assertEqual(result["date"], "2026-10-01")

    def test_ppsspp_normalizes_release_tag_for_catalog_comparison(self):
        payload = {
            "tag_name": "v1.21.0",
            "published_at": "2026-10-02T12:00:00Z",
            "assets": [{
                "name": "PPSSPP-iOS-v1.21.0.ipa",
                "browser_download_url": "https://github.com/hrydgard/ppsspp/releases/download/v1.21.0/app.ipa",
                "size": 456,
            }],
        }
        with patch.object(check_official_updates, "fetch_json", return_value=payload):
            result = check_official_updates.resolve_latest("PPSSPP")
        self.assertEqual(result["label"], "1.21.0")
        self.assertEqual(result["url"], payload["assets"][0]["browser_download_url"])
        self.assertEqual(result["date"], "2026-10-02")


if __name__ == "__main__":
    unittest.main()
