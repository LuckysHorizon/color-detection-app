# Color Detection Web App

## Overview
A web application built using Python that allows users to upload images and detect the predominant colors in them. application is live at https://color-detection-app-jceb.onrender.com/

## Features
- Image upload for color detection.
- Displays detected colors and their RGB values.
- Supports JPEG and PNG formats.

## Technologies Used
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Libraries**: OpenCV, NumPy

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/LuckysHorizon/color-detection-app.git
   cd color-detection-app
   pip install -r requirements.txt
   ```

## Deployment on Render
1. Create a new web service on Render.
2. Connect your GitHub repository.
3. Set the build command to:
   ```
   pip install -r requirements.txt
   ```
4. Set the start command to:
   ```
   gunicorn app:app
   ```
5. Add environment variables for AWS credentials in Render dashboard.
6. Deploy the service.
7. The app will be available at the Render URL.

## Features
- Image upload for color detection.
- Displays detected colors and their RGB values.
- Supports JPEG and PNG formats.
- Responsive design for desktop, tablet, and mobile devices.

## Technologies Used
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Libraries**: OpenCV, NumPy
   pip install -r requirements.txt
