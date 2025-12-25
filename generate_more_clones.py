#!/usr/bin/env python3
"""
Generate Multiple Voice Clones
Creates multiple cloned voice samples using the best refined audio.
"""

import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Configure extensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Apply PyTorch patch
try:
    import patch_torch_load
    patch_torch_load.patch_torch_load()
except Exception as e:
    logger.warning(f"Could not apply patch: {e}")

def generate_clones(num_clones=10, reference_audio=None):
    """Generate multiple voice clones."""
    
    logger.info("=" * 100)
    logger.info("GENERATING MULTIPLE VOICE CLONES")
    logger.info("=" * 100)
    logger.info("")
    
    # Set environment
    os.environ["COQUI_TOS_AGREED"] = "1"
    
    # Find best refined audio
    refined_dir = Path("refined_audio")
    if not refined_dir.exists():
        logger.error("❌ refined_audio/ directory not found. Run refine_and_clone.py first.")
        return False
    
    # Get reference audio
    if reference_audio is None:
        # Find the best quality refined audio (top1)
        refined_files = sorted(refined_dir.glob("refined_top*.wav"))
        if not refined_files:
            logger.error("❌ No refined audio files found. Run refine_and_clone.py first.")
            return False
        reference_audio = refined_files[0]  # Use top1
        logger.info(f"Using reference audio: {reference_audio.name}")
    else:
        reference_audio = Path(reference_audio)
        if not reference_audio.exists():
            logger.error(f"❌ Reference audio not found: {reference_audio}")
            return False
    
    # Load XTTS model
    try:
        import torch
        from TTS.api import TTS
        
        # Add safe globals
        try:
            from TTS.tts.configs.xtts_config import XttsConfig
            torch.serialization.add_safe_globals([XttsConfig])
        except:
            pass
        
        logger.info("Loading XTTS model...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)
        logger.info("✅ XTTS model loaded")
        
    except Exception as e:
        logger.error(f"❌ Failed to load XTTS model: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Test phrases for variety
    test_phrases = [
        "Hello, this is a voice cloning demonstration using advanced machine learning technology.",
        "The quality of voice synthesis has improved dramatically in recent years.",
        "This system can clone voices with just a few seconds of audio sample.",
        "Voice cloning technology has many applications in content creation and accessibility.",
        "The neural network analyzes voice characteristics and reproduces them accurately.",
        "Modern text-to-speech systems can generate natural-sounding human voices.",
        "This voice clone was created using refined audio samples for optimal quality.",
        "Artificial intelligence continues to revolutionize how we interact with technology.",
        "Voice synthesis technology enables new forms of creative expression and communication.",
        "The future of voice technology holds exciting possibilities for innovation.",
        "Machine learning models can learn to mimic human speech patterns remarkably well.",
        "This demonstration showcases the capabilities of state-of-the-art voice cloning systems.",
        "Audio processing and refinement ensure the highest quality voice replication.",
        "The combination of deep learning and signal processing creates realistic voice synthesis.",
        "Voice cloning technology opens doors to personalized content and accessibility tools.",
        "Advanced algorithms analyze spectral characteristics to capture unique voice signatures.",
        "This system processes audio through multiple refinement stages for optimal results.",
        "The integration of neural networks and audio engineering produces impressive voice clones.",
        "Voice synthesis technology continues to evolve with each new breakthrough.",
        "This demonstration highlights the potential of AI-driven voice replication systems.",
    ]
    
    # Create output directory
    output_dir = Path("test_outputs/batch_clones")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate clones
    logger.info("")
    logger.info(f"Generating {num_clones} voice clones...")
    logger.info("")
    
    results = []
    start_time = time.time()
    
    for i in range(1, num_clones + 1):
        phrase = test_phrases[(i - 1) % len(test_phrases)]
        output_file = output_dir / f"clone_{i:03d}.wav"
        
        logger.info(f"[{i}/{num_clones}] Generating clone...")
        logger.info(f"  Text: '{phrase[:60]}...'")
        
        clone_start = time.time()
        try:
            tts.tts_to_file(
                text=phrase,
                speaker_wav=str(reference_audio),
                language="en",
                file_path=str(output_file)
            )
            clone_time = time.time() - clone_start
            
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"  ✅ Generated: {output_file.name} ({size_mb:.2f} MB, {clone_time:.2f}s)")
                results.append({
                    "number": i,
                    "file": str(output_file),
                    "text": phrase,
                    "time": clone_time,
                    "size_mb": size_mb
                })
            else:
                logger.error(f"  ❌ File not created: {output_file}")
                
        except Exception as e:
            logger.error(f"  ❌ Generation failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        logger.info("")
    
    total_time = time.time() - start_time
    
    # Summary
    logger.info("=" * 100)
    logger.info("GENERATION SUMMARY")
    logger.info("=" * 100)
    logger.info(f"Total clones requested: {num_clones}")
    logger.info(f"Successfully generated: {len(results)}/{num_clones}")
    logger.info(f"Total time: {total_time:.2f} seconds")
    if results:
        logger.info(f"Average time per clone: {sum(r['time'] for r in results) / len(results):.2f} seconds")
        logger.info(f"Total output size: {sum(r['size_mb'] for r in results):.2f} MB")
        logger.info(f"Output directory: {output_dir}")
    logger.info("")
    logger.info("✅ Generation complete!")
    
    return len(results) == num_clones

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate multiple voice clones")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of clones to generate (default: 10)")
    parser.add_argument("-r", "--reference", type=str, default=None, help="Path to reference audio file")
    
    args = parser.parse_args()
    
    success = generate_clones(num_clones=args.num, reference_audio=args.reference)
    sys.exit(0 if success else 1)

