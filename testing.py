import os
from backend import detect_skin_tone_and_season

# Path to the folder with test images
folder_path = "testing_images"

if not os.path.exists(folder_path):
    print(f"Folder '{folder_path}' does not exist. Please check the path.")
    exit()

# Process all test images
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if filename.lower().endswith(('.jpg', '.png', '.jpeg')):  # Check for image files
        print(f"\nProcessing {filename}...")
        avg_skin_tone, season, jewelry = detect_skin_tone_and_season(file_path)
        if avg_skin_tone is not None:
            print(f"Detected Average Skin Tone (HSV): {avg_skin_tone}")
            print(f"Detected Seasonal Palette: {season}")
            print(f"Recommended Jewelry Colors: {', '.join(jewelry)}")
        else:
            print(f"Error for {filename}: {season}")
    else:
        print(f"Skipping non-image file: {filename}")
