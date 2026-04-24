/* ============================================
   RAGNARÖK - Visual Effects
   Matrix rain + ambient animations
   ============================================ */

// Matrix Rain Effect
(function() {
    const canvas = document.getElementById('matrix-rain');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const fontSize = 14;

    // Set canvas size and keep the drop state aligned to the viewport.
    let drops = [];

    function syncDrops(columnCount) {
        if (drops.length < columnCount) {
            for (let i = drops.length; i < columnCount; i++) {
                drops[i] = Math.random() * -100;
            }
            return;
        }

        if (drops.length > columnCount) {
            drops = drops.slice(0, columnCount);
        }
    }

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const columnCount = Math.max(1, Math.floor(canvas.width / fontSize));
        syncDrops(columnCount);
    }

    resize();
    window.addEventListener('resize', resize);

    // Characters - mix of Norse runes and tech symbols
    const chars = 'ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊᛏᛒᛖᛗᛚᛝᛟᛞ01アイウエオカキクケコ';
    const charArray = chars.split('');

    function draw() {
        // Semi-transparent black to create fade effect
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Green text
        ctx.fillStyle = '#00ff41';
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            // Random character
            const char = charArray[Math.floor(Math.random() * charArray.length)];

            // Draw character
            ctx.fillText(char, i * fontSize, drops[i] * fontSize);

            // Reset drop to top randomly after it falls off screen
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            drops[i]++;
        }
    }

    // Run animation
    setInterval(draw, 50);
})();

// Add subtle ambient glow animation to title
(function() {
    const title = document.querySelector('h1');
    if (!title) return;

    let hue = 30; // Start at orange

    function animateGlow() {
        // Subtle hue shift between orange and yellow
        hue = 30 + Math.sin(Date.now() / 2000) * 10;
        const color = `hsl(${hue}, 100%, 50%)`;

        title.style.textShadow = `
            0 0 20px ${color}80,
            0 0 40px ${color}50,
            0 0 60px ${color}30
        `;

        requestAnimationFrame(animateGlow);
    }

    animateGlow();
})();

// Status indicator random flicker
(function() {
    const indicator = document.querySelector('.status-indicator');
    if (!indicator) return;

    function flicker() {
        if (Math.random() > 0.95) {
            indicator.style.opacity = '0.3';
            setTimeout(() => {
                indicator.style.opacity = '1';
            }, 50);
        }
        setTimeout(flicker, 100);
    }

    flicker();
})();

// LCARS blocks subtle animation
(function() {
    const blocks = document.querySelectorAll('.lcars-block');

    blocks.forEach((block, index) => {
        // Random subtle brightness pulse
        setInterval(() => {
            if (Math.random() > 0.9) {
                block.style.filter = 'brightness(1.3)';
                setTimeout(() => {
                    block.style.filter = 'brightness(1)';
                }, 100);
            }
        }, 1000 + index * 200);
    });
})();
