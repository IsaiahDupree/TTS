#!/usr/bin/env python3
"""
Generation Test - Test TTS text-to-speech generation without voice cloning.
Tests basic TTS functionality with default voices.
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

def test_coqui_generation():
    """Test Coqui TTS generation."""
    logger.info("=" * 80)
    logger.info("COQUI TTS GENERATION TEST")
    logger.info("=" * 80)
    
    try:
        from TTS.api import TTS
        
        test_texts = [
            "Hello, this is a test of text-to-speech generation.",
            "The quick brown fox jumps over the lazy dog.",
            "Voice cloning technology has advanced significantly in recent years.",
        ]
        
        logger.info("Initializing Coqui TTS model...")
        start_time = time.time()
        tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True)
        load_time = time.time() - start_time
        logger.info(f"✅ Model loaded in {load_time:.2f} seconds")
        
        output_dir = Path("test_outputs/generation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for i, text in enumerate(test_texts, 1):
            logger.info("")
            logger.info(f"Test {i}/{len(test_texts)}: Generating speech...")
            logger.info(f"Text: '{text}'")
            
            output_file = output_dir / f"coqui_generation_{i}.wav"
            
            gen_start = time.time()
            tts.tts_to_file(text=text, file_path=str(output_file))
            gen_time = time.time() - gen_start
            
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"✅ Generated: {output_file.name} ({size_mb:.2f} MB, {gen_time:.2f}s)")
                results.append({
                    "text": text,
                    "file": str(output_file),
                    "time": gen_time,
                    "size_mb": size_mb
                })
            else:
                logger.error(f"❌ Failed to generate: {output_file}")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("GENERATION TEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Total tests: {len(results)}/{len(test_texts)}")
        logger.info(f"Average generation time: {sum(r['time'] for r in results) / len(results):.2f}s")
        logger.info(f"Total output size: {sum(r['size_mb'] for r in results):.2f} MB")
        
        return len(results) == len(test_texts)
        
    except Exception as e:
        logger.error(f"❌ Generation test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    logger.info("=" * 80)
    logger.info("TTS GENERATION TEST SUITE")
    logger.info("=" * 80)
    logger.info("")
    
    # Test Coqui TTS
    success = test_coqui_generation()
    
    logger.info("")
    if success:
        logger.info("✅ ALL GENERATION TESTS PASSED")
    else:
        logger.error("❌ SOME GENERATION TESTS FAILED")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

