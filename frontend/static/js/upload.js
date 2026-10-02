/* Drag & Drop File Upload Handler */
let currentUploadedFilename = null;

document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');

    if (!dropzone || !fileInput) return;

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
});

async function handleFileUpload(file) {
    // Validate client-side extension
    const validExts = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validExts.includes(file.type)) {
        alert('Invalid file format. Please upload JPG, PNG, or WEBP images.');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        alert('File size exceeds 16 MB limit.');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    // Update UI step
    setPipelineStep('step-detect');

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        if (!res.ok || !data.success) {
            alert('Upload failed: ' + (data.error || 'Unknown error'));
            setPipelineStep('step-upload');
            return;
        }

        currentUploadedFilename = data.filename;

        // Display Upload Summary & Detected Bounding Box Preview
        const width = (data.metadata && data.metadata.width) ? data.metadata.width : (data.width || 'N/A');
        const height = (data.metadata && data.metadata.height) ? data.metadata.height : (data.height || 'N/A');
        const sizeKb = (data.metadata && data.metadata.size_kb) ? data.metadata.size_kb : '';
        const sizeTxt = sizeKb ? ` • ${sizeKb} KB` : '';

        document.getElementById('file-name-txt').textContent = data.original_name || file.name;
        document.getElementById('file-meta-txt').textContent = `${width}x${height} px${sizeTxt}`;
        document.getElementById('faces-detected-badge').textContent = `Detected Faces: ${data.face_count !== undefined ? data.face_count : 0}`;

        const previewImg = document.getElementById('detected-preview-img');
        if (previewImg && data.detected_preview) {
            previewImg.src = `/media/outputs/${data.detected_preview}?t=${Date.now()}`;
        }
        
        const summaryElem = document.getElementById('upload-summary');
        if (summaryElem) {
            summaryElem.style.display = 'block';
        }

        // Enable Process button
        const procBtn = document.getElementById('process-btn');
        if (procBtn) {
            procBtn.disabled = false;
        }

    } catch (err) {
        console.error("Upload error caught:", err);
        alert('Error uploading image: ' + (err.message || err));
        setPipelineStep('step-user');
    }
}
