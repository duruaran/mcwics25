import unittest
from app import app
import os

class FunctionalTestCase(unittest.TestCase):

    def setUp(self):
        """Set up the test client and test files."""
        app.testing = True
        self.client = app.test_client()
        # Update the paths to match your folder structure
        self.test_image_path = os.path.join(os.getcwd(), "static", "uploads", "test_face.jpg")
        self.no_face_image_path = os.path.join(os.getcwd(), "static", "uploads", "no_face.jpg")
        self.invalid_file_path = os.path.join(os.getcwd(), "static", "uploads", "test_invalid.txt")

    def test_file_upload_success(self):
        """Test if uploading an image works and generates a PDF."""
        with open(self.test_image_path, "rb") as test_image:
            data = {"image": test_image}
            response = self.client.post("/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"%PDF", response.data)  # PDF files start with "%PDF"



    def test_file_upload_no_face(self):
        """Test if uploading an image with no face triggers the error."""
        with open(self.no_face_image_path, "rb") as test_image:
            data = {"image": test_image}
            response = self.client.post("/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No face detected", response.data)

    def test_invalid_file_type(self):
        """Test if uploading an invalid file type returns an error."""
        with open(self.invalid_file_path, "rb") as test_file:
            data = {"image": test_file}
            response = self.client.post("/analyze", data=data, content_type="multipart/form-data")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
