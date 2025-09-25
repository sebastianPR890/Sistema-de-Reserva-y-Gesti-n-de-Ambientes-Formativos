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
