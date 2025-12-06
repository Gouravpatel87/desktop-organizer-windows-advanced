#!/usr/bin/env python3
"""
Windows Desktop Organizer — Advanced Mode

Features:
- Scans the Windows Desktop (or specified folder)
- Organizes files into categories and fine-grained subfolders
- Supports custom rules via JSON config
- Dry-run mode and logging
- Safe: skips .lnk shortcuts and system-protected items
- Handles name collisions safely

Usage:
    python organizer.py --dry-run
    python organizer.py --desktop-path "C:\\Users\\Alice\\Desktop" --config config.example.json

Optional dependencies (watch mode): watchdog
"""

from __future__ import annotations
import argparse
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# -----------------------------
# Defaults and helper config
# -----------------------------
DEFAULT_MAP = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".md"],
    "Code": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".html", ".css", ".json"],
    "Video": [".mp4", ".mkv", ".mov", ".avi", ".wmv"],
    "Audio": [".mp3", ".wav", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi"],
    "Shortcuts": [".lnk"],
}

SYSTEM_EXCLUDE = {"desktop.ini", "thumbs.db"}
LOG_FILENAME = "organizer.log"

# -----------------------------
# Utilities
# -----------------------------
def setup_logging(log_path: Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

def load_config(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        return DEFAULT_MAP
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Normalize keys to lists of lowercased extensions
        norm = {k: [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in v] for k, v in data.items()}
        return norm
    except Exception as e:
        logging.warning("Failed to load config %s: %s — using defaults", path, e)
        return DEFAULT_MAP

def ensure_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def resolve_collision(dest: Path) -> Path:
    """If dest exists, append a counter or timestamp to avoid overwriting."""
    if not dest.exists():
        return dest
    base = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    for i in range(1, 1000):
        candidate = parent / f"{base} ({i}){suffix}"
        if not candidate.exists():
            return candidate
    # fallback to timestamp
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return parent / f"{base} {ts}{suffix}"

# -----------------------------
# Core logic
# -----------------------------
def categorize_file(file_path: Path, rules: Dict[str, List[str]]) -> Tuple[str, str]:
    """Return (category, subfolder) where subfolder may be the extension-based subfolder in advanced mode."""
    ext = file_path.suffix.lower()
    if file_path.name.lower() in SYSTEM_EXCLUDE:
        return ("_skip", "")
    if ext == "":
        return ("Others", "")
    for category, exts in rules.items():
        if ext in exts:
            # For advanced mode, subfolder by extension for many categories
            subfolder = ext.lstrip('.') if category in {"Images", "Documents", "Code", "Video", "Audio", "Archives", "Installers"} else ""
            return (category, subfolder)
    return ("Others", "")

def is_system_shortcut(path: Path) -> bool:
    # Simple heuristic: skip .lnk items (shortcuts) to avoid messing with pinned items
    return path.suffix.lower() == ".lnk"

def organize_folder(folder: Path, rules: Dict[str, List[str]], dry_run: bool = True, verbose: bool = True) -> List[Tuple[Path, Path]]:
    moved = []
    for item in folder.iterdir():
        try:
            if item.is_dir():
                # skip folders we created (heuristic: skip folders that match our categories)
                if item.name in rules.keys() or item.name == "Others":
                    if verbose:
                        logging.debug("Skipping folder: %s", item)
                    continue
                # optionally could recurse into subfolders, but default: skip
                if verbose:
                    logging.info("Skipping existing folder: %s", item.name)
                continue

            if is_system_shortcut(item):
                logging.info("Skipping shortcut: %s", item.name)
                continue

            category, sub = categorize_file(item, rules)
            if category == "_skip":
                logging.info("Skipping system file: %s", item.name)
                continue

            dest_folder = folder / category
            if sub:
                dest_folder = dest_folder / sub.upper()

            ensure_folder(dest_folder)

            dest_path = dest_folder / item.name
            safe_dest = resolve_collision(dest_path)

            if dry_run:
                logging.info("[DRY RUN] Would move: %s -> %s", item, safe_dest)
                moved.append((item, safe_dest))
            else:
                shutil.move(str(item), str(safe_dest))
                logging.info("Moved: %s -> %s", item, safe_dest)
                moved.append((item, safe_dest))
        except Exception as e:
            logging.exception("Error handling %s: %s", item, e)
    return moved

# -----------------------------
# CLI
# -----------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Organize Windows Desktop files (Advanced Mode)")
    p.add_argument("--desktop-path", type=str, default=None, help="Path to the desktop folder (defaults to current user Desktop)")
    p.add_argument("--config", type=str, default="config.example.json", help="Custom JSON rules file")
    p.add_argument("--dry-run", action="store_true", help="Show actions without moving files")
    p.add_argument("--watch", action="store_true", help="Enable watch mode (requires watchdog)")
    p.add_argument("--verbose", action="store_true", help="Verbose logging")
    return p.parse_args()

def main():
    args = parse_args()
    # Resolve desktop path
    if args.desktop_path:
        desktop = Path(args.desktop_path).expanduser().resolve()
    else:
        desktop = Path.home() / "Desktop"

    log_path = desktop / LOG_FILENAME
    setup_logging(log_path)

    logging.info("Starting Desktop Organizer (advanced mode)")
    logging.info("Target desktop: %s", desktop)

    config_path = Path(args.config)
    rules = load_config(config_path)

    if not desktop.exists():
        logging.error("Desktop path does not exist: %s", desktop)
        sys.exit(2)

    moved = organize_folder(desktop, rules, dry_run=args.dry_run, verbose=args.verbose)

    logging.info("Completed. Items processed: %d", len(moved))

    if args.watch:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class DesktopChangeHandler(FileSystemEventHandler):
                def on_created(self, event):
                    logging.info("Detected change, running organizer")
                    organize_folder(desktop, rules, dry_run=args.dry_run, verbose=args.verbose)

            observer = Observer()
            observer.schedule(DesktopChangeHandler(), str(desktop), recursive=False)
            observer.start()
            logging.info("Watch mode active. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping watch mode")
            observer.stop()
            observer.join()
        except Exception as e:
            logging.warning("Watch mode unavailable or failed: %s", e)

if __name__ == "__main__":
    main()
