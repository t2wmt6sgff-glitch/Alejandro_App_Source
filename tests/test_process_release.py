import plistlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts import process_release


PNG = b"\x89PNG\r\n\x1a\n" + b"test-icon"


def plist(**values):
    return plistlib.dumps(values)


class InspectIpaTests(unittest.TestCase):
    def make_ipa(self, path):
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("Payload/Demo.app/Info.plist", plist(
                CFBundleIdentifier="com.example.demo",
                CFBundleName="Demo",
                CFBundleShortVersionString="1.2",
                CFBundleVersion="12",
                MinimumOSVersion="15.0",
                CFBundleIcons={"CFBundlePrimaryIcon": {"CFBundleIconFiles": ["AppIcon60x60"]}},
                NSCameraUsageDescription="Camera for scanning",
            ))
            archive.writestr("Payload/Demo.app/AppIcon60x60@2x~ipad.png", PNG)
            archive.writestr("Payload/Demo.app/PlugIns/Share.appex/Info.plist", plist(
                CFBundleIdentifier="com.example.demo.share",
                NSPhotoLibraryUsageDescription="Photo access for sharing",
            ))

    def test_extracts_app_and_extension_permissions_privacy_and_icon(self):
        with tempfile.TemporaryDirectory() as folder:
            ipa = Path(folder) / "demo.ipa"
            self.make_ipa(ipa)
            with patch.object(process_release, "signed_entitlements", side_effect=[
                {"com.apple.security.application-groups": ["group.example"], "application-identifier": "ignored"},
                {"com.apple.developer.usernotifications": True},
            ]):
                data = process_release.inspect_ipa(ipa, Path(folder) / "expanded")
        self.assertEqual(data["info"]["CFBundleIdentifier"], "com.example.demo")
        self.assertEqual(data["entitlements"], ["com.apple.developer.usernotifications", "com.apple.security.application-groups"])
        self.assertEqual(data["privacy"], {
            "NSCameraUsageDescription": "Camera for scanning",
            "NSPhotoLibraryUsageDescription": "Photo access for sharing",
        })
        self.assertEqual(data["icon"], PNG)

    def test_rejects_archive_path_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            ipa = Path(folder) / "bad.ipa"
            with zipfile.ZipFile(ipa, "w") as archive:
                archive.writestr("Payload/Demo.app/Info.plist", plist(
                    CFBundleIdentifier="com.example.demo",
                    CFBundleIcons={"CFBundlePrimaryIcon": {"CFBundleIconFiles": ["AppIcon"]}},
                ))
                archive.writestr("Payload/Demo.app/../../outside", "bad")
            with self.assertRaises(SystemExit):
                process_release.inspect_ipa(ipa, Path(folder) / "expanded")

    def test_codesign_failure_is_fatal(self):
        with patch.object(process_release.subprocess, "run", return_value=type("Result", (), {
            "stdout": b"", "stderr": b"code object is not signed", "returncode": 1,
        })()):
            with self.assertRaisesRegex(SystemExit, "catálogo sin cambios"):
                process_release.signed_entitlements(Path("Demo.app"))


if __name__ == "__main__":
    unittest.main()

