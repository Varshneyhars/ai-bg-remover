const { exec } = require("child_process");
const path = require("path");
const fs = require("fs");

// Get the absolute path to the Python script
function getPythonScriptPath() {
    // Get the directory where this module is located
    const moduleDir = path.dirname(require.main.filename);
    // Look for the script in the node_modules directory
    const scriptPath = path.join(moduleDir, 'node_modules', '@varshneyhars/ai-bg-remover', 'src', 'remove_bg.py');
    
    // If not found in node_modules, try the current directory (for development)
    if (!fs.existsSync(scriptPath)) {
        const devScriptPath = path.join(__dirname, 'remove_bg.py');
        if (fs.existsSync(devScriptPath)) {
            return devScriptPath;
        }
    }
    
    return scriptPath;
}

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
        
        // Get the Python script path
        const scriptPath = getPythonScriptPath();
        if (!fs.existsSync(scriptPath)) {
            throw new Error(`Python script not found at: ${scriptPath}`);
        }

        let command = `${pythonCmd} "${scriptPath}" "${inputPath}" "${outputPath}"`;

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