#!/usr/bin/env python3
"""
Quick Emotion Benchmark
A faster, focused version of the emotion benchmark for quick testing.
Tests only the most important emotions and intensities.
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from benchmark_emotions import EmotionBenchmarker

def main():
    """Quick benchmark with essential emotions only."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick emotion benchmark (essential emotions only)")
    parser.add_argument('--voice', type=str, required=True,
                        help='Path to voice reference audio file')
    parser.add_argument('--text', type=str, action='append',
                        help='Text to synthesize (can be used multiple times)')
    parser.add_argument('--output-dir', type=str, default='test_outputs/quick_emotion_benchmark',
                        help='Output directory')
    
    args = parser.parse_args()
    
    if not args.text:
        texts = [
            "This is a neutral statement for baseline comparison.",
            "I'm feeling extremely happy and excited about this!",
        ]
    else:
        texts = args.text
    
    # Override emotion configs for quick test
    benchmarker = EmotionBenchmarker()
    
    # Quick configs: only essential emotions at medium intensity
    original_generate = benchmarker.generate_emotion_configs
    
    def quick_emotion_configs():
        """Quick emotion configurations (essential only)."""
        configs = [
            {
                "name": "natural",
                "description": "Natural emotion (baseline)",
                "emo_control_method": "Same as the voice reference",
                "emotion_vectors": None,
                "emotion_weight": 1.0,
                "is_baseline": True
            },
            # Essential emotions at medium intensity
            {"name": "happy_medium", "emotion": "happy", "intensity": 0.6},
            {"name": "sad_medium", "emotion": "sad", "intensity": 0.6},
            {"name": "angry_medium", "emotion": "angry", "intensity": 0.6},
            {"name": "surprised_medium", "emotion": "surprised", "intensity": 0.6},
            {"name": "calm_medium", "emotion": "calm", "intensity": 0.6},
        ]
        
        result = []
        for c in configs:
            if c.get("is_baseline"):
                result.append(c)
            else:
                result.append({
                    "name": c["name"],
                    "description": f"{c['emotion'].capitalize()} (medium intensity: {c['intensity']})",
                    "emo_control_method": "Use emotion vectors",
                    "emotion_vectors": {c["emotion"]: c["intensity"]},
                    "emotion_weight": 0.7,
                    "is_baseline": False
                })
        
        return result
    
    benchmarker.generate_emotion_configs = quick_emotion_configs
    
    logger.info("=" * 100)
    logger.info("QUICK EMOTION BENCHMARK")
    logger.info("=" * 100)
    logger.info("Testing essential emotions only (faster)")
    logger.info("")
    
    results, report = benchmarker.run_benchmark(
        voice_reference=args.voice,
        texts=texts,
        output_dir=args.output_dir
    )
    
    logger.info("")
    logger.info("✅ Quick benchmark complete!")
    logger.info("For full benchmark, use: benchmark_emotions.py")
    logger.info("")
    
    sys.exit(0 if results else 1)

if __name__ == "__main__":
    main()

