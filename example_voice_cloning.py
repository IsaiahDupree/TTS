"""
Example script for voice cloning using Coqui XTTS
This is the easiest option to get started with voice cloning.
"""

import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Configure detailed logging FIRST (before any imports that might fail)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Try to import audio metadata libraries
try:
    import librosa
    LIBROSA_AVAILABLE = True
    logger.info("✅ librosa imported successfully")
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("⚠️  librosa not available - audio metadata will be limited")

# Try to import TTS
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
    logger.info("✅ TTS library imported successfully")
except ImportError as e:
    TTS_AVAILABLE = False
    logger.error(f"❌ TTS library not available: {e}")
    logger.error("Please install TTS: pip install TTS")
    logger.error("Note: TTS requires Python 3.9-3.11 (current: Python 3.14)")
    # Create a dummy TTS class for demonstration
    class TTS:
        def __init__(self, *args, **kwargs):
            raise ImportError("TTS library not installed")
        @staticmethod
        def list_models():
            return []


def log_system_info():
    """Log system information for debugging."""
    logger.info("=" * 80)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 80)
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Working Directory: {os.getcwd()}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for GPU
    try:
        import torch
        logger.info(f"PyTorch Version: {torch.__version__}")
        logger.info(f"CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Device Count: {torch.cuda.device_count()}")
    except ImportError:
        logger.warning("PyTorch not available - cannot check GPU status")
    
    logger.info("=" * 80)


def log_audio_file_info(audio_path):
    """Log detailed information about the audio file."""
    logger.info("=" * 80)
    logger.info("AUDIO FILE ANALYSIS")
    logger.info("=" * 80)
    
    if not os.path.exists(audio_path):
        logger.error(f"Audio file does not exist: {audio_path}")
        return False
    
    # Basic file info
    file_path = Path(audio_path)
    file_size = os.path.getsize(audio_path)
    file_size_mb = file_size / (1024 * 1024)
    
    logger.info(f"File Path: {audio_path}")
    logger.info(f"File Exists: {os.path.exists(audio_path)}")
    logger.info(f"File Size: {file_size:,} bytes ({file_size_mb:.2f} MB)")
    logger.info(f"File Extension: {file_path.suffix}")
    logger.info(f"File Name: {file_path.name}")
    logger.info(f"Absolute Path: {os.path.abspath(audio_path)}")
    
    # Audio metadata if librosa is available
    if LIBROSA_AVAILABLE:
        try:
            logger.info("Loading audio metadata with librosa...")
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            logger.info(f"Sample Rate: {sr} Hz")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Number of Samples: {len(y):,}")
            logger.info(f"Audio Shape: {y.shape}")
            logger.info(f"Audio Data Type: {y.dtype}")
            
            # Check if duration is sufficient
            if duration < 3:
                logger.warning(f"⚠️  Audio duration ({duration:.2f}s) is less than recommended 3 seconds")
            else:
                logger.info(f"✅ Audio duration ({duration:.2f}s) meets minimum requirement")
                
        except Exception as e:
            logger.error(f"Error loading audio metadata: {e}")
            logger.warning("Continuing without detailed audio metadata...")
    else:
        logger.warning("librosa not available - install with: pip install librosa")
    
    logger.info("=" * 80)
    return True


def clone_voice_with_xtts(text, speaker_audio_path, output_path, language="en"):
    """
    Clone a voice using Coqui XTTS model with extensive logging.
    
    Args:
        text: The text you want to synthesize
        speaker_audio_path: Path to your reference audio file (3+ seconds)
        output_path: Where to save the generated audio
        language: Language code (en, es, fr, de, etc.)
    """
    if not TTS_AVAILABLE:
        logger.error("=" * 80)
        logger.error("TTS LIBRARY NOT AVAILABLE")
        logger.error("=" * 80)
        logger.error("Cannot proceed with voice cloning - TTS library is not installed.")
        logger.error("Please install TTS: pip install TTS")
        logger.error("Note: TTS requires Python 3.9-3.11")
        raise ImportError("TTS library not installed. Please install with: pip install TTS")
    
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info("VOICE CLONING PROCESS STARTED")
    logger.info("=" * 80)
    logger.info(f"Input Text: '{text}'")
    logger.info(f"Text Length: {len(text)} characters")
    logger.info(f"Speaker Audio: {speaker_audio_path}")
    logger.info(f"Output Path: {output_path}")
    logger.info(f"Language: {language}")
    
    # Step 1: Validate speaker audio file
    logger.info("")
    logger.info("STEP 1: Validating speaker audio file...")
    if not log_audio_file_info(speaker_audio_path):
        raise FileNotFoundError(f"Speaker audio file not found: {speaker_audio_path}")
    
    # Step 2: Initialize TTS model
    logger.info("")
    logger.info("STEP 2: Initializing XTTS model...")
    logger.info("Model: tts_models/multilingual/multi-dataset/xtts_v2")
    logger.info("This may take a while on first run (model download)...")
    
    model_load_start = time.time()
    try:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        model_load_time = time.time() - model_load_start
        logger.info(f"✅ Model loaded successfully in {model_load_time:.2f} seconds")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise
    
    # Step 3: Prepare output directory
    logger.info("")
    logger.info("STEP 3: Preparing output directory...")
    output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else "."
    if output_dir and not os.path.exists(output_dir):
        logger.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"✅ Output directory created: {output_dir}")
    else:
        logger.info(f"✅ Output directory exists: {output_dir}")
    
    # Step 4: Generate speech
    logger.info("")
    logger.info("STEP 4: Generating speech...")
    logger.info(f"Processing text: '{text}'")
    logger.info(f"Using speaker reference: {speaker_audio_path}")
    logger.info(f"Language setting: {language}")
    
    generation_start = time.time()
    try:
        logger.info("Calling tts.tts_to_file()...")
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_audio_path,
            language=language,
            file_path=output_path
        )
        generation_time = time.time() - generation_start
        logger.info(f"✅ Speech generation completed in {generation_time:.2f} seconds")
    except Exception as e:
        logger.error(f"❌ Speech generation failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise
    
    # Step 5: Verify output file
    logger.info("")
    logger.info("STEP 5: Verifying output file...")
    if os.path.exists(output_path):
        output_size = os.path.getsize(output_path)
        output_size_mb = output_size / (1024 * 1024)
        logger.info(f"✅ Output file created successfully")
        logger.info(f"Output Path: {os.path.abspath(output_path)}")
        logger.info(f"Output Size: {output_size:,} bytes ({output_size_mb:.2f} MB)")
        
        if LIBROSA_AVAILABLE:
            try:
                y, sr = librosa.load(output_path, sr=None)
                duration = len(y) / sr
                logger.info(f"Output Duration: {duration:.2f} seconds")
                logger.info(f"Output Sample Rate: {sr} Hz")
            except Exception as e:
                logger.warning(f"Could not analyze output audio: {e}")
    else:
        logger.error(f"❌ Output file was not created: {output_path}")
        raise FileNotFoundError(f"Output file not found: {output_path}")
    
    # Summary
    total_time = time.time() - start_time
    logger.info("")
    logger.info("=" * 80)
    logger.info("VOICE CLONING PROCESS COMPLETED")
    logger.info("=" * 80)
    logger.info(f"Total Processing Time: {total_time:.2f} seconds")
    logger.info(f"Model Load Time: {model_load_time:.2f} seconds")
    logger.info(f"Generation Time: {generation_time:.2f} seconds")
    logger.info(f"Output File: {os.path.abspath(output_path)}")
    logger.info("=" * 80)
    
    return output_path


def list_available_models():
    """List all available TTS models from Coqui with detailed logging."""
    if not TTS_AVAILABLE:
        logger.error("TTS library not available - cannot list models")
        return []
    
    logger.info("=" * 80)
    logger.info("FETCHING AVAILABLE TTS MODELS")
    logger.info("=" * 80)
    
    try:
        logger.info("Initializing TTS API...")
        tts = TTS()
        logger.info("✅ TTS API initialized")
        
        logger.info("Fetching model list...")
        models = tts.list_models()
        logger.info(f"✅ Found {len(models)} available models")
        
        logger.info("")
        logger.info("Available TTS models:")
        for i, model in enumerate(models, 1):
            logger.info(f"  {i:3d}. {model}")
        
        logger.info("")
        logger.info(f"Total models: {len(models)}")
        logger.info("=" * 80)
        
        return models
    except Exception as e:
        logger.error(f"❌ Failed to list models: {e}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise


if __name__ == "__main__":
    # Log system information at startup
    log_system_info()
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("COQUI XTTS VOICE CLONING EXAMPLE")
    logger.info("=" * 80)
    logger.info("")
    
    # Configuration
    YOUR_TEXT = "Hello, this is a test of voice cloning technology."
    SPEAKER_AUDIO = "path/to/your/voice_sample.wav"  # Replace with your audio file
    OUTPUT_FILE = "output_cloned_voice.wav"
    LANGUAGE = "en"  # Change to your language: en, es, fr, de, etc.
    
    logger.info("CONFIGURATION:")
    logger.info(f"  Text to synthesize: '{YOUR_TEXT}'")
    logger.info(f"  Speaker audio file: {SPEAKER_AUDIO}")
    logger.info(f"  Output file: {OUTPUT_FILE}")
    logger.info(f"  Language: {LANGUAGE}")
    logger.info("")
    
    # Uncomment to see available models
    # logger.info("Listing available models...")
    # list_available_models()
    # logger.info("")
    
    # Clone the voice
    try:
        logger.info("Starting voice cloning process...")
        logger.info("")
        clone_voice_with_xtts(
            text=YOUR_TEXT,
            speaker_audio_path=SPEAKER_AUDIO,
            output_path=OUTPUT_FILE,
            language=LANGUAGE
        )
        logger.info("")
        logger.info("✅ SUCCESS! Voice cloning completed successfully.")
    except FileNotFoundError as e:
        logger.error("")
        logger.error("=" * 80)
        logger.error("FILE NOT FOUND ERROR")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error("")
        logger.error("Please update SPEAKER_AUDIO path with your audio file location.")
        logger.error("Example: SPEAKER_AUDIO = '/path/to/your/voice.wav'")
        sys.exit(1)
    except Exception as e:
        logger.error("")
        logger.error("=" * 80)
        logger.error("ERROR OCCURRED")
        logger.error("=" * 80)
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {e}")
        import traceback
        logger.error("")
        logger.error("Full Traceback:")
        logger.error(traceback.format_exc())
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("  1. Make sure you have installed TTS: pip install TTS")
        logger.error("  2. Check that your audio file exists and is accessible")
        logger.error("  3. Verify audio file format (WAV, MP3, FLAC)")
        logger.error("  4. Ensure audio file is at least 3 seconds long")
        logger.error("  5. Check available disk space (models can be 1-5GB+)")
        sys.exit(1)

