<<<<<<< HEAD
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
        return jsonify({'color': color_name, 'rgb': {'r': r, 'g': g, 'b': b}})

    return jsonify({'error': 'Coordinates out of bounds'}), 400

# Route to handle color detection for webcam (RGB values)
@app.route('/get_color_webcam', methods=['POST'])
def get_color_webcam():
    data = request.json
    r, g, b = data['r'], data['g'], data['b']

    # Get the closest color name using the RGB values
    color_name = getColorName(r, g, b)

    return jsonify({'color': color_name, 'rgb': {'r': r, 'g': g, 'b': b}})

if __name__ == '__main__':
    app.run(debug=True)
=======
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
        return jsonify({'color': color_name, 'rgb': {'r': r, 'g': g, 'b': b}})

    return jsonify({'error': 'Coordinates out of bounds'}), 400

# Route to handle color detection for webcam (RGB values)
@app.route('/get_color_webcam', methods=['POST'])
def get_color_webcam():
    data = request.json
    r, g, b = data['r'], data['g'], data['b']

    # Get the closest color name using the RGB values
    color_name = getColorName(r, g, b)

    return jsonify({'color': color_name, 'rgb': {'r': r, 'g': g, 'b': b}})

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 39f1fbe (Add files via upload)
