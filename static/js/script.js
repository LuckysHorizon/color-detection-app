document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('imageCanvas');
    const context = canvas.getContext('2d');
    const video = document.createElement('video');
    const colorResult = document.getElementById('colorResult');
    const loadingOverlay = document.getElementById('loadingOverlay'); // Loading overlay element
    let isWebcamActive = false;
    let uploadedImage; // Variable to store the uploaded image
    let uploadedImageDataURL = ''; // Store the image URL for switching back
    let imageScale = { x: 1, y: 1 }; // To store the scaling factors for correct color detection

    // Webcam button click
    document.getElementById('webcamButton').addEventListener('click', () => {
        if (isWebcamActive) {
            stopWebcam();
        } else {
            startWebcam();
        }
    });

    // Start webcam and draw video on the canvas
    function startWebcam() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    video.srcObject = stream;
                    video.play();
                    isWebcamActive = true;

                    video.addEventListener('loadeddata', () => {
                        canvas.width = 600;
                        canvas.height = 400;
                        drawWebcamFrame();
                    });
                })
                .catch((err) => {
                    console.error("Error accessing webcam:", err);
                });
        }
    }

    function stopWebcam() {
        if (isWebcamActive) {
            video.pause();
            video.srcObject.getTracks().forEach(track => track.stop());
            isWebcamActive = false;
            context.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    function drawWebcamFrame() {
        if (isWebcamActive) {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            requestAnimationFrame(drawWebcamFrame);
        }
    }

    // Resize image to fit within the canvas and adjust borders
    function drawImageOnCanvas(image) {
        const canvasMaxWidth = 600;
        const canvasMaxHeight = 400;

        const imageRatio = image.width / image.height;
        let drawWidth, drawHeight;

        // Adjust canvas dimensions based on image aspect ratio
        if (imageRatio > 1) { // Landscape image
            drawWidth = canvasMaxWidth;
            drawHeight = canvasMaxWidth / imageRatio;
        } else { // Portrait or square image
            drawHeight = canvasMaxHeight;
            drawWidth = canvasMaxHeight * imageRatio;
        }

        // Set canvas size to match image
        canvas.width = drawWidth;
        canvas.height = drawHeight;

        // Store scaling factors for accurate color detection
        imageScale.x = image.width / drawWidth;
        imageScale.y = image.height / drawHeight;

        // Draw the image centered inside the canvas
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(image, 0, 0, drawWidth, drawHeight);

        // Add a border around the canvas
        canvas.style.border = "5px solid #4CAF50";
        canvas.style.borderRadius = "10px";
    }

    // Handle double-click to get color from image
    canvas.addEventListener('dblclick', (event) => {
        const x = event.offsetX * imageScale.x; // Scale the x-coordinate to match the original image
        const y = event.offsetY * imageScale.y; // Scale the y-coordinate to match the original image

        // Get pixel data only if an image is displayed on the canvas
        if (uploadedImage) {
            const pixelData = context.getImageData(event.offsetX, event.offsetY, 1, 1).data; // Get the pixel data (RGBA)
            const r = pixelData[0];
            const g = pixelData[1];
            const b = pixelData[2];

            // Send the RGB data to the server for color name detection
            fetch('/get_color_webcam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ r: r, g: g, b: b }),
            })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    colorResult.textContent = data.error;
                } else {
                    // Create color box beside color name
                    const colorBox = `<div class="color-box" style="background-color: rgb(${data.rgb.r}, ${data.rgb.g}, ${data.rgb.b});"></div>`;
                    const colorText = `<span>${data.color} (RGB: ${data.rgb.r}, ${data.rgb.g}, ${data.rgb.b})</span>`;
                    colorResult.innerHTML = `${colorBox} ${colorText}`;
                }
            })
            .catch((err) => {
                console.error("Error detecting color:", err);
            });
        } else {
            console.warn("No uploaded image to detect color from.");
        }
    });

    // Handle image upload and display
    document.getElementById('uploadForm').addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent default form submission
        loadingOverlay.style.display = 'flex'; // Show loading overlay

        const formData = new FormData(event.target);

        fetch(event.target.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingOverlay.style.display = 'none'; // Hide loading overlay

            if (data.url) {
                const imageUrl = encodeURI(data.url);
                uploadedImage = new Image();
                uploadedImage.crossOrigin = 'anonymous'; // Allow cross-origin image loading

                uploadedImage.onload = function () {
                    // Stop webcam if it's active when an image is uploaded
                    if (isWebcamActive) {
                        stopWebcam();
                    }

                    // Draw the resized uploaded image on the canvas
                    drawImageOnCanvas(uploadedImage);
                    uploadedImageDataURL = imageUrl; // Store the uploaded image URL
                };

                uploadedImage.src = imageUrl;
            } else {
                console.error("Error: No image URL returned");
            }
        })
        .catch(err => {
            loadingOverlay.style.display = 'none'; // Hide loading overlay
            console.error("Error uploading image:", err);
        });
    });
});
