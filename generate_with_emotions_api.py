#!/usr/bin/env python3
"""
Generate Multiple Samples with Different Emotions using IndexTTS2 API
Uses the Hugging Face API to generate voice clones with various emotions.
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

# Import the API caller
from call_indextts2_api import call_indextts2_api

def generate_emotion_samples(voice_reference, texts, output_dir="test_outputs/emotion_samples_api"):
    """Generate samples with different emotions."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Emotion configurations
    emotions = [
        {
            "name": "natural",
            "method": "Same as the voice reference",
            "vectors": None
        },
        {
            "name": "happy",
            "method": "Use emotion vectors",
            "vectors": {"happy": 0.8, "calm": 0.2}
        },
        {
            "name": "sad",
            "method": "Use emotion vectors",
            "vectors": {"sad": 0.8, "melancholic": 0.2}
        },
        {
            "name": "surprised",
            "method": "Use emotion vectors",
            "vectors": {"surprised": 0.8}
        },
        {
            "name": "angry",
            "method": "Use emotion vectors",
            "vectors": {"angry": 0.8}
        },
        {
            "name": "calm",
            "method": "Use emotion vectors",
            "vectors": {"calm": 0.9}
        }
    ]
    
    results = []
    
    for i, text in enumerate(texts, 1):
        for emotion in emotions:
            output_file = output_path / f"sample_{i:02d}_{emotion['name']}.wav"
            
            logger.info(f"Generating: sample_{i:02d}_{emotion['name']}")
            logger.info(f"  Text: '{text[:60]}...'")
            logger.info(f"  Emotion: {emotion['name']}")
            logger.info("")
            
            start_time = time.time()
            
            success = call_indextts2_api(
                voice_reference=voice_reference,
                text=text,
                output_file=str(output_file),
                emo_control_method=emotion["method"],
                emotion_vectors=emotion.get("vectors"),
                emotion_weight=0.8
            )
            
            gen_time = time.time() - start_time
            
            if success and output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                results.append({
                    "text_number": i,
                    "emotion": emotion["name"],
                    "output_file": str(output_file),
                    "generation_time": gen_time,
                    "size_mb": size_mb,
                    "success": True
                })
                logger.info(f"  ✅ Generated in {gen_time:.2f}s ({size_mb:.2f} MB)")
            else:
                logger.warning(f"  ⚠️  Generation failed or file not created")
            
            logger.info("")
    
    # Summary
    logger.info("=" * 100)
    logger.info("GENERATION SUMMARY")
    logger.info("=" * 100)
    logger.info(f"Total samples: {len(results)}")
    logger.info(f"Emotions tested: {len(emotions)}")
    logger.info(f"Texts used: {len(texts)}")
    logger.info("")
    
    if results:
        logger.info("Generated files:")
        for r in results:
            logger.info(f"  {r['text_number']:2d}. {Path(r['output_file']).name} ({r['emotion']}) - {r['size_mb']:.2f} MB")
        logger.info("")
    
    return results

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate emotion samples using IndexTTS2 API")
    parser.add_argument('--voice', type=str, required=True,
                        help='Path to voice reference audio file')
    parser.add_argument('--text', type=str, action='append',
                        help='Text to synthesize (can be used multiple times)')
    parser.add_argument('--output-dir', type=str, default='test_outputs/emotion_samples_api',
                        help='Output directory for generated samples')
    
    args = parser.parse_args()
    
    if not args.text:
        # Default texts
        texts = [
            "This is a test of emotion control in voice synthesis.",
            "I'm feeling very happy about this new technology!",
            "This makes me sad to think about.",
            "Wow, I'm so surprised by this result!",
            "I'm getting really angry about this situation."
        ]
    else:
        texts = args.text
    
    results = generate_emotion_samples(
        voice_reference=args.voice,
        texts=texts,
        output_dir=args.output_dir
    )
    
    sys.exit(0 if results else 1)

if __name__ == "__main__":
    main()

