/* Quantum Canvas Particle Animation & Global State */
document.addEventListener('DOMContentLoaded', () => {
    initQuantumCanvas();
    fetchQuantumStatus();
});

function initQuantumCanvas() {
    const canvas = document.getElementById('quantum-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    // Create 45 quantum particles
    const particles = [];
    const particleCount = 45;
    const colors = ['rgba(0, 243, 255, ', 'rgba(157, 78, 221, ', 'rgba(0, 255, 157, '];

    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 2 + 1,
            vx: (Math.random() - 0.5) * 0.6,
            vy: (Math.random() - 0.5) * 0.6,
            colorPrefix: colors[Math.floor(Math.random() * colors.length)],
            alpha: Math.random() * 0.6 + 0.2
        });
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);

        // Draw quantum entanglement connecting lines
        for (let i = 0; i < particleCount; i++) {
            for (let j = i + 1; j < particleCount; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 130) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(0, 243, 255, ${0.15 * (1 - dist / 130)})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }

        // Render particles
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.colorPrefix + p.alpha + ')';
            ctx.shadowBlur = 10;
            ctx.shadowColor = p.colorPrefix + '0.8)';
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        requestAnimationFrame(draw);
    }

    draw();
}

async function fetchQuantumStatus() {
    const textElem = document.getElementById('quantum-status-text');
    if (!textElem) return;

    try {
        const res = await fetch('/api/quantum/status');
        const data = await res.json();
        if (data && data.backend_name) {
            textElem.textContent = data.label || data.backend_name;
        }
    } catch (err) {
        textElem.textContent = 'Qiskit Aer Simulator (Local)';
    }
}
