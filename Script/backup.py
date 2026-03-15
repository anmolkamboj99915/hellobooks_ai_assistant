import os
import time
import glob
import json
import hashlib
import argparse
from collections import defaultdict
from typing import Dict, Set, List

# === Settings ===
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

STRUCTURE_FILE = os.path.join(LOG_DIR, "project_structure.txt")
HASH_FILE = os.path.join(LOG_DIR, "project_hashes.json")
MEMORY_FILE = os.path.join(LOG_DIR, "structure_memory.json")
timestamp = time.strftime("%Y%m%d_%H%M%S")
TIMESTAMPED_FILE = os.path.join(LOG_DIR, f"project_structure_{timestamp}.txt")

# === Exclusions & Force Includes ===
EXCLUDED_DIRS: Set[str] = {
    ".git", ".vscode",
    "__pycache__", ".pytest_cache", "logs", "node_modules", ".venv", "Scripts", ".anm", ".idea", "migrations"
}

IGNORED_SUFFIXES: Set[str] = {
    ".db", ".wav"
}

FORCE_INCLUDE_FILES: Set[str] = {"main.py", "config.py"}
FORCE_INCLUDE_DIRS: Set[str] = {"modules"}

INCLUDE_CONTENT_SUFFIXES: Set[str] = {
    ".py", ".html", ".css", ".js", ".jsx", ".config.js", ".ts", ".tsx", ".txt", ".md"
}

# === Tracking ===
included_files = 0
included_lines = 0
skipped_files = 0
file_hashes: Dict[str, str] = {}

# === Utilities ===
def normalize_path(path: str) -> str:
    return (
        os.path.normpath(path)
        if os.path.isabs(path)
        else os.path.normpath(os.path.join(PROJECT_ROOT, path))
    )

def should_exclude(path: str) -> bool:
    parts = os.path.normpath(path).split(os.sep)

    # Do not exclude if it's a .py file
    if os.path.splitext(path)[1].lower() == ".py":
        return False
    return any(part in EXCLUDED_DIRS for part in parts)

def hash_file(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return "ERROR"

def is_force_included(path: str) -> bool:
    rel = os.path.relpath(path, PROJECT_ROOT)
    filename = os.path.basename(path)
    parts = rel.split(os.sep)
    return filename in FORCE_INCLUDE_FILES or any(p in FORCE_INCLUDE_DIRS for p in parts)

# === Core logic ===
def dump_structure_from_list(file_list: List[str], verbose: bool = False) -> str:
    global included_files, included_lines, skipped_files, file_hashes
    included_files = included_lines = skipped_files = 0
    file_hashes.clear()

    result = ""
    normalized_paths = sorted(
        set(filter(os.path.isfile, (normalize_path(fp) for fp in file_list)))
    )

    print("\n📂 Building structure... Logging file decisions:")
    dir_files = defaultdict(list)
    for path in normalized_paths:
        dir_files[os.path.dirname(path)].append(path)

    for directory in sorted(dir_files.keys(), key=lambda d: d.lower()):
        rel_dir = os.path.relpath(directory, PROJECT_ROOT)
        indent_level = 0 if rel_dir == "." else len(rel_dir.split(os.sep))
        indent = "    " * indent_level

        if should_exclude(rel_dir):
            result += f"{indent}📁 {os.path.basename(directory)}/  ← skipped (excluded folder)\n"
            print(f"[-] Skipped folder: {rel_dir}/  ← excluded folder")
            continue

        result += (
            f"{indent}📁 {os.path.basename(directory)}/\n"
            if rel_dir != "."
            else f"📁 {os.path.basename(directory)} (root)\n"
        )

        for file_path in sorted(dir_files[directory], key=lambda f: os.path.basename(f).lower()):
            file_name = os.path.basename(file_path)
            suffix = os.path.splitext(file_name)[1].lower()
            rel_path = os.path.relpath(file_path, PROJECT_ROOT)

            # Skip unless force included
            if suffix in IGNORED_SUFFIXES and not is_force_included(file_path):
                skipped_files += 1
                print(f"[-] Skipped: {rel_path}  ← ignored suffix {suffix}")
                continue

            sub_indent = indent + "    "
            result += f"{sub_indent}📄 {file_name}\n"

            file_hashes[rel_path] = hash_file(file_path)

            # Content inclusion
            if suffix in INCLUDE_CONTENT_SUFFIXES or is_force_included(file_path):
                try:
                    with open(file_path, "rb") as f:
                        raw = f.read()
                    try:
                        content = raw.decode("utf-8")
                    except UnicodeDecodeError:
                        try:
                            content = raw.decode("latin-1")
                        except Exception:
                            content = raw.decode("utf-8", errors="replace")
                            
                    if "\x00" in content:
                        raise ValueError("Binary detected")

                    included_files += 1
                    lines = content.splitlines()
                    included_lines += len(lines)

                    if verbose:
                        print(f"[+] Included: {rel_path} ✔ content dumped")

                    result += f"{sub_indent}    --- BEGIN CONTENT ---\n"
                    for line in lines:
                        result += f"{sub_indent}    {line}\n"
                    result += f"{sub_indent}    --- END CONTENT ---\n"

                except Exception as e:
                    skipped_files += 1
                    print(f"[~] Skipped content: {rel_path} ← error {e}")
                    result += f"{sub_indent}    ⚠️ Skipped: {e}\n"
            else:
                skipped_files += 1
                print(f"[~] Skipped content only: {rel_path} ← non-text file")

    return result

# === Memory Comparison ===
def compare_with_last_memory() -> Dict[str, List[str]]:
    if not os.path.exists(MEMORY_FILE):
        return {"Added": [], "Removed": [], "Changed": []}

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        last = json.load(f).get("hashes", {})

    added = [f for f in file_hashes if f not in last]
    removed = [f for f in last if f not in file_hashes]
    changed = [f for f in file_hashes if f in last and file_hashes[f] != last[f]]

    return {"Added": added, "Removed": removed, "Changed": changed}

# === Output Handling ===
def save_json_hashes() -> None:
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(file_hashes, f, indent=2)

def cleanup_old_snapshots(max_files: int = 5) -> None:
    all_snapshots = sorted(
        glob.glob(os.path.join(LOG_DIR, "project_structure_*.txt")), reverse=True
    )
    for old_file in all_snapshots[max_files:]:
        try:
            os.remove(old_file)
        except Exception as e:
            print(f"⚠️ Couldn't remove {old_file}: {e}")


def write_full_structure(args: argparse.Namespace) -> None:
    print(f"📦 Scanning: {PROJECT_ROOT}")
    files_to_dump = []

    # --- Scan directories with FORCE_INCLUDE override ---
    for dirpath, _, filenames in os.walk(PROJECT_ROOT):
        rel_dir = os.path.relpath(dirpath, PROJECT_ROOT)
        parts = rel_dir.split(os.sep)

        # Skip only if exluded AND not forced
        if should_exclude(dirpath) and not any(p in FORCE_INCLUDE_DIRS for p in parts):
            continue

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            files_to_dump.append(file_path)

    # --- Remove duplicates + sort for stable output --- 
    files_to_dump = sorted(set(files_to_dump))

    # --- Build structure from actual included file List ---
    structure = dump_structure_from_list(files_to_dump, verbose=args.verbose)

    # --- Header wih timestamp ----
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    header = f"📦 Project Snapshot: {time.ctime()}\nRoot: {PROJECT_ROOT}\n\n"

    # --- Write latest + timestamped snapshot ---
    with open(STRUCTURE_FILE, "w", encoding="utf-8") as f:
        f.write(header + structure)
    with open(TIMESTAMPED_FILE.replace("{timestamp}", timestamp), "w", encoding="utf-8") as f:
        f.write(header + structure)
    
    # --- Save JSON hashes for change detection ---
    save_json_hashes()

    # --- Memory handling ---
    if args.memory:
        diffs = compare_with_last_memory()
        with open(MEMORY_FILE, "w", encoding="utf-8") as mem:
            json.dump({"hashes": file_hashes, "timestamp": timestamp}, mem, indent=2)
        
        print("🧠 Memory updated. Changes since last run:")
        for k, v in diffs.items():
            if v:
                print(f" {k}: {len(v)} files")
                for f in v[:10]:
                    print(f" - {f}")
    
    # --- Summary ---
    if args.summary:
        print(f"\n📊 Total scanned: {len(files_to_dump)}")
        print(f"📄 Included: {included_files}")
        print(f"📑 Lines dumped: {included_lines}")
        print(f"🧹 Skipped: {skipped_files}")

    # --- Cleanup old snapshots ---
    cleanup_old_snapshots()


# === CLI ===
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="📦 Project Snapshot Dumper")
    parser.add_argument("--verbose", action="store_true", help="Show detailed logs")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    parser.add_argument("--memory", action="store_true", help="Track changes with memory")
    args = parser.parse_args()
    if not any(vars(args).values()):
        args.verbose = args.summary = args.memory = True
    return args

if __name__ == "__main__":
    args = parse_args()
    write_full_structure(args)
