"""
Free TTS using Microsoft Edge TTS (edge-tts)
No API key required, excellent voice quality, no rate limits.
"""
import asyncio
import edge_tts
from pathlib import Path
from typing import List


async def generate_tts_async(texts: List[str], slug: str, voice: str = "en-US-AriaNeural") -> List[str]:
    """
    Generate TTS audio files using edge-tts (Microsoft Edge voices).
    
    Args:
        texts: List of text strings to convert to speech
        slug: Video slug for output directory
        voice: Edge TTS voice (default: en-US-AriaNeural)
               Other good options: en-US-GuyNeural, en-GB-SoniaNeural, en-AU-NatashaNeural
    
    Returns:
        List of paths to generated MP3 files
    """
    output_dir = Path(f"content/audio/{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    for i, text in enumerate(texts):
        communicate = edge_tts.Communicate(text, voice)
        path = output_dir / f"tts_{i:02d}.mp3"
        await communicate.save(str(path))
        paths.append(str(path))

    return paths


def generate_tts(texts: List[str], slug: str, voice: str = "en-US-AriaNeural") -> List[str]:
    """
    Synchronous wrapper for generate_tts_async.
    """
    return asyncio.run(generate_tts_async(texts, slug, voice))


# Voice options for different styles
VOICES = {
    "default": "en-US-AriaNeural",      # Female, clear, professional
    "male": "en-US-GuyNeural",          # Male, neutral
    "british_female": "en-GB-SoniaNeural",
    "british_male": "en-GB-RyanNeural",
    "australian": "en-AU-NatashaNeural",
    "indian": "en-IN-NeerjaNeural",
    "excited": "en-US-JennyMultilingualNeural",
    "calm": "en-US-AnaNeural",
}


def generate_tts_styled(texts: List[str], slug: str, style: str = "default") -> List[str]:
    """
    Generate TTS with a specific voice style.
    """
    voice = VOICES.get(style, VOICES["default"])
    return generate_tts(texts, slug, voice)