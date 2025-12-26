# Windows Compatibility Guide

## Why Windows May Have Issues

The scripts are designed to work cross-platform, but Windows has some differences:

### 1. Path Separators
**Issue**: Windows uses backslashes (`\`) while Unix uses forward slashes (`/`)

**Solution**: All scripts use `Path` from `pathlib` which handles this automatically. ✅ Already compatible!

### 2. Environment Variables
**Issue**: Windows uses different syntax for environment variables

**Unix/Mac:**
```bash
export HF_TOKEN='your_token'
```

**Windows (Command Prompt):**
```cmd
set HF_TOKEN=your_token
```

**Windows (PowerShell):**
```powershell
$env:HF_TOKEN='your_token'
```

**Solution**: Use the provided setup scripts:
- `setup_windows.bat` for Command Prompt
- `setup_windows.ps1` for PowerShell

### 3. Shell Differences
**Issue**: Windows doesn't have bash/zsh by default

**Solutions**:
- Use PowerShell or Command Prompt (scripts work in both)
- Or install Git Bash / WSL (Windows Subsystem for Linux) for bash compatibility

### 4. Python Path Issues
**Issue**: Windows may have different Python executable paths

**Solution**: 
- Use `python` instead of `python3` on Windows
- Or create an alias: `doskey python3=python`

### 5. Virtual Environment Activation
**Issue**: Different activation scripts on Windows

**Unix/Mac:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Note**: PowerShell may require execution policy changes:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 6. File Permissions
**Issue**: Windows has stricter file permissions

**Solution**: Run as Administrator if needed, or adjust file permissions

## Quick Start for Windows

### Option 1: Command Prompt
```cmd
setup_windows.bat
python run_emotion_generations.py --voice "path\to\voice.wav" --text "Your text"
```

### Option 2: PowerShell
```powershell
.\setup_windows.ps1
python run_emotion_generations.py --voice "path\to\voice.wav" --text "Your text"
```

### Option 3: Manual Setup
```cmd
REM Replace YOUR_HF_TOKEN_HERE with your actual Hugging Face token
set HF_TOKEN=YOUR_HF_TOKEN_HERE
set HUGGINGFACE_HUB_TOKEN=YOUR_HF_TOKEN_HERE
venv\Scripts\activate.bat
python run_emotion_generations.py --voice "path\to\voice.wav" --text "Your text"
```

## Testing on Windows

All Python scripts should work identically on Windows because:
- ✅ Using `pathlib.Path` for cross-platform paths
- ✅ Using `os.getenv()` for environment variables (works on all platforms)
- ✅ No shell-specific commands in Python code
- ✅ Standard Python libraries only

The only differences are:
- Environment variable setup (use provided scripts)
- Virtual environment activation (different script names)
- Python command (`python` vs `python3`)

## Troubleshooting

### "Module not found" errors
```cmd
pip install -r requirements.txt
```

### "Permission denied" errors
- Run Command Prompt/PowerShell as Administrator
- Or adjust file/folder permissions

### "Execution policy" errors (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Environment variables not persisting
- Use the setup scripts each time you open a new terminal
- Or set them permanently in System Properties → Environment Variables

