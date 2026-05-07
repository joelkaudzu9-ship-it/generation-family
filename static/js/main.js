// ==================== MOBILE MENU ====================
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const mobileClose = document.getElementById('mobileClose');

// Create overlay
const overlay = document.createElement('div');
overlay.className = 'mobile-menu-overlay';
document.body.appendChild(overlay);

function openMenu() {
    hamburger.classList.add('active');
    mobileMenu.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMenu() {
    hamburger.classList.remove('active');
    mobileMenu.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}

hamburger.addEventListener('click', openMenu);
mobileClose.addEventListener('click', closeMenu);
overlay.addEventListener('click', closeMenu);

// Mobile accordion
document.querySelectorAll('.mobile-accordion-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const content = btn.nextElementSibling;
        const isOpen = btn.classList.contains('active');
        
        // Close all
        document.querySelectorAll('.mobile-accordion-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.mobile-accordion-content').forEach(c => c.style.maxHeight = null);
        
        // Open clicked
        if (!isOpen) {
            btn.classList.add('active');
            content.style.maxHeight = content.scrollHeight + 'px';
        }
    });
});

// ==================== SEARCH TOGGLE ====================
const searchToggle = document.querySelector('.search-toggle');
const searchBar = document.getElementById('searchBar');

if (searchToggle && searchBar) {
    searchToggle.addEventListener('click', () => {
        searchBar.classList.toggle('active');
        if (searchBar.classList.contains('active')) {
            searchBar.querySelector('input').focus();
        }
    });
}

// ==================== HERO SLIDESHOW ====================
const slides = document.querySelectorAll('.hero-slide');
const dots = document.querySelectorAll('.hero-dot');
let currentSlide = 0;
let slideInterval;

function goToSlide(index) {
    slides.forEach(s => s.classList.remove('active'));
    dots.forEach(d => d.classList.remove('active'));
    slides[index].classList.add('active');
    dots[index].classList.add('active');
    currentSlide = index;
}

function nextSlide() {
    const next = (currentSlide + 1) % slides.length;
    goToSlide(next);
}

function startSlideshow() {
    if (slides.length > 1) {
        slideInterval = setInterval(nextSlide, 6000);
    }
}

function stopSlideshow() {
    clearInterval(slideInterval);
}

dots.forEach((dot, i) => {
    dot.addEventListener('click', () => {
        goToSlide(i);
        stopSlideshow();
        startSlideshow();
    });
});

startSlideshow();

// ==================== TESTIMONIAL SLIDER ====================
const tSlides = document.querySelectorAll('.testimonial-slide');
const tDots = document.querySelectorAll('.t-dot');
let currentT = 0;

function goToTestimonial(index) {
    tSlides.forEach(s => s.classList.remove('active'));
    tDots.forEach(d => d.classList.remove('active'));
    tSlides[index].classList.add('active');
    tDots[index].classList.add('active');
    currentT = index;
}

if (tSlides.length > 1) {
    setInterval(() => {
        currentT = (currentT + 1) % tSlides.length;
        goToTestimonial(currentT);
    }, 5000);
}

tDots.forEach((dot, i) => {
    dot.addEventListener('click', () => goToTestimonial(i));
});

// ==================== SIDE SOCIAL LINKS ====================
const socialLinks = {
    whatsapp: 'https://wa.me/265983142415',
    email: 'mailto:gizmokzu@gmail.com',
    facebook: 'https://facebook.com/TheGenerationFamily',
    instagram: 'https://instagram.com/TheGenerationFamily',
    linkedin: 'https://linkedin.com/company/TheGenerationFamily',
    tiktok: 'https://tiktok.com/@TheGenerationFamily'
};

document.querySelectorAll('.side-icon').forEach(icon => {
    const classes = icon.classList;
    for (const [platform, url] of Object.entries(socialLinks)) {
        if (classes.contains(platform)) {
            icon.href = url;
            icon.target = '_blank';
            icon.rel = 'noopener';
        }
    }
});

// Email icon
const emailIcon = document.querySelector('.side-icon.email');
if (emailIcon) {
    emailIcon.href = 'mailto:info@thegenerationfamily.org';
}

// ==================== NEWSLETTER FORM ====================
const newsletterForm = document.getElementById('newsletterForm');
const newsletterMsg = document.getElementById('newsletterMsg');

if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('newsletterEmail').value.trim();
        const button = newsletterForm.querySelector('button');
        
        if (!email) {
            newsletterMsg.textContent = 'Please enter your email.';
            newsletterMsg.style.color = '#e74c3c';
            return;
        }
        
        button.textContent = 'Subscribing...';
        button.disabled = true;
        newsletterMsg.textContent = '';
        
        try {
            const formData = new FormData();
            formData.append('email', email);
            
            const response = await fetch('/subscribe', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                newsletterMsg.textContent = '✓ Subscribed! Welcome!';
                newsletterMsg.style.color = '#4caf50';
                document.getElementById('newsletterEmail').value = '';
            } else {
                newsletterMsg.textContent = data.message;
                newsletterMsg.style.color = '#e74c3c';
            }
        } catch (err) {
            console.error('Error:', err);
            newsletterMsg.textContent = 'Network error. Try again.';
            newsletterMsg.style.color = '#e74c3c';
        }
        
        button.textContent = 'Subscribe';
        button.disabled = false;
        
        setTimeout(() => {
            newsletterMsg.textContent = '';
        }, 5000);
    });
}