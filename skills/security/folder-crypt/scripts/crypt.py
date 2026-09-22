"""Password-based folder encrypt / decrypt (AES-256-GCM).

On-disk layout (version 1):
  magic (4) | version (1) | pbkdf2_iterations uint32be (4) | salt (16) | nonce (12) | ciphertext+tag
"""

from __future__ import annotations

import io
import os
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


def _pack_folder(folder: Path) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(folder, arcname=".", filter=_skip_links)
    return buf.getvalue()


def _unpack_folder(payload: bytes, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    dest = dest.resolve()
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as tar:
        for member in tar.getmembers():
            member_path = (dest / member.name).resolve()
            if not member_path.is_relative_to(dest):
                raise CryptError(f"unsafe path in archive: {member.name}")
        tar.extractall(dest)


def encrypt_folder(folder: Path, password: str, output: Path) -> int:
    folder = folder.resolve()
    output = output.resolve()
    if not folder.is_dir():
        raise CryptError(f"not a directory: {folder}")
    if output.exists():
        raise CryptError(f"output already exists: {output}")
    if output.is_relative_to(folder):
        raise CryptError("output archive must not be inside the folder being encrypted")
    plaintext = _pack_folder(folder)
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = _kdf(password, salt, PBKDF2_ITERATIONS)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, MAGIC)
    header = MAGIC + bytes([VERSION]) + struct.pack(">I", PBKDF2_ITERATIONS) + salt + nonce
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(header + ciphertext)
    return output.stat().st_size


def decrypt_archive(archive: Path, password: str, dest: Path) -> int:
    if not archive.is_file():
        raise CryptError(f"not a file: {archive}")
    if dest.is_file():
        raise CryptError(f"destination already exists: {dest}")
    if dest.is_dir() and any(dest.iterdir()):
        raise CryptError(f"destination already exists: {dest}")
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
    _unpack_folder(plaintext, dest)
    return dest.stat().st_size
