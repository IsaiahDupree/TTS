#!/usr/bin/env python3
"""
Download audio from YouTube channel for voice cloning training.
Uses yt-dlp for reliable downloads.
"""

import logging
import os
import sys
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        import yt_dlp
        logger.info("✅ yt-dlp is installed")
        return True
    except ImportError:
        logger.warning("⚠️  yt-dlp not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "--quiet"])
            logger.info("✅ yt-dlp installed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to install yt-dlp: {e}")
            return False

def download_channel_audio(channel_url, output_dir="audio_samples", max_videos=10):
    """
    Download audio from a YouTube channel.
    
    Args:
        channel_url: YouTube channel URL (e.g., https://www.youtube.com/@channelname)
        output_dir: Directory to save audio files
        max_videos: Maximum number of videos to download
    """
    if not check_yt_dlp():
        return False
    
    import yt_dlp
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    logger.info("=" * 80)
    logger.info("DOWNLOADING YOUTUBE CHANNEL AUDIO")
    logger.info("=" * 80)
    logger.info(f"Channel URL: {channel_url}")
    logger.info(f"Output directory: {output_path}")
    logger.info(f"Max videos: {max_videos}")
    logger.info("")
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'extractaudio': True,
        'audioformat': 'wav',
        'audioquality': '0',  # Best quality
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'playlistend': max_videos,  # Limit number of videos
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Extracting channel information...")
            # Extract info without downloading first
            info = ydl.extract_info(channel_url, download=False)
            
            if 'entries' in info:
                logger.info(f"Found {len(info['entries'])} videos in channel")
                logger.info(f"Downloading up to {max_videos} videos...")
            else:
                logger.info("Processing single video/channel...")
            
            # Now download
            ydl.download([channel_url])
            
            logger.info("✅ Download completed!")
            
            # List downloaded files
            audio_files = list(output_path.glob("*.wav"))
            if not audio_files:
                audio_files = list(output_path.glob("*.m4a")) + list(output_path.glob("*.mp3"))
            
            logger.info("")
            logger.info(f"Downloaded {len(audio_files)} audio files:")
            for f in audio_files[:10]:  # Show first 10
                size_mb = f.stat().st_size / (1024 * 1024)
                logger.info(f"  - {f.name} ({size_mb:.2f} MB)")
            
            if len(audio_files) > 10:
                logger.info(f"  ... and {len(audio_files) - 10} more files")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    logger.info("=" * 80)
    logger.info("YOUTUBE CHANNEL AUDIO DOWNLOADER")
    logger.info("=" * 80)
    
    # Get channel URL from user or use default
    if len(sys.argv) > 1:
        channel_url = sys.argv[1]
    else:
        logger.info("Please provide your YouTube channel URL")
        logger.info("Example: https://www.youtube.com/@YourChannelName")
        logger.info("Or: https://www.youtube.com/c/YourChannelName")
        logger.info("Or: https://www.youtube.com/channel/CHANNEL_ID")
        channel_url = input("\nEnter channel URL: ").strip()
    
    if not channel_url:
        logger.error("❌ No channel URL provided")
        sys.exit(1)
    
    # Get max videos (optional)
    max_videos = 10
    if len(sys.argv) > 2:
        try:
            max_videos = int(sys.argv[2])
        except ValueError:
            pass
    
    # Download audio
    success = download_channel_audio(channel_url, max_videos=max_videos)
    
    if success:
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ DOWNLOAD COMPLETE")
        logger.info("=" * 80)
        logger.info("Next steps:")
        logger.info("  1. Review audio files in audio_samples/")
        logger.info("  2. Run generation test: python3 run_generation_test.py")
        logger.info("  3. Run voice cloning test: python3 run_voice_cloning_test.py")
        logger.info("  4. Run assessment test: python3 run_assessment_test.py")
    else:
        logger.error("")
        logger.error("❌ DOWNLOAD FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()

