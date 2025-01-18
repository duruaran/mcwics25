import face_recognition
import cv2

# image = face_recognition.load_image_file("input.jpg")
# face_locations = face_recognition.face_locations(image)
#
# top, right, bottom, left = face_locations[0]
# face_image = image[top:bottom, left:right]

test_images = ["testing_images/image1.jpeg", "testing_images/image2.jpg", "testing_images/image3.jpg", "testing_images/image4.jpeg", "testing_images/no_face.jpeg"]
for img_path in test_images:
    image = face_recognition.load_image_file(img_path)
    face_locations = face_recognition.face_locations(image)
    if face_locations:
        top, right, bottom, left = face_locations[0]
        print(f"Face detected in {img_path}: Top={top}, Right={right}, Bottom={bottom}, Left={left}")
    else:
        print(f"No face detected in {img_path}")

