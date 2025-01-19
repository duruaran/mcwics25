document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById("image");

    if (!fileInput.files[0]) {
        alert("Please select an image file to upload.");
        return;
    }

    formData.append("image", fileInput.files[0]);

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "An error occurred while processing the image.");
        }

        // For successful response, handle PDF download
        const blob = await response.blob();
        const fileURL = URL.createObjectURL(blob);

        // Display the PDF download link
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `
            <h2>Analysis Complete!</h2>
            <p>Your seasonal color type has been determined.</p>
            <a href="${fileURL}" download="Analysis_Result.pdf" class="btn">Download PDF</a>
        `;
        resultDiv.classList.remove("hidden");
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});
