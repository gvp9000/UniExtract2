import os
import sys
import hashlib
from pathlib import Path

# ============================================================
# UniExtract2 update index generator
# Creates an "index" file in every subfolder, but NOT in the
# chosen root folder itself, using full relative paths from the chosen root.
#
# Default behavior:
# - If a folder path is given as a command-line argument, use it.
# - Otherwise, use the folder where this script is located.
#
# Example output lines:
#   UniExtract.exe,123456,0123456789abcdef0123456789abcdef
#   bin/,129995485
#   bin\index contains:
#   bin/7ZSplit.exe,9728,5c7a019b5cb72fec6e40e952909e9c8a
#   bin/x64/,12345678
#
# Notes:
# - Generated "index" files are excluded from manifests and size totals.
# - Top-level special metadata files are excluded from manifests:
#   news, ffmpeg, ffmpeg-32, ffmpeg-xp
# ============================================================

DEFAULT_BASE_DIR = Path(__file__).resolve().parent
INDEX_FILENAME = "index"

# Exclude from every folder
SCRIPT_FILENAME = Path(__file__).name

# Exclude from every folder
ALWAYS_EXCLUDE_FILENAMES = {
    INDEX_FILENAME,
    SCRIPT_FILENAME,
}

# Exclude only when these files are in the top-level root folder
TOP_LEVEL_SPECIAL_EXCLUDE_FILENAMES = {
    "news",
    "ffmpeg",
    "ffmpeg-32",
    "ffmpeg-xp",
}


def md5_file(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the MD5 hash of a file."""
    h = hashlib.md5()
    with file_path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def is_excluded_file(file_path: Path, base_dir: Path) -> bool:
    """Return True if file should be excluded from manifests and size totals."""
    name = file_path.name

    if name in ALWAYS_EXCLUDE_FILENAMES:
        return True

    if file_path.parent == base_dir and name in TOP_LEVEL_SPECIAL_EXCLUDE_FILENAMES:
        return True

    return False


def rel_posix(path: Path, base_dir: Path) -> str:
    """Return path relative to base_dir using forward slashes."""
    return path.relative_to(base_dir).as_posix()


def directory_total_size(dir_path: Path, base_dir: Path) -> int:
    """
    Return recursive directory size excluding generated 'index' files
    and excluded top-level metadata files.
    """
    total = 0

    for root, _, files in os.walk(dir_path):
        root_path = Path(root)
        for filename in files:
            file_path = root_path / filename
            if is_excluded_file(file_path, base_dir):
                continue

            try:
                total += file_path.stat().st_size
            except OSError:
                print(f"[WARN] Could not read size: {file_path}")

    return total


def sorted_immediate_entries(folder: Path, base_dir: Path):
    """Return sorted immediate files and dirs for a folder."""
    files = []
    dirs = []

    try:
        for entry in folder.iterdir():
            if entry.is_file():
                if is_excluded_file(entry, base_dir):
                    continue
                files.append(entry)
            elif entry.is_dir():
                dirs.append(entry)
    except OSError as e:
        print(f"[WARN] Could not read folder: {folder} ({e})")

    # Sort case-insensitively
    files.sort(key=lambda p: p.name.lower())
    dirs.sort(key=lambda p: p.name.lower())

    # Top-level: force UniExtract.exe first if it exists
    if folder == base_dir:
        uniextract_files = [f for f in files if f.name.lower() == "uniextract.exe"]
        other_files = [f for f in files if f.name.lower() != "uniextract.exe"]
        files = uniextract_files + other_files

    return files, dirs


def build_index_lines(folder: Path, base_dir: Path) -> list[str]:
    """
    Build manifest lines for one folder.

    Files and directories are emitted as full paths relative to the root base_dir.
    """
    lines: list[str] = []

    files, dirs = sorted_immediate_entries(folder, base_dir)

    # Files first
    for file_path in files:
        try:
            size = file_path.stat().st_size
            md5 = md5_file(file_path)
            rel = rel_posix(file_path, base_dir)
            lines.append(f"{rel},{size},{md5}")
        except OSError as e:
            print(f"[WARN] Skipping unreadable file: {file_path} ({e})")

    # Then immediate directories
    for dir_path in dirs:
        try:
            rel = rel_posix(dir_path, base_dir) + "/"
            size = directory_total_size(dir_path, base_dir)
            lines.append(f"{rel},{size}")
        except OSError as e:
            print(f"[WARN] Skipping unreadable directory: {dir_path} ({e})")

    return lines


def all_directories_topdown(base_dir: Path) -> list[Path]:
    """Return all directories including root, sorted top-down."""
    dirs = []

    for root, subdirs, _ in os.walk(base_dir):
        subdirs.sort(key=lambda s: s.lower())
        dirs.append(Path(root))

    dirs.sort(key=lambda p: (len(p.relative_to(base_dir).parts), rel_posix(p, base_dir).lower()))
    return dirs


def write_index_file(folder: Path, lines: list[str]) -> None:
    """Write the index file for one folder."""
    index_path = folder / INDEX_FILENAME
    with index_path.open("w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")


def resolve_base_dir() -> Path | None:
    """
    Resolve the root folder.

    Priority:
    1) First command-line argument, if provided.
    2) Folder where this script is located.
    """
    if len(sys.argv) > 1:
        chosen = Path(sys.argv[1]).expanduser().resolve()
        if not chosen.exists() or not chosen.is_dir():
            print(f"[ERROR] Folder does not exist or is not a directory: {chosen}")
            return None
        return chosen

    if DEFAULT_BASE_DIR.exists() and DEFAULT_BASE_DIR.is_dir():
        return DEFAULT_BASE_DIR

    print(f"[ERROR] Script folder does not exist or is not a directory: {DEFAULT_BASE_DIR}")
    return None


def main() -> None:
    print("UniExtract2 recursive index generator")
    print()

    base_dir = resolve_base_dir()
    if base_dir is None:
        input("\nPress Enter to exit...")
        return

    print(f"[INFO] Root folder: {base_dir}")
    print()

    dirs = all_directories_topdown(base_dir)
    if not dirs:
        print("[ERROR] No folders found.")
        input("\nPress Enter to exit...")
        return

    created = 0

    for folder in dirs:
        if folder == base_dir:
            print(f"[INFO] Skipping root folder (no index created): {folder}")
            continue

        lines = build_index_lines(folder, base_dir)
        try:
            write_index_file(folder, lines)
            created += 1
            rel_folder = rel_posix(folder, base_dir)
            print(f"[OK] Wrote index: {folder / INDEX_FILENAME}  ({len(lines)} entries, folder '{rel_folder}')")
        except OSError as e:
            print(f"[ERROR] Failed to write index in {folder}: {e}")

    print()
    print(f"[DONE] Created/updated {created} index file(s).")
    print()
    print("No index is created in the root folder:")
    print(base_dir)

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
