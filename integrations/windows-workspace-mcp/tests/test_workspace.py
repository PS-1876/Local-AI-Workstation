import concurrent.futures
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workspace import MAX_TEXT_BYTES, Workspace, WorkspaceError, result_for


@unittest.skipUnless(os.name == "nt", "Native Windows filesystem tests")
class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="local-ai-workspace-mcp-")
        self.base = Path(self.temporary.name).resolve(strict=True)
        self.root = self.base / "workspace"
        self.outside = self.base / "outside"
        self.root.mkdir()
        self.outside.mkdir()
        self.links = []
        self.workspace = Workspace(str(self.root))

    def tearDown(self):
        # Remove only test-created links, without traversing their destinations.
        for link in reversed(self.links):
            if link.is_junction():
                link.rmdir()
            elif link.is_symlink():
                link.unlink()
            elif link.exists():  # a test-created hard link
                link.unlink()
        # Verify the absolute temporary deletion target before recursive cleanup.
        self.assertEqual(self.base.resolve(strict=True), self.base)
        self.assertEqual(self.base.parent, Path(tempfile.gettempdir()).resolve(strict=True))
        self.assertTrue(self.base.name.startswith("local-ai-workspace-mcp-"))
        self.temporary.cleanup()

    def assert_denied(self, operation, *arguments, code=None):
        result = result_for(operation, *arguments)
        self.assertFalse(result["ok"])
        if code:
            self.assertEqual(result["error"]["code"], code)
        self.assertNotIn(str(self.base), result["error"]["message"])
        return result

    def test_create_read_exact_unicode_and_digest(self):
        text = "Hello, workstation.\r\nCaf\u00e9 \U0001f642\n"
        result = self.workspace.create("hello.txt", text)
        expected = text.encode("utf-8")
        self.assertTrue(result["created"] and result["verified"])
        self.assertEqual(result["sha256"], hashlib.sha256(expected).hexdigest())
        self.assertEqual(result["bytes"], len(expected))
        self.assertEqual((self.root / "hello.txt").read_bytes(), expected)
        self.assertEqual(self.workspace.read("hello.txt")["text"], text)

    def test_empty_file_is_supported(self):
        result = self.workspace.create("empty.txt", "")
        self.assertEqual(result["bytes"], 0)
        self.assertEqual(self.workspace.read("empty.txt")["text"], "")

    def test_existing_parent_and_backslash_path(self):
        (self.root / "nested").mkdir()
        self.assertEqual(self.workspace.create("nested\\file.txt", "x")["path"], "nested/file.txt")
        self.assertEqual(self.workspace.read("nested/file.txt")["text"], "x")

    def test_missing_parent_is_not_created(self):
        self.assert_denied(self.workspace.create, "missing/file.txt", "x")
        self.assertFalse((self.root / "missing").exists())

    def test_duplicate_create_never_overwrites(self):
        self.workspace.create("keep.txt", "original")
        self.assert_denied(self.workspace.create, "keep.txt", "replacement", code="already_exists")
        self.assertEqual((self.root / "keep.txt").read_text(), "original")

    def test_concurrent_creates_have_exactly_one_winner(self):
        barrier = threading.Barrier(8)

        def create(index):
            barrier.wait()
            return result_for(self.workspace.create, "race.txt", f"writer {index}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(create, range(8)))
        self.assertEqual(sum(result["ok"] for result in results), 1)
        self.assertIn(self.workspace.read("race.txt")["text"], {f"writer {index}" for index in range(8)})
        self.assertEqual([path.name for path in self.root.iterdir()], ["race.txt"])

    def test_invalid_paths_reject_read_and_create(self):
        paths = [
            "", "../escape.txt", "sub/../escape.txt", "sub//file.txt", "./file.txt",
            "C:/outside.txt", "C:outside.txt", "/outside.txt", "\\outside.txt",
            "\\\\server\\share\\file.txt", "\\\\?\\C:\\outside.txt", "file.txt:stream",
            "NUL.txt", "CON", "COM1.log", "LPT1", "trailing.", "trailing ",
            "bad\nname", "bad\x00name", "bad?.txt", ".workspace-create-test.tmp",
        ]
        for path in paths:
            with self.subTest(path=repr(path)):
                self.assert_denied(self.workspace.read, path, code="invalid_path")
                self.assert_denied(self.workspace.create, path, "x", code="invalid_path")
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_size_limits_use_encoded_bytes(self):
        self.workspace.create("limit.txt", "x" * MAX_TEXT_BYTES)
        self.assertEqual(self.workspace.read("limit.txt")["bytes"], MAX_TEXT_BYTES)
        self.assert_denied(self.workspace.create, "large.txt", "\u00e9" * (MAX_TEXT_BYTES // 2 + 1), code="too_large")
        self.assertFalse((self.root / "large.txt").exists())
        (self.root / "oversized.txt").write_bytes(b"x" * (MAX_TEXT_BYTES + 1))
        self.assert_denied(self.workspace.read, "oversized.txt", code="too_large")

    def test_invalid_text_and_non_utf8_reads(self):
        self.assert_denied(self.workspace.create, "nul.txt", "a\x00b", code="invalid_text")
        self.assert_denied(self.workspace.create, "surrogate.txt", "\ud800", code="invalid_text")
        (self.root / "binary.txt").write_bytes(b"\xff")
        self.assert_denied(self.workspace.read, "binary.txt", code="not_utf8")
        (self.root / "zero-byte.txt").write_bytes(b"a\x00b")
        self.assert_denied(self.workspace.read, "zero-byte.txt", code="not_text")

    def test_directory_is_not_a_text_file(self):
        (self.root / "directory").mkdir()
        self.assert_denied(self.workspace.read, "directory", code="not_file")
        self.assert_denied(self.workspace.create, "directory", "x", code="not_file")

    def test_explicit_existing_local_root_is_required(self):
        for root in ["", "relative", "C:\\", "\\\\server\\share\\folder", str(self.base / "absent")]:
            with self.subTest(root=root):
                with self.assertRaises(WorkspaceError):
                    Workspace(root)
        with self.assertRaises(WorkspaceError):
            Workspace.from_environment({})

    def test_hard_link_is_rejected(self):
        outside = self.outside / "secret.txt"
        outside.write_text("outside fixture")
        link = self.root / "linked.txt"
        os.link(outside, link)
        self.links.append(link)
        self.assert_denied(self.workspace.read, "linked.txt", code="link_rejected")
        self.assert_denied(self.workspace.create, "linked.txt", "x", code="link_rejected")
        self.assertEqual(outside.read_text(), "outside fixture")

    def test_file_symlink_is_rejected(self):
        outside = self.outside / "secret.txt"
        outside.write_text("outside fixture")
        link = self.root / "linked.txt"
        try:
            os.symlink(outside, link)
        except OSError as exc:
            if getattr(exc, "winerror", None) == 1314:
                self.skipTest("Creating symlinks requires Windows Developer Mode or privilege")
            raise
        self.links.append(link)
        self.assert_denied(self.workspace.read, "linked.txt", code="link_rejected")
        self.assert_denied(self.workspace.create, "linked.txt", "x", code="link_rejected")

    def _junction(self, link, destination):
        self.assertTrue(link.parent.resolve(strict=True).is_relative_to(self.base))
        self.assertTrue(destination.resolve(strict=True).is_relative_to(self.base))
        environment = dict(os.environ)
        environment["WORKSPACE_MCP_TEST_LINK"] = str(link)
        environment["WORKSPACE_MCP_TEST_TARGET"] = str(destination)
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
             "New-Item -ItemType Junction -Path $env:WORKSPACE_MCP_TEST_LINK -Target $env:WORKSPACE_MCP_TEST_TARGET -ErrorAction Stop | Out-Null"],
            env=environment, capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, "Could not create an isolated test junction")
        self.links.append(link)
        self.assertTrue(link.is_junction())

    def test_directory_junction_rejected_for_read_and_create(self):
        (self.outside / "secret.txt").write_text("outside fixture")
        self._junction(self.root / "linked", self.outside)
        self.assert_denied(self.workspace.read, "linked/secret.txt", code="link_rejected")
        self.assert_denied(self.workspace.create, "linked/new.txt", "x", code="link_rejected")
        self.assertFalse((self.outside / "new.txt").exists())

    def test_junction_root_or_ancestor_is_rejected(self):
        (self.outside / "nested").mkdir()
        link = self.base / "alias"
        self._junction(link, self.outside)
        for root in [link, link / "nested"]:
            with self.assertRaises(WorkspaceError) as raised:
                Workspace(str(root))
            self.assertEqual(raised.exception.code, "link_rejected")


if __name__ == "__main__":
    unittest.main()
