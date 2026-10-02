"""
Free Image Generation using Pollinations.ai (Flux model)
No API key required, good quality, supports custom prompts.
"""
import requests
from pathlib import Path
from typing import List
from urllib.parse import quote


def generate_images(prompts: List[str], slug: str, width: int = 1080, height: int = 1920, model: str = "flux") -> List[str]:
    """
    Generate images using Pollinations.ai free API.
    
    Args:
        prompts: List of image prompts
        slug: Video slug for output directory
        width: Image width (default 1080 for vertical video)
        height: Image height (default 1920 for vertical video)
        model: Model to use (flux, gptimage, dall-e-3, etc.)
    
    Returns:
        List of paths to generated PNG files
    """
    output_dir = Path(f"content/images/{slug}")
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    for i, prompt in enumerate(prompts):
        # Clean prompt for URL
        clean_prompt = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={width}&height={height}&nologo=true&model={model}"
        
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            
            path = output_dir / f"img_{i:02d}.png"
            path.write_bytes(resp.content)
            paths.append(str(path))
            print(f"Generated image {i+1}/{len(prompts)}: {path}")
            
        except Exception as e:
            print(f"Failed to generate image {i}: {e}")
            # Create a placeholder
            path = output_dir / f"img_{i:02d}.png"
            # Create a simple colored placeholder
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (width, height), color=(20, 30, 50))
            draw = ImageDraw.Draw(img)
            draw.text((width//2, height//2), f"Image {i+1}\n{prompt[:50]}", fill=(255,255,255), anchor="mm")
            img.save(path)
            paths.append(str(path))

    return paths


def generate_images_with_style(prompts: List[str], slug: str, style: str = "cinematic") -> List[str]:
    """
    Generate images with predefined style modifiers.
    """
    style_modifiers = {
        "cinematic": "cinematic lighting, 8k, highly detailed, vertical composition",
        "minimal": "minimalist, clean, simple, flat design, vertical",
        "dark": "dark moody atmosphere, low key lighting, vertical",
        "bright": "bright vibrant colors, high key lighting, vertical",
        "anime": "anime style, cel shaded, vertical composition",
        "sketch": "hand drawn sketch, pencil style, vertical",
    }
    
    modifier = style_modifiers.get(style, style_modifiers["cinematic"])
    styled_prompts = [f"{p}, {modifier}" for p in prompts]
    
    return generate_images(styled_prompts, slug)