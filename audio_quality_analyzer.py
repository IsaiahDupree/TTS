#!/usr/bin/env python3
"""
Comprehensive Audio Quality Analyzer
Analyzes audio files and ranks them by quality for voice cloning.
Multiple layers of quality assessment.
"""

import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime
import json

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

class AudioQualityAnalyzer:
    """Comprehensive audio quality analysis for voice cloning."""
    
    def __init__(self, audio_dir="audio_samples"):
        self.audio_dir = Path(audio_dir)
        self.results = []
        
    def analyze_audio_file(self, audio_path):
        """Analyze a single audio file with multiple quality metrics."""
        logger.info(f"  → Analyzing: {Path(audio_path).name}")
        
        try:
            import librosa
            import numpy as np
            import soundfile as sf
            
            # Load audio
            logger.debug(f"    Loading audio file...")
            y, sr = librosa.load(str(audio_path), sr=None, mono=True)
            duration = len(y) / sr
            file_size = Path(audio_path).stat().st_size
            
            # Basic metrics
            metrics = {
                "file": str(audio_path),
                "filename": Path(audio_path).name,
                "sample_rate": int(sr),
                "duration": float(duration),
                "file_size_mb": float(file_size / (1024 * 1024)),
                "num_samples": len(y),
            }
            
            logger.debug(f"    Sample rate: {sr} Hz, Duration: {duration:.2f}s, Size: {file_size/(1024*1024):.2f} MB")
            
            # Quality Layer 1: Signal Quality Metrics
            logger.debug(f"    Computing signal quality metrics...")
            
            # RMS Energy (overall loudness)
            rms = librosa.feature.rms(y=y)[0]
            metrics["rms_mean"] = float(np.mean(rms))
            metrics["rms_std"] = float(np.std(rms))
            
            # Zero Crossing Rate (indicates speech vs noise)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            metrics["zcr_mean"] = float(np.mean(zcr))
            metrics["zcr_std"] = float(np.std(zcr))
            
            # Spectral Centroid (brightness of sound)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            metrics["spectral_centroid_mean"] = float(np.mean(spectral_centroids))
            
            # Quality Layer 2: Noise Assessment
            logger.debug(f"    Assessing noise levels...")
            
            # Estimate noise floor (using quiet segments)
            energy_threshold = np.percentile(rms, 10)  # Bottom 10% as noise estimate
            speech_energy = rms[rms > energy_threshold * 2]
            
            if len(speech_energy) > 0:
                snr_estimate = np.mean(speech_energy) / (energy_threshold + 1e-10)
                metrics["snr_estimate"] = float(snr_estimate)
            else:
                metrics["snr_estimate"] = 0.0
            
            # Quality Layer 3: Speech Characteristics
            logger.debug(f"    Analyzing speech characteristics...")
            
            # Spectral Rolloff (frequency content)
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            metrics["spectral_rolloff_mean"] = float(np.mean(rolloff))
            
            # Bandwidth (spectral spread)
            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            metrics["spectral_bandwidth_mean"] = float(np.mean(bandwidth))
            
            # Quality Layer 4: Clarity Metrics
            logger.debug(f"    Computing clarity metrics...")
            
            # Harmonic-to-noise ratio (rough estimate)
            try:
                y_harmonic, y_percussive = librosa.effects.hpss(y)
                harmonic_energy = np.sum(y_harmonic ** 2)
                percussive_energy = np.sum(y_percussive ** 2)
                hnr = harmonic_energy / (percussive_energy + 1e-10)
                metrics["harmonic_noise_ratio"] = float(hnr)
            except:
                metrics["harmonic_noise_ratio"] = 1.0
            
            # Quality Layer 5: Duration and Completeness
            logger.debug(f"    Checking duration and completeness...")
            
            # Check for silence at start/end
            frame_length = 2048
            hop_length = 512
            frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
            frame_energy = np.sum(frames ** 2, axis=0)
            
            # Find speech segments
            energy_threshold = np.percentile(frame_energy, 20)
            speech_frames = frame_energy > energy_threshold
            
            if np.any(speech_frames):
                speech_start = np.argmax(speech_frames) * hop_length / sr
                speech_end = (len(speech_frames) - np.argmax(speech_frames[::-1])) * hop_length / sr
                effective_duration = speech_end - speech_start
                metrics["effective_duration"] = float(effective_duration)
                metrics["silence_ratio"] = float(1.0 - (effective_duration / duration))
            else:
                metrics["effective_duration"] = 0.0
                metrics["silence_ratio"] = 1.0
            
            # Quality Layer 6: Overall Quality Score
            logger.debug(f"    Computing overall quality score...")
            
            # Calculate composite quality score (0-100)
            quality_score = 0.0
            
            # Duration score (0-25 points)
            if duration >= 10:
                quality_score += 25
            elif duration >= 5:
                quality_score += 20
            elif duration >= 3:
                quality_score += 15
            else:
                quality_score += 5
            
            # SNR score (0-25 points)
            if metrics["snr_estimate"] > 20:
                quality_score += 25
            elif metrics["snr_estimate"] > 10:
                quality_score += 20
            elif metrics["snr_estimate"] > 5:
                quality_score += 15
            else:
                quality_score += 5
            
            # Clarity score (0-25 points)
            if metrics["harmonic_noise_ratio"] > 2.0:
                quality_score += 25
            elif metrics["harmonic_noise_ratio"] > 1.0:
                quality_score += 20
            else:
                quality_score += 10
            
            # Completeness score (0-25 points)
            if metrics["silence_ratio"] < 0.1:
                quality_score += 25
            elif metrics["silence_ratio"] < 0.3:
                quality_score += 20
            elif metrics["silence_ratio"] < 0.5:
                quality_score += 15
            else:
                quality_score += 5
            
            metrics["quality_score"] = float(quality_score)
            
            logger.info(f"    ✅ Quality Score: {quality_score:.1f}/100")
            logger.debug(f"      - Duration: {duration:.2f}s ({'✅' if duration >= 10 else '⚠️'})")
            logger.debug(f"      - SNR Estimate: {metrics['snr_estimate']:.2f} ({'✅' if metrics['snr_estimate'] > 10 else '⚠️'})")
            logger.debug(f"      - Harmonic/Noise: {metrics['harmonic_noise_ratio']:.2f} ({'✅' if metrics['harmonic_noise_ratio'] > 1.0 else '⚠️'})")
            logger.debug(f"      - Silence Ratio: {metrics['silence_ratio']:.2f} ({'✅' if metrics['silence_ratio'] < 0.3 else '⚠️'})")
            
            return metrics
            
        except Exception as e:
            logger.error(f"    ❌ Error analyzing {audio_path}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def analyze_all_audio(self):
        """Analyze all audio files in directory."""
        logger.info("=" * 100)
        logger.info("AUDIO QUALITY ANALYSIS")
        logger.info("=" * 100)
        logger.info("")
        
        if not self.audio_dir.exists():
            logger.error(f"❌ Audio directory not found: {self.audio_dir}")
            return []
        
        # Find all audio files
        audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(list(self.audio_dir.glob(f"*{ext}")))
            audio_files.extend(list(self.audio_dir.glob(f"*{ext.upper()}")))
        
        logger.info(f"Found {len(audio_files)} audio files to analyze")
        logger.info("")
        
        # Analyze each file
        for i, audio_file in enumerate(audio_files, 1):
            logger.info(f"[{i}/{len(audio_files)}] Analyzing audio file...")
            metrics = self.analyze_audio_file(audio_file)
            if metrics:
                self.results.append(metrics)
            logger.info("")
        
        # Sort by quality score
        self.results.sort(key=lambda x: x['quality_score'], reverse=True)
        
        logger.info("=" * 100)
        logger.info("QUALITY ANALYSIS SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Total files analyzed: {len(self.results)}")
        logger.info("")
        
        # Show top files
        logger.info("Top 10 Highest Quality Files:")
        for i, result in enumerate(self.results[:10], 1):
            logger.info(f"  {i:2d}. {result['filename'][:60]:60s} | Score: {result['quality_score']:5.1f} | Duration: {result['duration']:6.2f}s | SNR: {result['snr_estimate']:5.2f}")
        
        return self.results
    
    def filter_high_quality(self, min_score=60, min_duration=5.0, max_silence=0.4):
        """Filter audio files by quality criteria."""
        logger.info("")
        logger.info("=" * 100)
        logger.info("FILTERING HIGH QUALITY AUDIO")
        logger.info("=" * 100)
        logger.info(f"Criteria:")
        logger.info(f"  - Minimum Quality Score: {min_score}")
        logger.info(f"  - Minimum Duration: {min_duration}s")
        logger.info(f"  - Maximum Silence Ratio: {max_silence}")
        logger.info("")
        
        filtered = []
        for result in self.results:
            if (result['quality_score'] >= min_score and
                result['duration'] >= min_duration and
                result['silence_ratio'] <= max_silence):
                filtered.append(result)
        
        logger.info(f"Files passing filter: {len(filtered)}/{len(self.results)}")
        logger.info("")
        
        if filtered:
            logger.info("Filtered High Quality Files:")
            for i, result in enumerate(filtered, 1):
                logger.info(f"  {i:2d}. {result['filename'][:60]:60s} | Score: {result['quality_score']:5.1f} | Duration: {result['duration']:6.2f}s")
        
        return filtered
    
    def save_results(self, output_file="audio_quality_results.json"):
        """Save analysis results to JSON."""
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to: {output_path}")

