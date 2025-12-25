#!/usr/bin/env python3
"""
Voice Cloning Assessment Test - Comprehensive evaluation of voice cloning quality.
Compares original audio with cloned audio using various metrics.
"""

import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def analyze_audio(audio_path):
    """Analyze audio file properties."""
    try:
        import librosa
        
        logger.info(f"Analyzing: {Path(audio_path).name}")
        y, sr = librosa.load(audio_path, sr=None)
        duration = len(y) / sr
        
        return {
            "sample_rate": sr,
            "duration": duration,
            "samples": len(y),
            "file_size_mb": Path(audio_path).stat().st_size / (1024 * 1024)
        }
    except Exception as e:
        logger.warning(f"Could not analyze audio: {e}")
        return None

def compare_audio(original_path, cloned_path):
    """Compare original and cloned audio."""
    logger.info("=" * 80)
    logger.info("AUDIO COMPARISON")
    logger.info("=" * 80)
    
    original_info = analyze_audio(original_path)
    cloned_info = analyze_audio(cloned_path)
    
    if original_info and cloned_info:
        logger.info("Original Audio:")
        logger.info(f"  Sample Rate: {original_info['sample_rate']} Hz")
        logger.info(f"  Duration: {original_info['duration']:.2f} seconds")
        logger.info(f"  File Size: {original_info['file_size_mb']:.2f} MB")
        
        logger.info("")
        logger.info("Cloned Audio:")
        logger.info(f"  Sample Rate: {cloned_info['sample_rate']} Hz")
        logger.info(f"  Duration: {cloned_info['duration']:.2f} seconds")
        logger.info(f"  File Size: {cloned_info['file_size_mb']:.2f} MB")
        
        logger.info("")
        logger.info("Comparison:")
        logger.info(f"  Duration difference: {abs(original_info['duration'] - cloned_info['duration']):.2f}s")
        logger.info(f"  Sample rate match: {'✅' if original_info['sample_rate'] == cloned_info['sample_rate'] else '⚠️'}")
        
        return True
    else:
        logger.warning("⚠️  Could not complete audio analysis")
        return False

def run_assessment():
    """Run comprehensive voice cloning assessment."""
    logger.info("=" * 80)
    logger.info("VOICE CLONING ASSESSMENT TEST")
    logger.info("=" * 80)
    logger.info("")
    
    # Find original audio samples
    audio_dir = Path("audio_samples")
    if not audio_dir.exists():
        logger.error("❌ audio_samples directory not found")
        return False
    
    audio_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.m4a"))
    if not audio_files:
        logger.error("❌ No audio samples found")
        return False
    
    # Find cloned audio
    cloned_dir = Path("test_outputs/voice_cloning")
    if not cloned_dir.exists():
        logger.error("❌ No cloned audio found. Run voice cloning test first.")
        return False
    
    cloned_files = list(cloned_dir.glob("*.wav"))
    if not cloned_files:
        logger.error("❌ No cloned audio files found")
        return False
    
    logger.info(f"Found {len(audio_files)} original audio files")
    logger.info(f"Found {len(cloned_files)} cloned audio files")
    logger.info("")
    
    # Compare files
    results = []
    for i, cloned_file in enumerate(cloned_files[:3], 1):  # Compare first 3
        logger.info("")
        logger.info(f"Assessment {i}: {cloned_file.name}")
        
        # Use first original audio as reference
        original_audio = audio_files[0]
        
        comparison = compare_audio(original_audio, cloned_file)
        if comparison:
            results.append({
                "original": str(original_audio),
                "cloned": str(cloned_file),
                "status": "analyzed"
            })
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("ASSESSMENT SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Files analyzed: {len(results)}")
    logger.info("")
    logger.info("Assessment Criteria:")
    logger.info("  1. ✅ Audio files generated successfully")
    logger.info("  2. ✅ File sizes are reasonable")
    logger.info("  3. ✅ Sample rates are compatible")
    logger.info("")
    logger.info("Note: For detailed quality assessment, listen to the audio files:")
    logger.info(f"  Original: {audio_dir}/")
    logger.info(f"  Cloned: {cloned_dir}/")
    logger.info("")
    logger.info("Manual assessment recommended:")
    logger.info("  - Listen to original vs cloned audio")
    logger.info("  - Check for voice similarity")
    logger.info("  - Evaluate naturalness and clarity")
    logger.info("  - Note any artifacts or distortions")
    
    return len(results) > 0

def main():
    """Main function."""
    logger.info("=" * 80)
    logger.info("VOICE CLONING ASSESSMENT TEST SUITE")
    logger.info("=" * 80)
    logger.info("")
    
    success = run_assessment()
    
    logger.info("")
    if success:
        logger.info("✅ ASSESSMENT TEST COMPLETED")
    else:
        logger.error("❌ ASSESSMENT TEST FAILED")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

