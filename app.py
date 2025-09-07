import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import base64
from io import BytesIO
from PIL import Image
from color_processor import ColorProcessor
from palette_generator import PaletteGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "colormind-ai-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize processors
color_processor = ColorProcessor()
palette_generator = PaletteGenerator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload JPG or PNG images only.'}), 400
        
        # Process the image
        image = Image.open(file.stream)
        
        # Extract colors using K-Means
        dominant_colors = color_processor.extract_dominant_colors(image)
        
        # Get style and mood from request
        style = request.form.get('style', 'scandinavian')
        mood = request.form.get('mood', 'calm')
        lighting = request.form.get('lighting', 'daylight')
        
        # Generate palette
        palette_data = palette_generator.generate_palette(
            dominant_colors, style, mood, lighting
        )
        
        return jsonify({
            'success': True,
            'dominant_colors': dominant_colors,
            'palette': palette_data
        })
        
    except Exception as e:
        logging.error(f"Error processing upload: {str(e)}")
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/generate_palette', methods=['POST'])
def generate_palette():
    try:
        data = request.get_json()
        
        # Get base colors from request
        base_colors = data.get('colors', [])
        style = data.get('style', 'scandinavian')
        mood = data.get('mood', 'calm')
        lighting = data.get('lighting', 'daylight')
        harmony_type = data.get('harmony', 'complementary')
        
        if not base_colors:
            return jsonify({'error': 'No base colors provided'}), 400
        
        # Generate palette based on color theory
        palette_data = palette_generator.generate_harmony_palette(
            base_colors, harmony_type, style, mood, lighting
        )
        
        return jsonify({
            'success': True,
            'palette': palette_data
        })
        
    except Exception as e:
        logging.error(f"Error generating palette: {str(e)}")
        return jsonify({'error': f'Error generating palette: {str(e)}'}), 500

@app.route('/export_palette', methods=['POST'])
def export_palette():
    try:
        data = request.get_json()
        palette_colors = data.get('colors', [])
        palette_name = data.get('name', 'ColorMind Palette')
        export_format = data.get('format', 'png')
        
        if not palette_colors:
            return jsonify({'error': 'No colors to export'}), 400
        
        if export_format == 'png':
            # Generate PNG swatch
            image_buffer = palette_generator.create_swatch_image(palette_colors, palette_name)
            
            return send_file(
                BytesIO(image_buffer),
                mimetype='image/png',
                as_attachment=True,
                download_name=f'{palette_name.replace(" ", "_")}_palette.png'
            )
        
        elif export_format == 'json':
            # Return JSON data
            export_data = {
                'name': palette_name,
                'colors': palette_colors,
                'created_at': palette_generator.get_current_timestamp()
            }
            
            return jsonify(export_data)
        
    except Exception as e:
        logging.error(f"Error exporting palette: {str(e)}")
        return jsonify({'error': f'Error exporting palette: {str(e)}'}), 500

@app.route('/adjust_lighting', methods=['POST'])
def adjust_lighting():
    try:
        data = request.get_json()
        colors = data.get('colors', [])
        lighting_type = data.get('lighting', 'daylight')
        
        if not colors:
            return jsonify({'error': 'No colors provided'}), 400
        
        adjusted_colors = palette_generator.adjust_for_lighting(colors, lighting_type)
        
        return jsonify({
            'success': True,
            'colors': adjusted_colors
        })
        
    except Exception as e:
        logging.error(f"Error adjusting lighting: {str(e)}")
        return jsonify({'error': f'Error adjusting lighting: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    logging.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error occurred'}), 500
