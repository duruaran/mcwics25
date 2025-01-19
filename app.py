from flask import Flask, request, jsonify, send_file, render_template
import os
import face_recognition
import cv2
import numpy as np
from PyPDF2 import PdfReader, PdfWriter
from sklearn.cluster import KMeans

# Flask app setup
app = Flask(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, "static/uploads")
RESULTS_FOLDER = os.path.join(current_dir, "results")
TEMPLATES_FOLDER = os.path.join(current_dir, "pdf_templates")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Seasonal palettes and KMeans setup
palette_colors = {
    "Bright Winter": [[255, 0, 0], [0, 0, 255], [255, 255, 255], [0, 255, 255]],
    "True Winter": [[0, 0, 139], [139, 0, 139], [255, 255, 255], [25, 25, 112]],
    "Dark Winter": [[139, 69, 19], [128, 0, 0], [0, 100, 0], [47, 79, 79]],
    "Bright Spring": [[255, 140, 0], [255, 215, 0], [127, 255, 0], [255, 105, 180]],
    "True Spring": [[255, 165, 0], [255, 223, 186], [255, 250, 205], [127, 255, 212]],
    "Light Spring": [[255, 239, 213], [255, 228, 196], [240, 230, 140], [173, 216, 230]],
    "Light Summer": [[176, 224, 230], [224, 255, 255], [216, 191, 216], [135, 206, 250]],
    "True Summer": [[70, 130, 180], [100, 149, 237], [176, 196, 222], [135, 206, 250]],
    "Soft Summer": [[119, 136, 153], [112, 128, 144], [211, 211, 211], [47, 79, 79]],
    "Soft Autumn": [[205, 133, 63], [210, 105, 30], [139, 69, 19], [160, 82, 45]],
    "True Autumn": [[222, 184, 135], [210, 105, 30], [178, 34, 34], [128, 0, 0]],
    "Dark Autumn": [[85, 107, 47], [139, 69, 19], [34, 139, 34], [0, 100, 0]],
}

X = np.array([color for colors in palette_colors.values() for color in colors])
y = np.array([season for season, colors in palette_colors.items() for _ in colors])
classifier = KMeans(n_clusters=len(palette_colors), random_state=42)
classifier.fit(X)

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/references")
def references():
    return render_template("references.html")

@app.route("/color_seasons")
def color_seasons():
    return render_template("color_seasons.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No 'image' file in the request."}), 400

    file = request.files["image"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    avg_skin_tone, season = detect_skin_tone_and_season(file_path)
    if avg_skin_tone is not None:
        template_path = os.path.join(TEMPLATES_FOLDER, f"{season.lower().replace(' ', '_')}_template.pdf")
        output_pdf_path = os.path.join(RESULTS_FOLDER, f"{file.filename.split('.')[0]}_results.pdf")
        overlay_image_on_template(template_path, file_path, output_pdf_path)

        return send_file(output_pdf_path, as_attachment=True)
    else:
        # Return an error message if no face is detected
        return jsonify({"error": season}), 400

# Helper functions
def detect_skin_tone_and_season(image_path):
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            return None, "No face detected."

        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
        hsv_face = cv2.cvtColor(face_image_bgr, cv2.COLOR_BGR2HSV)

        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv_face, lower_skin, upper_skin)

        skin_pixels = hsv_face[mask > 0]
        if skin_pixels.size == 0:
            return None, "No skin pixels detected."

        avg_skin_tone = np.mean(skin_pixels, axis=0)
        skin_tone_label = classifier.predict([avg_skin_tone])
        season = y[skin_tone_label[0]]
        return avg_skin_tone, season
    except Exception as e:
        return None, str(e)

def overlay_image_on_template(template_path, face_image_path, output_pdf_path):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, landscape
        from PyPDF2 import PdfReader, PdfWriter

        temp_pdf = os.path.join(RESULTS_FOLDER, "temp_overlay.pdf")

        custom_pagesize = (1920, 1400)

        # Create the overlay canvas
        c = canvas.Canvas(temp_pdf, pagesize=landscape(custom_pagesize))

        # Adjust the y-coordinate to move the image further up
        c.drawImage(face_image_path, 140, 750, width=200, height=200)  # Adjusted y=850 for a higher position
        c.save()

        # Merge the overlay with the template
        template_reader = PdfReader(template_path)
        overlay_reader = PdfReader(temp_pdf)
        writer = PdfWriter()

        for template_page, overlay_page in zip(template_reader.pages, overlay_reader.pages):
            template_page.merge_page(overlay_page)
            writer.add_page(template_page)

        # Save the final PDF
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

    except Exception as e:
        print(f"ERROR: Failed to overlay image on template. {e}")


if __name__ == "__main__":
    app.run(debug=True)
