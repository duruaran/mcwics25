document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData();
    const fileInput = document.getElementById("image");
    const resultDiv = document.getElementById("result");

    if (!fileInput.files[0]) {
        alert("Please select an image file to upload.");
        return;
    }

    formData.append("image", fileInput.files[0]);

    // Show the result div and display "Processing..."
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

        // Redirect to a new page to display the result
        resultDiv.innerHTML = `
            <h2>Analysis Complete!</h2>
            <p>Your seasonal color type is determined. Download your personalized result below:</p>
            <a href="${fileURL}" download="Skin_Tone_Analysis.pdf" class="btn">Download PDF</a>
            <p><img src="${URL.createObjectURL(fileInput.files[0])}" alt="Uploaded Image" style="max-width: 200px; margin-top: 20px;"></p>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<h2>Error</h2><p>${error.message}</p>`;
    }
});
