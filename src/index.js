const { exec } = require("child_process");
const path = require("path");
const fs = require("fs");

// Check if the file exists and is a valid image
function validateImageFile(inputImage) {
    return new Promise((resolve, reject) => {
        const allowedExtensions = [".jpg", ".jpeg", ".png"];
        const ext = path.extname(inputImage).toLowerCase();

        if (!fs.existsSync(inputImage)) {
            reject(`❌ Error: The input file does not exist: ${inputImage}`);
            return;
        }

        if (!allowedExtensions.includes(ext)) {
            reject(`❌ Error: Unsupported file format. Please use JPG or PNG.`);
            return;
        }

        const stats = fs.statSync(inputImage);
        const fileSize = stats.size / (1024 * 1024); // MB
        const maxSize = 5; // MB

        if (fileSize > maxSize) {
            reject(`❌ Error: File size exceeds the ${maxSize}MB limit.`);
            return;
        }

        resolve(inputImage);
    });
}

// Main function for background removal with options
async function removeBackground(inputImage, outputImage, options = {}) {
    try {
        const validImagePath = await validateImageFile(inputImage);
        const pythonCmd = process.platform === "win32" ? "python" : "python3";
        const inputPath = path.resolve(validImagePath).replace(/\\/g, "/");
        const outputPath = path.resolve(outputImage).replace(/\\/g, "/");

        let command = `${pythonCmd} src/remove_bg.py "${inputPath}" "${outputPath}"`;

        // Add background replacement if specified
        if (options.background) {
            command += ` --background "${options.background}"`;
        }

        // Add AI enhancement if specified
        if (options.enhance) {
            command += ` --enhance`;
        }

        // Add vector conversion if specified
        if (options.vector) {
            command += ` --vector`;
        }

        // Add model selection if specified
        if (options.model) {
            command += ` --model "${options.model}"`;
        }

        console.log(`🚀 Running background removal with options: ${JSON.stringify(options)}`);

        return new Promise((resolve, reject) => {
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    reject(`❌ Error: ${stderr || error.message}`);
                    return;
                }
                console.log(`✅ Background removed successfully: ${outputImage}`);
                resolve({
                    success: true,
                    outputPath: outputImage,
                    message: "Background removed successfully"
                });
            });
        });
    } catch (error) {
        console.error(`❌ Error: ${error}`);
        throw error;
    }
}

// Export functions
module.exports = { removeBackground };