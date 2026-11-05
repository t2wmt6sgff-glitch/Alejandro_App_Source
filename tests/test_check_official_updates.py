import unittest
from unittest.mock import patch

from scripts import check_official_updates


class ResolveLatestTests(unittest.TestCase):
    def test_ppsspp_selects_ios_ipa_from_official_latest_release(self):
        payload = {
            "tag_name": "v1.21.0",
            "published_at": "2026-10-02T12:00:00Z",
            "assets": [
                {"name": "PPSSPP-android.apk", "browser_download_url": "https://github.com/example/app.apk", "size": 99},
                {
                    "name": "PPSSPP-iOS-v1.21.0.ipa",
                    "browser_download_url": "https://github.com/hrydgard/ppsspp/releases/download/v1.21.0/app.ipa",
                    "size": 456,
                },
            ],
        }
        with patch.object(check_official_updates, "fetch_json", return_value=payload):
            result = check_official_updates.resolve_latest("PPSSPP")
        self.assertEqual(result["label"], "1.21.0")
        self.assertEqual(result["url"], payload["assets"][1]["browser_download_url"])
        self.assertEqual(result["date"], "2026-10-02")

    def test_version_order_prevents_downgrade(self):
        self.assertGreater(
            check_official_updates.version_tuple("1.20.4"),
            check_official_updates.version_tuple("1.9.9"),
        )
        self.assertLess(
            check_official_updates.version_tuple("1.20.3"),
            check_official_updates.version_tuple("1.20.4"),
        )

if __name__ == "__main__":
    unittest.main()
