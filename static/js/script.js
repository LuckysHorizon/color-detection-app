document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('imageCanvas');
    const context = canvas.getContext('2d');
    const video = document.createElement('video');
    const colorResult = document.getElementById('colorResult');
    const loadingOverlay = document.getElementById('loadingOverlay');
    let isWebcamActive = false;
    let uploadedImage; 
    let uploadedImageDataURL = ''; 
    let imageScale = { x: 1, y: 1 };

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
            if (uploadedImage) {
                // If an image was uploaded, draw it back onto the canvas
                drawImageOnCanvas(uploadedImage);
            }
        }
    }

    function drawWebcamFrame() {
        if (isWebcamActive) {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            requestAnimationFrame(drawWebcamFrame);
        }
    }

    // Draw the uploaded image on the canvas
    function drawImageOnCanvas(image) {
        const canvasMaxWidth = 600;
        const canvasMaxHeight = 400;

        const imageRatio = image.width / image.height;
        let drawWidth, drawHeight;

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

    // Handle double-click to get color from the canvas or webcam
    canvas.addEventListener('dblclick', (event) => {
        const x = event.offsetX;
        const y = event.offsetY;

        // Get pixel data directly from the canvas
        const pixelData = context.getImageData(x, y, 1, 1).data;
        const r = pixelData[0];
        const g = pixelData[1];
        const b = pixelData[2];

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
                const colorBox = `<div class="color-box" style="background-color: rgb(${data.rgb.r}, ${data.rgb.g}, ${data.rgb.b});"></div>`;
                const colorText = `<span>${data.color} (RGB: ${data.rgb.r}, ${data.rgb.g}, ${data.rgb.b})</span>`;
                colorResult.innerHTML = `${colorBox} ${colorText}`;
            }
        })
        .catch((err) => {
            console.error("Error detecting color:", err);
        });
    });

    // Handle image upload and display
    document.getElementById('uploadForm').addEventListener('submit', (event) => {
        event.preventDefault(); 
        loadingOverlay.style.display = 'flex'; 

        const formData = new FormData(event.target);

        fetch(event.target.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            loadingOverlay.style.display = 'none'; 

            if (data.url) {
                const imageUrl = encodeURI(data.url);
                uploadedImage = new Image();
                uploadedImage.crossOrigin = 'anonymous'; 

                uploadedImage.onload = function () {
                    if (isWebcamActive) {
                        stopWebcam();
                    }

                    drawImageOnCanvas(uploadedImage);
                    uploadedImageDataURL = imageUrl; 
                };

                uploadedImage.src = imageUrl;
            } else {
                console.error("Error: No image URL returned");
            }
        })
        .catch(err => {
            loadingOverlay.style.display = 'none'; 
            console.error("Error uploading image:", err);
        });
    });
});
