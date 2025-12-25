#!/usr/bin/env python3
"""
Audio Refinement Processor
Multi-stage audio processing and refinement for optimal voice cloning quality.
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

class AudioRefinementProcessor:
    """Multi-stage audio refinement for voice cloning."""
    
    def __init__(self, input_dir="audio_samples", output_dir="refined_audio"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def stage_1_normalize_audio(self, input_path, output_path):
        """Stage 1: Normalize audio levels."""
        logger.info("  → Stage 1: Normalizing audio levels...")
        
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None, mono=True)
            
            # Normalize to -3dB peak (safe headroom)
            peak = np.max(np.abs(y))
            if peak > 0:
                target_peak = 10 ** (-3 / 20)  # -3dB
                y_normalized = y * (target_peak / peak)
            else:
                y_normalized = y
            
            # Save normalized audio
            sf.write(str(output_path), y_normalized, sr)
            
            logger.info(f"    ✅ Normalized: peak {20*np.log10(peak+1e-10):.2f}dB -> -3dB")
            return True
            
        except Exception as e:
            logger.error(f"    ❌ Normalization failed: {e}")
            return False
    
    def stage_2_remove_silence(self, input_path, output_path):
        """Stage 2: Remove leading/trailing silence."""
        logger.info("  → Stage 2: Removing leading/trailing silence...")
        
        try:
            import librosa
            import soundfile as sf
            
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None, mono=True)
            original_duration = len(y) / sr
            
            # Trim silence
            y_trimmed, _ = librosa.effects.trim(
                y,
                top_db=20,  # Remove sounds quieter than 20dB below peak
                frame_length=2048,
                hop_length=512
            )
            
            trimmed_duration = len(y_trimmed) / sr
            removed = original_duration - trimmed_duration
            
            # Save trimmed audio
            sf.write(str(output_path), y_trimmed, sr)
            
            logger.info(f"    ✅ Trimmed: {original_duration:.2f}s -> {trimmed_duration:.2f}s (removed {removed:.2f}s)")
            return True
            
        except Exception as e:
            logger.error(f"    ❌ Silence removal failed: {e}")
            return False
    
    def stage_3_noise_reduction(self, input_path, output_path):
        """Stage 3: Reduce background noise."""
        logger.info("  → Stage 3: Reducing background noise...")
        
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            from scipy import signal
            
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None, mono=True)
            
            # Simple noise reduction using spectral gating
            # Compute spectrogram
            stft = librosa.stft(y, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor (using first 0.5 seconds)
            noise_frames = int(0.5 * sr / 512)
            if noise_frames > 0 and noise_frames < magnitude.shape[1]:
                noise_floor = np.median(magnitude[:, :noise_frames], axis=1, keepdims=True)
            else:
                noise_floor = np.percentile(magnitude, 10, axis=1, keepdims=True)
            
            # Apply spectral gating (attenuate below noise floor)
            threshold = noise_floor * 2.0  # 6dB above noise floor
            mask = magnitude > threshold
            magnitude_denoised = magnitude * mask + magnitude * 0.1 * (~mask)
            
            # Reconstruct audio
            stft_denoised = magnitude_denoised * np.exp(1j * phase)
            y_denoised = librosa.istft(stft_denoised, hop_length=512)
            
            # Save denoised audio
            sf.write(str(output_path), y_denoised, sr)
            
            logger.info(f"    ✅ Noise reduction applied")
            return True
            
        except Exception as e:
            logger.error(f"    ❌ Noise reduction failed: {e}")
            # If noise reduction fails, just copy the file
            import shutil
            shutil.copy(input_path, output_path)
            return False
    
    def stage_4_resample_optimal(self, input_path, output_path, target_sr=22050):
        """Stage 4: Resample to optimal sample rate for TTS."""
        logger.info(f"  → Stage 4: Resampling to {target_sr} Hz...")
        
        try:
            import librosa
            import soundfile as sf
            
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None, mono=True)
            
            if sr != target_sr:
                # Resample
                y_resampled = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
                logger.info(f"    ✅ Resampled: {sr} Hz -> {target_sr} Hz")
            else:
                y_resampled = y
                logger.info(f"    ✅ Already at {target_sr} Hz")
            
            # Save resampled audio
            sf.write(str(output_path), y_resampled, target_sr)
            
            return True
            
        except Exception as e:
            logger.error(f"    ❌ Resampling failed: {e}")
            return False
    
    def stage_5_extract_best_segment(self, input_path, output_path, target_duration=15.0):
        """Stage 5: Extract best quality segment."""
        logger.info(f"  → Stage 5: Extracting best {target_duration}s segment...")
        
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None, mono=True)
            duration = len(y) / sr
            
            if duration <= target_duration:
                # Audio is already short enough
                logger.info(f"    ✅ Audio duration ({duration:.2f}s) is already optimal")
                import shutil
                shutil.copy(input_path, output_path)
                return True
            
            # Find best segment using energy analysis
            frame_length = 2048
            hop_length = 512
            frames = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)
            frame_energy = np.sum(frames ** 2, axis=0)
            
            # Find window with highest average energy
            target_frames = int(target_duration * sr / hop_length)
            if target_frames > len(frame_energy):
                target_frames = len(frame_energy)
            
            # Sliding window to find best segment
            max_energy = 0
            best_start = 0
            
            for i in range(len(frame_energy) - target_frames + 1):
                window_energy = np.mean(frame_energy[i:i+target_frames])
                if window_energy > max_energy:
                    max_energy = window_energy
                    best_start = i
            
            # Extract segment
            start_sample = best_start * hop_length
            end_sample = start_sample + int(target_duration * sr)
            
            if end_sample > len(y):
                end_sample = len(y)
                start_sample = end_sample - int(target_duration * sr)
            
            y_segment = y[start_sample:end_sample]
            
            # Save segment
            sf.write(str(output_path), y_segment, sr)
            
            logger.info(f"    ✅ Extracted: {start_sample/sr:.2f}s - {end_sample/sr:.2f}s (best quality segment)")
            return True
            
        except Exception as e:
            logger.error(f"    ❌ Segment extraction failed: {e}")
            return False
    
    def process_audio_file(self, input_path, output_name=None):
        """Process a single audio file through all refinement stages."""
        input_path = Path(input_path)
        
        logger.info("")
        logger.info("=" * 100)
        logger.info(f"PROCESSING: {input_path.name}")
        logger.info("=" * 100)
        
        if output_name is None:
            output_name = f"refined_{input_path.stem}.wav"
        
        # Stage outputs
        stage1_path = self.output_dir / f"stage1_norm_{input_path.stem}.wav"
        stage2_path = self.output_dir / f"stage2_trimmed_{input_path.stem}.wav"
        stage3_path = self.output_dir / f"stage3_denoised_{input_path.stem}.wav"
        stage4_path = self.output_dir / f"stage4_resampled_{input_path.stem}.wav"
        final_path = self.output_dir / output_name
        
        start_time = time.time()
        
        # Run all stages
        success = True
        success &= self.stage_1_normalize_audio(input_path, stage1_path)
        success &= self.stage_2_remove_silence(stage1_path, stage2_path)
        success &= self.stage_3_noise_reduction(stage2_path, stage3_path)
        success &= self.stage_4_resample_optimal(stage3_path, stage4_path)
        success &= self.stage_5_extract_best_segment(stage4_path, final_path)
        
        processing_time = time.time() - start_time
        
        # Cleanup intermediate files
        for stage_file in [stage1_path, stage2_path, stage3_path, stage4_path]:
            if stage_file.exists() and stage_file != final_path:
                stage_file.unlink()
        
        if success and final_path.exists():
            # Analyze final output
            import librosa
            y_final, sr_final = librosa.load(str(final_path), sr=None)
            final_duration = len(y_final) / sr_final
            final_size = final_path.stat().st_size / (1024 * 1024)
            
            logger.info("")
            logger.info(f"✅ Processing complete in {processing_time:.2f} seconds")
            logger.info(f"   Final file: {final_path.name}")
            logger.info(f"   Duration: {final_duration:.2f}s")
            logger.info(f"   Sample Rate: {sr_final} Hz")
            logger.info(f"   File Size: {final_size:.2f} MB")
            
            return {
                "input": str(input_path),
                "output": str(final_path),
                "duration": final_duration,
                "sample_rate": sr_final,
                "file_size_mb": final_size,
                "processing_time": processing_time,
                "success": True
            }
        else:
            logger.error(f"❌ Processing failed")
            return {"success": False}
    
    def process_high_quality_files(self, quality_results, top_n=5):
        """Process top N highest quality files."""
        logger.info("=" * 100)
        logger.info("REFINEMENT PROCESSING")
        logger.info("=" * 100)
        logger.info(f"Processing top {top_n} highest quality files...")
        logger.info("")
        
        processed = []
        for i, result in enumerate(quality_results[:top_n], 1):
            logger.info(f"[{i}/{top_n}] Processing: {result['filename']}")
            result_data = self.process_audio_file(result['file'], f"refined_top{i}_{Path(result['file']).stem}.wav")
            if result_data.get('success'):
                processed.append(result_data)
            logger.info("")
        
        logger.info("=" * 100)
        logger.info("REFINEMENT SUMMARY")
        logger.info("=" * 100)
        logger.info(f"Successfully processed: {len(processed)}/{top_n} files")
        logger.info("")
        logger.info("Refined audio files:")
        for i, result in enumerate(processed, 1):
            logger.info(f"  {i}. {Path(result['output']).name}")
            logger.info(f"     Duration: {result['duration']:.2f}s, Size: {result['file_size_mb']:.2f} MB")
        
        return processed

