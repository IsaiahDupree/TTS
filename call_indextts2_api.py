#!/usr/bin/env python3
"""
Call IndexTTS2 Hugging Face Spaces API
Uses the IndexTTS2 demo API for emotion-controlled voice synthesis.
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

def call_indextts2_api(
    voice_reference,
    text,
    output_file,
    emo_control_method="Same as the voice reference",
    emotion_reference=None,
    emotion_weight=0.8,
    emotion_vectors=None,
    emotion_text="",
    max_text_tokens=120,
    **generation_params
):
    """
    Call IndexTTS2 API for voice synthesis with emotion control.
    
    Args:
        voice_reference: Path to voice reference audio file
        text: Text to synthesize
        output_file: Path to save output audio
        emo_control_method: "Same as the voice reference", "Use emotion reference audio", or "Use emotion vectors"
        emotion_reference: Path to emotion reference audio (if using emotion reference method)
        emotion_weight: Emotion control weight (0.0-1.0)
        emotion_vectors: Dict with keys: happy, angry, sad, afraid, disgusted, melancholic, surprised, calm (0.0-1.0)
        emotion_text: Text description of emotion (if using text-based emotion)
        max_text_tokens: Maximum tokens per generation segment
        **generation_params: Additional generation parameters
    """
    logger.info("=" * 100)
    logger.info("CALLING INDEXTTS2 HUGGING FACE API")
    logger.info("=" * 100)
    logger.info("")
    
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        logger.error("❌ gradio_client not installed!")
        logger.info("Install with: pip install gradio_client")
        return False
    
    # Validate inputs
    voice_ref_path = Path(voice_reference)
    if not voice_ref_path.exists():
        logger.error(f"❌ Voice reference not found: {voice_reference}")
        return False
    
    logger.info(f"Voice reference: {voice_ref_path.name}")
    logger.info(f"Text: '{text}'")
    logger.info(f"Emotion method: {emo_control_method}")
    logger.info("")
    
    # Initialize client
    logger.info("Connecting to IndexTTS2 API...")
    logger.info("Space: IndexTeam/IndexTTS-2-Demo")
    logger.info("")
    
    # Check for Hugging Face token
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if hf_token:
        logger.info("✅ Hugging Face token found in environment")
        logger.info("Using authenticated access (may have higher quota)")
    else:
        logger.warning("⚠️  No Hugging Face token found")
        logger.warning("Using anonymous access (limited GPU quota)")
        logger.warning("Set HF_TOKEN or HUGGINGFACE_HUB_TOKEN for better quota")
        logger.info("")
    
    try:
        # Set token in environment if provided (gradio_client reads from env)
        if hf_token:
            os.environ["HF_TOKEN"] = hf_token
            os.environ["HUGGINGFACE_HUB_TOKEN"] = hf_token
            logger.info("Token set in environment variables")
        
        client = Client("IndexTeam/IndexTTS-2-Demo")
        logger.info("✅ Connected to API")
        if hf_token:
            logger.info("✅ Using authenticated access with token")
        logger.info("")
    except Exception as e:
        logger.error(f"❌ Failed to connect to API: {e}")
        logger.error("")
        logger.error("Full error details:")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Prepare emotion vectors (default to all zeros)
    if emotion_vectors is None:
        emotion_vectors = {
            "happy": 0,
            "angry": 0,
            "sad": 0,
            "afraid": 0,
            "disgusted": 0,
            "melancholic": 0,
            "surprised": 0,
            "calm": 0
        }
    
    # Map emotion vectors to API format
    vec1 = emotion_vectors.get("happy", 0)
    vec2 = emotion_vectors.get("angry", 0)
    vec3 = emotion_vectors.get("sad", 0)
    vec4 = emotion_vectors.get("afraid", 0)
    vec5 = emotion_vectors.get("disgusted", 0)
    vec6 = emotion_vectors.get("melancholic", 0)
    vec7 = emotion_vectors.get("surprised", 0)
    vec8 = emotion_vectors.get("calm", 0)
    
    # Handle emotion reference
    if emotion_reference:
        emo_ref_path = handle_file(str(emotion_reference))
    else:
        # Use voice reference as default
        emo_ref_path = handle_file(str(voice_ref_path))
    
    # Default generation parameters
    default_params = {
        "param_16": True,  # do_sample
        "param_17": 0.8,   # top_p
        "param_18": 30,    # top_k
        "param_19": 0.8,   # temperature
        "param_20": 0,     # length_penalty
        "param_21": 3,     # num_beams
        "param_22": 10,    # repetition_penalty
        "param_23": 1500,  # max_mel_tokens
    }
    default_params.update(generation_params)
    
    # Call API
    logger.info("Calling /gen_single endpoint...")
    logger.info("This may take a while...")
    logger.info("Note: Hugging Face Spaces have GPU quota limits on free tier")
    logger.info("")
    
    start_time = time.time()
    max_retries = 3
    retry_delay = 30  # seconds
    
    for attempt in range(max_retries):
        try:
            result = client.predict(
                emo_control_method=emo_control_method,
                prompt=handle_file(str(voice_ref_path)),
                text=text,
                emo_ref_path=emo_ref_path,
                emo_weight=emotion_weight,
                vec1=vec1,
                vec2=vec2,
                vec3=vec3,
                vec4=vec4,
                vec5=vec5,
                vec6=vec6,
                vec7=vec7,
                vec8=vec8,
                emo_text=emotion_text,
                emo_random=False,
                max_text_tokens_per_segment=max_text_tokens,
                **default_params,
                api_name="/gen_single"
            )
            
            generation_time = time.time() - start_time
            break  # Success, exit retry loop
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Log full error details
            logger.error("")
            logger.error("=" * 100)
            logger.error("FULL API ERROR DETAILS")
            logger.error("=" * 100)
            logger.error(f"Error Type: {error_type}")
            logger.error(f"Error Message: {error_msg}")
            logger.error("")
            
            # Check for specific error types
            if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                logger.error("ERROR TYPE: GPU Quota Exceeded")
                logger.error("")
                logger.error("This means:")
                logger.error("  - The Hugging Face Space has used up its free GPU quota")
                logger.error("  - Free tier typically has ~60 seconds of GPU time")
                logger.error("  - Quota resets periodically (usually every few hours)")
                logger.error("")
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    logger.warning(f"⚠️  GPU quota exceeded. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                    logger.warning("Note: Free Hugging Face Spaces have limited GPU time")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ GPU quota exceeded after {max_retries} attempts")
                    logger.error("")
                    logger.error("SOLUTIONS:")
                    logger.error("  1. Wait 10-30 minutes and try again (quota resets)")
                    logger.error("  2. Use local IndexTTS2 instead (no quota limits)")
                    logger.error("  3. Set HF_TOKEN environment variable (may help with quota)")
                    logger.error("     export HF_TOKEN='your_huggingface_token'")
                    logger.error("  4. Upgrade to Hugging Face Pro for more GPU time")
                    logger.error("")
                    return False
            elif "authentication" in error_msg.lower() or "token" in error_msg.lower() or "unauthorized" in error_msg.lower():
                logger.error("ERROR TYPE: Authentication Issue")
                logger.error("")
                logger.error("This means:")
                logger.error("  - API key/token may be invalid or missing")
                logger.error("  - Or the Space requires authentication")
                logger.error("")
                logger.error("SOLUTIONS:")
                logger.error("  1. Get your Hugging Face token from:")
                logger.error("     https://huggingface.co/settings/tokens")
                logger.error("  2. Set it as environment variable:")
                logger.error("     export HF_TOKEN='your_token_here'")
                logger.error("  3. Or pass it to the script")
                logger.error("")
                return False
            else:
                # Other error, don't retry
                logger.error("ERROR TYPE: Unknown/Other")
                logger.error("")
                import traceback
                logger.error("Full traceback:")
                logger.error(traceback.format_exc())
                raise
    
    # Download result (only if we got a result)
    try:
        # Download result
        logger.info("Downloading generated audio...")
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Result can be a dict with file info or a file path
        import urllib.request
        import shutil
        
        file_path = None
        
        if isinstance(result, dict):
            # Gradio file dict format - check multiple possible keys
            if 'value' in result:
                # Gradio update format: {'visible': True, 'value': '/path/to/file', '__type__': 'update'}
                file_path = result['value']
            elif 'path' in result:
                file_path = result['path']
            elif 'url' in result:
                file_path = result['url']
            elif 'name' in result:
                file_path = result['name']
            else:
                logger.error(f"❌ Unexpected result dict structure: {result}")
                logger.error("Available keys: " + ", ".join(result.keys()))
                return False
        elif hasattr(result, 'path'):
            # FileData object
            file_path = result.path
        elif isinstance(result, str):
            # Direct file path or URL
            file_path = result
        
        if not file_path:
            logger.error(f"❌ Could not extract file path from result: {result}")
            return False
        
        logger.info(f"Extracted file path: {file_path}")
        
        # Download or copy file
        if file_path.startswith('http'):
            # URL - download it
            logger.info(f"  Downloading from: {file_path}")
            urllib.request.urlretrieve(file_path, str(output_path))
        else:
            # Local file path - copy it
            logger.info(f"  Copying from: {file_path}")
            if Path(file_path).exists():
                shutil.copy(file_path, str(output_path))
            else:
                # Try to download from Gradio server
                if not file_path.startswith('http'):
                    # Construct URL
                    base_url = "https://indexteam-indextts-2-demo.hf.space"
                    if file_path.startswith('/'):
                        file_url = base_url + file_path
                    else:
                        file_url = base_url + "/gradio_api/file=" + file_path
                    logger.info(f"  Downloading from: {file_url}")
                    urllib.request.urlretrieve(file_url, str(output_path))
                else:
                    urllib.request.urlretrieve(file_path, str(output_path))
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info("")
            logger.info("=" * 100)
            logger.info("GENERATION COMPLETE")
            logger.info("=" * 100)
            logger.info(f"Generation time: {generation_time:.2f} seconds")
            logger.info(f"Output file: {output_path}")
            logger.info(f"Output size: {size_mb:.2f} MB")
            logger.info("")
            return True
        else:
            logger.error(f"❌ Output file not created: {output_path}")
            return False
            
    except Exception as e:
        generation_time = time.time() - start_time
        logger.error(f"❌ API call failed after {generation_time:.2f} seconds: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("")
        logger.error("Alternative: Use local IndexTTS2 installation:")
        logger.error("  python3 clone_voice_indextts2_emotion.py --text 'Your text' --voice-ref 'voice.wav'")
        return False


def generate_with_emotions(voice_reference, texts, output_dir="test_outputs/indextts2_api", **kwargs):
    """Generate multiple samples with different emotion settings."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Test different emotion methods
    emotion_configs = [
        {
            "name": "natural",
            "emo_control_method": "Same as the voice reference",
            "emotion_vectors": None
        },
        {
            "name": "happy",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"happy": 0.8, "calm": 0.2}
        },
        {
            "name": "sad",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"sad": 0.8, "melancholic": 0.2}
        },
        {
            "name": "surprised",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"surprised": 0.8}
        },
        {
            "name": "angry",
            "emo_control_method": "Use emotion vectors",
            "emotion_vectors": {"angry": 0.8}
        }
    ]
    
    for i, text in enumerate(texts, 1):
        for config in emotion_configs:
            output_file = output_path / f"test_{i:02d}_{config['name']}.wav"
            
            logger.info(f"Generating: test_{i:02d}_{config['name']}")
            
            success = call_indextts2_api(
                voice_reference=voice_reference,
                text=text,
                output_file=str(output_file),
                emo_control_method=config["emo_control_method"],
                emotion_vectors=config.get("emotion_vectors"),
                **kwargs
            )
            
            if success:
                results.append({
                    "text_number": i,
                    "emotion": config["name"],
                    "output_file": str(output_file),
                    "success": True
                })
            
            logger.info("")
    
    return results


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Call IndexTTS2 Hugging Face API")
    parser.add_argument('--voice', type=str, required=True,
                        help='Path to voice reference audio file')
    parser.add_argument('--text', type=str, required=True,
                        help='Text to synthesize')
    parser.add_argument('--output', type=str, required=True,
                        help='Output audio file path')
    parser.add_argument('--emotion-method', type=str,
                        choices=['Same as the voice reference', 'Use emotion reference audio', 'Use emotion vectors'],
                        default='Same as the voice reference',
                        help='Emotion control method')
    parser.add_argument('--emotion-reference', type=str,
                        help='Path to emotion reference audio (if using emotion reference method)')
    parser.add_argument('--emotion-weight', type=float, default=0.8,
                        help='Emotion control weight (0.0-1.0)')
    parser.add_argument('--happy', type=float, default=0,
                        help='Happy emotion vector (0.0-1.0)')
    parser.add_argument('--angry', type=float, default=0,
                        help='Angry emotion vector (0.0-1.0)')
    parser.add_argument('--sad', type=float, default=0,
                        help='Sad emotion vector (0.0-1.0)')
    parser.add_argument('--surprised', type=float, default=0,
                        help='Surprised emotion vector (0.0-1.0)')
    parser.add_argument('--calm', type=float, default=0,
                        help='Calm emotion vector (0.0-1.0)')
    parser.add_argument('--emotion-text', type=str, default="",
                        help='Text description of emotion')
    
    args = parser.parse_args()
    
    emotion_vectors = {
        "happy": args.happy,
        "angry": args.angry,
        "sad": args.sad,
        "surprised": args.surprised,
        "calm": args.calm
    }
    
    success = call_indextts2_api(
        voice_reference=args.voice,
        text=args.text,
        output_file=args.output,
        emo_control_method=args.emotion_method,
        emotion_reference=args.emotion_reference,
        emotion_weight=args.emotion_weight,
        emotion_vectors=emotion_vectors,
        emotion_text=args.emotion_text
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

