from flask import Flask, request, jsonify, send_file
import os
import face_recognition
import cv2
import numpy as np
from fpdf import FPDF
from sklearn.cluster import KMeans
from datetime import datetime

# Flask app setup
app = Flask(__name__)

# Ensure directories exist for uploads and results
UPLOAD_FOLDER = os.path.join(".", "uploads").replace("\\", "/")
RESULTS_FOLDER = os.path.join(".", "results").replace("\\", "/")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Define palette colors and recommendations
palette_colors = {
    "Spring": [[34, 70, 85], [60, 200, 180]],
    "Summer": [[100, 150, 200], [120, 180, 220]],
    "Autumn": [[20, 80, 70], [40, 140, 90]],
    "Winter": [[0, 0, 100], [180, 150, 200]]
}

jewelry_recommendations = {
    "Spring": ["gold", "rose gold", "amber", "bronze"],
    "Summer": ["silver", "platinum", "white gold", "aquamarine"],
    "Autumn": ["gold", "bronze", "copper", "garnet"],
    "Winter": ["silver", "platinum", "white gold", "ruby"]
}

# Train a KMeans model for seasonal classification
X = np.array([color for colors in palette_colors.values() for color in colors])
y = np.array([season for season, colors in palette_colors.items() for _ in colors])
classifier = KMeans(n_clusters=4, random_state=42)
classifier.fit(X)

# Function to detect skin tone and seasonal palette
def detect_skin_tone_and_season(image_path):
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)

        if face_locations:
            top, right, bottom, left = face_locations[0]
            face_image = image[top:bottom, left:right]

            face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
            hsv_face = cv2.cvtColor(face_image_bgr, cv2.COLOR_BGR2HSV)

            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv_face, lower_skin, upper_skin)

            skin_pixels = hsv_face[mask > 0]
            if len(skin_pixels) > 0:
                avg_skin_tone = np.mean(skin_pixels, axis=0)
                skin_tone_label = classifier.predict([avg_skin_tone])
                season = y[skin_tone_label[0]]
                jewelry = jewelry_recommendations.get(season, ["No recommendations available"])
                return avg_skin_tone, season, jewelry
            else:
                return None, "No skin pixels detected.", None
        else:
            return None, "No face detected.", None
    except Exception as e:
        return None, str(e), None

# Function to generate a PDF
def generate_pdf(file_name, avg_skin_tone, season, jewelry):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Skin Tone Analysis Results", ln=True, align='C')
    pdf.ln(10)  # Line break

    pdf.cell(0, 10, txt=f"Uploaded File: {file_name}", ln=True)
    pdf.cell(0, 10, txt=f"Average Skin Tone (HSV): {avg_skin_tone}", ln=True)
    pdf.cell(0, 10, txt=f"Detected Seasonal Palette: {season}", ln=True)
    pdf.cell(0, 10, txt=f"Recommended Jewelry: {', '.join(jewelry)}", ln=True)

    pdf_file_path = os.path.join(RESULTS_FOLDER, f"{file_name.split('.')[0]}_results.pdf")
    pdf.output(pdf_file_path)

    return pdf_file_path

# Flask route to handle uploads and analysis
@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["image"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Process the image
    avg_skin_tone, season, jewelry = detect_skin_tone_and_season(file_path)

    if avg_skin_tone is not None:
        # Generate a PDF with the results
        pdf_file_path = generate_pdf(file.filename, avg_skin_tone.tolist(), season, jewelry)

        # Return the PDF as a downloadable file
        return send_file(pdf_file_path, as_attachment=True)
    else:
        return jsonify({"error": season})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
