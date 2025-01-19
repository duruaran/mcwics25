# mcwics25

## About the Project

### What Our Project Does

*Color Seasons* is a web application that helps users discover their personalized seasonal color palette based on their unique skin tone.

By simply uploading a photo, the application analyzes the image using advanced AI techniques and provides a downloadable PDF with tailored color recommendations. 

The personalized PDF includes:

* **Seasonal Color Analysis** : Identifies whether you belong to one of 12 nuanced seasonal categories (e.g., True Winter, Bright Spring).
* **Jewelry Options** : Suggests jewelry tones and stones that suit your complexion.
* **Clothing Suggestions** : Recommends clothing colors and styles that complement your unique palette.
* **Celebrity Inspiration** : Provides examples of celebrities who share your seasonal palette, offering style inspiration from recognizable figures.

### How We Built It

This project was developed using a modern technology stack with a focus on scalability, accuracy, and user-friendliness:

* **Backend** : Built with Flask, integrating libraries such as `face_recognition` for image analysis, `KMeans` for skin tone clustering, and `ReportLab` for generating personalized PDF outputs.
* **Frontend** : Designed with HTML, CSS, and JavaScript for an intuitive, responsive user interface.
* **Architecture** :
* Users upload their photo, which is processed by the Flask backend.
* The backend performs facial detection and seasonal color analysis.
* Results are compiled into a professional PDF document and made available for download.
* **Error Handling** : The system manages edge cases, such as invalid file formats or images without a face, ensuring a seamless user experience.
