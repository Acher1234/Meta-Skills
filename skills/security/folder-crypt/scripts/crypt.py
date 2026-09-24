"""Password-based file or folder encrypt / decrypt (AES-256-GCM).

On-disk layout (version 1):
  magic (4) | version (1) | pbkdf2_iterations uint32be (4) | salt (16) | nonce (12) | ciphertext+tag
"""

from __future__ import annotations

import io
import os
import shutil
import struct
import tarfile
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"FCR1"
VERSION = 1
SALT_LEN = 16
NONCE_LEN = 12
KEY_LEN = 32
PBKDF2_ITERATIONS = 480_000
HEADER_LEN = 4 + 1 + 4 + SALT_LEN + NONCE_LEN


class CryptError(Exception):
    pass


def archive_path_for(folder: Path) -> Path:
    return folder.parent / f"{folder.name}.fcr"


def folder_path_for(archive: Path) -> Path:
    name = archive.name
    if name.endswith(".fcr"):
        name = name[: -len(".fcr")]
    return archive.parent / name


def _kdf(password: str, salt: bytes, iterations: int) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode("utf-8"))


def _skip_links(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
    if tarinfo.issym() or tarinfo.islnk():
        return None
    return tarinfo


def _pack(source: Path) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        if source.is_file():
            tar.add(source, arcname=source.name, filter=_skip_links)
        else:
            tar.add(source, arcname=".", filter=_skip_links)
    return buf.getvalue()


def _single_file(tar: tarfile.TarFile) -> tarfile.TarInfo | None:
    """A one-file archive has no directory member. Folder archives include '.'."""
    members = tar.getmembers()
    if any(member.isdir() for member in members):
        return None
    files = [member for member in members if member.isfile()]
    if len(members) == 1 and len(files) == 1:
        name = Path(files[0].name)
        if name.is_absolute() or ".." in name.parts:
            raise CryptError(f"unsafe path in archive: {files[0].name}")
        return files[0]
    raise CryptError("unsupported archive layout")


def _unpack_folder(tar: tarfile.TarFile, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    dest = dest.resolve()
    for member in tar.getmembers():
        member_path = (dest / member.name).resolve()
        if not member_path.is_relative_to(dest):
            raise CryptError(f"unsafe path in archive: {member.name}")
    tar.extractall(dest)


def _clear(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        resolved = path.resolve()
        if resolved == Path(resolved.anchor):
            raise CryptError(f"refusing to replace filesystem root: {resolved}")
        shutil.rmtree(path)


def _unpack_file(tar: tarfile.TarFile, member: tarfile.TarInfo, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    extracted = tar.extractfile(member)
    if extracted is None:
        raise CryptError("archive member is not a file")
    with extracted:
        dest.write_bytes(extracted.read())


def encrypt_folder(folder: Path, password: str, output: Path) -> int:
    if folder.is_symlink():
        raise CryptError(f"refusing to encrypt a symlink: {folder}")
    folder = folder.resolve()
    output = output.resolve()
    if not folder.is_file() and not folder.is_dir():
        raise CryptError(f"not a file or directory: {folder}")
    if output == folder or (folder.is_dir() and output.is_relative_to(folder)):
        raise CryptError("output archive must not be the file being encrypted or inside the folder")
    plaintext = _pack(folder)
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = _kdf(password, salt, PBKDF2_ITERATIONS)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, MAGIC)
    header = MAGIC + bytes([VERSION]) + struct.pack(">I", PBKDF2_ITERATIONS) + salt + nonce
    output.parent.mkdir(parents=True, exist_ok=True)
    _clear(output)
    output.write_bytes(header + ciphertext)
    return output.stat().st_size


def decrypt_archive(archive: Path, password: str, dest: Path) -> int:
    if not archive.is_file():
        raise CryptError(f"not a file: {archive}")
    archive = archive.resolve()
    dest = dest.resolve()
    if dest == archive or archive.is_relative_to(dest):
        raise CryptError("destination must not be the archive or a parent of it")
    blob = archive.read_bytes()
    if len(blob) < HEADER_LEN + 16:
        raise CryptError("file is too small to be a folder-crypt archive")
    if blob[:4] != MAGIC:
        raise CryptError("not a folder-crypt archive (bad magic)")
    version = blob[4]
    if version != VERSION:
        raise CryptError(f"unsupported archive version: {version}")
    iterations = struct.unpack(">I", blob[5:9])[0]
    if iterations < 100_000:
        raise CryptError("invalid KDF iterations")
    salt = blob[9 : 9 + SALT_LEN]
    nonce = blob[9 + SALT_LEN : HEADER_LEN]
    ciphertext = blob[HEADER_LEN:]
    key = _kdf(password, salt, iterations)
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, MAGIC)
    except InvalidTag as exc:
        raise CryptError("wrong password or corrupted archive") from exc
    # Password already checked: replacing dest cannot throw away plaintext on a bad password.
    _clear(dest)
    with tarfile.open(fileobj=io.BytesIO(plaintext), mode="r:gz") as tar:
        file_member = _single_file(tar)
        if file_member is not None:
            _unpack_file(tar, file_member, dest)
        else:
            _unpack_folder(tar, dest)
    return dest.stat().st_size
