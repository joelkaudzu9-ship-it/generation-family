// ==================== LOADING SCREEN ====================
window.addEventListener('load', () => {
    const loader = document.getElementById('loaderWrapper');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('hidden');
        }, 600);
    }
});

// ==================== SMOOTH PAGE TRANSITIONS ====================
document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (link && link.href && link.href.startsWith(window.location.origin) && !link.hasAttribute('download') && link.target !== '_blank' && !link.closest('.mobile-menu') && !link.closest('.admin-nav')) {
        e.preventDefault();
        const main = document.querySelector('main');
        if (main) {
            main.style.opacity = '0';
            main.style.transform = 'translateY(10px)';
            main.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        }
        setTimeout(() => {
            window.location.href = link.href;
        }, 250);
    }
});

// ==================== MOBILE MENU ====================
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const mobileClose = document.getElementById('mobileClose');

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

if (hamburger) hamburger.addEventListener('click', openMenu);
if (mobileClose) mobileClose.addEventListener('click', closeMenu);
overlay.addEventListener('click', closeMenu);

document.querySelectorAll('.mobile-accordion-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const content = btn.nextElementSibling;
        const isOpen = btn.classList.contains('active');
        document.querySelectorAll('.mobile-accordion-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.mobile-accordion-content').forEach(c => c.style.maxHeight = null);
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
    if (slides[index]) slides[index].classList.add('active');
    if (dots[index]) dots[index].classList.add('active');
    currentSlide = index;
}

function nextSlide() {
    const next = (currentSlide + 1) % slides.length;
    goToSlide(next);
}

function startSlideshow() {
    if (slides.length > 1) slideInterval = setInterval(nextSlide, 6000);
}

dots.forEach((dot, i) => {
    dot.addEventListener('click', () => {
        goToSlide(i);
        clearInterval(slideInterval);
        startSlideshow();
    });
});

startSlideshow();

// ==================== PARALLAX HERO ====================
const hero = document.querySelector('.hero');
if (hero) {
    window.addEventListener('scroll', () => {
        const scroll = window.pageYOffset;
        hero.querySelectorAll('.hero-slide').forEach(slide => {
            slide.style.transform = `translateY(${scroll * 0.4}px)`;
        });
        const heroContent = hero.querySelector('.hero-content');
        if (heroContent) heroContent.style.transform = `translateY(${scroll * 0.15}px)`;
    });
}

// ==================== SCROLL REVEAL ====================
const revealElements = document.querySelectorAll('.mvv-card, .impact-card, .leader-card, .ministry-card, .event-card, .blog-card, .sermon-card, .faq-item, .resource-card');
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

revealElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s cubic-bezier(0.22, 0.61, 0.36, 1), transform 0.6s cubic-bezier(0.22, 0.61, 0.36, 1)';
    revealObserver.observe(el);
});

const sectionHeadings = document.querySelectorAll('.section-heading, .page-title');
sectionHeadings.forEach(heading => {
    heading.style.opacity = '0';
    heading.style.transform = 'translateY(20px)';
    heading.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    observer.observe(heading);
});

// ==================== NUMBER COUNTER ====================
const impactNumbers = document.querySelectorAll('.impact-number');
const countObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            const target = el.textContent;
            const numericPart = target.replace(/[^0-9]/g, '');
            if (numericPart) {
                const suffix = target.replace(/[0-9]/g, '');
                let current = 0;
                const increment = Math.ceil(parseInt(numericPart) / 40);
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= parseInt(numericPart)) {
                        current = parseInt(numericPart);
                        clearInterval(timer);
                    }
                    el.textContent = current.toLocaleString() + suffix;
                }, 30);
            }
            countObserver.unobserve(el);
        }
    });
}, { threshold: 0.5 });
impactNumbers.forEach(num => countObserver.observe(num));

// ==================== TESTIMONIAL SLIDER ====================
const tSlides = document.querySelectorAll('.testimonial-slide');
const tDots = document.querySelectorAll('.t-dot');
let currentT = 0;

function goToTestimonial(index) {
    tSlides.forEach(s => s.classList.remove('active'));
    tDots.forEach(d => d.classList.remove('active'));
    if (tSlides[index]) tSlides[index].classList.add('active');
    if (tDots[index]) tDots[index].classList.add('active');
    currentT = index;
}

if (tSlides.length > 1) {
    setInterval(() => {
        currentT = (currentT + 1) % tSlides.length;
        goToTestimonial(currentT);
    }, 5000);
}

tDots.forEach((dot, i) => dot.addEventListener('click', () => goToTestimonial(i)));

// ==================== SOCIAL LINKS ====================
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

const emailIcon = document.querySelector('.side-icon.email');
if (emailIcon) emailIcon.href = 'mailto:gizmokzu@gmail.com';

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
            const response = await fetch('/subscribe', { method: 'POST', body: formData });
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
            newsletterMsg.textContent = 'Network error. Try again.';
            newsletterMsg.style.color = '#e74c3c';
        }
        button.textContent = 'Subscribe';
        button.disabled = false;
        setTimeout(() => { newsletterMsg.textContent = ''; }, 5000);
    });
}