"""
Quick installation check script.
Run this anytime to verify everything is set up correctly.
"""

import sys
import os

def check_installation():
    """Check if everything is installed correctly."""
    print("=" * 80)
    print("VOICE CLONING INSTALLATION CHECK")
    print("=" * 80)
    print()
    
    # Check Python version
    print("1. Checking Python version...")
    version = sys.version_info
    print(f"   Python: {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and 9 <= version.minor <= 11:
        print("   ✅ Python version is compatible")
    else:
        print(f"   ⚠️  Python version should be 3.9-3.11 (you have {version.major}.{version.minor})")
    print()
    
    # Check virtual environment
    print("2. Checking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Virtual environment is active")
        print(f"   Python path: {sys.executable}")
    else:
        print("   ⚠️  Virtual environment may not be active")
        print("   Run: source venv/bin/activate")
    print()
    
    # Check required packages
    print("3. Checking required packages...")
    packages = {
        "TTS": "TTS",
        "librosa": "librosa",
        "soundfile": "soundfile",
        "transformers": "transformers",
        "torch": "torch",
        "torchaudio": "torchaudio",
        "numpy": "numpy",
        "scipy": "scipy"
    }
    
    all_ok = True
    for name, module in packages.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"   ✅ {name}: {version}")
        except ImportError:
            print(f"   ❌ {name}: NOT INSTALLED")
            all_ok = False
    
    print()
    
    # Test TTS import
    print("4. Testing TTS import...")
    try:
        from TTS.api import TTS
        print("   ✅ TTS can be imported")
        
        # Try to initialize (this may take a moment)
        print("   Testing TTS initialization...")
        tts = TTS()
        print("   ✅ TTS initialized successfully")
    except Exception as e:
        print(f"   ❌ TTS import/initialization failed: {e}")
        all_ok = False
    
    print()
    
    # Check disk space
    print("5. Checking disk space...")
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024**3)
    print(f"   Available: {free_gb:.2f} GB")
    if free_gb >= 5:
        print("   ✅ Sufficient disk space")
    else:
        print("   ⚠️  Low disk space - models can be 1-5GB+")
    
    print()
    print("=" * 80)
    if all_ok:
        print("✅ ALL CHECKS PASSED - Everything is ready!")
        print()
        print("Next steps:")
        print("  1. Update SPEAKER_AUDIO path in example_voice_cloning.py")
        print("  2. Run: python3 example_voice_cloning.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("Run: python3 setup_and_verify.py")
    print("=" * 80)
    
    return all_ok

if __name__ == "__main__":
    success = check_installation()
    sys.exit(0 if success else 1)

