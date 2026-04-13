"""
Image Utilities — resize and crop images for WordPress thumbnails.
"""

from PIL import Image
import os


def resize_to_square(
    input_path: str,
    output_path: str = None,
    size: int = 150,
    quality: int = 85,
) -> str:
    """
    Resize and crop an image to a square thumbnail.

    Args:
        input_path: Path to the input image file
        output_path: Path to save the resized image (defaults to input_path)
        size: Target size in pixels (default: 150)
        quality: JPEG quality (1-100, default: 85)

    Returns:
        Path to the resized image file
    """
    if output_path is None:
        output_path = input_path

    # Open image
    with Image.open(input_path) as img:
        # Convert to RGB if necessary (for JPEG output)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Calculate crop dimensions to center-crop to square
        width, height = img.size
        min_dimension = min(width, height)

        # Calculate crop box (center crop)
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension

        # Crop to square
        img = img.crop((left, top, right, bottom))

        # Resize to target size
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Save with appropriate format
        ext = os.path.splitext(output_path)[1].lower()
        if ext in [".jpg", ".jpeg"]:
            img.save(output_path, "JPEG", quality=quality, optimize=True)
        elif ext == ".png":
            img.save(output_path, "PNG", optimize=True)
        else:
            # Default to JPEG for unknown formats
            output_path = os.path.splitext(output_path)[0] + ".jpg"
            img.save(output_path, "JPEG", quality=quality, optimize=True)

    return output_path
