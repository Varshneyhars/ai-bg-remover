import { removeBackground } from '@varshneyhars/ai-bg-remover';
import path from 'path';
import fs from 'fs';
import { promisify } from 'util';
import formidable from 'formidable';

// Disable the default body parser
export const config = {
  api: {
    bodyParser: false,
  },
};

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(process.cwd(), 'public', 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Parse the form data
    const form = formidable({
      uploadDir: uploadsDir,
      keepExtensions: true,
      maxFileSize: 5 * 1024 * 1024, // 5MB
    });

    const [fields, files] = await new Promise((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });

    const file = files.image;
    if (!file) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    // Generate output paths
    const timestamp = Date.now();
    const outputFileName = `output-${timestamp}.png`;
    const outputPath = path.join(uploadsDir, outputFileName);

    // Process the image
    const options = {
      background: fields.background || 'linear-gradient(to right, #ff7e5f, #feb47b)',
      enhance: fields.enhance === 'true',
      vector: fields.vector === 'true',
      model: fields.model || 'silueta'
    };

    const result = await removeBackground(file.filepath, outputPath, options);

    // Return the result
    return res.status(200).json({
      ...result,
      outputUrl: `/uploads/${outputFileName}`,
      svgUrl: options.vector ? `/uploads/output-${timestamp}.svg` : null
    });

  } catch (error) {
    console.error('🔥 Error removing background:', error);
    return res.status(500).json({ 
      error: error.message || 'Failed to process image',
      details: error.toString()
    });
  }
} 