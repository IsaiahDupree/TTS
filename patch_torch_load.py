"""
Monkey patch to fix PyTorch 2.6+ weights_only issue with TTS models.
This patches torch.load to use weights_only=False for TTS model loading.
"""

import torch
import functools

# Store original torch.load
_original_torch_load = torch.load

@functools.wraps(_original_torch_load)
def patched_torch_load(*args, **kwargs):
    """Patched torch.load that defaults weights_only=False for TTS models."""
    # If weights_only is not explicitly set, default to False for TTS compatibility
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    # If it's explicitly True, we still need to set it to False for TTS
    elif kwargs.get('weights_only') is True:
        kwargs['weights_only'] = False
    
    return _original_torch_load(*args, **kwargs)

# Apply the patch
torch.load = patched_torch_load

print("✅ Patched torch.load to use weights_only=False for TTS compatibility")

