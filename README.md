# AI Background Remover

[![npm version](https://badge.fury.io/js/ai-bg-remover.svg)](https://badge.fury.io/js/ai-bg-remover)

🚀 A high-performance AI-powered background removal library for Node.js, utilizing the powerful `rembg` Python library.

Easily remove backgrounds from images, apply custom backgrounds (solid colors or gradients), enhance image quality, and even convert the result to a high-fidelity SVG vector format.

## Features

*   **AI-Powered Background Removal:** Leverages state-of-the-art models via `rembg`:
    * `silueta` (43MB) - Default, optimized for human subjects
    * `u2netp` (4.7MB) - Lightweight model
    * `u2net` (176MB) - Original model with highest quality
    * `isnet-general-use` (44MB) - Medium size with good performance
*   **Custom Backgrounds:** Replace the removed background with solid colors (HEX) or linear gradients.
*   **Image Enhancement:** Basic image sharpening and contrast adjustments.
*   **Vector Conversion:** Convert the background-removed image into a scalable SVG format.
*   **Simple Node.js API:** Easy integration into your Node.js projects.
*   **Command-Line Interface:** Includes a Python script for direct command-line usage.

## Prerequisites

This library acts as a Node.js wrapper around a Python script. Therefore, you need Python installed on your system, along with the necessary Python packages.

1.  **Python:** Ensure Python 3.7+ is installed and accessible in your system's PATH.
2.  **Pip:** Python's package installer.

## Installation

1.  **Install the Node.js package:**

    ```sh
    npm install ai-bg-remover
    # or
    yarn add ai-bg-remover
    ```

2.  **Install required Python packages:**

    ```sh
    pip install rembg[gpu] # Or rembg[cpu] if you don't have a compatible GPU
    pip install opencv-python numpy Pillow scikit-image scikit-learn
    ```

    *   `rembg`: The core background removal library.
    *   `opencv-python`: For image processing tasks.
    *   `numpy`: Required by OpenCV and other libraries.
    *   `Pillow`: Image processing library.
    *   `scikit-image`, `scikit-learn`: Used for advanced image segmentation and vector conversion.

3.  **(Optional) Install SVG Optimization Tools:** For optimizing the generated SVG files:

    *   **SVGO (Recommended):**
        ```sh
        npm install -g svgo
        ```
    *   **Scour (Python):**
        ```sh
        pip install scour
        ```

## Usage (Node.js)

```javascript
const path = require('path');
const { removeBackground } = require('ai-bg-remover');

const inputFile = path.join(__dirname, 'input.jpg');
const outputFile = path.join(__dirname, 'output.png');

const options = {
    // background: '#FFFFFF', // Solid white background
    background: 'linear-gradient(to right, #ff7e5f, #feb47b)', // Gradient background
    enhance: true,       // Enhance image quality
    vector: true,        // Convert output to SVG
    // vectorQuality: 'medium' // SVG quality: 'low', 'medium', 'high' (default)
    model: 'silueta'     // Model to use: 'silueta' (default), 'u2netp', 'u2net', 'isnet-general-use'
};

removeBackground(inputFile, outputFile, options)
    .then(() => {
        console.log(`✅ Background removed and saved to ${outputFile}`);
        // If vector: true, an SVG file (e.g., output.svg) will also be created
    })
    .catch(err => {
        console.error(`❌ Error: ${err}`);
    });
```

## API

### `removeBackground(inputImage, outputImage, [options])`

*   `inputImage` (String): Path to the input image file (JPG, JPEG, PNG).
*   `outputImage` (String): Path to save the output PNG image.
*   `options` (Object, Optional): Configuration options:
    *   `background` (String): Background to apply.
        *   Solid Color: HEX code (e.g., `"#FF0000"`, `"#fff"`).
        *   Gradient: CSS-like `linear-gradient` string (e.g., `"linear-gradient(to right, #ff7e5f, #feb47b)"`). Requires at least two HEX colors.
    *   `enhance` (Boolean): If `true`, applies basic image enhancement. Defaults to `false`.
    *   `vector` (Boolean): If `true`, converts the `outputImage` (PNG) to an SVG file (saved as `outputImage` with `.svg` extension). Defaults to `false`.
    *   `vectorQuality` (String): Quality preset for SVG conversion (`'low'`, `'medium'`, `'high'`). Defaults to `'high'`.
    *   `model` (String): Model to use for background removal. Options:
        * `'silueta'` (default) - Optimized for human subjects (43MB)
        * `'u2netp'` - Lightweight model (4.7MB)
        * `'u2net'` - Original model with highest quality (176MB)
        * `'isnet-general-use'` - Medium size with good performance (44MB)

## Command-Line Usage (Python)

You can also use the underlying Python script directly:

```sh
python src/remove_bg.py <input_path> <output_path> [options]
```

**Options:**

*   `--background "<value>"`: Set background color or gradient.
*   `--enhance`: Enable image enhancement.
*   `--vector`: Enable SVG conversion.
*   `--model <name>`: Model to use (default: silueta)
    * Choices: silueta, u2netp, u2net, isnet-general-use

**Example:**

```sh
python src/remove_bg.py images/input.jpg results/output.png --enhance --vector --model silueta
```

## How it Works

This library executes the `src/remove_bg.py` Python script using Node.js's `child_process`. The Python script handles the core image processing tasks using `rembg` and `opencv-python`.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

[MIT](LICENSE) (Assuming you will add an MIT license file)
