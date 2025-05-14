document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('imageCanvas');
    const context = canvas.getContext('2d');
    const video = document.createElement('video');
    const loadingOverlay = document.getElementById('loadingOverlay');
    let isWebcamActive = false;
    let uploadedImage;
    let imageScale = { x: 1, y: 1 };

    // Webcam start/stop functionality
    document.getElementById('webcamButton').addEventListener('click', () => {
        if (isWebcamActive) {
            stopWebcam();
        } else {
            startWebcam();
        }
    });

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

    function drawImageOnCanvas(image) {
        const canvasMaxWidth = 600;
        const canvasMaxHeight = 400;
        const imageRatio = image.width / image.height;
        let drawWidth, drawHeight;

        if (imageRatio > 1) {
            drawWidth = canvasMaxWidth;
            drawHeight = canvasMaxWidth / imageRatio;
        } else {
            drawHeight = canvasMaxHeight;
            drawWidth = canvasMaxHeight * imageRatio;
        }

        canvas.width = drawWidth;
        canvas.height = drawHeight;

        imageScale.x = image.width / drawWidth;
        imageScale.y = image.height / drawHeight;

        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(image, 0, 0, drawWidth, drawHeight);
    }

    // Detect color on double-click
    canvas.addEventListener('dblclick', (event) => {
        const x = event.offsetX * imageScale.x;
        const y = event.offsetY * imageScale.y;

        if (uploadedImage) {
            const pixelData = context.getImageData(event.offsetX, event.offsetY, 1, 1).data;
            const r = pixelData[0];
            const g = pixelData[1];
            const b = pixelData[2];

            // Send RGB values to the server for color detection
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
                    document.getElementById("colorLabel").textContent = data.error;
                } else {
                    // Update the color preview box
                    document.getElementById("colorPreview").style.backgroundColor = `rgb(${data.rgb.r}, ${data.rgb.g}, ${data.rgb.b})`;

                    // Update each color value box with detected values
                    document.getElementById("rgbValue").textContent = `${data.rgb.r}, ${data.rgb.g}, ${data.rgb.b}`;
                    document.getElementById("hexValue").textContent = `${data.hex}`;
                    document.getElementById("hslValue").textContent = `HSL: ${data.hsl[0]}, ${data.hsl[1]}%, ${data.hsl[2]}%`;
                    document.getElementById("hsvValue").textContent = `HSV: ${data.hsv[0]}, ${data.hsv[1]}%, ${data.hsv[2]}%`;
                    document.getElementById("cmykValue").textContent = `CMYK: ${data.cmyk[0]}%, ${data.cmyk[1]}%, ${data.cmyk[2]}%, ${data.cmyk[3]}%`;                    
                    // Display color name
                    document.getElementById("color_name").textContent = `Color Name: ${data.color}`;
                }
            })
            .catch((err) => {
                console.error("Error detecting color:", err);
            });
        } else {
            console.warn("No uploaded image to detect color from.");
        }
    });

    // Handle image upload
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
                uploadedImage = new Image();
                uploadedImage.crossOrigin = 'anonymous';
                uploadedImage.onload = function () {
                    if (isWebcamActive) {
                        stopWebcam();
                    }
                    drawImageOnCanvas(uploadedImage);
                };
                uploadedImage.src = encodeURI(data.url);
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
