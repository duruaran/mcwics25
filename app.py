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
UPLOAD_FOLDER = os.path.join(current_dir, "uploads")
RESULTS_FOLDER = os.path.join(current_dir, "results")
TEMPLATES_FOLDER = os.path.join(current_dir, "pdf_templates")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)

# Flask configuration for static files
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULTS_FOLDER"] = RESULTS_FOLDER
app.config["TEMPLATES_FOLDER"] = TEMPLATES_FOLDER

# Debugging: Print paths to verify
print(f"UPLOAD_FOLDER: {os.path.abspath(UPLOAD_FOLDER)}")
print(f"RESULTS_FOLDER: {os.path.abspath(RESULTS_FOLDER)}")
print(f"TEMPLATES_FOLDER: {os.path.abspath(TEMPLATES_FOLDER)}")

# Add your existing backend code here...

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

# Define the 12 categories, their color palettes, and jewelry recommendations
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

jewelry_recommendations = {
    "Bright Winter": ["silver", "platinum", "white gold", "aquamarine"],
    "True Winter": ["silver", "platinum", "amethyst", "sapphire"],
    "Dark Winter": ["silver", "garnet", "onyx", "platinum"],
    "Bright Spring": ["gold", "rose gold", "amber", "coral"],
    "True Spring": ["gold", "rose gold", "citrine", "topaz"],
    "Light Spring": ["gold", "rose gold", "pearls", "moonstone"],
    "Light Summer": ["silver", "white gold", "aquamarine", "morganite"],
    "True Summer": ["silver", "platinum", "topaz", "sapphire"],
    "Soft Summer": ["silver", "matte metals", "jade", "moonstone"],
    "Soft Autumn": ["gold", "copper", "garnet", "amber"],
    "True Autumn": ["gold", "bronze", "citrine", "carnelian"],
    "Dark Autumn": ["gold", "tiger's eye", "bronze", "garnet"],
}

# Mapping seasons to template filenames
palette_templates = {
    "Bright Winter": "bright_winter_template.pdf",
    "True Winter": "true_winter_template.pdf",
    "Dark Winter": "dark_winter_template.pdf",
    "Bright Spring": "bright_spring_template.pdf",
    "True Spring": "true_spring_template.pdf",
    "Light Spring": "light_spring_template.pdf",
    "Light Summer": "light_summer_template.pdf",
    "True Summer": "true_summer_template.pdf",
    "Soft Summer": "soft_summer_template.pdf",
    "Soft Autumn": "soft_autumn_template.pdf",
    "True Autumn": "true_autumn_template.pdf",
    "Dark Autumn": "dark_autumn_template.pdf",
}

# Train a KMeans model for seasonal classification
X = np.array([color for colors in palette_colors.values() for color in colors])
y = np.array([season for season, colors in palette_colors.items() for _ in colors])
classifier = KMeans(n_clusters=12, random_state=42)
classifier.fit(X)

# Detect skin tone and season
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

                cropped_face_path = os.path.join(RESULTS_FOLDER, f"{os.path.basename(image_path).split('.')[0]}_face.jpg")
                cv2.imwrite(cropped_face_path, face_image_bgr)

                return avg_skin_tone, season, jewelry, cropped_face_path
            else:
                return None, "No skin pixels detected.", None, None
        else:
            return None, "No face detected.", None, None
    except Exception as e:
        return None, str(e), None, None

# Overlay the face image onto the template
def overlay_image_on_template(template_path, face_image_path, output_pdf_path):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from PyPDF2 import PdfReader, PdfWriter

        temp_pdf = os.path.join(RESULTS_FOLDER, "temp_overlay.pdf")

        c = canvas.Canvas(temp_pdf, pagesize=letter)
        c.drawImage(face_image_path, 100, 500, width=100, height=100)
        c.save()

        template_reader = PdfReader(template_path)
        overlay_reader = PdfReader(temp_pdf)
        writer = PdfWriter()

        for template_page, overlay_page in zip(template_reader.pages, overlay_reader.pages):
            template_page.merge_page(overlay_page)
            writer.add_page(template_page)

        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

    except Exception as e:
        print(f"ERROR: Failed to overlay image on template. {e}")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No 'image' file in the request."}), 400

    file = request.files["image"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    avg_skin_tone, season, jewelry, cropped_face_path = detect_skin_tone_and_season(file_path)
    if avg_skin_tone is not None:
        template_path = os.path.join(TEMPLATES_FOLDER, palette_templates[season])
        output_pdf_path = os.path.join(RESULTS_FOLDER, f"{file.filename.split('.')[0]}_results.pdf")
        overlay_image_on_template(template_path, cropped_face_path, output_pdf_path)

        # Serve the season-specific image and recommendations
        result_image_path = f"/results/{file.filename.split('.')[0]}_face.jpg"
        return jsonify({
            "season": season,
            "jewelry": jewelry,
            "image_url": result_image_path,
            "pdf_url": f"/results/{file.filename.split('.')[0]}_results.pdf",
        })
    else:
        return jsonify({"error": season}), 400
    
@app.route("/test", methods=["POST"])
def test():
    return jsonify({"message": "Test route is working!"})

if __name__ == "__main__":
    print(app.url_map)  # Print all registered routes
    app.run(debug=True)

