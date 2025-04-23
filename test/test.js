const { removeBackground } = require("../src/index");
const path = require("path");
const fs = require("fs");

// Set input and output file paths
const inputFile = path.join(__dirname, "input.jpeg"); // Change to your actual file name
const outputFile = path.join(__dirname, "output.png");

// ✅ Check if input file exists
if (!fs.existsSync(inputFile)) {
    console.error("❌ Error: Input file not found. Please add an image to the 'test' folder.");
    process.exit(1);
}

// Define user options
const options = {
    background: "linear-gradient(to right,#feb47b, #feb47b)", // Example: Gradient background
    enhance: true, // AI enhancement
    vector: true,  // Convert to vector
    model: "silueta" // Use silueta model (default)
};

console.log(`🚀 Processing image: ${inputFile}...`);
console.log(`🔧 Options: ${JSON.stringify(options)}`);

removeBackground(inputFile, outputFile, options)
    .then(result => {
        console.log('✅ Success:', result);
        // Expected output:
        // {
        //     success: true,
        //     outputPath: '/path/to/output.png',
        //     message: 'Background removed successfully'
        // }
        
        // Check if output files exist
        if (fs.existsSync(result.outputPath)) {
            console.log(`✅ Output PNG file created: ${result.outputPath}`);
        }
        
        // Check for SVG file if vector option was enabled
        const svgFile = result.outputPath.replace('.png', '.svg');
        if (options.vector && fs.existsSync(svgFile)) {
            console.log(`✅ Output SVG file created: ${svgFile}`);
        }
    })
    .catch(err => {
        console.error(`❌ Error: ${err}`);
        // Possible error messages:
        // - ❌ Error: The input file does not exist: <path>
        // - ❌ Error: Unsupported file format. Please use JPG or PNG.
        // - ❌ Error: File size exceeds the 5MB limit.
        // - ❌ Error: <Python script error message>
    });
