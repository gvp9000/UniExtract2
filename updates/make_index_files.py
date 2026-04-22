import os
import sys
import hashlib
from pathlib import Path

# ============================================================
# UniExtract2 update index generator
#
# Correct output structure for your current AU3 setup:
#
# updates/
#   data/
#     UniExtract.exe
#     news
#     index
#     bin/
#       index
#       ...
#   nightly/
#     UniExtract.exe
#     news
#     index
#     bin/
#       index
#       ...
#
# IMPORTANT:
# - No index is created in the parent "updates" folder.
# - If run on the parent "updates" folder, only immediate child folders
#   that contain UniExtract.exe are treated as channels.
# - Paths written into each index are relative to that channel root:
#     data/index      -> UniExtract.exe,...   news,...   bin/,...
#     data/bin/index  -> bin/7ZSplit.exe,...
#   NOT:
#     data/UniExtract.exe
#     data/bin/7ZSplit.exe
#
# Keeps the CMD window open at the end.
# ============================================================

DEFAULT_BASE_DIR = Path(__file__).resolve().parent
INDEX_FILENAME = "index"
SCRIPT_FILENAME = Path(__file__).name

# Exclude from every manifest and size total
ALWAYS_EXCLUDE_FILENAMES = {
    INDEX_FILENAME,
    SCRIPT_FILENAME,
}

# Exclude only when these files are directly in the channel root
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


def is_excluded_file(file_path: Path, channel_root: Path) -> bool:
    """Return True if file should be excluded from manifests and size totals."""
    name = file_path.name

    if name in ALWAYS_EXCLUDE_FILENAMES:
        return True

    if file_path.parent == channel_root and name in TOP_LEVEL_SPECIAL_EXCLUDE_FILENAMES:
        return True

    return False


def rel_posix(path: Path, channel_root: Path) -> str:
    """Return path relative to channel_root using forward slashes."""
    return path.relative_to(channel_root).as_posix()


def directory_total_size(dir_path: Path, channel_root: Path) -> int:
    """Return recursive directory size excluding generated index files and exclusions."""
    total = 0

    for root, _, files in os.walk(dir_path):
        root_path = Path(root)
        for filename in files:
            file_path = root_path / filename
            if is_excluded_file(file_path, channel_root):
                continue

            try:
                total += file_path.stat().st_size
            except OSError:
                print(f"[WARN] Could not read size: {file_path}")

    return total


def sorted_immediate_entries(folder: Path, channel_root: Path):
    """Return sorted immediate files and dirs for a folder."""
    files = []
    dirs = []

    try:
        for entry in folder.iterdir():
            if entry.is_file():
                if is_excluded_file(entry, channel_root):
                    continue
                files.append(entry)
            elif entry.is_dir():
                dirs.append(entry)
    except OSError as e:
        print(f"[WARN] Could not read folder: {folder} ({e})")

    files.sort(key=lambda p: p.name.lower())
    dirs.sort(key=lambda p: p.name.lower())

    # For channel root, force UniExtract.exe first if it exists.
    if folder == channel_root:
        ordered = []
        rest = []

        for f in files:
            lname = f.name.lower()
            if lname == "uniextract.exe":
                ordered.insert(0, f)
            else:
                rest.append(f)

        files = ordered + [f for f in rest if f not in ordered]

    return files, dirs


def build_index_lines(folder: Path, channel_root: Path) -> list[str]:
    """
    Build manifest lines for one folder.

    Files and directories are emitted as paths relative to the channel root.
    """
    lines: list[str] = []

    files, dirs = sorted_immediate_entries(folder, channel_root)

    # Files first
    for file_path in files:
        try:
            size = file_path.stat().st_size
            md5 = md5_file(file_path)
            rel = rel_posix(file_path, channel_root)
            lines.append(f"{rel},{size},{md5}")
        except OSError as e:
            print(f"[WARN] Skipping unreadable file: {file_path} ({e})")

    # Then immediate directories
    for dir_path in dirs:
        try:
            rel = rel_posix(dir_path, channel_root) + "/"
            size = directory_total_size(dir_path, channel_root)
            lines.append(f"{rel},{size}")
        except OSError as e:
            print(f"[WARN] Skipping unreadable directory: {dir_path} ({e})")

    return lines


def all_directories_topdown(channel_root: Path) -> list[Path]:
    """Return all directories including channel root, sorted top-down."""
    dirs = []

    for root, subdirs, _ in os.walk(channel_root):
        subdirs.sort(key=lambda s: s.lower())
        dirs.append(Path(root))

    dirs.sort(key=lambda p: (len(p.relative_to(channel_root).parts), rel_posix(p, channel_root).lower()))
    return dirs


def write_index_file(folder: Path, lines: list[str]) -> None:
    """Write the index file for one folder."""
    index_path = folder / INDEX_FILENAME
    with index_path.open("w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line + "\n")


def resolve_base_dir() -> Path | None:
    """
    Resolve the chosen folder.

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


def determine_channel_roots(base_dir: Path) -> list[Path]:
    """
    Determine which folders should get their own top-level index.

    Rules:
    - If base_dir itself contains UniExtract.exe, treat base_dir as one channel.
    - Otherwise, only process immediate subfolders that contain UniExtract.exe.
    """
    if (base_dir / "UniExtract.exe").exists():
        return [base_dir]

    channel_roots = []
    skipped = []

    for entry in sorted(base_dir.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_dir():
            continue

        if (entry / "UniExtract.exe").exists():
            channel_roots.append(entry)
        else:
            skipped.append(entry.name)

    if skipped:
        print("[INFO] Ignoring subfolders without UniExtract.exe:")
        for name in skipped:
            print(f"       {name}")
        print()

    return channel_roots


def main() -> None:
    print("UniExtract2 index generator")
    print()

    base_dir = resolve_base_dir()
    if base_dir is None:
        input("\nPress Enter to exit...")
        return

    print(f"[INFO] Chosen folder: {base_dir}")
    print()

    channel_roots = determine_channel_roots(base_dir)
    if not channel_roots:
        print("[ERROR] No valid channel roots found.")
        print("A valid channel root must contain UniExtract.exe.")
        input("\nPress Enter to exit...")
        return

    created = 0

    if base_dir not in channel_roots:
        print(f"[INFO] Skipping parent root folder (no index created): {base_dir}")
        print()

    for channel_root in channel_roots:
        print(f"[INFO] Channel root: {channel_root}")
        dirs = all_directories_topdown(channel_root)

        for folder in dirs:
            lines = build_index_lines(folder, channel_root)
            try:
                write_index_file(folder, lines)
                created += 1
                rel_folder = "." if folder == channel_root else rel_posix(folder, channel_root)
                print(f"[OK] Wrote index: {folder / INDEX_FILENAME}  ({len(lines)} entries, folder '{rel_folder}')")
            except OSError as e:
                print(f"[ERROR] Failed to write index in {folder}: {e}")

        print()

    print(f"[DONE] Created/updated {created} index file(s).")
    print()
    print("Expected result:")
    print("- no index in the parent updates folder")
    print("- data/index and nightly/index contain paths relative to data/nightly")
    print("- data/bin/index and nightly/bin/index contain paths starting with bin/")
    print("- news is excluded from channel-root indexes")
    print("- this script file is excluded")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
