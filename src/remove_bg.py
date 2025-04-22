# remove_bg.py
import cv2
import numpy as np
import argparse
import os
from rembg import remove, new_session
from utils import apply_background, enhance_image, convert_to_vector

def remove_bg(input_path, output_path, background=None, enhance=False, vector=False, model_name='silueta'):
    """
    Remove background from an image and perform optional processing.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
        background (str, optional): Background color or gradient
        enhance (bool): Whether to enhance image quality
        vector (bool): Whether to convert to vector format
        model_name (str): Name of the model to use (silueta, u2netp, u2net, isnet-general-use)
    """
    # Create a new session with the specified model
    session = new_session(model_name)
    
    # Read input image
    img = cv2.imread(input_path)
    if img is None:
        print(f"❌ Error: Unable to read file {input_path}")
        return
    
    print(f"Removing background using {model_name} model...")
    # Remove background
    no_bg = remove(img, session=session)
    
    # Apply background replacement if specified
    if background:
        print(f"Applying background: {background}")
        no_bg = apply_background(no_bg, background.strip())
    
    # Enhance image if specified
    if enhance:
        print("Enhancing image...")
        no_bg = enhance_image(no_bg)
    
    # Save the processed image
    print(f"Saving to {output_path}...")
    cv2.imwrite(output_path, no_bg)
    
    # Convert to vector if specified
    if vector:
        print("Converting to vector format...")
        vector_path = convert_to_vector(output_path)
        print(f"Vector saved to {vector_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove background from image.")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument("--background", help="Background color or gradient")
    parser.add_argument("--enhance", action="store_true", help="Enhance image quality")
    parser.add_argument("--vector", action="store_true", help="Convert to vector")
    parser.add_argument("--model", default="silueta", choices=["silueta", "u2netp", "u2net", "isnet-general-use"], 
                        help="Model to use for background removal")
    args = parser.parse_args()
    
    remove_bg(args.input, args.output, args.background, args.enhance, args.vector, args.model)