/* Interactive Split Slider & Final Outputs Renderer */
document.addEventListener('DOMContentLoaded', () => {
    initSplitSlider();
    loadResultsData();
});

function initSplitSlider() {
    const container = document.getElementById('split-container');
    const overlay = document.getElementById('split-overlay');
    const handle = document.getElementById('split-handle');

    if (!container || !overlay || !handle) return;

    let isDragging = false;

    function moveSlider(clientX) {
        const rect = container.getBoundingClientRect();
        let x = clientX - rect.left;
        x = Math.max(0, Math.min(x, rect.width));

        const percentage = (x / rect.width) * 100;
        overlay.style.width = percentage + '%';
        handle.style.left = percentage + '%';
    }

    container.addEventListener('mousedown', (e) => {
        isDragging = true;
        moveSlider(e.clientX);
    });

    window.addEventListener('mouseup', () => { isDragging = false; });
    window.addEventListener('mousemove', (e) => {
        if (isDragging) moveSlider(e.clientX);
    });

    container.addEventListener('touchstart', (e) => {
        isDragging = true;
        moveSlider(e.touches[0].clientX);
    });
    window.addEventListener('touchend', () => { isDragging = false; });
    window.addEventListener('touchmove', (e) => {
        if (isDragging) moveSlider(e.touches[0].clientX);
    });
}

async function loadResultsData() {
    const pathParts = window.location.pathname.split('/');
    const jobId = pathParts[pathParts.length - 1];

    if (!jobId || isNaN(jobId)) {
        try {
            const histRes = await fetch('/api/history');
            const history = await histRes.json();
            if (history && history.length > 0) {
                renderResultDetails(history[0]);
            }
        } catch (e) {
            console.error('Error fetching fallback history:', e);
        }
        return;
    }

    try {
        const res = await fetch(`/api/result/${jobId}`);
        const data = await res.json();

        if (res.ok) {
            renderResultDetails(data);
        } else {
            alert('Failed to load result: ' + data.error);
        }
    } catch (err) {
        console.error('Error loading result payload:', err);
    }
}

function renderResultDetails(data) {
    document.getElementById('res-job-id').textContent = `#${data.id}`;
    
    // Output 1: Images
    const beforeImg = document.getElementById('split-img-before');
    const afterImg = document.getElementById('split-img-after');
    if (beforeImg) beforeImg.src = `/media/uploads/${data.original_filename}?t=${Date.now()}`;
    if (afterImg) afterImg.src = `/media/outputs/${data.output_filename}?t=${Date.now()}`;

    document.getElementById('res-faces-badge').textContent = `Faces Protected: ${data.faces_protected || data.face_count}`;

    document.getElementById('download-output-btn').href = `/api/download/${data.output_filename}?type=output`;
    document.getElementById('download-enc-btn').href = `/api/download/${data.encrypted_filename}?type=encrypted`;

    // Output 2: Integrity Report
    document.getElementById('val-sha256').textContent = data.sha256_hash || data.file_hash || 'N/A';
    document.getElementById('val-watermark-status').innerHTML = `<span class="badge badge-green">${data.watermark_status || 'VALID'}</span>`;
    document.getElementById('val-ssim').textContent = data.ssim;
    document.getElementById('val-psnr').textContent = `${data.psnr} dB`;

    // Output 3: AI Resistance Report
    document.getElementById('val-rec-proxy').textContent = `Proxy: ${data.recognition_resistance_proxy}/100`;
    document.getElementById('val-identity-after').textContent = `${data.identity_similarity_after}%`;
    document.getElementById('val-identity-separation').textContent = `+${data.identity_separation}%`;
}
