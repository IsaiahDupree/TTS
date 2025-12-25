"""
Comprehensive setup and verification script for voice cloning project.
This script checks all requirements and installs missing components.
"""

import logging
import os
import sys
import subprocess
import platform
from pathlib import Path

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def run_command(cmd, check=True, capture_output=False):
    """Run a shell command and return the result."""
    try:
        logger.debug(f"Running command: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        if capture_output:
            return result.stdout.strip(), result.returncode
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}")
        if capture_output:
            return e.stdout.strip() if hasattr(e, 'stdout') else "", e.returncode
        return False


def check_python_version():
    """Check if Python 3.11 is available."""
    logger.info("=" * 80)
    logger.info("CHECKING PYTHON VERSION")
    logger.info("=" * 80)
    
    # Check system Python
    python_version = sys.version_info
    logger.info(f"System Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check for Python 3.11
    python311_paths = [
        "/opt/homebrew/bin/python3.11",
        "/usr/local/bin/python3.11",
        "python3.11"
    ]
    
    python311_found = None
    for path in python311_paths:
        output, code = run_command(f"which {path}", check=False, capture_output=True)
        if code == 0 and output:
            python311_found = output
            logger.info(f"✅ Python 3.11 found at: {output}")
            break
    
    if not python311_found:
        # Try direct path
        if os.path.exists("/opt/homebrew/bin/python3.11"):
            python311_found = "/opt/homebrew/bin/python3.11"
            logger.info(f"✅ Python 3.11 found at: {python311_found}")
        else:
            logger.error("❌ Python 3.11 not found")
            logger.error("Please install Python 3.11: brew install python@3.11")
            return None
    
    # Verify Python 3.11 version
    output, code = run_command(f"{python311_found} --version", check=False, capture_output=True)
    if code == 0:
        logger.info(f"Python 3.11 version: {output}")
    
    return python311_found


def setup_virtual_environment(python311_path):
    """Set up virtual environment with Python 3.11."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("SETTING UP VIRTUAL ENVIRONMENT")
    logger.info("=" * 80)
    
    venv_path = Path(__file__).parent / "venv"
    
    if venv_path.exists():
        logger.info(f"Virtual environment exists at: {venv_path}")
        logger.info("Removing old virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
        logger.info("✅ Old virtual environment removed")
    
    logger.info(f"Creating virtual environment with Python 3.11...")
    logger.info(f"Using Python: {python311_path}")
    
    success = run_command(f"{python311_path} -m venv venv", check=False)
    if success:
        logger.info(f"✅ Virtual environment created at: {venv_path}")
        return True
    else:
        logger.error("❌ Failed to create virtual environment")
        return False


def get_pip_command():
    """Get the pip command for the virtual environment."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"


def install_dependencies():
    """Install all required dependencies."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("INSTALLING DEPENDENCIES")
    logger.info("=" * 80)
    
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    logger.info("Upgrading pip...")
    run_command(f"{pip_cmd} install --upgrade pip", check=False)
    logger.info("✅ pip upgraded")
    
    # Install dependencies from requirements.txt
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        logger.info(f"Installing dependencies from {requirements_file}...")
        success = run_command(f"{pip_cmd} install -r requirements.txt", check=False)
        if success:
            logger.info("✅ Dependencies installed from requirements.txt")
        else:
            logger.warning("⚠️  Some dependencies may have failed to install")
    else:
        logger.warning(f"⚠️  requirements.txt not found, installing core packages...")
        packages = ["TTS", "librosa", "soundfile", "transformers", "torch", "torchaudio"]
        for package in packages:
            logger.info(f"Installing {package}...")
            run_command(f"{pip_cmd} install {package}", check=False)
    
    return True


def verify_installation():
    """Verify that all required packages are installed."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("VERIFYING INSTALLATION")
    logger.info("=" * 80)
    
    pip_cmd = get_pip_command()
    python_cmd = "venv/bin/python3" if platform.system() != "Windows" else "venv\\Scripts\\python"
    
    required_packages = {
        "TTS": "TTS",
        "librosa": "librosa",
        "soundfile": "soundfile",
        "transformers": "transformers",
        "torch": "torch",
        "torchaudio": "torchaudio",
        "numpy": "numpy",
        "scipy": "scipy"
    }
    
    all_installed = True
    
    for package_name, import_name in required_packages.items():
        logger.info(f"Checking {package_name}...")
        try:
            # Try importing
            output, code = run_command(
                f"{python_cmd} -c 'import {import_name}; print({import_name}.__version__)'",
                check=False,
                capture_output=True
            )
            if code == 0 and output:
                logger.info(f"  ✅ {package_name} installed (version: {output})")
            else:
                logger.error(f"  ❌ {package_name} not properly installed")
                all_installed = False
        except Exception as e:
            logger.error(f"  ❌ {package_name} check failed: {e}")
            all_installed = False
    
    # Special check for TTS
    logger.info("")
    logger.info("Testing TTS import...")
    output, code = run_command(
        f"{python_cmd} -c 'from TTS.api import TTS; print(\"TTS imported successfully\")'",
        check=False,
        capture_output=True
    )
    if code == 0:
        logger.info("  ✅ TTS library can be imported")
    else:
        logger.error("  ❌ TTS library cannot be imported")
        logger.error(f"  Error: {output}")
        all_installed = False
    
    return all_installed


def check_system_resources():
    """Check system resources (disk space, memory, etc.)."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("SYSTEM RESOURCES CHECK")
    logger.info("=" * 80)
    
    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024**3)
    logger.info(f"Available disk space: {free_gb:.2f} GB")
    
    if free_gb < 5:
        logger.warning("⚠️  Low disk space - models can be 1-5GB+")
    else:
        logger.info("✅ Sufficient disk space available")
    
    # Check Python version in venv
    python_cmd = "venv/bin/python3" if platform.system() != "Windows" else "venv\\Scripts\\python"
    if os.path.exists(python_cmd) or os.path.exists("venv/bin/python3"):
        output, code = run_command(
            f"{python_cmd} --version",
            check=False,
            capture_output=True
        )
        if code == 0:
            logger.info(f"Virtual environment Python: {output}")
    
    logger.info("=" * 80)


def main():
    """Main setup and verification function."""
    logger.info("=" * 80)
    logger.info("VOICE CLONING PROJECT - SETUP AND VERIFICATION")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Check Python 3.11
    python311_path = check_python_version()
    if not python311_path:
        logger.error("")
        logger.error("❌ SETUP FAILED: Python 3.11 is required")
        logger.error("Please install Python 3.11: brew install python@3.11")
        sys.exit(1)
    
    # Step 2: Setup virtual environment
    if not setup_virtual_environment(python311_path):
        logger.error("")
        logger.error("❌ SETUP FAILED: Could not create virtual environment")
        sys.exit(1)
    
    # Step 3: Install dependencies
    install_dependencies()
    
    # Step 4: Verify installation
    all_installed = verify_installation()
    
    # Step 5: Check system resources
    check_system_resources()
    
    # Final summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("SETUP SUMMARY")
    logger.info("=" * 80)
    
    if all_installed:
        logger.info("✅ All required packages are installed!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Activate virtual environment: source venv/bin/activate")
        logger.info("  2. Update SPEAKER_AUDIO path in example_voice_cloning.py")
        logger.info("  3. Run: python3 example_voice_cloning.py")
        logger.info("")
        logger.info("=" * 80)
        return 0
    else:
        logger.error("")
        logger.error("⚠️  Some packages may not be installed correctly")
        logger.error("Please check the errors above and try installing manually:")
        logger.error("  source venv/bin/activate")
        logger.error("  pip install -r requirements.txt")
        logger.error("")
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

