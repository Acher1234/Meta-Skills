"""FOLDER list parsing and encrypt/decrypt target selection."""

from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import cli  # noqa: E402
from crypt import CryptError, decrypt_archive, encrypt_folder  # noqa: E402
from skill_env import split_folders  # noqa: E402


class SplitFoldersTests(unittest.TestCase):
    def test_single_path(self) -> None:
        self.assertEqual(split_folders("/only"), ["/only"])

    def test_comma_separated_with_spaces(self) -> None:
        self.assertEqual(split_folders("a, b, c"), ["a", "b", "c"])

    def test_empty_segments_dropped(self) -> None:
        self.assertEqual(split_folders("a, , b,,"), ["a", "b"])
        self.assertEqual(split_folders("  ,  "), [])
        self.assertEqual(split_folders(None), [])
        self.assertEqual(split_folders(""), [])

    def test_folder_is_first_entry(self) -> None:
        saved = dict(cli.ENV.env)
        try:
            cli.ENV.env = {"FOLDER": "a, b, c"}
            self.assertEqual(cli.ENV.folders(), ["a", "b", "c"])
            self.assertEqual(cli.ENV.folder(), "a")
            cli.ENV.env = {}
            self.assertIsNone(cli.ENV.folder())
        finally:
            cli.ENV.env = saved


class ResolvePathTests(unittest.TestCase):
    def test_relative_path_starts_at_project_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.dict("os.environ", {"PROJECT_PATH": str(root)}):
                self.assertEqual(cli.resolve_path("secrets"), (root / "secrets").resolve())
                absolute = root / "abs"
                self.assertEqual(cli.resolve_path(str(absolute)), absolute.resolve())


def _run(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, json.loads(buf.getvalue())


class EncryptTargetTests(unittest.TestCase):
    def test_encrypt_all_reports_each_path_including_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ["good", "bad", "also"]

            def fake_encrypt(folder: Path, password: str, output: Path) -> int:
                self.assertEqual(password, "pw")
                if folder.name == "bad":
                    raise CryptError("boom")
                return 8

            with (
                patch.object(cli.ENV, "folders", return_value=names),
                patch.object(cli.ENV, "password", return_value=None),
                patch.object(cli, "encrypt_folder", side_effect=fake_encrypt) as enc,
                patch.dict("os.environ", {"PROJECT_PATH": str(root)}),
            ):
                code, data = _run(["encrypt", "--password", "pw"])

            self.assertEqual(enc.call_count, 3)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertEqual(data["action"], "encrypt")
            self.assertEqual([item["folder"] for item in data["items"]], [str((root / name).resolve()) for name in names])
            self.assertTrue(data["items"][0]["ok"])
            self.assertFalse(data["items"][1]["ok"])
            self.assertEqual(data["items"][1]["error"], "boom")
            self.assertTrue(data["items"][2]["ok"])

    def test_positional_encrypts_only_that_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            only = root / "only"
            with (
                patch.object(cli.ENV, "folders", return_value=["a", "b", "c"]) as listed,
                patch.object(cli, "encrypt_folder", return_value=4) as enc,
                patch.dict("os.environ", {"PROJECT_PATH": str(root)}),
            ):
                code, data = _run(["encrypt", "only", "--password", "pw"])

            listed.assert_not_called()
            self.assertEqual(enc.call_count, 1)
            self.assertEqual(enc.call_args.args[0], only.resolve())
            self.assertEqual(code, 0)
            self.assertTrue(data["ok"])
            self.assertNotIn("items", data)
            self.assertEqual(data["folder"], str(only.resolve()))

    def test_output_rejected_when_folder_lists_several_paths(self) -> None:
        with (
            patch.object(cli.ENV, "folders", return_value=["a", "b"]),
            patch.object(cli, "encrypt_folder") as enc,
        ):
            code, data = _run(["encrypt", "-o", "out.fcr", "--password", "pw"])
        self.assertEqual(code, 1)
        self.assertTrue(data["error"])
        self.assertIn("single target", data["message"])
        enc.assert_not_called()

    def test_output_allowed_for_one_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root / "out.fcr"
            with (
                patch.object(cli.ENV, "folders", return_value=["secrets"]),
                patch.object(cli, "encrypt_folder", return_value=3) as enc,
                patch.dict("os.environ", {"PROJECT_PATH": str(root)}),
            ):
                code, data = _run(["encrypt", "-o", str(dest), "--password", "pw"])
            self.assertEqual(code, 0)
            self.assertEqual(enc.call_args.args[0], (root / "secrets").resolve())
            self.assertEqual(enc.call_args.args[2], dest.resolve())
            self.assertEqual(len(data["items"]), 1)


class DecryptTargetTests(unittest.TestCase):
    def test_decrypt_all_uses_sibling_fcr_for_a_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            notes = root / "notes"
            notes.mkdir()
            (root / "notes.fcr").write_bytes(b"x")
            (root / "secrets.fcr").write_bytes(b"y")
            with (
                patch.object(cli.ENV, "folders", return_value=["notes", "secrets.fcr"]),
                patch.object(cli, "decrypt_archive", return_value=1) as dec,
                patch.dict("os.environ", {"PROJECT_PATH": str(root)}),
            ):
                code, data = _run(["decrypt", "--password", "pw"])
            self.assertEqual(code, 0)
            self.assertEqual(
                [call.args[0] for call in dec.call_args_list],
                [(root / "notes.fcr").resolve(), (root / "secrets.fcr").resolve()],
            )
            self.assertEqual(len(data["items"]), 2)

    def test_positional_decrypts_only_that_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "only.fcr"
            archive.write_bytes(b"x")
            with (
                patch.object(cli.ENV, "folders", return_value=["notes", "secrets"]) as listed,
                patch.object(cli, "decrypt_archive", return_value=1) as dec,
            ):
                code, data = _run(["decrypt", str(archive), "--password", "pw"])
            listed.assert_not_called()
            self.assertEqual(dec.call_count, 1)
            self.assertEqual(dec.call_args.args[0], archive.resolve())
            self.assertNotIn("items", data)
            self.assertEqual(code, 0)


class FileRoundtripTests(unittest.TestCase):
    def test_encrypt_and_decrypt_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "notes.txt"
            source.write_text("hello file", encoding="utf-8")
            archive = root / "notes.txt.fcr"
            encrypt_folder(source, "pw", archive)
            source.unlink()
            decrypt_archive(archive, "pw", source)
            self.assertEqual(source.read_text(encoding="utf-8"), "hello file")
            self.assertTrue(source.is_file())

    def test_encrypt_and_decrypt_replace_existing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "notes.txt"
            archive = root / "notes.txt.fcr"
            source.write_text("one", encoding="utf-8")
            encrypt_folder(source, "pw", archive)
            source.write_text("two", encoding="utf-8")
            encrypt_folder(source, "pw", archive)
            source.write_text("keep-me", encoding="utf-8")
            with self.assertRaises(CryptError):
                decrypt_archive(archive, "nope", source)
            self.assertEqual(source.read_text(encoding="utf-8"), "keep-me")
            decrypt_archive(archive, "pw", source)
            self.assertEqual(source.read_text(encoding="utf-8"), "two")

    def test_decrypt_replaces_an_existing_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "secrets"
            folder.mkdir()
            (folder / "a.txt").write_text("inside", encoding="utf-8")
            archive = root / "secrets.fcr"
            encrypt_folder(folder, "pw", archive)
            (folder / "stale.txt").write_text("old", encoding="utf-8")
            decrypt_archive(archive, "pw", folder)
            self.assertEqual((folder / "a.txt").read_text(encoding="utf-8"), "inside")
            self.assertFalse((folder / "stale.txt").exists())

    def test_encrypt_and_decrypt_a_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "secrets"
            folder.mkdir()
            (folder / "a.txt").write_text("inside", encoding="utf-8")
            archive = root / "secrets.fcr"
            encrypt_folder(folder, "pw", archive)
            shutil.rmtree(folder)
            decrypt_archive(archive, "pw", folder)
            self.assertEqual((folder / "a.txt").read_text(encoding="utf-8"), "inside")

    def test_remove_unlinks_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "notes.txt"
            source.write_text("x", encoding="utf-8")
            with patch.object(cli, "encrypt_folder", return_value=4):
                code, data = _run(["encrypt", str(source), "--password", "pw", "--remove"])
            self.assertEqual(code, 0)
            self.assertTrue(data["removed"])
            self.assertFalse(source.exists())

    def test_decrypt_plaintext_file_uses_sibling_fcr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes.txt").write_text("x", encoding="utf-8")
            archive = root / "notes.txt.fcr"
            archive.write_bytes(b"x")
            with (
                patch.object(cli.ENV, "folders", return_value=["notes.txt"]),
                patch.object(cli, "decrypt_archive", return_value=1) as dec,
                patch.dict("os.environ", {"PROJECT_PATH": str(root)}),
            ):
                code, _data = _run(["decrypt", "--password", "pw"])
            self.assertEqual(code, 0)
            self.assertEqual(dec.call_args.args[0], archive.resolve())


class EnvCommandTests(unittest.TestCase):
    def test_env_shows_raw_folder_and_hides_password(self) -> None:
        workspace = Path("/tmp/folder-crypt-workspace")
        with (
            patch.object(cli.ENV, "env_path", return_value=workspace / ".env"),
            patch.object(
                cli.ENV,
                "read_env",
                return_value={"FOLDER": "a, b, ,c", "PASSWORD": "s3cret"},
            ),
            patch.object(cli.ENV, "folders", return_value=["a", "b", "c"]),
            patch.object(cli.ENV, "env_cred", return_value=SimpleNamespace(workspace=workspace)),
            patch.dict("os.environ", {"PROJECT_PATH": "/proj"}),
        ):
            code, data = _run(["env"])
        self.assertEqual(code, 0)
        self.assertEqual(data["FOLDER"], "a, b, ,c")
        self.assertEqual(data["folders"], ["a", "b", "c"])
        self.assertEqual(data["PASSWORD"], "set")
        self.assertEqual(data["PROJECT_PATH"], "/proj")
        self.assertNotIn("s3cret", json.dumps(data))


if __name__ == "__main__":
    unittest.main()
