// ==================== TOAST SYSTEM ====================
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <span class="toast-icon"><i class="fas ${icons[type] || icons.success}"></i></span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

const socialLinks = {
    whatsapp: 'https://wa.me/265983142415',
    email: 'mailto:gizmokzu@gmail.com',
    facebook: 'https://www.facebook.com/profile.php?id=61563027572825',
    instagram: 'https://www.instagram.com/thegenerationfamily/',
    tiktok: 'https://www.tiktok.com/@thegenerationfamily'
};

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
    
    // Reset all accordions
    document.querySelectorAll('.mobile-accordion-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.mobile-accordion-content').forEach(content => {
        content.style.maxHeight = null;
    });
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

// ==================== HERO SLIDESHOW ====================
const slides = document.querySelectorAll('.hero-slide');
const dotsContainer = document.querySelector('.hero-dots');
let dots = document.querySelectorAll('.hero-dot');
let currentSlide = 0;
let slideInterval;

function getDots() {
    return document.querySelectorAll('.hero-dot');
}

function goToSlide(index) {
    slides.forEach(s => s.classList.remove('active'));
    const currentDots = getDots();
    currentDots.forEach(d => d.classList.remove('active'));
    
    if (slides[index]) slides[index].classList.add('active');
    if (currentDots[index]) currentDots[index].classList.add('active');
    
    currentSlide = index;
}

function nextSlide() {
    if (slides.length === 0) return;
    const next = (currentSlide + 1) % slides.length;
    goToSlide(next);
}

function startSlideshow() {
    if (slides.length > 1) {
        clearInterval(slideInterval);
        slideInterval = setInterval(nextSlide, 6000);
    }
}

function buildHeroDots() {
    if (!dotsContainer) return;
    const slidesCount = slides.length;
    
    dotsContainer.innerHTML = '';
    
    for (let i = 0; i < slidesCount; i++) {
        const dot = document.createElement('span');
        dot.className = `hero-dot${i === 0 ? ' active' : ''}`;
        dot.addEventListener('click', () => {
            goToSlide(i);
            startSlideshow();
        });
        dotsContainer.appendChild(dot);
    }
    
    dots = document.querySelectorAll('.hero-dot');
}

buildHeroDots();
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

// ==================== PROFESSIONAL BACK BUTTON HANDLING ====================
(function() {
    
    window.addEventListener('popstate', function(event) {
        
        // Close mobile menu AND overlay if open
        if (mobileMenu && mobileMenu.classList.contains('active')) {
            closeMenu(); // This already removes overlay + menu + resets body scroll
            history.replaceState({ menuClosed: true }, '', window.location.href);
            return;
        }
        
        // Close confirmation modal if open
        const confirmModal = document.getElementById('confirmModal');
        if (confirmModal && confirmModal.style.visibility === 'visible') {
            confirmModal.style.opacity = '0';
            confirmModal.style.visibility = 'hidden';
            history.replaceState({ modalClosed: true }, '', window.location.href);
            return;
        }
        
        // Otherwise let browser navigate normally
    });
    
})();
// ==================== BACK TO TOP ====================
const backToTop = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    if (window.pageYOffset > 500) {
        backToTop.classList.add('visible');
    } else {
        backToTop.classList.remove('visible');
    }
});

backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ==================== FROZEN HEADER SCROLL STATE ====================
const header = document.getElementById('header');

window.addEventListener('scroll', () => {
    if (window.pageYOffset > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});


// ==================== NEWSLETTER FORM ====================
const newsletterForm = document.getElementById('newsletterForm');
const newsletterMsg = document.getElementById('newsletterMsg');

if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('newsletterEmail').value.trim();
        const button = newsletterForm.querySelector('button');
        
        if (!email) {
            showToast('Please enter your email address.', 'error');
            return;
        }
        
        button.classList.add('btn-loading');
        button.textContent = 'Subscribing';
        
        try {
            const formData = new FormData();
            formData.append('email', email);
            const response = await fetch('/subscribe', { method: 'POST', body: formData });
            const data = await response.json();
            
            if (data.status === 'success') {
                showToast('Welcome to the family! Check your inbox.', 'success');
                document.getElementById('newsletterEmail').value = '';
            } else {
                showToast(data.message || 'Subscription failed.', 'error');
            }
        } catch (err) {
            showToast('Network error. Please try again.', 'error');
        }
        
        button.classList.remove('btn-loading');
        button.textContent = 'Subscribe';
    });
}

// ==================== EVENT COUNTDOWN ====================
const countdownTimer = document.querySelector('.countdown-timer');

if (countdownTimer) {
    const eventDate = countdownTimer.dataset.date;
    const eventTime = countdownTimer.dataset.time || '00:00';
    
    if (eventDate) {
        const targetDate = new Date(eventDate + 'T' + eventTime);
        
        function updateCountdown() {
            const now = new Date();
            const diff = targetDate - now;
            
            if (diff <= 0) {
                countdownTimer.innerHTML = '<span class="countdown-expired">Happening Now!</span>';
                return;
            }
            
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            
            document.getElementById('countDays').textContent = String(days).padStart(2, '0');
            document.getElementById('countHours').textContent = String(hours).padStart(2, '0');
            document.getElementById('countMins').textContent = String(mins).padStart(2, '0');
        }
        
        updateCountdown();
        setInterval(updateCountdown, 60000); // Update every minute
    }
}

// ==================== CONFIRMATION MODAL ====================
function showConfirm(title, message, onConfirm) {
    const modal = document.getElementById('confirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const messageEl = document.getElementById('confirmMessage');
    const cancelBtn = document.getElementById('confirmCancel');
    const okBtn = document.getElementById('confirmOk');
    
    titleEl.textContent = title;
    messageEl.textContent = message;
    modal.classList.add('active');
    
    function close() {
        modal.classList.remove('active');
        cancelBtn.removeEventListener('click', close);
        okBtn.removeEventListener('click', handleConfirm);
    }
    
    function handleConfirm() {
    okBtn.classList.add('btn-loading');
    okBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
    okBtn.disabled = true;
    close();
    if (onConfirm) onConfirm();
}
    cancelBtn.addEventListener('click', close);
    okBtn.addEventListener('click', handleConfirm);
    
    // Close on overlay click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) close();
    });
}

// ==================== LIGHTBOX ====================
(function() {
    var lightbox = document.getElementById('lightbox');
    var lightboxContent = document.getElementById('lightboxContent');
    var lightboxClose = document.getElementById('lightboxClose');
    var lightboxPrev = document.getElementById('lightboxPrev');
    var lightboxNext = document.getElementById('lightboxNext');
    
    var currentGroup = [];
    var currentIndex = 0;
    
    function openLightbox(items, index) {
        currentGroup = items;
        currentIndex = index;
        showItem();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeLightbox() {
        lightbox.classList.remove('active');
        lightboxContent.innerHTML = '';
        document.body.style.overflow = '';
        currentGroup = [];
        currentIndex = 0;
    }
    
    function showItem() {
        var item = currentGroup[currentIndex];
        lightboxContent.innerHTML = '';
        
        if (item.tagName === 'IMG') {
            var img = document.createElement('img');
            img.src = item.src;
            img.alt = item.alt || '';
            lightboxContent.appendChild(img);
        } else if (item.tagName === 'VIDEO') {
            var video = document.createElement('video');
            video.src = item.querySelector('source')?.src || item.src;
            video.controls = true;
            video.autoplay = true;
            lightboxContent.appendChild(video);
        } else if (item.tagName === 'AUDIO' || (item.dataset && item.dataset.audio)) {
            var audio = document.createElement('audio');
            audio.src = item.querySelector('source')?.src || item.dataset.audio || item.src;
            audio.controls = true;
            audio.autoplay = true;
            lightboxContent.appendChild(audio);
        }
        
        // Hide prev/next if only one item
        lightboxPrev.style.display = currentGroup.length <= 1 ? 'none' : '';
        lightboxNext.style.display = currentGroup.length <= 1 ? 'none' : '';
    }
    
    function nextItem() {
        currentIndex = (currentIndex + 1) % currentGroup.length;
        showItem();
    }
    
    function prevItem() {
        currentIndex = (currentIndex - 1 + currentGroup.length) % currentGroup.length;
        showItem();
    }
    
    lightboxClose.addEventListener('click', closeLightbox);
    lightboxNext.addEventListener('click', nextItem);
    lightboxPrev.addEventListener('click', prevItem);
    
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) closeLightbox();
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (!lightbox.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowRight') nextItem();
        if (e.key === 'ArrowLeft') prevItem();
    });
    
    // Make images clickable
    document.addEventListener('click', function(e) {
        var mediaImage = e.target.closest('.media-image img');
        var mediaVideo = e.target.closest('.media-card video');
        var eventImage = e.target.closest('.event-image img');
        var blogImage = e.target.closest('.blog-image img');
        
        if (mediaImage || eventImage || blogImage) {
            var clicked = mediaImage || eventImage || blogImage;
            var siblings = [];
            
            // Find all images in the same gallery
            var container = clicked.closest('.media-grid, .events-grid, .blog-grid');
            if (container) {
                siblings = Array.from(container.querySelectorAll('img'));
            } else {
                siblings = [clicked];
            }
            
            var index = siblings.indexOf(clicked);
            openLightbox(siblings, index >= 0 ? index : 0);
        }
    });
})();

// ==================== DELETE FORM HANDLER ====================
document.addEventListener('click', function(e) {
    const deleteBtn = e.target.closest('.delete-form button') || e.target.closest('form[action*="/delete"]')?.querySelector('button');
    
    if (deleteBtn) {
        const form = deleteBtn.closest('form');
        if (form.classList.contains('delete-form') || form.action.includes('/delete')) {
            e.preventDefault();
            const name = form.dataset.name || 'this item';
            showConfirm(
                'Delete ' + name + '?',
                'This action cannot be undone.',
                function() {
                    form.submit();
                }
            );
        }
    }
});