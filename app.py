from flask import Flask, render_template, request, jsonify, flash
import cv2
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import boto3
import io
from botocore.exceptions import NoCredentialsError

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'supersecretkey'

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# Load the CSV file containing color information
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# Function to get the closest color name from RGB values
def getColorName(R, G, B):
    minimum = float('inf')
    color_name = "Unknown"
    for i in range(len(csv)):
        d = np.sqrt((R - int(csv.loc[i, "R"])) ** 2 +
                    (G - int(csv.loc[i, "G"])) ** 2 +
                    (B - int(csv.loc[i, "B"])) ** 2)
        if d < minimum:
            minimum = d
            color_name = csv.loc[i, "color_name"]
    return color_name

# Conversion Functions
def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

def rgb_to_hsl(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
    max_color, min_color = max(r, g, b), min(r, g, b)
    l = (max_color + min_color) / 2
    if max_color == min_color:
        h = s = 0
    else:
        d = max_color - min_color
        s = d / (2 - max_color - min_color) if l > 0.5 else d / (max_color + min_color)
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[max_color]
        h /= 6
    return int(h * 360), int(s * 100), int(l * 100)

def rgb_to_hsv(r, g, b):
    r, g, b = r / 255, g / 255, b / 255
    max_color, min_color = max(r, g, b), min(r, g, b)
    v = max_color
    d = max_color - min_color
    s = 0 if max_color == 0 else d / max_color
    h = 0
    if max_color != min_color:
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[max_color]
        h /= 6
    return int(h * 360), int(s * 100), int(v * 100)

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100
    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255
    k = min(c, m, y)
    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    return int(c * 100), int(m * 100), int(y * 100), int(k * 100)

# Upload to AWS S3
def upload_to_aws(file_stream, bucket, s3_file):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name='eu-north-1')  # Replace with your bucket's region

    try:
        # Upload file to S3
        s3.upload_fileobj(file_stream, bucket, s3_file)  # Upload using file-like object
        file_url = f'https://{bucket}.s3.amazonaws.com/{s3_file}'
        print(f'Successfully uploaded {s3_file} to {bucket}. File URL: {file_url}')
        return file_url  # Return the URL of the uploaded file
    except FileNotFoundError:
        print('File not found. Please check the file path.')  # Log file not found error
        return None
    except NoCredentialsError:
        print('Credentials not available. Please check your AWS credentials.')  # Log credentials error
        return None
    except Exception as e:
        print(f'Error uploading file: {str(e)}')  # Log any other exceptions
        return None

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')  # Render home.html

@app.route('/index')
def index():
    return render_template('index.html')

# Route to upload an image
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Convert file to file-like object
            file_stream = io.BytesIO()
            file.save(file_stream)
            file_stream.seek(0)  # Reset file stream position

            # Upload to S3
            image_url = upload_to_aws(file_stream, AWS_BUCKET_NAME, file.filename)
            
            if image_url:
                print(f"Image URL returned: {image_url}")  # Debug: Log the URL being returned
                return jsonify({'url': image_url}), 200  # Return the S3 image URL
            else:
                return jsonify({'error': 'Failed to upload to AWS'}), 500
        except Exception as e:
            print(f'Error uploading to AWS: {str(e)}')  # Log any exceptions
            return jsonify({'error': 'Error uploading to AWS'}), 500

# Route to handle color detection for uploaded images
@app.route('/get_color_image', methods=['POST'])
def get_color_image():
    data = request.json
    x, y = data['x'], data['y']
    img_path = data['image']

    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], img_path))

    if img is None:
        return jsonify({'error': 'Image not found'}), 404

    img = cv2.resize(img, (600, 400))  # Resize image to fit the canvas

    height, width, _ = img.shape
    if 0 <= x < width and 0 <= y < height:
        b, g, r = img[y, x]
        color_name = getColorName(r, g, b)

        # Add conversions
        hex_color = rgb_to_hex(r, g, b)
        hsl_color = rgb_to_hsl(r, g, b)
        hsv_color = rgb_to_hsv(r, g, b)
        cmyk_color = rgb_to_cmyk(r, g, b)

        return jsonify({
            'color': color_name,
            'rgb': {'r': r, 'g': g, 'b': b},
            'hex': hex_color,
            'hsl': hsl_color,
            'hsv': hsv_color,
            'cmyk': cmyk_color
        })

    return jsonify({'error': 'Coordinates out of bounds'}), 400

# New Route to handle zoom-in magnifier
@app.route('/get_zoomed_image', methods=['POST'])
def get_zoomed_image():
    data = request.json
    x, y = data['x'], data['y']
    zoom_factor = data.get('zoom_factor', 2)  # Default zoom factor is 2
    img_path = data['image']

    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], img_path))

    if img is None:
        return jsonify({'error': 'Image not found'}), 404

    height, width, _ = img.shape
    zoom_size = 100  # Size of the zoomed area

    x1 = max(0, x - zoom_size // 2)
    y1 = max(0, y - zoom_size // 2)
    x2 = min(width, x + zoom_size // 2)
    y2 = min(height, y + zoom_size // 2)

    cropped_img = img[y1:y2, x1:x2]
    zoomed_img = cv2.resize(cropped_img, (zoom_size * zoom_factor, zoom_size * zoom_factor), interpolation=cv2.INTER_CUBIC)

    _, buffer = cv2.imencode('.jpg', zoomed_img)
    zoomed_img_bytes = buffer.tobytes()

    return jsonify({'zoomed_image': zoomed_img_bytes.hex()})

# Route to handle color detection for webcam (RGB values)
@app.route('/get_color_webcam', methods=['POST'])
def get_color_webcam():
    data = request.json
    r, g, b = data['r'], data['g'], data['b']

    # Get the closest color name using the RGB values
    color_name = getColorName(r, g, b)

    # Add conversions
    hex_color = rgb_to_hex(r, g, b)
    hsl_color = rgb_to_hsl(r, g, b)
    hsv_color = rgb_to_hsv(r, g, b)
    cmyk_color = rgb_to_cmyk(r, g, b)

    return jsonify({
        'color': color_name,
        'rgb': {'r': r, 'g': g, 'b': b},
        'hex': hex_color,
        'hsl': hsl_color,
        'hsv': hsv_color,
        'cmyk': cmyk_color
    })

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
