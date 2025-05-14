import cv2
import numpy as np
import pandas as pd
import argparse
import sys

# ----------------------------
# Read the CSV file containing color information
# ----------------------------
index = ["color", "color_name", "hex", "R", "G", "B"]

try:
    csv = pd.read_csv('colors.csv', names=index, header=None)
except FileNotFoundError:
    print("Error: 'colors.csv' file not found. Please ensure it's in the working directory.")
    sys.exit(1)

# ----------------------------
# Function to get the closest color name
# ----------------------------
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

# ----------------------------
# Mouse callback function
# ----------------------------
def draw_function(event, x, y, flags, param):
    global clicked, xpos, ypos, b, g, r
    image = param  # Get the image passed as a parameter

    if event == cv2.EVENT_LBUTTONDBLCLK:
        clicked = True
        xpos, ypos = x, y
        # Ensure the coordinates are within the frame boundaries
        if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
            b, g, r = image[y, x]
            b = int(b)
            g = int(g)
            r = int(r)
        else:
            clicked = False  # Ignore clicks outside the image

# ----------------------------
# Main function
# ----------------------------
def main():
    global clicked, xpos, ypos, b, g, r
    clicked = False
    xpos = ypos = 0
    b = g = r = 0
    color_name = ""
    color_r = color_g = color_b = 0

    # Argument parsing
    parser = argparse.ArgumentParser(description='Color Detection from Webcam or Image')
    parser.add_argument('-i', '--image', type=str, help='Path to the image file')
    args = parser.parse_args()

    # ----------------------------
    # Image Mode
    # ----------------------------
    if args.image:
        img_path = args.image
        img = cv2.imread(img_path)

        if img is None:
            print(f"Error: Unable to load image at '{img_path}'. Please check the path.")
            sys.exit(1)

        cv2.namedWindow('Image')
        cv2.setMouseCallback('Image', draw_function, img)

        while True:
            display_img = img.copy()

            if clicked:
                color_name = getColorName(r, g, b)
                color_r, color_g, color_b = r, g, b
                clicked = False

            # Draw rectangle with selected color
            cv2.rectangle(display_img, (20, 20), (400, 60), (color_b, color_g, color_r), -1)
            text = f'{color_name} R={color_r} G={color_g} B={color_b}'

            # Adjust text color for light background
            if (color_r + color_g + color_b) >= 600:
                text_color = (0, 0, 0)  # Black
            else:
                text_color = (255, 255, 255)  # White

            cv2.putText(display_img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)

            cv2.imshow('Image', display_img)

            if cv2.waitKey(20) & 0xFF == 27:
                break

        cv2.destroyAllWindows()

    # ----------------------------
    # Webcam Mode
    # ----------------------------
    else:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Cannot access the webcam.")
            sys.exit(1)

        cv2.namedWindow('Webcam')

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture frame from webcam.")
                break

            # Set mouse callback on the current frame for webcam
            cv2.setMouseCallback('Webcam', draw_function, frame)

            if clicked:
                color_name = getColorName(r, g, b)
                color_r, color_g, color_b = r, g, b
                clicked = False

            # Draw rectangle with selected color
            cv2.rectangle(frame, (20, 20), (400, 60), (color_b, color_g, color_r), -1)
            text = f'{color_name} R={color_r} G={color_g} B={color_b}'

            # Adjust text color for light background
            if (color_r + color_g + color_b) >= 600:
                text_color = (0, 0, 0)  # Black
            else:
                text_color = (255, 255, 255)  # White

            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)

            cv2.imshow('Webcam', frame)

            if cv2.waitKey(20) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

# ----------------------------
# Entry point
# ----------------------------
if __name__ == "__main__":
    main()
