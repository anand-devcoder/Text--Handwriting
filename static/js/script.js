document.addEventListener('DOMContentLoaded', function () {

    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3'); // Step 3 container for preview

    const toStep2 = document.getElementById('toStep2'); // Step 1 → Step 2
    const toStep3 = document.getElementById('toStep3'); // Step 2 → Step 3
    const backStep2 = document.getElementById('backStep2'); // Back button in Step 2
    const newBtn = document.getElementById('new');

    const previewContainer = document.getElementById('previewContainer');
    const downloadLink = document.getElementById('downloadLink');

    // =======================
    // STEP 1 → STEP 2 with custom popup validation
    // =======================
    toStep2.addEventListener('click', () => {
        const textInput = document.getElementById('text_input').value.trim();
        const uploadImage = document.getElementById('upload_image').files;

        // Only show popup if both text and image are empty
        if (!textInput && uploadImage.length === 0) {
            const popupOverlay = document.getElementById('popupOverlay');
            const popupText = document.getElementById('popupText');
            popupText.textContent = "You have not entered any text or uploaded any image. Please enter text or upload an image before proceeding.";
            popupOverlay.style.display = 'flex'; // show popup
            return; // stop moving to Step 2
        }

        // If either text or image is present, move to Step 2 as usual
        step1.style.display = 'none';
        step2.style.display = 'block';
    });

    // =======================
    // STEP 2 → STEP 3 (Generate + Preview) – unchanged
    // =======================
    toStep3.addEventListener('click', async () => {
        step2.style.display = 'none';
        step3.style.display = 'block';

        const formData = new FormData();
        formData.append('text_input', document.getElementById('text_input').value);
        if (document.getElementById('upload_image').files.length > 0) {
            formData.append('upload_image', document.getElementById('upload_image').files[0]);
        }
        formData.append('paper', document.getElementById('paper').value);
        formData.append('orientation', document.querySelector('input[name="orientation"]:checked').value);
        formData.append('margin_top', document.getElementById('margin_top').value);
        formData.append('margin_bottom', document.getElementById('margin_bottom').value);
        formData.append('margin_left', document.getElementById('margin_left').value);
        formData.append('margin_right', document.getElementById('margin_right').value);
        formData.append('font_size', document.getElementById('font_size').value);
        formData.append('output_type', document.getElementById('output_type').value);

        try {
            const res = await fetch('/process', { method: 'POST', body: formData });
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            previewContainer.innerHTML = '';

            if (document.getElementById('output_type').value === 'pdf') {
                previewContainer.innerHTML = `<iframe src="${data.preview}" style="width:100%;height:600px;border:0;"></iframe>`;
                downloadLink.href = data.download;
                downloadLink.download = 'handwritten.pdf';
            } else {
                previewContainer.innerHTML = `<img src="${data.preview}" alt="Preview" />`;
                downloadLink.href = data.download;
                downloadLink.download = 'handwritten.png';
            }

        } catch (err) {
            alert('Server error: ' + err);
        }
    });

    // =======================
    // BACK STEP 2 → STEP 1
    // =======================
    backStep2.addEventListener('click', () => {
        step2.style.display = 'none';
        step1.style.display = 'block';
    });

    // =======================
    // NEW button → Reset to Step 1
    // =======================
    newBtn.addEventListener('click', () => {
        step3.style.display = 'none';
        step1.style.display = 'block';

        document.getElementById('text_input').value = '';
        document.getElementById('upload_image').value = '';
        previewContainer.innerHTML = '';
    });

    // =======================
    // Close popup button
    // =======================
    document.getElementById('popupClose').addEventListener('click', () => {
        document.getElementById('popupOverlay').style.display = 'none';
    });

});
