#!/usr/bin/env python3
"""
Master script to run all voice cloning tests in sequence:
1. Download audio from YouTube channel
2. Run generation test
3. Run voice cloning test
4. Run assessment test
"""

import logging
import sys
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def run_script(script_name, *args):
    """Run a Python script and return success status."""
    script_path = Path(script_name)
    if not script_path.exists():
        logger.error(f"❌ Script not found: {script_name}")
        return False
    
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"RUNNING: {script_name}")
    logger.info("=" * 80)
    
    try:
        cmd = [sys.executable, str(script_path)] + list(args)
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main function to run all tests."""
    logger.info("=" * 80)
    logger.info("VOICE CLONING COMPLETE TEST SUITE")
    logger.info("=" * 80)
    logger.info("")
    
    # Check if channel URL provided
    channel_url = None
    if len(sys.argv) > 1:
        channel_url = sys.argv[1]
    else:
        logger.info("Please provide your YouTube channel URL")
        logger.info("Example: https://www.youtube.com/@YourChannelName")
        channel_url = input("\nEnter channel URL (or press Enter to skip download): ").strip()
    
    results = {}
    
    # Step 1: Download audio (if URL provided)
    if channel_url:
        logger.info("")
        logger.info("STEP 1: Downloading audio from YouTube channel...")
        results['download'] = run_script("download_channel_audio.py", channel_url, "10")
    else:
        logger.info("")
        logger.info("STEP 1: Skipping download (no URL provided)")
        logger.info("Assuming audio_samples/ already contains audio files")
        results['download'] = Path("audio_samples").exists()
    
    # Step 2: Generation test
    logger.info("")
    logger.info("STEP 2: Running generation test...")
    results['generation'] = run_script("run_generation_test.py")
    
    # Step 3: Voice cloning test
    logger.info("")
    logger.info("STEP 3: Running voice cloning test...")
    results['voice_cloning'] = run_script("run_voice_cloning_test.py")
    
    # Step 4: Assessment test
    logger.info("")
    logger.info("STEP 4: Running assessment test...")
    results['assessment'] = run_script("run_assessment_test.py")
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUITE SUMMARY")
    logger.info("=" * 80)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("")
    if all_passed:
        logger.info("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    else:
        logger.warning("⚠️  SOME TESTS FAILED - Check logs above for details")
    
    logger.info("")
    logger.info("Output files:")
    logger.info("  - Generation: test_outputs/generation/")
    logger.info("  - Voice Cloning: test_outputs/voice_cloning/")
    logger.info("  - Audio Samples: audio_samples/")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

