// Toggle del menú
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const contentWrapper = document.querySelector('.content-wrapper'); // Asegúrate de que este selector es correcto

function toggleMenu() {
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
    menuToggle.classList.toggle('active');
    if (contentWrapper) {
        contentWrapper.classList.toggle('sidebar-open');
    }
}

if (menuToggle && sidebar && overlay) {
    menuToggle.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu);
}

// Crear partículas flotantes
function createParticles() {
    const particles = document.getElementById('particles');
    if (!particles) return; // Evitar error si no existe el elemento
    
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        const size = Math.random() * 4 + 2;
        const startPosition = Math.random() * 100;
        const animationDuration = Math.random() * 10 + 10;
        const animationDelay = Math.random() * 5;
        
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = startPosition + '%';
        particle.style.animationDuration = animationDuration + 's';
        particle.style.animationDelay = animationDelay + 's';
        
        particles.appendChild(particle);
    }
}

// Efecto de escritura en el título
function typeWriter(element, text, speed = 100) {
    if (!element) return;
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Inicializar efectos
document.addEventListener('DOMContentLoaded', function() {
    createParticles();
    
    // Agregar efecto de hover a los botones
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Efecto parallax suave en el scroll
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        heroSection.style.transform = `translateY(${scrolled * 0.1}px)`;
    }
});


/* =========================================
    WIDGET DE ACCESIBILIDAD V3 - OPTIMIZADO
   ========================================== */
document.addEventListener('DOMContentLoaded', () => {
    // Crear estilos dinámicamente
    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
        .font-size-1 { font-size: 110% !important; }
        .font-size-2 { font-size: 120% !important; }
        .font-size-3 { font-size: 130% !important; }
        .high-contrast { 
            filter: contrast(150%) !important;
            background: white !important;
            color: black !important;
        }
        .grayscale { filter: grayscale(100%) !important; }
        .highlight-links a { 
            background: yellow !important;
            color: black !important;
            text-decoration: underline !important;
        }
        .highlight-headers h1, 
        .highlight-headers h2, 
        .highlight-headers h3 { 
            background: #ffeb3b !important;
            padding: 5px !important;
        }
        .big-cursor, 
        .big-cursor * { cursor: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAA/0lEQVR4Ae2WgQbDQBRFkxBCCCGEEEIIIYQQQggh9PvP2bHjx9nZ8QdjrTX3jHXvvTvz3nvvvffee++997333nvvvffee++9955nd0Yxu2N2x+yO2R2zO2Z3zO6Y3TG7Y3bH7I7ZHbN7/e69997X73vvvffee++9r9/33nvvvffee++999577733//F+GcfB7uM4Tdb7MAyu4zh43DOS9T4M1vs4jFyPg3VB1vul7axLz8nKoe8665yk73vrZB266TWRDt1oya4fLPPc91YXZJ3nrosiH0JvxVnf2vXSNNalKPPYNlYh6fveivPcNVVjx6mr8rGurB1k/QD3FZN6HhRMWQAAAABJRU5ErkJggg==') 12 12, auto !important; 
        }
    `;
    document.head.appendChild(styleSheet);

    const settings = {
        fontSize: 0,
        highContrast: false,
        grayscale: false,
        highlightLinks: false,
        highlightHeaders: false,
        bigCursor: false,
    };

    function applySettings() {
        // Limpiar clases existentes
        const classesToRemove = [
            'font-size-1', 'font-size-2', 'font-size-3',
            'high-contrast', 'grayscale', 'highlight-links',
            'highlight-headers', 'big-cursor'
        ];
        document.body.classList.remove(...classesToRemove);

        // Aplicar configuraciones actuales
        if (settings.fontSize > 0) {
            document.body.classList.add(`font-size-${settings.fontSize}`);
        }
        
        Object.entries(settings).forEach(([key, value]) => {
            if (key !== 'fontSize' && value === true) {
                document.body.classList.add(key.replace(/[A-Z]/g, m => '-' + m.toLowerCase()));
            }
        });

        // Guardar configuración
        localStorage.setItem('accessibilitySettings', JSON.stringify(settings));
        updateButtonsState();
    }

    function updateButtonsState() {
        gridButtons.forEach(button => {
            const action = button.dataset.action;
            if (action === 'increase-text' || action === 'decrease-text' || action === 'reset') return;

            const camelCaseAction = toCamelCase(action);
            if (settings[camelCaseAction]) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }

    fab.addEventListener('click', () => panel.classList.add('active'));
    closeBtn.addEventListener('click', () => panel.classList.remove('active'));

    gridButtons.forEach(button => {
        button.addEventListener('click', () => {
            const action = button.dataset.action;
            const camelCaseAction = toCamelCase(action);

            switch (action) {
                case 'increase-text':
                    if (settings.fontSize < FONT_CLASSES.length - 1) settings.fontSize++;
                    break;
                case 'decrease-text':
                    if (settings.fontSize > 0) settings.fontSize--;
                    break;
                case 'reset':
                    for (const key in settings) {
                        settings[key] = typeof settings[key] === 'boolean' ? false : 0;
                    }
                    break;
                default:
                    if (typeof settings[camelCaseAction] === 'boolean') {
                        settings[camelCaseAction] = !settings[camelCaseAction];
                    }
                    break;
            }
            applySettings();
            saveSettings();
        });
    });

    loadSettings();
});
