#!/usr/bin/env python3
"""
Fixed Voice Cloning Test - Attempts to work around PyTorch compatibility issues.
"""

import logging
import os
import sys
import time
from pathlib import Path

# Apply PyTorch patch FIRST (before any TTS imports)
try:
    import patch_torch_load
    logger_temp = logging.getLogger(__name__)
    logger_temp.info("✅ Applied PyTorch weights_only patch")
except Exception as e:
    pass  # Patch may not be needed

# Configure extensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def find_audio_samples(audio_dir="audio_samples"):
    """Find audio samples for voice cloning."""
    audio_path = Path(audio_dir)
    if not audio_path.exists():
        logger.error(f"❌ Audio directory not found: {audio_dir}")
        return []
    
    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(list(audio_path.glob(f"*{ext}")))
        audio_files.extend(list(audio_path.glob(f"*{ext.upper()}")))
    
    audio_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    logger.info(f"Found {len(audio_files)} audio files in {audio_dir}")
    return audio_files

def test_voice_cloning_with_workarounds(audio_files):
    """Test voice cloning with all possible workarounds."""
    logger.info("=" * 100)
    logger.info("VOICE CLONING TEST WITH COMPREHENSIVE WORKAROUNDS")
    logger.info("=" * 100)
    
    if not audio_files:
        logger.error("❌ No audio files found")
        return False
    
    # Set environment variables
    os.environ["COQUI_TOS_AGREED"] = "1"
    os.environ["TORCH_LOAD_WEIGHTS_ONLY"] = "False"
    
    reference_audio = audio_files[0]
    logger.info(f"Using reference audio: {reference_audio.name}")
    logger.info(f"File size: {reference_audio.stat().st_size / (1024*1024):.2f} MB")
    
    test_texts = [
        "This is a voice cloning test using Coqui XTTS.",
        "The voice should sound similar to the reference audio.",
        "Voice cloning technology allows us to replicate speech patterns.",
    ]
    
    logger.info("")
    logger.info("Attempting to load XTTS model with workarounds...")
    
    try:
        # Try to add safe globals
        import torch
        try:
            from TTS.tts.configs.xtts_config import XttsConfig
            torch.serialization.add_safe_globals([XttsConfig])
            logger.info("✅ Added XttsConfig to safe globals")
        except Exception as e:
            logger.warning(f"⚠️  Could not add safe globals: {e}")
        
        from TTS.api import TTS
        
        logger.info("Loading XTTS model (this may take a while)...")
        start_time = time.time()
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)
        load_time = time.time() - start_time
        logger.info(f"✅ XTTS model loaded in {load_time:.2f} seconds")
        
        output_dir = Path("test_outputs/voice_cloning")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for i, text in enumerate(test_texts, 1):
            logger.info("")
            logger.info(f"Test {i}/{len(test_texts)}: Cloning voice...")
            logger.info(f"Text: '{text}'")
            
            output_file = output_dir / f"coqui_cloned_{i}.wav"
            
            clone_start = time.time()
            try:
                tts.tts_to_file(
                    text=text,
                    speaker_wav=str(reference_audio),
                    language="en",
                    file_path=str(output_file)
                )
                clone_time = time.time() - clone_start
                
                if output_file.exists():
                    size_mb = output_file.stat().st_size / (1024 * 1024)
                    logger.info(f"✅ Cloned: {output_file.name} ({size_mb:.2f} MB, {clone_time:.2f}s)")
                    results.append({
                        "text": text,
                        "file": str(output_file),
                        "time": clone_time,
                        "size_mb": size_mb
                    })
                else:
                    logger.error(f"❌ Failed to create: {output_file}")
            except Exception as e:
                logger.error(f"❌ Cloning failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info("")
        logger.info("=" * 100)
        logger.info("VOICE CLONING TEST RESULTS")
        logger.info("=" * 100)
        logger.info(f"Reference audio: {reference_audio.name}")
        logger.info(f"Total tests: {len(results)}/{len(test_texts)}")
        if results:
            logger.info(f"Average cloning time: {sum(r['time'] for r in results) / len(results):.2f}s")
            logger.info(f"Total output size: {sum(r['size_mb'] for r in results):.2f} MB")
        
        return len(results) == len(test_texts)
        
    except Exception as e:
        logger.error(f"❌ Voice cloning test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    logger.info("=" * 100)
    logger.info("COMPREHENSIVE VOICE CLONING TEST")
    logger.info("=" * 100)
    logger.info("")
    
    audio_files = find_audio_samples()
    
    if not audio_files:
        logger.error("❌ No audio samples found!")
        return False
    
    success = test_voice_cloning_with_workarounds(audio_files)
    
    logger.info("")
    if success:
        logger.info("✅ ALL VOICE CLONING TESTS PASSED")
    else:
        logger.error("❌ SOME VOICE CLONING TESTS FAILED")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

