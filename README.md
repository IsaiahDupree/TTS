# Voice Cloning Project

This repository contains tools and examples for voice cloning using your own audio data, with comprehensive audio quality analysis and multi-stage refinement for optimal results.

## 🖥️ Mac Mini Setup (Apple Silicon)

**⚠️ Important for Mac Mini Users:** This project has been specifically tested and optimized for Mac Mini (ARM64) running macOS 26.0.1. See **[MAC_MINI_SETUP.md](MAC_MINI_SETUP.md)** for detailed explanation of why this setup works.

### Quick Mac Mini Setup

```bash
# 1. Install prerequisites
brew install python@3.11 ffmpeg

# 2. Create virtual environment with Python 3.11 (required!)
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verify installation
python3 check_installation.py
```

**Why Python 3.11?** macOS 26.0.1 ships with Python 3.14, which is too new for TTS libraries. Python 3.11 is the latest compatible version. See [MAC_MINI_SETUP.md](MAC_MINI_SETUP.md) for complete explanation.

### Key Mac Mini Considerations

- ✅ **Python 3.11 Required** (not system Python 3.14)
- ✅ **Virtual Environment Essential** (protects system Python)
- ✅ **PyTorch Patch Included** (handles `weights_only` security feature)
- ✅ **ARM64 Native** (all packages compiled for Apple Silicon)
- ✅ **Version Pinning** (ensures compatibility across dependencies)

## Quick Start

### Option 1: Coqui XTTS (Recommended for Beginners)

**Prerequisites:** Follow Mac Mini setup above if on Apple Silicon.

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run the example:**
   ```bash
   python3 example_voice_cloning.py
   ```

3. **Update the script** with your audio file path and text to synthesize.

**Note:** The script automatically applies PyTorch compatibility patches. See `patch_torch_load.py` for details.

### Option 2: Using Hugging Face Models

1. **Install dependencies:**
   ```bash
   pip install transformers torch torchaudio
   ```

2. **Use MetaVoice-1B or Chatterbox** (see guide for details)

## Files

### Core Scripts
- `example_voice_cloning.py` - Working example using Coqui XTTS
- `refine_and_clone.py` - Complete pipeline: quality analysis → refinement → cloning
- `audio_quality_analyzer.py` - Multi-layer audio quality assessment
- `audio_refinement_processor.py` - 5-stage audio refinement pipeline
- `download_channel_audio.py` - Download audio from YouTube channels
- `run_all_tests.py` - Complete test suite

### Setup & Configuration
- `requirements.txt` - Python dependencies (with version constraints)
- `patch_torch_load.py` - PyTorch compatibility patch for Mac Mini
- `check_installation.py` - Verify all components are installed
- `MAC_MINI_SETUP.md` - **Detailed Mac Mini setup guide and explanations**

### Documentation
- `voice_cloning_guide.md` - Comprehensive guide to all voice cloning tools
- `SETUP.md` - General setup instructions
- `REFINEMENT_REPORT.md` - Audio refinement results and methodology

## Audio File Requirements

- **Format:** WAV, MP3, or FLAC
- **Duration:** 3 seconds minimum (for XTTS)
- **Quality:** Clear audio with minimal background noise
- **Sample Rate:** Most tools auto-convert, but 16-22kHz is ideal

## Recommended Workflow

### Complete Pipeline (Recommended)

1. **Download audio from YouTube:**
   ```bash
   python3 download_channel_audio.py --channel-url "https://www.youtube.com/@your_channel"
   ```

2. **Analyze and refine audio quality:**
   ```bash
   python3 refine_and_clone.py
   ```
   This runs the complete pipeline:
   - Quality analysis (6 layers of assessment)
   - High-quality filtering
   - Multi-stage refinement (normalization, denoising, resampling)
   - Voice cloning with best quality audio

3. **Use refined audio for cloning:**
   - Refined audio files are in `refined_audio/`
   - Cloned voice samples are in `test_outputs/refined_voice_cloning/`

### Basic Workflow

1. **Prepare your audio files:**
   - Record or collect clear audio samples
   - Remove background noise if possible
   - Ensure good audio quality

2. **Choose a tool:**
   - Start with Coqui XTTS for easiest setup
   - Use `refine_and_clone.py` for best quality results
   - Try Hugging Face models if you need API integration

3. **Test with a small sample:**
   - Use 3-10 seconds of audio first
   - Verify the output quality
   - Adjust settings as needed

4. **Scale up:**
   - Use more audio data for better results
   - Run quality analysis to find best samples
   - Use refined audio for optimal cloning

## Features

### 🎯 Audio Quality Analysis
- **6-layer quality assessment:** Signal quality, noise, speech characteristics, clarity, duration, completeness
- **Quality scoring:** 0-100 composite score for each audio file
- **Intelligent filtering:** Automatically identifies highest quality samples

### 🎚️ Multi-Stage Audio Refinement
- **Stage 1:** Audio normalization (-3dB peak)
- **Stage 2:** Silence removal (leading/trailing)
- **Stage 3:** Noise reduction (spectral gating)
- **Stage 4:** Optimal resampling (22050 Hz for TTS)
- **Stage 5:** Best segment extraction (15s optimal segments)

### 🎤 Voice Cloning
- **Coqui XTTS v2:** State-of-the-art voice cloning
- **Refined audio support:** Uses highest quality processed audio
- **Batch processing:** Process multiple files automatically
- **Quality assessment:** Compare cloned vs original audio

### 📊 Comprehensive Testing
- Generation tests
- Voice cloning tests
- Quality assessment tests
- Complete test suite with logging

## Resources

- [Coqui TTS Documentation](https://github.com/coqui-ai/TTS/wiki)
- [Hugging Face TTS Models](https://huggingface.co/models?pipeline_tag=text-to-speech)
- See `voice_cloning_guide.md` for detailed information on all tools
- See `MAC_MINI_SETUP.md` for Mac Mini setup explanations
- See `REFINEMENT_REPORT.md` for audio refinement methodology

## System Requirements

### Mac Mini (Tested)
- **macOS:** 26.0.1 (or compatible)
- **Architecture:** ARM64 (Apple Silicon)
- **Python:** 3.11 (via Homebrew)
- **RAM:** 2-4 GB minimum (8+ GB recommended)
- **Disk:** 10+ GB for models and audio

### Other Systems
- **Python:** 3.9-3.11
- **OS:** Linux, macOS, or Windows
- **RAM:** 2-4 GB minimum
- **Disk:** 10+ GB for models and audio

## License

See LICENSE file for details.

## Troubleshooting

### Mac Mini Specific Issues

**"externally-managed-environment" error:**
- **Solution:** Always use virtual environment (see Mac Mini setup above)
- Never install packages to system Python on macOS

**"ModuleNotFoundError: No module named 'TTS'":**
- **Solution:** Ensure virtual environment is activated: `source venv/bin/activate`
- Verify Python version: `python3 --version` (should be 3.11.x)
- Reinstall: `pip install -r requirements.txt`

**"WeightsUnpickler error: Unsupported global":**
- **Solution:** This is handled automatically by `patch_torch_load.py`
- Ensure you import the patch before using TTS:
  ```python
  import patch_torch_load
  patch_torch_load.patch_torch_load()
  from TTS.api import TTS
  ```

**"ImportError: cannot import name 'BeamSearchScorer'":**
- **Solution:** transformers version too new. Reinstall with pinned version:
  ```bash
  pip install "transformers>=4.30.0,<4.40.0"
  ```

**"numba requires numpy<2.4":**
- **Solution:** numpy version too new. Reinstall with pinned version:
  ```bash
  pip install "numpy<2.3.0,>=1.24.0"
  ```

### General Issues

**Installation issues:**
- **Mac Mini:** Use Python 3.11 (not 3.14). See [MAC_MINI_SETUP.md](MAC_MINI_SETUP.md)
- **Other systems:** Ensure Python 3.9-3.11 is installed
- Always use virtual environment: `python3 -m venv venv && source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Audio issues:**
- Convert audio to WAV format if needed
- Ensure audio is clear and not corrupted
- Check file paths are correct
- For YouTube downloads, ensure `ffmpeg` is installed: `brew install ffmpeg`

**Model loading issues:**
- Models download automatically on first use
- Ensure stable internet connection
- Check available disk space (models can be 1-5GB+)
- First load may take 15-20 seconds, subsequent loads are faster

**Performance issues:**
- Voice cloning takes ~4-5 seconds per phrase (normal)
- Audio processing takes ~0.3-0.5 seconds per file
- Ensure sufficient RAM (2-4 GB recommended)

### Getting Help

1. **Check [MAC_MINI_SETUP.md](MAC_MINI_SETUP.md)** for Mac Mini specific issues
2. **Run verification:** `python3 check_installation.py`
3. **Check logs:** All scripts include extensive logging
4. **Review test results:** See `FULL_TEST_RESULTS.md` for expected outputs

