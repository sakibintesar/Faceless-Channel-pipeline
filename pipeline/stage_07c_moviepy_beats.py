# pipeline/stage_07c_moviepy_beats.py
from __future__ import annotations
from pathlib import Path
import gc
import subprocess
import sys
import tempfile
import os
from moviepy import ImageClip, ColorClip, CompositeVideoClip
from moviepy.video.fx import FadeIn, FadeOut
from .common import VISUALS_DIR, slugify

FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
FONT_SIZE = 64
FONT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 2
MAX_CHARS_PER_CLIP = 7  # TextClip crashes on >= 8 chars on this system


def _create_word_png(word: str, font_size: int = FONT_SIZE) -> str | None:
    """
    Create a PNG for a single word using TextClip in a subprocess.
    Returns the path to the temporary PNG file, or None on failure.
    """
    script = f'''
import gc
from moviepy import TextClip
import tempfile
import os

word = {repr(word)}
font_size = {font_size}

gc.collect()
clip = TextClip(
    font="{FONT_PATH}",
    text=word,
    font_size=font_size,
    color="{FONT_COLOR}",
    stroke_color="{STROKE_COLOR}",
    stroke_width={STROKE_WIDTH},
    method="label",
    text_align="center",
)

with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
    temp_path = f.name
    clip.save_frame(temp_path, t=0)
    print(temp_path)
'''
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=r"C:\Users\sakib\.cline\data\workspaces\chat\faceless-research"
    )
    if result.returncode != 0:
        print(f"Warning: Subprocess failed for '{word}': {result.stderr}")
        return None
    png_path = result.stdout.strip()
    if not png_path or not os.path.exists(png_path):
        print(f"Warning: No PNG created for '{word}'")
        return None
    return png_path


def _beat_clip(text: str, duration: float, size=(1080, 1920)) -> CompositeVideoClip:
    """
    Create a beat clip by rendering each word as a separate PNG (via subprocess)
    to avoid the >=8 char crash and ImageMagick state issues, then compositing
    them as ImageClips.
    """
    w, h = size
    # dark gradient background
    bg = ColorClip(size, color=(13, 22, 32)).with_duration(duration)
    gc.collect()

    # Split text into words
    words = text.split()
    if not words:
        # Fallback: empty clip with just background
        return CompositeVideoClip([bg], size=size)

    # Create PNG for each word (split long words into chunks)
    word_pngs = []
    for word in words:
        if len(word) > MAX_CHARS_PER_CLIP:
            chunks = [word[i:i+MAX_CHARS_PER_CLIP] for i in range(0, len(word), MAX_CHARS_PER_CLIP)]
        else:
            chunks = [word]
        
        for chunk in chunks:
            gc.collect()
            png_path = _create_word_png(chunk)
            if png_path:
                word_pngs.append((chunk, png_path))

    if not word_pngs:
        return CompositeVideoClip([bg], size=size)

    # Load all PNGs as ImageClips
    word_clips = []
    for word, png_path in word_pngs:
        try:
            clip = ImageClip(png_path).with_duration(duration)
            word_clips.append((word, clip))
        except Exception as e:
            print(f"Warning: Failed to load PNG for '{word}': {e}")

    # Cleanup PNG files
    for _, png_path in word_pngs:
        try:
            os.unlink(png_path)
        except:
            pass

    if not word_clips:
        return CompositeVideoClip([bg], size=size)

    # Layout words into lines (simple horizontal flow with wrapping)
    max_line_width = w - 120
    line_height = FONT_SIZE + 10  # approximate line spacing
    x_start = 60  # left margin
    y_center = h * 0.6

    # Calculate positions for each word clip
    positioned_clips = []
    current_x = x_start
    current_y = y_center - (len(word_clips) * line_height) / 2  # rough centering
    line_words = []
    line_width = 0

    for word, clip in word_clips:
        clip_w, clip_h = clip.size
        # Check if adding this word would exceed line width
        if line_width + clip_w > max_line_width and line_words:
            # Move to next line
            current_y += line_height
            current_x = x_start
            line_width = 0
            line_words = []

        # Position this word with fade effects (moviepy 2.x API)
        positioned_clips.append(
            clip.with_position((current_x, current_y))
                .with_effects([FadeIn(0.3), FadeOut(0.3)])
        )
        current_x += clip_w + 10  # word spacing
        line_width += clip_w + 10
        line_words.append(word)

    gc.collect()
    return CompositeVideoClip([bg] + positioned_clips, size=size)


def render_beats(beats: list[str], slug: str, total_dur: float) -> list[Path]:
    """Split total_dur evenly across beats, render each to MP4."""
    out_dir = VISUALS_DIR / "moviepy_beats" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    per = total_dur / max(1, len(beats))
    paths = []
    for i, beat in enumerate(beats):
        clip = _beat_clip(beat, per)
        gc.collect()
        dst = out_dir / f"beat_{i:02d}.mp4"
        clip.write_videofile(str(dst), fps=24, codec="libx264", audio_codec="aac", logger=None)
        gc.collect()
        paths.append(dst)
    return paths
def assemble_final(clip_paths: list[str], output_path: str) -> str:
    """
    Assemble multiple beat clips into a single final video.
    
    Args:
        clip_paths: List of paths to beat clip MP4 files
        output_path: Path for the final assembled video
    
    Returns:
        Path to the assembled video
    """
    from moviepy import VideoFileClip, concatenate_videoclips
    
    clips = []
    for path in clip_paths:
        clip = VideoFileClip(path)
        clips.append(clip)
    
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    
    # Clean up
    for clip in clips:
        clip.close()
    final.close()
    
    return output_path