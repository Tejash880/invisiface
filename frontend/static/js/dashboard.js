/* Quantum InvisiFace Dashboard & Pipeline Timeline Visualizer */
function setPipelineStep(stepId) {
    const steps = ['step-user', 'step-flask', 'step-preprocess', 'step-qrng', 'step-protection', 'step-verification', 'step-output'];
    let reached = false;

    steps.forEach(id => {
        const elem = document.getElementById(id);
        if (!elem) return;

        if (id === stepId) {
            reached = true;
            elem.className = 'pipeline-step active';
        } else if (!reached) {
            elem.className = 'pipeline-step completed';
        } else {
            elem.className = 'pipeline-step';
        }
    });
}

async function executeQuantumProtection() {
    if (!currentUploadedFilename) {
        alert('Please upload a face image first.');
        return;
    }

    const btn = document.getElementById('process-btn');
    btn.disabled = true;

    // Timeline progress animation
    setPipelineStep('step-flask');
    await new Promise(r => setTimeout(r, 200));

    setPipelineStep('step-preprocess');
    await new Promise(r => setTimeout(r, 200));

    setPipelineStep('step-qrng');
    await new Promise(r => setTimeout(r, 350));

    setPipelineStep('step-protection');
    await new Promise(r => setTimeout(r, 350));

    setPipelineStep('step-verification');

    try {
        const res = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentUploadedFilename
            })
        });

        let data = {};
        try {
            data = await res.json();
        } catch (e) {
            console.error("Failed to parse JSON response from /api/process:", e);
            throw new Error(`Server returned HTTP status ${res.status}`);
        }

        if (!res.ok || !data.success) {
            const errorMsg = data.error || data.message || `Server Error (HTTP ${res.status})`;
            console.error("Pipeline server error:", errorMsg);
            alert('Pipeline Execution Notice: ' + errorMsg);
            btn.disabled = false;
            setPipelineStep('step-user');
            return;
        }

        setPipelineStep('step-output');
        await new Promise(r => setTimeout(r, 250));

        // Redirect to result view
        window.location.href = `/result/${data.job_id}`;

    } catch (err) {
        console.error("Fetch exception caught in executeQuantumProtection:", err);
        const userMsg = (err.name === 'TypeError' || err.message.includes('fetch'))
            ? 'Cannot connect to Flask server at http://127.0.0.1:5000. Please verify the backend is running.'
            : (err.message || 'Pipeline execution failed');
        alert('Pipeline Execution Exception: ' + userMsg);
        btn.disabled = false;
        setPipelineStep('step-user');
    }
}
