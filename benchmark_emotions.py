#!/usr/bin/env python3
"""
Emotion Expression Benchmarking System
Comprehensive benchmarking of emotional expressions using IndexTTS2 API.
Analyzes pitch, energy, tempo, spectral features, and emotional expressiveness.
"""

import logging
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from call_indextts2_api import call_indextts2_api

class EmotionBenchmarker:
    """Comprehensive emotion expression benchmarking system."""
    
    def __init__(self):
        self.results = []
        self.analysis_cache = {}
        
    def extract_emotion_features(self, audio_path):
        """Extract emotion-related audio features."""
        try:
            import librosa
            import numpy as np
            
            logger.debug(f"Extracting features from: {Path(audio_path).name}")
            
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None, mono=True)
            duration = len(y) / sr
            
            # 1. Pitch Features (F0 - fundamental frequency)
            try:
                # Try librosa.pyin (requires librosa >= 0.9.0)
                if hasattr(librosa, 'pyin'):
                    f0, voiced_flag, voiced_probs = librosa.pyin(
                        y, 
                        fmin=librosa.note_to_hz('C2'), 
                        fmax=librosa.note_to_hz('C7')
                    )
                    f0_clean = f0[~np.isnan(f0)]
                    voiced_ratio = float(np.sum(voiced_flag) / len(voiced_flag)) if len(voiced_flag) > 0 else 0.0
                else:
                    # Fallback: use autocorrelation-based pitch estimation
                    try:
                        import scipy.signal
                    except ImportError:
                        scipy = None
                    # Simple autocorrelation pitch estimation
                    frame_length = 2048
                    hop_length = 512
                    frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
                    f0_clean = []
                    for frame in frames.T:
                        # Autocorrelation
                        autocorr = np.correlate(frame, frame, mode='full')
                        autocorr = autocorr[len(autocorr)//2:]
                        # Find peak (excluding DC)
                        if len(autocorr) > 100:
                            peak_idx = np.argmax(autocorr[20:]) + 20
                            if peak_idx > 0:
                                f0_est = sr / peak_idx
                                if 80 <= f0_est <= 400:  # Human voice range
                                    f0_clean.append(f0_est)
                    f0_clean = np.array(f0_clean)
                    voiced_ratio = len(f0_clean) / (len(frames[0]) if len(frames) > 0 else 1)
            except Exception as e:
                logger.warning(f"Pitch extraction failed, using fallback: {e}")
                # Fallback: estimate from spectral centroid
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                f0_clean = spectral_centroids / 4  # Rough approximation
                voiced_ratio = 0.5
            
            pitch_features = {
                "pitch_mean": float(np.mean(f0_clean)) if len(f0_clean) > 0 else 0.0,
                "pitch_std": float(np.std(f0_clean)) if len(f0_clean) > 0 else 0.0,
                "pitch_range": float(np.max(f0_clean) - np.min(f0_clean)) if len(f0_clean) > 0 else 0.0,
                "pitch_variation": float(np.std(f0_clean) / np.mean(f0_clean)) if len(f0_clean) > 0 and np.mean(f0_clean) > 0 else 0.0,
                "voiced_ratio": float(voiced_ratio),
            }
            
            # 2. Energy Features (intensity, dynamics)
            rms = librosa.feature.rms(y=y)[0]
            energy_features = {
                "energy_mean": float(np.mean(rms)),
                "energy_std": float(np.std(rms)),
                "energy_max": float(np.max(rms)),
                "energy_min": float(np.min(rms)),
                "energy_range": float(np.max(rms) - np.min(rms)),
                "energy_dynamics": float(np.std(rms) / np.mean(rms)) if np.mean(rms) > 0 else 0.0,
            }
            
            # 3. Tempo/Rhythm Features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            tempo_features = {
                "tempo_bpm": float(tempo),
                "beat_count": int(len(beats)),
                "beats_per_second": float(len(beats) / duration) if duration > 0 else 0.0,
            }
            
            # 4. Spectral Features (timbre, brightness)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            spectral_features = {
                "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                "spectral_centroid_std": float(np.std(spectral_centroids)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                "spectral_rolloff_std": float(np.std(spectral_rolloff)),
                "brightness": float(np.mean(spectral_centroids)),  # Higher = brighter
                "mfcc_mean": [float(np.mean(mfcc)) for mfcc in mfccs],
            }
            
            # 5. Prosody Features (speech rhythm, stress patterns)
            # Zero crossing rate variation (speech vs silence patterns)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            prosody_features = {
                "zcr_mean": float(np.mean(zcr)),
                "zcr_std": float(np.std(zcr)),
                "speech_rate": float(np.mean(zcr) * sr / 2),  # Approximate speech rate
            }
            
            # 6. Emotional Expressiveness Score
            # Combines multiple features to estimate emotional expressiveness
            expressiveness_score = (
                pitch_features["pitch_variation"] * 30 +  # More pitch variation = more expressive
                energy_features["energy_dynamics"] * 25 +  # More energy dynamics = more expressive
                min(pitch_features["pitch_range"] / 200, 1.0) * 20 +  # Wider pitch range
                min(energy_features["energy_range"] / 0.5, 1.0) * 15 +  # Wider energy range
                min(spectral_features["spectral_centroid_std"] / 1000, 1.0) * 10  # Spectral variation
            )
            
            features = {
                "duration": float(duration),
                "pitch": pitch_features,
                "energy": energy_features,
                "tempo": tempo_features,
                "spectral": spectral_features,
                "prosody": prosody_features,
                "expressiveness_score": float(expressiveness_score),
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from {audio_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def compare_emotions(self, baseline_features, emotion_features):
        """Compare emotion features against baseline (natural)."""
        if not baseline_features or not emotion_features:
            return None
        
        comparisons = {}
        
        # Pitch comparison
        pitch_diff = {
            "mean_diff": emotion_features["pitch"]["pitch_mean"] - baseline_features["pitch"]["pitch_mean"],
            "std_diff": emotion_features["pitch"]["pitch_std"] - baseline_features["pitch"]["pitch_std"],
            "range_diff": emotion_features["pitch"]["pitch_range"] - baseline_features["pitch"]["pitch_range"],
            "variation_diff": emotion_features["pitch"]["pitch_variation"] - baseline_features["pitch"]["pitch_variation"],
        }
        
        # Energy comparison
        energy_diff = {
            "mean_diff": emotion_features["energy"]["energy_mean"] - baseline_features["energy"]["energy_mean"],
            "std_diff": emotion_features["energy"]["energy_std"] - baseline_features["energy"]["energy_std"],
            "dynamics_diff": emotion_features["energy"]["energy_dynamics"] - baseline_features["energy"]["energy_dynamics"],
        }
        
        # Expressiveness comparison
        expressiveness_diff = emotion_features["expressiveness_score"] - baseline_features["expressiveness_score"]
        
        comparisons = {
            "pitch": pitch_diff,
            "energy": energy_diff,
            "expressiveness_diff": float(expressiveness_diff),
            "more_expressive": expressiveness_diff > 0,
        }
        
        return comparisons
    
    def generate_emotion_configs(self):
        """Generate comprehensive emotion test configurations."""
        configs = []
        
        # Baseline: Natural
        configs.append({
            "name": "natural",
            "description": "Natural emotion (baseline)",
            "emo_control_method": "Same as the voice reference",
            "emotion_vectors": None,
            "emotion_weight": 1.0,
            "is_baseline": True
        })
        
        # Single emotions with varying intensities
        emotions = ["happy", "sad", "angry", "surprised", "calm", "afraid", "disgusted", "melancholic"]
        
        for emotion in emotions:
            # Low intensity (0.3)
            configs.append({
                "name": f"{emotion}_low",
                "description": f"{emotion.capitalize()} (low intensity: 0.3)",
                "emo_control_method": "Use emotion vectors",
                "emotion_vectors": {emotion: 0.3},
                "emotion_weight": 0.5,
                "is_baseline": False
            })
            
            # Medium intensity (0.6)
            configs.append({
                "name": f"{emotion}_medium",
                "description": f"{emotion.capitalize()} (medium intensity: 0.6)",
                "emo_control_method": "Use emotion vectors",
                "emotion_vectors": {emotion: 0.6},
                "emotion_weight": 0.7,
                "is_baseline": False
            })
            
            # High intensity (0.9)
            configs.append({
                "name": f"{emotion}_high",
                "description": f"{emotion.capitalize()} (high intensity: 0.9)",
                "emo_control_method": "Use emotion vectors",
                "emotion_vectors": {emotion: 0.9},
                "emotion_weight": 0.9,
                "is_baseline": False
            })
        
        # Mixed emotions
        mixed_configs = [
            {"name": "happy_calm", "vectors": {"happy": 0.6, "calm": 0.4}},
            {"name": "sad_melancholic", "vectors": {"sad": 0.7, "melancholic": 0.3}},
            {"name": "surprised_happy", "vectors": {"surprised": 0.5, "happy": 0.5}},
            {"name": "angry_afraid", "vectors": {"angry": 0.6, "afraid": 0.4}},
        ]
        
        for mixed in mixed_configs:
            configs.append({
                "name": mixed["name"],
                "description": f"Mixed: {mixed['name'].replace('_', ' + ')}",
                "emo_control_method": "Use emotion vectors",
                "emotion_vectors": mixed["vectors"],
                "emotion_weight": 0.8,
                "is_baseline": False
            })
        
        return configs
    
    def run_benchmark(self, voice_reference, texts, output_dir="test_outputs/emotion_benchmark"):
        """Run comprehensive emotion benchmarking."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("=" * 100)
        logger.info("EMOTION EXPRESSION BENCHMARKING")
        logger.info("=" * 100)
        logger.info("")
        logger.info(f"Voice reference: {Path(voice_reference).name}")
        logger.info(f"Number of texts: {len(texts)}")
        logger.info(f"Output directory: {output_path}")
        logger.info("")
        
        # Generate emotion configurations
        configs = self.generate_emotion_configs()
        logger.info(f"Total emotion configurations: {len(configs)}")
        logger.info("")
        
        all_results = []
        baseline_results = {}
        
        total_start = time.time()
        
        # Phase 1: Generate all samples
        logger.info("-" * 100)
        logger.info("PHASE 1: GENERATING SAMPLES")
        logger.info("-" * 100)
        logger.info("")
        
        for i, text in enumerate(texts, 1):
            logger.info(f"Text {i}/{len(texts)}: '{text[:60]}...'")
            logger.info("")
            
            for config in configs:
                output_file = output_path / f"text_{i:02d}_{config['name']}.wav"
                
                logger.info(f"  Generating: {config['name']} ({config['description']})")
                
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
                        all_results.append({
                            "text_number": i,
                            "text": text,
                            "config": config,
                            "output_file": str(output_file),
                            "generation_time": gen_time,
                            "success": True
                        })
                        
                        # Store baseline for comparison
                        if config.get("is_baseline"):
                            baseline_key = f"text_{i}"
                            if baseline_key not in baseline_results:
                                baseline_results[baseline_key] = str(output_file)
                        
                        logger.info(f"    ✅ Generated in {gen_time:.2f}s")
                    else:
                        logger.warning(f"    ⚠️  Generation failed")
                        all_results.append({
                            "text_number": i,
                            "text": text,
                            "config": config,
                            "success": False
                        })
                except Exception as e:
                    logger.error(f"    ❌ Error: {e}")
                    all_results.append({
                        "text_number": i,
                        "text": text,
                        "config": config,
                        "success": False,
                        "error": str(e)
                    })
                
                logger.info("")
            
            logger.info("")
        
        # Phase 2: Analyze all generated samples
        logger.info("-" * 100)
        logger.info("PHASE 2: ANALYZING EMOTION FEATURES")
        logger.info("-" * 100)
        logger.info("")
        
        analysis_results = []
        
        for result in all_results:
            if not result.get("success"):
                continue
            
            output_file = result["output_file"]
            logger.info(f"Analyzing: {Path(output_file).name}")
            
            features = self.extract_emotion_features(output_file)
            
            if features:
                result["features"] = features
                analysis_results.append(result)
                
                # Compare with baseline if not baseline
                if not result["config"].get("is_baseline"):
                    baseline_key = f"text_{result['text_number']}"
                    if baseline_key in baseline_results:
                        baseline_file = baseline_results[baseline_key]
                        baseline_features = self.extract_emotion_features(baseline_file)
                        if baseline_features:
                            comparison = self.compare_emotions(baseline_features, features)
                            result["comparison"] = comparison
                
                logger.info(f"  ✅ Expressiveness score: {features['expressiveness_score']:.2f}")
            else:
                logger.warning(f"  ⚠️  Feature extraction failed")
            
            logger.info("")
        
        # Phase 3: Generate report
        logger.info("-" * 100)
        logger.info("PHASE 3: GENERATING BENCHMARK REPORT")
        logger.info("-" * 100)
        logger.info("")
        
        report = self.generate_report(analysis_results, output_path)
        
        total_time = time.time() - total_start
        
        logger.info("")
        logger.info("=" * 100)
        logger.info("BENCHMARKING COMPLETE")
        logger.info("=" * 100)
        logger.info(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        logger.info(f"Successful generations: {len([r for r in all_results if r.get('success')])}")
        logger.info(f"Successful analyses: {len(analysis_results)}")
        logger.info(f"Report saved to: {output_path / 'benchmark_report.json'}")
        logger.info("")
        
        return analysis_results, report
    
    def generate_report(self, results, output_dir):
        """Generate comprehensive benchmark report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(results),
            "emotions_tested": {},
            "statistics": {},
            "rankings": {},
            "comparisons": []
        }
        
        # Group by emotion
        by_emotion = defaultdict(list)
        for result in results:
            emotion_name = result["config"]["name"]
            by_emotion[emotion_name].append(result)
        
        # Calculate statistics per emotion
        for emotion, samples in by_emotion.items():
            if not samples or not any(s.get("features") for s in samples):
                continue
            
            expressiveness_scores = [s["features"]["expressiveness_score"] for s in samples if s.get("features")]
            pitch_variations = [s["features"]["pitch"]["pitch_variation"] for s in samples if s.get("features")]
            energy_dynamics = [s["features"]["energy"]["energy_dynamics"] for s in samples if s.get("features")]
            
            report["emotions_tested"][emotion] = {
                "count": len(samples),
                "avg_expressiveness": float(sum(expressiveness_scores) / len(expressiveness_scores)) if expressiveness_scores else 0.0,
                "avg_pitch_variation": float(sum(pitch_variations) / len(pitch_variations)) if pitch_variations else 0.0,
                "avg_energy_dynamics": float(sum(energy_dynamics) / len(energy_dynamics)) if energy_dynamics else 0.0,
            }
        
        # Overall statistics
        all_expressiveness = [r["features"]["expressiveness_score"] for r in results if r.get("features")]
        if all_expressiveness:
            import numpy as np
            report["statistics"] = {
                "avg_expressiveness": float(np.mean(all_expressiveness)),
                "std_expressiveness": float(np.std(all_expressiveness)),
                "min_expressiveness": float(np.min(all_expressiveness)),
                "max_expressiveness": float(np.max(all_expressiveness)),
            }
        
        # Rankings
        if all_expressiveness:
            sorted_emotions = sorted(
                report["emotions_tested"].items(),
                key=lambda x: x[1]["avg_expressiveness"],
                reverse=True
            )
            report["rankings"] = {
                "most_expressive": [e[0] for e in sorted_emotions[:5]],
                "least_expressive": [e[0] for e in sorted_emotions[-5:]],
            }
        
        # Detailed results
        report["detailed_results"] = []
        for result in results:
            if result.get("features"):
                report["detailed_results"].append({
                    "text_number": result["text_number"],
                    "emotion": result["config"]["name"],
                    "expressiveness_score": result["features"]["expressiveness_score"],
                    "pitch_variation": result["features"]["pitch"]["pitch_variation"],
                    "energy_dynamics": result["features"]["energy"]["energy_dynamics"],
                    "comparison": result.get("comparison"),
                })
        
        # Save report
        report_path = output_dir / "benchmark_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Report saved to: {report_path}")
        
        # Print summary
        logger.info("")
        logger.info("BENCHMARK SUMMARY:")
        logger.info("")
        if report["rankings"].get("most_expressive"):
            logger.info("Most expressive emotions:")
            for i, emotion in enumerate(report["rankings"]["most_expressive"][:5], 1):
                score = report["emotions_tested"][emotion]["avg_expressiveness"]
                logger.info(f"  {i}. {emotion}: {score:.2f}")
            logger.info("")
        
        return report

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark emotion expressions using IndexTTS2 API")
    parser.add_argument('--voice', type=str, required=True,
                        help='Path to voice reference audio file')
    parser.add_argument('--text', type=str, action='append',
                        help='Text to synthesize (can be used multiple times)')
    parser.add_argument('--output-dir', type=str, default='test_outputs/emotion_benchmark',
                        help='Output directory for generated samples and report')
    
    args = parser.parse_args()
    
    if not args.text:
        # Default test texts
        texts = [
            "This is a neutral statement for baseline comparison.",
            "I'm feeling extremely happy and excited about this!",
            "This situation makes me feel very sad and disappointed.",
        ]
    else:
        texts = args.text
    
    benchmarker = EmotionBenchmarker()
    results, report = benchmarker.run_benchmark(
        voice_reference=args.voice,
        texts=texts,
        output_dir=args.output_dir
    )
    
    sys.exit(0 if results else 1)

if __name__ == "__main__":
    main()

