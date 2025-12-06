# Desktop Organizer — Windows (Advanced Mode)

Automatically organize your Windows Desktop into logical folders and extension-based subfolders.

## What it does
- Moves files into category folders (Images, Documents, Code, Video, Audio, Archives, Installers, Others)
- Further splits major categories into extension-named subfolders (e.g., Images/JPG)
- Skips shortcuts and system files
- Handles name collisions safely
- Dry-run mode for preview

## Quick start
1. Clone the repo
```
git clone <your-repo-url>
cd desktop-organizer-windows-advanced
```
2. (Optional) Create a virtualenv and install watchdog if you want watch mode:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
3. Try a dry run:
```
python organizer.py --dry-run
```
4. Execute for real:
```
python organizer.py
```
5. To target a different desktop path:
```
python organizer.py --desktop-path "D:\\Users\\Alice\\Desktop"
```

## Customization
Edit `config.example.json` and pass `--config myconfig.json` to change category rules.

## .kiro
The `.kiro/` folder contains the Kiro prompts and session notes used while developing this project. **Do not** add `.kiro` to `.gitignore` — include it in the repository.

## License
MIT
