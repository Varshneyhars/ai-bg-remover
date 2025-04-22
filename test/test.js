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
    .then(() => console.log(`✅ Background removed successfully: ${outputFile}`))
    .catch(err => console.error(`❌ Error: ${err}`));
