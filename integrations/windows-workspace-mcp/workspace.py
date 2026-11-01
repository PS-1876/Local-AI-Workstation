"""Bounded UTF-8 file operations for an explicitly selected Windows workspace."""

from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import tempfile
from typing import Mapping

MAX_TEXT_BYTES = 200 * 1024
ROOT_VARIABLE = "WORKSTATION_WORKSPACE_ROOT"
_TEMP_PREFIX = ".workspace-create-"


class WorkspaceError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _identity(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _reject_link(info: os.stat_result) -> None:
    if stat.S_ISLNK(info.st_mode) or (
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    ):
        raise WorkspaceError("link_rejected", "Links and reparse points are not allowed.")


def _check_directory_chain(path: Path) -> os.stat_result:
    """Inspect every ancestor with lstat, before following any directory entry."""
    current = Path(path.anchor)
    info = current.lstat()
    _reject_link(info)
    for part in path.parts[1:]:
        current /= part
        info = current.lstat()
        _reject_link(info)
        if not stat.S_ISDIR(info.st_mode):
            raise WorkspaceError("not_directory", "A required directory does not exist.")
    return info


def _relative_parts(value: str) -> tuple[str, ...]:
    if not isinstance(value, str) or not value or len(value) > 1024:
        raise WorkspaceError("invalid_path", "Supply a nonempty workspace-relative file path.")
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or ":" in normalized:
        raise WorkspaceError("invalid_path", "Absolute paths, drive paths, and streams are not allowed.")
    parts = tuple(normalized.split("/"))
    for part in parts:
        if (
            part in ("", ".", "..")
            or part.endswith((" ", "."))
            or any(ord(char) < 32 or ord(char) == 127 or char in '<>"|?*' for char in part)
            or PureWindowsPath(part).is_reserved()
            or part.casefold().startswith(_TEMP_PREFIX)
        ):
            raise WorkspaceError("invalid_path", "Path contains a forbidden or reserved component.")
    return parts


class Workspace:
    """A path-based helper, not an OS sandbox or a hostile-filesystem boundary."""

    def __init__(self, root: str):
        if os.name != "nt":
            raise WorkspaceError("unsupported_platform", "Run this bridge with native Windows Python.")
        if not isinstance(root, str) or not root.strip():
            raise WorkspaceError("root_required", f"Set {ROOT_VARIABLE} explicitly.")
        value = root.replace("/", "\\")
        if not re.match(r"^[A-Za-z]:\\", value) or value.startswith("\\\\"):
            raise WorkspaceError("invalid_root", "The workspace root must be an absolute local Windows folder.")
        raw_parts = value[3:].rstrip("\\").split("\\")
        if not value[3:].strip("\\"):
            raise WorkspaceError("invalid_root", "Select a workspace folder, not an entire drive.")
        _relative_parts("/".join(raw_parts))
        self.root = Path(value)
        drive_type = ctypes.windll.kernel32.GetDriveTypeW
        drive_type.argtypes = [ctypes.c_wchar_p]
        drive_type.restype = ctypes.c_uint
        if drive_type(self.root.anchor) not in (2, 3, 6):
            raise WorkspaceError("invalid_root", "The workspace must be on a local writable drive.")
        try:
            root_info = _check_directory_chain(self.root)
        except OSError as exc:
            raise WorkspaceError("invalid_root", "The configured workspace folder must already exist.") from exc
        self._root_identity = _identity(root_info)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str] | None = None) -> "Workspace":
        environment = os.environ if environment is None else environment
        return cls(environment.get(ROOT_VARIABLE, ""))

    def _check_root(self) -> None:
        if _identity(_check_directory_chain(self.root)) != self._root_identity:
            raise WorkspaceError("root_changed", "The configured workspace directory changed; reconnect explicitly.")

    def _target(self, value: str, *, allow_missing: bool = False) -> tuple[Path, str]:
        parts = _relative_parts(value)
        self._check_root()
        target = self.root.joinpath(*parts)
        # The lexical validation forbids escapes; the lstat walk rejects links.
        # Do not resolve a user path first, since that would follow a reparse point.
        _check_directory_chain(target.parent)
        try:
            info = target.lstat()
        except FileNotFoundError:
            if allow_missing:
                return target, "/".join(parts)
            raise WorkspaceError("not_found", "The requested file does not exist.") from None
        _reject_link(info)
        if not stat.S_ISREG(info.st_mode):
            raise WorkspaceError("not_file", "Only regular text files are supported.")
        if info.st_nlink != 1:
            raise WorkspaceError("link_rejected", "Files with multiple hard links are not allowed.")
        return target, "/".join(parts)

    def read(self, path: str) -> dict:
        target, relative = self._target(path)
        with target.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            _reject_link(opened)
            if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise WorkspaceError("link_rejected", "Only a regular file with one link may be read.")
            self._target(path)
            if _identity(target.lstat()) != _identity(opened):
                raise WorkspaceError("file_changed", "The file changed while opening it; retry after review.")
            data = stream.read(MAX_TEXT_BYTES + 1)
            after = os.fstat(stream.fileno())
        self._target(path)
        if (
            _identity(target.lstat()) != _identity(opened)
            or (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns)
        ):
            raise WorkspaceError("file_changed", "The file changed while reading it; retry after review.")
        if len(data) > MAX_TEXT_BYTES:
            raise WorkspaceError("too_large", "Text must be at most 204800 UTF-8 bytes.")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise WorkspaceError("not_utf8", "Only UTF-8 text is supported.") from exc
        if "\x00" in text:
            raise WorkspaceError("not_text", "NUL bytes are not supported in text files.")
        return {
            "ok": True,
            "path": relative,
            "encoding": "utf-8",
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "text": text,
        }

    def create(self, path: str, text: str) -> dict:
        if not isinstance(text, str) or "\x00" in text:
            raise WorkspaceError("invalid_text", "Supply UTF-8 text without NUL bytes.")
        try:
            data = text.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise WorkspaceError("invalid_text", "Text cannot be encoded as UTF-8.") from exc
        if len(data) > MAX_TEXT_BYTES:
            raise WorkspaceError("too_large", "Text must be at most 204800 UTF-8 bytes.")
        target, relative = self._target(path, allow_missing=True)
        if target.exists():
            raise WorkspaceError("already_exists", "The file already exists; this tool never replaces it.")
        temporary: Path | None = None
        temporary_identity: tuple[int, int] | None = None
        published = False
        try:
            descriptor, name = tempfile.mkstemp(prefix=_TEMP_PREFIX, suffix=".tmp", dir=target.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as stream:
                temporary_identity = _identity(os.fstat(stream.fileno()))
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            self._target(path, allow_missing=True)
            try:
                # Windows rename on the same volume publishes the completed file
                # and refuses an existing destination. Never use os.replace here.
                os.rename(temporary, target)
            except FileExistsError as exc:
                raise WorkspaceError("already_exists", "The file already exists; this tool never replaces it.") from exc
            published = True
            try:
                result = self.read(path)
            except (OSError, WorkspaceError) as exc:
                raise WorkspaceError("verification_failed", "A new file was published, but verification failed; inspect it before retrying.") from exc
            if result["sha256"] != hashlib.sha256(data).hexdigest():
                raise WorkspaceError("verification_failed", "A new file may exist, but its read-back verification failed.")
            return {key: value for key, value in result.items() if key != "text"} | {"created": True, "verified": True}
        finally:
            # There is no delete tool. Cleanup only removes this operation's own
            # unpublished staging file, after rechecking its identity and parent.
            if temporary is not None and not published:
                try:
                    self._check_root()
                    _check_directory_chain(temporary.parent)
                    info = temporary.lstat()
                    _reject_link(info)
                    if _identity(info) == temporary_identity:
                        temporary.unlink()
                except (OSError, WorkspaceError):
                    # Leave an uncertain staging file for operator inspection.
                    pass


def result_for(operation, *args) -> dict:
    """Return stable errors without exposing the host's absolute filesystem paths."""
    try:
        return operation(*args)
    except WorkspaceError as exc:
        return {"ok": False, "error": {"code": exc.code, "message": str(exc)}}
    except OSError:
        return {"ok": False, "error": {"code": "filesystem_error", "message": "Filesystem access failed; inspect local permissions and directory state."}}
