import os
from app import detect_skin_tone_and_season, overlay_image_on_template

# Paths
folder_path = "testing_images"
results_path = "results"
templates_path = "pdf_templates"  # Updated path to match app.py

# Ensure directories exist
if not os.path.exists(folder_path):
    print(f"Error: Folder '{folder_path}' does not exist. Please check the path.")
    exit()

if not os.path.exists(results_path):
    os.makedirs(results_path)

# Process all test images
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):  # Check for image files
        print(f"\nProcessing {filename}...")

        # Detect skin tone, season, and other details
        avg_skin_tone, season, jewelry, cropped_face_path = detect_skin_tone_and_season(file_path)

        if avg_skin_tone is not None:
            print(f"Detected Average Skin Tone (HSV): {avg_skin_tone}")
            print(f"Detected Category: {season}")
            print(f"Recommended Jewelry Colors: {', '.join(jewelry)}")

            # Check if the template exists for the detected category
            template_file = f"{season.lower().replace(' ', '_')}_template.pdf"
            template_path = os.path.join(templates_path, template_file)
            if not os.path.exists(template_path):
                print(f"Error: Template for '{season}' not found: {template_file}")
                continue

            # Generate the output PDF
            output_pdf_path = os.path.join(
                results_path, f"{filename.split('.')[0]}_{season.lower().replace(' ', '_')}_results.pdf"
            )
            overlay_image_on_template(template_path, cropped_face_path, output_pdf_path)
            print(f"Generated PDF for {filename}: {output_pdf_path}")
        else:
            print(f"Error for {filename}: {season}")  # Error message if detection fails
    else:
        print(f"Skipping non-image file: {filename}")
