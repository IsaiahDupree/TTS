#!/usr/bin/env python3
"""
Run Generations With and Without Emotion
Generates multiple samples using IndexTTS2 API with different emotion settings.
"""

import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from call_indextts2_api import call_indextts2_api

def run_generations(voice_reference, texts, output_dir="test_outputs/emotion_comparison"):
    """Run generations with and without emotion control."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 100)
    logger.info("RUNNING GENERATIONS WITH AND WITHOUT EMOTION")
    logger.info("=" * 100)
    logger.info("")
    logger.info(f"Voice reference: {Path(voice_reference).name}")
    logger.info(f"Number of texts: {len(texts)}")
    logger.info(f"Output directory: {output_path}")
    logger.info("")
    
    # Test configurations
    configs = [
        {
            "name": "natural",
            "description": "Natural emotion (same as voice reference)",
            "emo_control_method": "Same as the voice reference",
            "emotion_vectors": None,
            "emotion_weight": 1.0
        },
        {
            "name": "happy",
            "description": "Happy emotion",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"happy": 0.8, "calm": 0.2},
            "emotion_weight": 0.8
        },
        {
            "name": "sad",
            "description": "Sad emotion",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"sad": 0.8, "melancholic": 0.2},
            "emotion_weight": 0.8
        },
        {
            "name": "surprised",
            "description": "Surprised emotion",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"surprised": 0.8},
            "emotion_weight": 0.8
        },
        {
            "name": "angry",
            "description": "Angry emotion",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"angry": 0.8},
            "emotion_weight": 0.8
        },
        {
            "name": "calm",
            "description": "Calm emotion",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"calm": 0.9},
            "emotion_weight": 0.8
        }
    ]
    
    results = []
    total_start = time.time()
    
    for i, text in enumerate(texts, 1):
        logger.info("-" * 100)
        logger.info(f"TEXT {i}/{len(texts)}: '{text}'")
        logger.info("-" * 100)
        logger.info("")
        
        for config in configs:
            output_file = output_path / f"text_{i:02d}_{config['name']}.wav"
            
            logger.info(f"Generating: {config['name']} ({config['description']})")
            logger.info(f"  Output: {output_file.name}")
            logger.info("")
            
            gen_start = time.time()
            
            try:
                success = call_indextts2_api(
                    voice_reference=voice_reference,
                    text=text,
                    output_file=str(output_file),
                    emo_control_method=config["emo_control_method"],
                    emotion_vectors=config.get("emotion_vectors"),
                    emotion_weight=config.get("emotion_weight", 0.8)
                )
                
                gen_time = time.time() - gen_start
                
                if success and output_file.exists():
                    size_mb = output_file.stat().st_size / (1024 * 1024)
                    results.append({
                        "text_number": i,
                        "text": text,
                        "emotion": config["name"],
                        "description": config["description"],
                        "output_file": str(output_file),
                        "generation_time": gen_time,
                        "size_mb": size_mb,
                        "success": True
                    })
                    logger.info(f"  ✅ Generated in {gen_time:.2f}s ({size_mb:.2f} MB)")
                else:
                    logger.warning(f"  ⚠️  Generation failed or file not created")
                    results.append({
                        "text_number": i,
                        "text": text,
                        "emotion": config["name"],
                        "success": False
                    })
            except Exception as e:
                gen_time = time.time() - gen_start
                logger.error(f"  ❌ Error: {e}")
                results.append({
                    "text_number": i,
                    "text": text,
                    "emotion": config["name"],
                    "generation_time": gen_time,
                    "success": False,
                    "error": str(e)
                })
            
            logger.info("")
        
        logger.info("")
    
    total_time = time.time() - total_start
    
    # Summary
    logger.info("=" * 100)
    logger.info("GENERATION SUMMARY")
    logger.info("=" * 100)
    logger.info("")
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    logger.info(f"Total generations: {len(results)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    logger.info(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    logger.info("")
    
    if successful:
        avg_time = sum(r['generation_time'] for r in successful) / len(successful)
        total_size = sum(r['size_mb'] for r in successful)
        logger.info(f"Average generation time: {avg_time:.2f} seconds")
        logger.info(f"Total output size: {total_size:.2f} MB")
        logger.info("")
        
        logger.info("Generated files by emotion:")
        by_emotion = {}
        for r in successful:
            emotion = r['emotion']
            if emotion not in by_emotion:
                by_emotion[emotion] = []
            by_emotion[emotion].append(r)
        
        for emotion, files in sorted(by_emotion.items()):
            logger.info(f"  {emotion}: {len(files)} files")
        logger.info("")
        
        logger.info("All generated files:")
        for r in successful:
            logger.info(f"  {Path(r['output_file']).name} ({r['emotion']}) - {r['size_mb']:.2f} MB")
        logger.info("")
    
    if failed:
        logger.warning("Failed generations:")
        for r in failed:
            logger.warning(f"  Text {r['text_number']}, Emotion: {r['emotion']}")
            if 'error' in r:
                logger.warning(f"    Error: {r['error']}")
        logger.info("")
    
    logger.info(f"✅ All outputs saved to: {output_path}")
    logger.info("")
    
    return results

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run generations with and without emotion")
    parser.add_argument('--voice', type=str, required=True,
                        help='Path to voice reference audio file')
    parser.add_argument('--text', type=str, action='append',
                        help='Text to synthesize (can be used multiple times)')
    parser.add_argument('--output-dir', type=str, default='test_outputs/emotion_comparison',
                        help='Output directory for generated samples')
    
    args = parser.parse_args()
    
    if not args.text:
        # Default test texts
        texts = [
            "This is a test of voice cloning with natural emotion.",
            "I'm feeling very excited about this new technology!",
            "This situation makes me feel quite disappointed.",
            "Wow, I can't believe how well this works!",
            "I'm getting frustrated with these technical issues."
        ]
    else:
        texts = args.text
    
    results = run_generations(
        voice_reference=args.voice,
        texts=texts,
        output_dir=args.output_dir
    )
    
    success_count = sum(1 for r in results if r.get('success', False))
    sys.exit(0 if success_count > 0 else 1)

if __name__ == "__main__":
    main()

