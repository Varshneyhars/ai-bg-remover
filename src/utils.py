import cv2
import numpy as np
import skimage
from PIL import Image, ImageEnhance
import re 
import sys

# Ensure UTF-8 encoding is used in Windows
sys.stdout.reconfigure(encoding='utf-8')

def apply_background(image, background):
    """Apply solid or gradient background to the image"""

    # Ensure the image is 3-channel (RGB) instead of 4-channel (RGBA)
    if image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    mask = np.all(image == [0, 0, 0], axis=-1)  # Mask for black pixels (background)

    if background.startswith("linear-gradient"):
        # Extract only hex color codes using regex
        colors = re.findall(r"#([0-9a-fA-F]{6})", background)

        if len(colors) < 2:
            raise ValueError("Gradient background requires at least two hex colors.")

        start_color = np.array([int(colors[0][i:i+2], 16) for i in (0, 2, 4)], dtype=np.uint8)  # Convert hex to RGB
        end_color = np.array([int(colors[1][i:i+2], 16) for i in (0, 2, 4)], dtype=np.uint8)

        h, w, _ = image.shape
        gradient = np.zeros((h, w, 3), dtype=np.uint8)

        # Create a vertical gradient
        for i in range(h):
            ratio = i / h
            interpolated_color = (1 - ratio) * start_color + ratio * end_color
            gradient[i, :] = interpolated_color.astype(np.uint8)  # Ensure correct data type

        # Apply the gradient only to the masked areas
        image[mask] = gradient[mask]

    else:
        # Convert solid color to RGB
        hex_match = re.search(r"#([0-9a-fA-F]{6})", background)
        if not hex_match:
            raise ValueError("Invalid solid color format. Use HEX color codes like #ffffff.")

        color = np.array([int(hex_match.group(1)[i:i+2], 16) for i in (0, 2, 4)], dtype=np.uint8)

        # Apply solid color only to the masked areas
        image[mask] = color

    return image

def enhance_image(image):
    """Enhances image using AI-based super-resolution."""
    image_pil = Image.fromarray(image)
    enhancer = ImageEnhance.Sharpness(image_pil)
    return np.array(enhancer.enhance(2.0))  # Sharpen by factor of 2

def convert_to_vector(image_path, quality_level='high'):
    """
    Convert an image to high-fidelity SVG vector format that closely matches the original image
    
    Parameters:
    image_path (str): Path to the input image
    quality_level (str): 'low', 'medium', or 'high' - controls detail level and file size
    
    Returns:
    str: Path to the generated SVG file
    """
    import cv2
    import numpy as np
    from sklearn.cluster import KMeans
    import os
    
    # Quality settings
    quality_settings = {
        'low': {
            'colors': 12,
            'simplify_factor': 0.01,
            'min_area': 100,
            'blur_size': 5
        },
        'medium': {
            'colors': 24,
            'simplify_factor': 0.005,
            'min_area': 50,
            'blur_size': 3
        },
        'high': {
            'colors': 32,
            'simplify_factor': 0.002,
            'min_area': 20,
            'blur_size': 1
        }
    }
    
    settings = quality_settings.get(quality_level, quality_settings['medium'])
    
    # Read the image with alpha channel
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if img is None:
        print(f"❌ Error: Could not load image {image_path}")
        return
    
    # Handle alpha channel properly
    has_alpha = img.shape[2] == 4 if len(img.shape) > 2 else False
    
    if has_alpha:
        # Separate color and alpha channels
        bgr = img[:,:,0:3]
        alpha = img[:,:,3]
        img_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
    
    height, width = img_rgb.shape[:2]
    
    # Apply mild blurring to reduce noise while preserving edges
    blur_size = settings['blur_size']
    if blur_size > 0:
        img_filtered = cv2.medianBlur(img_rgb, blur_size)
    else:
        img_filtered = img_rgb.copy()
    
    # Prepare image for color quantization
    pixels = img_filtered.reshape(-1, 3).astype(np.float32)
    
    # Apply mask for transparent areas if alpha channel exists
    if has_alpha:
        valid_pixels_mask = alpha.reshape(-1) > 10  # Only consider semi-opaque pixels
        valid_pixels = pixels[valid_pixels_mask]
        if len(valid_pixels) == 0:  # Handle completely transparent images
            valid_pixels = pixels
    else:
        valid_pixels = pixels
    
    # Perform color quantization with KMeans
    n_colors = settings['colors']
    if len(valid_pixels) > n_colors:
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(valid_pixels)
        
        # Map all pixels to the closest cluster center
        labels = kmeans.predict(pixels)
        centers = kmeans.cluster_centers_
        
        # Recreate quantized image
        quantized = centers[labels].reshape(img_rgb.shape).astype(np.uint8)
    else:
        # If we have fewer pixels than colors, just use the original
        quantized = img_rgb.copy()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(image_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create SVG output filename
    base_name = os.path.splitext(image_path)[0]
    svg_path = f"{base_name}.svg"
    
    # Prepare for contour finding - convert to grayscale
    gray = cv2.cvtColor(quantized, cv2.COLOR_RGB2GRAY)
    
    # Use quantized image directly for segmentation
    labels_img = labels.reshape(height, width)
    unique_labels = np.unique(labels)
    
    with open(svg_path, "w", encoding='utf-8') as f:
        # SVG header
        f.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<defs>
    <style>
        path {{ vector-effect: non-scaling-stroke; }}
    </style>
</defs>
<g>
''')
        
        # Add solid background if no transparency
        if not has_alpha:
            f.write(f'<rect x="0" y="0" width="{width}" height="{height}" fill="rgb(255,255,255)"/>\n')
        
        # Process each color cluster
        for label_idx in unique_labels:
            # Create binary mask for this color
            mask = np.zeros((height, width), dtype=np.uint8)
            mask[labels_img == label_idx] = 255
            
            # Get color for this segment
            color = centers[label_idx].astype(int)
            
            # Find contours in this color segment
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process each contour for this color
            for contour in contours:
                # Skip small contours
                if cv2.contourArea(contour) < settings['min_area']:
                    continue
                
                # Simplify contour 
                epsilon = settings['simplify_factor'] * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Calculate average alpha value for this contour
                contour_mask = np.zeros((height, width), dtype=np.uint8)
                cv2.drawContours(contour_mask, [contour], 0, 255, -1)
                mean_alpha = np.mean(alpha[contour_mask == 255]) if has_alpha else 255
                
                # Skip nearly transparent regions
                if mean_alpha < 10:
                    continue
                
                # Create path data
                path_data = ""
                for i, point in enumerate(approx):
                    x, y = point[0]
                    if i == 0:
                        path_data += f"M {x},{y} "
                    else:
                        path_data += f"L {x},{y} "
                
                # Close the path
                path_data += "Z"
                
                # Calculate opacity
                opacity = min(0.99, mean_alpha / 255.0)
                
                # Write path to SVG
                f.write(f'<path d="{path_data}" fill="rgb({color[0]},{color[1]},{color[2]})" '
                       f'opacity="{opacity:.2f}" />\n')
        
        # Close SVG
        f.write('</g>\n</svg>')
    
    # Optimize SVG with post-processing if available
    try:
        import subprocess
        try:
            # Try using svgo for optimization if installed
            subprocess.run(['svgo', '--multipass', svg_path], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print("✅ SVG optimized with SVGO")
        except (subprocess.SubprocessError, FileNotFoundError):
            # If svgo not available, try scour
            try:
                from scour import scour
                with open(svg_path, 'r') as svg_file:
                    svg_data = svg_file.read()
                
                options = scour.parse_args(['--enable-viewboxing',
                                          '--enable-id-stripping',
                                          '--enable-comment-stripping',
                                          '--shorten-ids',
                                          '--indent=none'])
                
                optimized = scour.scourString(svg_data, options)
                
                with open(svg_path, 'w') as svg_file:
                    svg_file.write(optimized)
                print("✅ SVG optimized with Scour")
            except ImportError:
                print("⚠️ SVG optimization skipped (neither SVGO nor Scour available)")
    except Exception as e:
        print(f"⚠️ SVG optimization error: {e}")
    
    print(f"✅ Vector conversion complete: {svg_path}")
    print(f"   - Created with {n_colors} colors and {settings['simplify_factor']} simplification")
    
    return svg_path


def batch_convert_to_svg(directory, pattern="*.png", quality="high"):
    """
    Convert all matching images in a directory to SVG
    
    Parameters:
    directory (str): Directory containing images
    pattern (str): Glob pattern to match files (e.g., "*.png", "*.jpg")
    quality (str): 'low', 'medium', or 'high'
    
    Returns:
    list: Paths to all generated SVG files
    """
    import os
    import glob
    
    # Get all matching files
    image_paths = glob.glob(os.path.join(directory, pattern))
    svg_paths = []
    
    print(f"Found {len(image_paths)} images to convert")
    
    # Process each file
    for image_path in image_paths:
        print(f"Converting {os.path.basename(image_path)}...")
        svg_path = convert_to_vector(image_path, quality)
        if svg_path:
            svg_paths.append(svg_path)
    
    print(f"Completed batch conversion: {len(svg_paths)} SVGs created")
    return svg_paths


def get_optimal_svg_settings(image_path):
    """
    Analyze image and determine optimal settings for SVG conversion
    
    Parameters:
    image_path (str): Path to the image
    
    Returns:
    dict: Settings for optimal conversion
    """
    import cv2
    import numpy as np
    
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return {'quality': 'medium'}  # Default if can't read image
    
    height, width = img.shape[:2]
    size = height * width
    
    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect edges
    edges = cv2.Canny(gray, 100, 200)
    edge_pixels = np.count_nonzero(edges)
    edge_density = edge_pixels / size
    
    # Calculate color variance
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    color_var = np.var(h) / 180.0  # Normalize by hue range
    
    # Determine optimal settings based on image characteristics
    if size > 1000000:  # Large image
        if edge_density > 0.05 or color_var > 0.1:
            quality = 'high'
            colors = min(48, int(32 + color_var * 32))
        else:
            quality = 'medium'
            colors = min(32, int(24 + color_var * 24))
    else:  # Small image
        if edge_density > 0.08 or color_var > 0.15:
            quality = 'medium'
            colors = min(32, int(24 + color_var * 24))
        else:
            quality = 'low'
            colors = min(24, int(16 + color_var * 16))
    
    # Scale simplification factor based on edge density
    simplify_factor = max(0.001, min(0.01, 0.005 - edge_density * 0.03))
    
    return {
        'quality': quality,
        'colors': colors,
        'simplify_factor': simplify_factor,
        'edge_density': edge_density,
        'color_variance': color_var
    }


# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Analyzing {image_path}...")
        
        # Auto-detect optimal settings
        settings = get_optimal_svg_settings(image_path)
        print(f"Detected image characteristics:")
        print(f"- Edge density: {settings['edge_density']:.4f}")
        print(f"- Color variance: {settings['color_variance']:.4f}")
        print(f"- Recommended quality: {settings['quality']}")
        
        # Convert with optimal settings
        convert_to_vector(image_path, settings['quality'])
    else:
        print("Usage: python script.py image_path")