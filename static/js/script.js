document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData();
    const fileInput = document.getElementById("image");
    const resultDiv = document.getElementById("result");

    if (!fileInput.files[0]) {
        alert("Please select an image file to upload.");
        return;
    }

    formData.append("image", fileInput.files[0]);

    resultDiv.classList.remove("hidden");
    resultDiv.innerHTML = "<h2>Processing...</h2><p>Your result will appear here shortly.</p>";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "An error occurred while processing the image.");
        }

        // Get the PDF file URL
        const blob = await response.blob();
        const fileURL = URL.createObjectURL(blob);

        resultDiv.innerHTML = `
            <h2>Analysis Complete!</h2>
            <p>Your seasonal color type has been determined. Download your personalized result below:</p>
            <a href="${fileURL}" download="Skin_Tone_Analysis.pdf">Download PDF</a>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<h2>Error</h2><p>${error.message}</p>`;
    }
});
