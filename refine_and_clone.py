#!/usr/bin/env python3
"""
Complete Audio Refinement and Voice Cloning Pipeline
1. Analyze audio quality
2. Filter high-quality samples
3. Refine audio through multiple stages
4. Clone voice using best quality audio
"""

import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Configure extensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Apply PyTorch patch
try:
    import patch_torch_load
except Exception:
    pass

def main():
    """Main refinement and cloning pipeline."""
    logger.info("=" * 100)
    logger.info("COMPLETE AUDIO REFINEMENT AND VOICE CLONING PIPELINE")
    logger.info("=" * 100)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    start_time = time.time()
    
    # Step 1: Analyze audio quality
    logger.info("=" * 100)
    logger.info("STEP 1: ANALYZING AUDIO QUALITY")
    logger.info("=" * 100)
    logger.info("")
    
    from audio_quality_analyzer import AudioQualityAnalyzer
    
    analyzer = AudioQualityAnalyzer("audio_samples")
    quality_results = analyzer.analyze_all_audio()
    
    if not quality_results:
        logger.error("❌ No audio files found or analysis failed")
        return False
    
    # Save quality analysis
    analyzer.save_results("audio_quality_results.json")
    logger.info("")
    
    # Step 2: Filter high-quality files
    logger.info("=" * 100)
    logger.info("STEP 2: FILTERING HIGH QUALITY AUDIO")
    logger.info("=" * 100)
    logger.info("")
    
    high_quality = analyzer.filter_high_quality(
        min_score=60,
        min_duration=5.0,
        max_silence=0.4
    )
    
    if not high_quality:
        logger.warning("⚠️  No files passed quality filter, using top 5 by score")
        high_quality = quality_results[:5]
    
    logger.info("")
    
    # Step 3: Refine audio
    logger.info("=" * 100)
    logger.info("STEP 3: REFINING HIGH QUALITY AUDIO")
    logger.info("=" * 100)
    logger.info("")
    
    from audio_refinement_processor import AudioRefinementProcessor
    
    processor = AudioRefinementProcessor(
        input_dir="audio_samples",
        output_dir="refined_audio"
    )
    
    # Process top 5 highest quality files
    refined_files = processor.process_high_quality_files(high_quality, top_n=5)
    
    if not refined_files:
        logger.error("❌ Audio refinement failed")
        return False
    
    logger.info("")
    
    # Step 4: Clone voice using best refined audio
    logger.info("=" * 100)
    logger.info("STEP 4: VOICE CLONING WITH REFINED AUDIO")
    logger.info("=" * 100)
    logger.info("")
    
    # Use the best refined audio file
    best_refined = refined_files[0]
    reference_audio = best_refined['output']
    
    logger.info(f"Using best refined audio: {Path(reference_audio).name}")
    logger.info(f"  Duration: {best_refined['duration']:.2f}s")
    logger.info(f"  Sample Rate: {best_refined['sample_rate']} Hz")
    logger.info(f"  File Size: {best_refined['file_size_mb']:.2f} MB")
    logger.info("")
    
    # Clone voice
    try:
        from TTS.api import TTS
        
        # Set environment
        os.environ["COQUI_TOS_AGREED"] = "1"
        
        # Add safe globals
        import torch
        try:
            from TTS.tts.configs.xtts_config import XttsConfig
            torch.serialization.add_safe_globals([XttsConfig])
        except:
            pass
        
        logger.info("Loading XTTS model...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)
        logger.info("✅ XTTS model loaded")
        
        # Test phrases
        test_texts = [
            "This is a high-quality voice cloning test using refined audio samples.",
            "The voice should sound natural and clear with excellent similarity to the original.",
            "Advanced audio processing ensures optimal voice cloning results.",
        ]
        
        output_dir = Path("test_outputs/refined_voice_cloning")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for i, text in enumerate(test_texts, 1):
            logger.info("")
            logger.info(f"Test {i}/{len(test_texts)}: Cloning with refined audio...")
            logger.info(f"Text: '{text}'")
            
            output_file = output_dir / f"refined_cloned_{i}.wav"
            
            clone_start = time.time()
            tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio,
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
        
        logger.info("")
        logger.info("=" * 100)
        logger.info("VOICE CLONING RESULTS (REFINED AUDIO)")
        logger.info("=" * 100)
        logger.info(f"Reference: {Path(reference_audio).name}")
        logger.info(f"Tests: {len(results)}/{len(test_texts)}")
        if results:
            logger.info(f"Average cloning time: {sum(r['time'] for r in results) / len(results):.2f}s")
            logger.info(f"Total output size: {sum(r['size_mb'] for r in results):.2f} MB")
        
    except Exception as e:
        logger.error(f"❌ Voice cloning failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Final summary
    total_time = time.time() - start_time
    
    logger.info("")
    logger.info("=" * 100)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 100)
    logger.info(f"Total processing time: {total_time:.2f} seconds")
    logger.info("")
    logger.info("Output files:")
    logger.info(f"  - Quality analysis: audio_quality_results.json")
    logger.info(f"  - Refined audio: refined_audio/")
    logger.info(f"  - Cloned voice: test_outputs/refined_voice_cloning/")
    logger.info("")
    logger.info("✅ ALL STAGES COMPLETED SUCCESSFULLY!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

