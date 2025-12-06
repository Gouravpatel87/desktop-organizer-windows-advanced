# I hate a messy Desktop — so I built an automated Desktop Organizer (Windows)

**By**: <Your Name>
**Project**: Desktop Organizer — Windows (Advanced Mode)

## Problem
My Windows Desktop accumulates screenshots, downloaded installers, and random docs. Every week I spend time sorting them into folders. It's boring and error-prone.

## What I built
A Python script that organizes the Desktop automatically:
- Categorizes files (Images, Documents, Code, Video, Audio, Archives, Installers, Others)
- Creates extension-specific subfolders for fine-grained organization (e.g., `Images/JPG`)
- Safe defaults: dry-run, skip `.lnk` shortcuts, handle name collisions

## Technical details
- Language: Python 3.9+
- Optional dependency: `watchdog` (for watch mode)

### Key code snippets
**Organize files and resolve name collisions**

```python
# snippet: resolve_collision
if dest.exists():
    for i in range(1, 1000):
        candidate = parent / f"{base} ({i}){suffix}"
        if not candidate.exists():
            return candidate
```

**Dry-run mode**

```python
if dry_run:
    logging.info("[DRY RUN] Would move: %s -> %s", item, safe_dest)
else:
    shutil.move(str(item), str(safe_dest))
```

## How Kiro accelerated development
- **Boilerplate generation**: I used Kiro to draft the initial script skeleton (CLI parsing, logging, folder utilities).
- **Iterative refinement**: I asked Kiro to convert the mapping into a configurable JSON file and to add collision handling.
- **Testing & debugging**: Kiro suggested safe patterns (dry-run, skip `.lnk`) that prevented accidental data loss.

> **Kiro evidence**: include screenshots or a short recording here showing the Kiro prompts and generated code. Save them under `.kiro/screenshots/` and reference them in this post.

## Demo
Include a GIF or a short video showing before/after of the Desktop and the script running.

## How to run
1. Clone repo
2. `pip install -r requirements.txt` (optional)
3. `python organizer.py --dry-run`
4. `python organizer.py` to run for real

## Future improvements
- Integrate with the Windows context menu for one-click runs
- Add smarter heuristics (OCR for images to detect receipts)
- Add a GUI with Electron or PySimpleGUI

## Link to GitHub
Add your repository URL here.
