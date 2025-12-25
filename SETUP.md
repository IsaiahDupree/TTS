# Setup Instructions

## Python Version Requirement

⚠️ **Important:** The TTS library requires Python 3.9-3.11. Your current Python version (3.14) is too new.

## Installing Python 3.11

### Option 1: Using pyenv (Recommended)

```bash
# Install pyenv if you don't have it
brew install pyenv

# Install Python 3.11
pyenv install 3.11.9

# Set it for this project
cd /Users/isaiahdupree/Documents/Software/TTS
pyenv local 3.11.9

# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using Homebrew

```bash
# Install Python 3.11
brew install python@3.11

# Create virtual environment
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start After Python Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Update the script with your audio file:**
   - Edit `example_voice_cloning.py`
   - Change `SPEAKER_AUDIO = "path/to/your/voice_sample.wav"` to your actual audio file path

4. **Run the script:**
   ```bash
   python3 example_voice_cloning.py
   ```

## Audio File Requirements

- **Format:** WAV, MP3, or FLAC
- **Duration:** At least 3 seconds
- **Quality:** Clear audio with minimal background noise
- **Sample Rate:** 16-22kHz (most tools auto-convert)

## Troubleshooting

If you encounter issues:

1. **Check Python version:**
   ```bash
   python3 --version
   ```
   Should be 3.9, 3.10, or 3.11

2. **Verify virtual environment:**
   ```bash
   which python3
   ```
   Should point to your venv

3. **Reinstall dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Check disk space:** Models can be 1-5GB+, ensure you have enough space


