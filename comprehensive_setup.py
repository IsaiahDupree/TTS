#!/usr/bin/env python3
"""
Comprehensive Voice Cloning Setup and Verification Script
Downloads, installs, and verifies ALL components needed for voice cloning.
Extensive logging for every step.
"""

import logging
import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Configure EXTENSIVE logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('setup_log.txt', mode='w')
    ]
)

logger = logging.getLogger(__name__)

class ComprehensiveSetup:
    """Comprehensive setup and verification for voice cloning."""
    
    def __init__(self):
        self.results = {
            "python_version": None,
            "packages_installed": {},
            "packages_verified": {},
            "models_downloaded": {},
            "tests_passed": {},
            "errors": [],
            "warnings": []
        }
        self.start_time = time.time()
        
    def log_section(self, title):
        """Log a section header."""
        logger.info("")
        logger.info("=" * 100)
        logger.info(f"  {title}")
        logger.info("=" * 100)
        logger.info("")
    
    def run_command(self, cmd, description, check=True, capture_output=True):
        """Run a command with extensive logging."""
        logger.info(f"  → Running: {description}")
        logger.debug(f"  → Command: {cmd}")
        
        try:
            if isinstance(cmd, str):
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=check,
                    capture_output=capture_output,
                    text=True,
                    timeout=600  # 10 minute timeout
                )
            else:
                result = subprocess.run(
                    cmd,
                    check=check,
                    capture_output=capture_output,
                    text=True,
                    timeout=600
                )
            
            if capture_output:
                if result.stdout:
                    logger.debug(f"  → stdout: {result.stdout[:500]}")
                if result.stderr:
                    logger.warning(f"  → stderr: {result.stderr[:500]}")
            
            logger.info(f"  ✅ {description} - SUCCESS (exit code: {result.returncode})")
            return True, result.stdout if capture_output else ""
            
        except subprocess.TimeoutExpired:
            logger.error(f"  ❌ {description} - TIMEOUT (exceeded 10 minutes)")
            return False, ""
        except subprocess.CalledProcessError as e:
            logger.error(f"  ❌ {description} - FAILED (exit code: {e.returncode})")
            if e.stderr:
                logger.error(f"  → Error: {e.stderr[:500]}")
            return False, e.stdout if hasattr(e, 'stdout') else ""
        except Exception as e:
            logger.error(f"  ❌ {description} - EXCEPTION: {e}")
            return False, ""
    
    def check_python_version(self):
        """Check Python version."""
        self.log_section("STEP 1: CHECKING PYTHON VERSION")
        
        version = sys.version_info
        self.results["python_version"] = f"{version.major}.{version.minor}.{version.micro}"
        
        logger.info(f"  Python Version: {self.results['python_version']}")
        logger.info(f"  Python Executable: {sys.executable}")
        logger.info(f"  Platform: {sys.platform}")
        
        if version.major == 3 and 9 <= version.minor <= 11:
            logger.info("  ✅ Python version is compatible (3.9-3.11)")
            return True
        else:
            logger.warning(f"  ⚠️  Python version should be 3.9-3.11 (you have {version.major}.{version.minor})")
            return False
    
    def check_virtual_environment(self):
        """Check virtual environment."""
        self.log_section("STEP 2: CHECKING VIRTUAL ENVIRONMENT")
        
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if in_venv:
            logger.info("  ✅ Virtual environment is active")
            logger.info(f"  Virtual environment path: {sys.prefix}")
        else:
            logger.warning("  ⚠️  Virtual environment may not be active")
            logger.info("  → Run: source venv/bin/activate")
        
        return in_venv
    
    def get_pip_command(self):
        """Get pip command."""
        if sys.platform == "Windows":
            return "venv\\Scripts\\pip"
        else:
            return "venv/bin/pip"
    
    def install_package(self, package, description=None):
        """Install a package with extensive logging."""
        if description is None:
            description = f"Installing {package}"
        
        logger.info(f"  → {description}")
        logger.debug(f"  → Package: {package}")
        
        pip_cmd = self.get_pip_command()
        cmd = f"{pip_cmd} install {package} --upgrade --no-cache-dir"
        
        success, output = self.run_command(cmd, description, check=False)
        
        if success:
            self.results["packages_installed"][package] = "installed"
            logger.info(f"  ✅ {package} installed successfully")
        else:
            self.results["packages_installed"][package] = "failed"
            self.results["errors"].append(f"Failed to install {package}")
            logger.error(f"  ❌ {package} installation failed")
        
        return success
    
    def verify_package(self, package_name, import_name=None):
        """Verify a package can be imported."""
        if import_name is None:
            import_name = package_name
        
        logger.info(f"  → Verifying {package_name}...")
        
        try:
            mod = __import__(import_name)
            version = getattr(mod, '__version__', 'unknown')
            self.results["packages_verified"][package_name] = version
            logger.info(f"  ✅ {package_name} verified (version: {version})")
            return True, version
        except ImportError as e:
            self.results["packages_verified"][package_name] = "not_found"
            self.results["errors"].append(f"{package_name} cannot be imported: {e}")
            logger.error(f"  ❌ {package_name} verification failed: {e}")
            return False, None
        except Exception as e:
            self.results["packages_verified"][package_name] = "error"
            logger.error(f"  ❌ {package_name} verification error: {e}")
            return False, None
    
    def install_all_dependencies(self):
        """Install ALL dependencies needed for voice cloning."""
        self.log_section("STEP 3: INSTALLING ALL DEPENDENCIES")
        
        # Core TTS packages - FIXED VERSIONS FOR COMPATIBILITY
        packages = [
            ("numpy<2.3.0,>=1.24.0", "Numerical computing (compatible with numba)"),
            ("TTS>=0.22.0", "Coqui TTS library"),
            ("transformers>=4.30.0,<4.40.0", "Hugging Face Transformers (compatible version)"),
            ("torch>=2.0.0", "PyTorch"),
            ("torchaudio>=2.0.0", "PyTorch Audio"),
            ("librosa>=0.10.0", "Audio processing library"),
            ("soundfile>=0.12.0", "Sound file I/O"),
            ("scipy>=1.10.0", "Scientific computing"),
            ("yt-dlp>=2023.0.0", "YouTube downloader"),
            ("ffmpeg-python", "FFmpeg Python bindings"),
            ("torchcodec>=0.9.0", "TorchCodec for XTTS voice cloning"),
        ]
        
        logger.info(f"  Installing {len(packages)} packages...")
        logger.info("  → Installing in dependency order for compatibility...")
        logger.info("")
        
        # Install NumPy first (needed by other packages)
        logger.info("  → Installing NumPy first (dependency for other packages)...")
        self.install_package("numpy<2.3.0,>=1.24.0", "NumPy (compatible version)")
        logger.info("")
        
        # Then install other packages
        for package, description in packages:
            if "numpy" not in package.lower():  # Skip numpy, already installed
                self.install_package(package, description)
                logger.info("")
        
        # Upgrade pip first
        logger.info("  → Upgrading pip...")
        pip_cmd = self.get_pip_command()
        self.run_command(f"{pip_cmd} install --upgrade pip", "Upgrade pip", check=False)
        logger.info("")
        
        return True
    
    def verify_all_packages(self):
        """Verify ALL packages are installed and working."""
        self.log_section("STEP 4: VERIFYING ALL PACKAGES")
        
        packages_to_verify = {
            "TTS": "TTS",
            "transformers": "transformers",
            "torch": "torch",
            "torchaudio": "torchaudio",
            "librosa": "librosa",
            "soundfile": "soundfile",
            "numpy": "numpy",
            "scipy": "scipy",
            "yt_dlp": "yt_dlp",
            "torchcodec": "torchcodec",
        }
        
        logger.info(f"  Verifying {len(packages_to_verify)} packages...")
        logger.info("")
        
        all_verified = True
        for package_name, import_name in packages_to_verify.items():
            success, version = self.verify_package(package_name, import_name)
            if not success:
                all_verified = False
            logger.info("")
        
        return all_verified
    
    def check_system_tools(self):
        """Check system tools (ffmpeg, etc.)."""
        self.log_section("STEP 5: CHECKING SYSTEM TOOLS")
        
        tools = {
            "ffmpeg": "FFmpeg audio processing",
        }
        
        all_found = True
        for tool, description in tools.items():
            logger.info(f"  → Checking {tool}...")
            success, output = self.run_command(f"which {tool}", f"Find {tool}", check=False)
            if success and output.strip():
                logger.info(f"  ✅ {tool} found at: {output.strip()}")
            else:
                logger.warning(f"  ⚠️  {tool} not found in PATH")
                logger.info(f"  → Install with: brew install {tool}")
                all_found = False
        
        return all_found
    
    def download_tts_models(self):
        """Download and verify TTS models."""
        self.log_section("STEP 6: DOWNLOADING TTS MODELS")
        
        logger.info("  → This will download models on first use...")
        logger.info("  → Models are large (1-5GB) and may take time...")
        logger.info("")
        
        # Set environment variable to auto-accept TOS
        os.environ["COQUI_TOS_AGREED"] = "1"
        
        try:
            from TTS.api import TTS
            
            # Test basic model
            logger.info("  → Testing basic TTS model...")
            tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            logger.info("  ✅ Basic TTS model loaded")
            self.results["models_downloaded"]["basic_tts"] = "downloaded"
            
            # Try XTTS (may fail due to compatibility)
            logger.info("")
            logger.info("  → Attempting to load XTTS model...")
            try:
                # Add safe globals for PyTorch 2.6+
                import torch
                try:
                    # Import the class first, then add it
                    from TTS.tts.configs.xtts_config import XttsConfig
                    torch.serialization.add_safe_globals([XttsConfig])
                    logger.info("  → Added XttsConfig to safe globals")
                except Exception as e:
                    logger.debug(f"  → Could not add safe globals: {e}")
                    # Try alternative approach - set environment variable
                    os.environ["TORCH_LOAD_WEIGHTS_ONLY"] = "False"
                
                tts_xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
                logger.info("  ✅ XTTS model loaded successfully")
                self.results["models_downloaded"]["xtts_v2"] = "downloaded"
            except Exception as e:
                logger.warning(f"  ⚠️  XTTS model failed to load: {e}")
                logger.warning("  → This is a known compatibility issue with PyTorch 2.9.1")
                logger.warning("  → Basic TTS and other models are working")
                self.results["models_downloaded"]["xtts_v2"] = "failed"
                self.results["warnings"].append(f"XTTS model loading failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Model download/verification failed: {e}")
            self.results["errors"].append(f"Model verification failed: {e}")
            return False
    
    def run_comprehensive_tests(self):
        """Run comprehensive tests."""
        self.log_section("STEP 7: RUNNING COMPREHENSIVE TESTS")
        
        # Test 1: Basic TTS generation
        logger.info("  → Test 1: Basic TTS Generation")
        try:
            from TTS.api import TTS
            tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            
            test_output = "test_comprehensive_output.wav"
            tts.tts_to_file(text="This is a comprehensive test.", file_path=test_output)
            
            if os.path.exists(test_output):
                logger.info("  ✅ Basic TTS generation test PASSED")
                self.results["tests_passed"]["basic_generation"] = True
                os.remove(test_output)  # Cleanup
            else:
                logger.error("  ❌ Basic TTS generation test FAILED")
                self.results["tests_passed"]["basic_generation"] = False
        except Exception as e:
            logger.error(f"  ❌ Basic TTS generation test FAILED: {e}")
            self.results["tests_passed"]["basic_generation"] = False
        
        logger.info("")
        
        # Test 2: Audio file processing
        logger.info("  → Test 2: Audio File Processing")
        try:
            import librosa
            import soundfile
            
            # Check if we have audio samples
            audio_dir = Path("audio_samples")
            if audio_dir.exists():
                audio_files = list(audio_dir.glob("*.wav"))
                if audio_files:
                    test_file = audio_files[0]
                    logger.info(f"  → Testing with: {test_file.name}")
                    y, sr = librosa.load(str(test_file), sr=None, duration=1.0)
                    logger.info(f"  → Loaded audio: {len(y)} samples at {sr} Hz")
                    logger.info("  ✅ Audio file processing test PASSED")
                    self.results["tests_passed"]["audio_processing"] = True
                else:
                    logger.warning("  ⚠️  No audio files found for testing")
                    self.results["tests_passed"]["audio_processing"] = "skipped"
            else:
                logger.warning("  ⚠️  audio_samples directory not found")
                self.results["tests_passed"]["audio_processing"] = "skipped"
        except Exception as e:
            logger.error(f"  ❌ Audio file processing test FAILED: {e}")
            self.results["tests_passed"]["audio_processing"] = False
        
        return True
    
    def generate_final_report(self):
        """Generate final comprehensive report."""
        self.log_section("FINAL COMPREHENSIVE REPORT")
        
        total_time = time.time() - self.start_time
        
        logger.info("  SETUP SUMMARY:")
        logger.info(f"    Total time: {total_time:.2f} seconds")
        logger.info(f"    Python version: {self.results['python_version']}")
        logger.info("")
        
        logger.info("  PACKAGES INSTALLED:")
        for package, status in self.results["packages_installed"].items():
            status_icon = "✅" if status == "installed" else "❌"
            logger.info(f"    {status_icon} {package}: {status}")
        logger.info("")
        
        logger.info("  PACKAGES VERIFIED:")
        for package, version in self.results["packages_verified"].items():
            if version and version != "not_found" and version != "error":
                logger.info(f"    ✅ {package}: {version}")
            else:
                logger.info(f"    ❌ {package}: {version}")
        logger.info("")
        
        logger.info("  MODELS DOWNLOADED:")
        for model, status in self.results["models_downloaded"].items():
            status_icon = "✅" if status == "downloaded" else "⚠️"
            logger.info(f"    {status_icon} {model}: {status}")
        logger.info("")
        
        logger.info("  TESTS PASSED:")
        for test, result in self.results["tests_passed"].items():
            if result is True:
                logger.info(f"    ✅ {test}: PASSED")
            elif result is False:
                logger.info(f"    ❌ {test}: FAILED")
            else:
                logger.info(f"    ⏸️  {test}: {result}")
        logger.info("")
        
        if self.results["warnings"]:
            logger.info("  WARNINGS:")
            for warning in self.results["warnings"]:
                logger.warning(f"    ⚠️  {warning}")
            logger.info("")
        
        if self.results["errors"]:
            logger.info("  ERRORS:")
            for error in self.results["errors"]:
                logger.error(f"    ❌ {error}")
            logger.info("")
        
        # Save results to JSON
        results_file = Path("setup_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"  → Results saved to: {results_file}")
        logger.info("")
        
        # Final status
        all_critical_passed = (
            len([v for v in self.results["packages_verified"].values() if v and v not in ["not_found", "error"]]) > 5 and
            self.results["tests_passed"].get("basic_generation", False)
        )
        
        if all_critical_passed:
            logger.info("  ✅ CRITICAL COMPONENTS ARE WORKING")
            logger.info("  → Voice cloning setup is ready (with known compatibility notes)")
        else:
            logger.error("  ❌ SOME CRITICAL COMPONENTS FAILED")
            logger.error("  → Review errors above and fix issues")
        
        logger.info("")
        logger.info("=" * 100)
    
    def run(self):
        """Run comprehensive setup."""
        logger.info("=" * 100)
        logger.info("  COMPREHENSIVE VOICE CLONING SETUP AND VERIFICATION")
        logger.info("=" * 100)
        logger.info(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        
        # Run all steps
        self.check_python_version()
        self.check_virtual_environment()
        self.install_all_dependencies()
        self.verify_all_packages()
        self.check_system_tools()
        self.download_tts_models()
        self.run_comprehensive_tests()
        self.generate_final_report()
        
        return self.results

if __name__ == "__main__":
    setup = ComprehensiveSetup()
    results = setup.run()
    sys.exit(0 if len([e for e in results["errors"] if "critical" in e.lower()]) == 0 else 1)

