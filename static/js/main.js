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

// ==================== HISTORY STATE MANAGEMENT ====================
// Initialize history state for proper back button behavior
if (!window.history.state || !window.history.state.pageLoaded) {
    window.history.replaceState({ 
        pageLoaded: true, 
        url: window.location.href,
        timestamp: Date.now()
    }, document.title, window.location.href);
}

// ==================== MOBILE MENU ====================
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const mobileClose = document.getElementById('mobileClose');

let overlay = document.querySelector('.mobile-menu-overlay');
if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'mobile-menu-overlay';
    document.body.appendChild(overlay);
}

function openMenu() {
    if (!hamburger || !mobileMenu || !overlay) return;
    hamburger.classList.add('active');
    mobileMenu.classList.add('active');
    overlay.classList.add('active');
    
    // Store current scroll position
    const scrollY = window.scrollY;
    document.body.style.overflow = 'hidden';
    document.body.style.position = 'fixed';
    document.body.style.top = `-${scrollY}px`;
    document.body.style.width = '100%';
    
    // Store the scroll position for later restoration
    mobileMenu.dataset.scrollY = scrollY;
}

function closeMenu() {
    if (!hamburger || !mobileMenu || !overlay) return;
    hamburger.classList.remove('active');
    mobileMenu.classList.remove('active');
    overlay.classList.remove('active');
    
    // Restore scroll position when closing menu
    const scrollY = parseInt(mobileMenu.dataset.scrollY || '0');
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';
    document.body.style.overflow = '';
    window.scrollTo(0, scrollY);
    
    // Reset accordion state
    document.querySelectorAll('.mobile-accordion-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.mobile-accordion-content').forEach(content => {
        content.style.maxHeight = null;
    });
}

// Force close menu function - closes instantly without scroll restoration
function forceCloseMenu() {
    if (!hamburger || !mobileMenu || !overlay) return;
    hamburger.classList.remove('active');
    mobileMenu.classList.remove('active');
    overlay.classList.remove('active');
    
    // Just reset body styles without scroll restoration
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';
    document.body.style.overflow = '';
}

if (hamburger) hamburger.addEventListener('click', openMenu);
if (mobileClose) mobileClose.addEventListener('click', closeMenu);
if (overlay) overlay.addEventListener('click', closeMenu);

// Mobile accordion
document.querySelectorAll('.mobile-accordion-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const content = btn.nextElementSibling;
        const isOpen = btn.classList.contains('active');
        document.querySelectorAll('.mobile-accordion-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.mobile-accordion-content').forEach(c => c.style.maxHeight = null);
        if (!isOpen && content) {
            btn.classList.add('active');
            content.style.maxHeight = content.scrollHeight + 'px';
        }
    });
});

// ==================== PROPER BACK BUTTON HANDLING ====================
// Track if menu was open to handle back button properly
let menuWasOpenBeforeNavigation = false;

// CRITICAL: Close menu IMMEDIATELY before any navigation
function prepareForNavigation() {
    if (mobileMenu && mobileMenu.classList.contains('active')) {
        menuWasOpenBeforeNavigation = true;
        forceCloseMenu();
    }
}

// ==================== SMOOTH PAGE TRANSITIONS ====================
document.addEventListener('click', (e) => {
    // Don't intercept if modifier keys are pressed (ctrl/cmd click = new tab)
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;
    
    const link = e.target.closest('a');
    if (link && link.href && link.href.startsWith(window.location.origin) && 
        !link.hasAttribute('download') && link.target !== '_blank' && 
        !link.closest('.mobile-menu') && !link.closest('.admin-nav')) {
        
        // Skip if it's a hash link on the same page
        if (link.href.split('#')[0] === window.location.href.split('#')[0] && link.hash) {
            return;
        }
        
        e.preventDefault();
        
        // CLOSE MENU IMMEDIATELY before any navigation animation
        if (mobileMenu && mobileMenu.classList.contains('active')) {
            forceCloseMenu();
            // Small delay to ensure DOM updates before transition
            setTimeout(() => {
                performNavigation(link.href);
            }, 50);
        } else {
            performNavigation(link.href);
        }
    }
});

function performNavigation(href) {
    // Push state before navigation
    window.history.pushState({ 
        pageLoaded: true,
        url: href,
        timestamp: Date.now()
    }, '', href);
    
    const main = document.querySelector('main');
    if (main) {
        main.style.opacity = '0';
        main.style.transform = 'translateY(10px)';
        main.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    }
    
    setTimeout(() => {
        window.location.href = href;
    }, 250);
}

// Handle browser back/forward buttons
window.addEventListener('popstate', (event) => {
    // If menu is open, FIRST close it, THEN navigate back
    if (mobileMenu && mobileMenu.classList.contains('active')) {
        // Close menu immediately
        forceCloseMenu();
        
        // Prevent the default back navigation
        event.preventDefault();
        
        // Navigate back after a tiny delay to ensure menu closes first
        setTimeout(() => {
            window.history.back();
        }, 50);
        
        return;
    }
    
    // If menu wasn't open, just let the navigation happen
    // We'll handle scroll position in pageshow
});

// CRITICAL: Close menu before page unloads (catches all navigation types)
window.addEventListener('beforeunload', () => {
    if (mobileMenu && mobileMenu.classList.contains('active')) {
        forceCloseMenu();
    }
});

// Handle page visibility change (tab switching, etc.)
document.addEventListener('visibilitychange', () => {
    if (document.hidden && mobileMenu && mobileMenu.classList.contains('active')) {
        forceCloseMenu();
    }
});

// Handle bfcache (back-forward cache) - pageshow fires when page is shown
window.addEventListener('pageshow', (event) => {
    // ALWAYS ensure menu is closed when page is shown
    if (mobileMenu && mobileMenu.classList.contains('active')) {
        forceCloseMenu();
    }
    
    // Reset body styles that might persist from bfcache
    document.body.style.overflow = '';
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';
    
    // ALWAYS scroll to top when arriving at a page
    window.scrollTo(0, 0);
    
    // Fade in content if coming from history navigation
    if (event.persisted) {
        const main = document.querySelector('main');
        if (main) {
            main.style.opacity = '0';
            main.style.transform = 'translateY(10px)';
            requestAnimationFrame(() => {
                main.style.opacity = '1';
                main.style.transform = 'translateY(0)';
            });
        }
    }
});

// Handle hash changes (for in-page navigation)
window.addEventListener('hashchange', () => {
    if (window.location.hash) {
        setTimeout(() => {
            const target = document.querySelector(window.location.hash);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    }
});

// Initialize on load - ensure we always start at top
window.addEventListener('load', () => {
    // Force scroll to top on initial load
    window.scrollTo(0, 0);
    
    // Handle initial hash if present
    if (window.location.hash) {
        setTimeout(() => {
            const target = document.querySelector(window.location.hash);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    }
});

// ==================== FORM STATE PRESERVATION ====================
// Save form data before navigating away
window.addEventListener('beforeunload', () => {
    document.querySelectorAll('form').forEach(form => {
        if (form.id) {
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            sessionStorage.setItem(`form_${form.id}`, JSON.stringify(data));
        }
    });
});

// Restore form data on back navigation
window.addEventListener('pageshow', () => {
    document.querySelectorAll('form').forEach(form => {
        if (form.id) {
            const savedData = sessionStorage.getItem(`form_${form.id}`);
            if (savedData) {
                try {
                    const data = JSON.parse(savedData);
                    Object.keys(data).forEach(key => {
                        const input = form.elements[key];
                        if (input && input.type !== 'submit' && input.type !== 'button') {
                            input.value = data[key];
                        }
                    });
                    sessionStorage.removeItem(`form_${form.id}`);
                } catch (e) {
                    // Invalid JSON, ignore
                }
            }
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
    if (!slides.length) return;
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

if (slides.length) {
    buildHeroDots();
    startSlideshow();
}

// ==================== PARALLAX HERO (THROTTLED) ====================
const hero = document.querySelector('.hero');
if (hero) {
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scroll = window.pageYOffset;
                hero.querySelectorAll('.hero-slide').forEach(slide => {
                    slide.style.transform = `translateY(${scroll * 0.4}px)`;
                });
                const heroContent = hero.querySelector('.hero-content');
                if (heroContent) heroContent.style.transform = `translateY(${scroll * 0.15}px)`;
                ticking = false;
            });
            ticking = true;
        }
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
    if (!tSlides.length) return;
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

// ==================== BACK TO TOP ====================
const backToTop = document.getElementById('backToTop');

window.addEventListener('scroll', () => {
    if (backToTop) {
        if (window.pageYOffset > 500) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    }
});

if (backToTop) {
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ==================== FROZEN HEADER SCROLL STATE ====================
const header = document.getElementById('header');

window.addEventListener('scroll', () => {
    if (header) {
        if (window.pageYOffset > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }
});

// ==================== NEWSLETTER FORM ====================
const newsletterForm = document.getElementById('newsletterForm');

if (newsletterForm) {
    newsletterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const emailInput = document.getElementById('newsletterEmail');
        if (!emailInput) return;
        
        const email = emailInput.value.trim();
        const button = newsletterForm.querySelector('button');
        
        if (!email) {
            showToast('Please enter your email address.', 'error');
            return;
        }
        
        if (button) {
            button.classList.add('btn-loading');
            button.textContent = 'Subscribing';
        }
        
        try {
            const formData = new FormData();
            formData.append('email', email);
            const response = await fetch('/subscribe', { method: 'POST', body: formData });
            const data = await response.json();
            
            if (data.status === 'success') {
                showToast('Welcome to the family! Check your inbox.', 'success');
                emailInput.value = '';
            } else {
                showToast(data.message || 'Subscription failed.', 'error');
            }
        } catch (err) {
            showToast('Network error. Please try again.', 'error');
        }
        
        if (button) {
            button.classList.remove('btn-loading');
            button.textContent = 'Subscribe';
        }
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
            
            const daysEl = document.getElementById('countDays');
            const hoursEl = document.getElementById('countHours');
            const minsEl = document.getElementById('countMins');
            
            if (daysEl) daysEl.textContent = String(days).padStart(2, '0');
            if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
            if (minsEl) minsEl.textContent = String(mins).padStart(2, '0');
        }
        
        updateCountdown();
        setInterval(updateCountdown, 60000);
    }
}

// ==================== CONFIRMATION MODAL ====================
function showConfirm(title, message, onConfirm) {
    const modal = document.getElementById('confirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const messageEl = document.getElementById('confirmMessage');
    const cancelBtn = document.getElementById('confirmCancel');
    const okBtn = document.getElementById('confirmOk');
    
    if (!modal || !titleEl || !messageEl || !cancelBtn || !okBtn) return;
    
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
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) close();
    });
}

// ==================== LIGHTBOX ====================
(function() {
    const lightbox = document.getElementById('lightbox');
    const lightboxContent = document.getElementById('lightboxContent');
    const lightboxClose = document.getElementById('lightboxClose');
    const lightboxPrev = document.getElementById('lightboxPrev');
    const lightboxNext = document.getElementById('lightboxNext');
    
    if (!lightbox || !lightboxContent) return;
    
    let currentGroup = [];
    let currentIndex = 0;
    
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
        const item = currentGroup[currentIndex];
        if (!item) return;
        lightboxContent.innerHTML = '';
        
        if (item.tagName === 'IMG') {
            const img = document.createElement('img');
            img.src = item.src;
            img.alt = item.alt || '';
            lightboxContent.appendChild(img);
        } else if (item.tagName === 'VIDEO') {
            const video = document.createElement('video');
            video.src = item.querySelector('source')?.src || item.src;
            video.controls = true;
            video.autoplay = true;
            lightboxContent.appendChild(video);
        } else if (item.tagName === 'AUDIO' || (item.dataset && item.dataset.audio)) {
            const audio = document.createElement('audio');
            audio.src = item.querySelector('source')?.src || item.dataset.audio || item.src;
            audio.controls = true;
            audio.autoplay = true;
            lightboxContent.appendChild(audio);
        }
        
        if (lightboxPrev) lightboxPrev.style.display = currentGroup.length <= 1 ? 'none' : '';
        if (lightboxNext) lightboxNext.style.display = currentGroup.length <= 1 ? 'none' : '';
    }
    
    function nextItem() {
        if (currentGroup.length === 0) return;
        currentIndex = (currentIndex + 1) % currentGroup.length;
        showItem();
    }
    
    function prevItem() {
        if (currentGroup.length === 0) return;
        currentIndex = (currentIndex - 1 + currentGroup.length) % currentGroup.length;
        showItem();
    }
    
    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    if (lightboxNext) lightboxNext.addEventListener('click', nextItem);
    if (lightboxPrev) lightboxPrev.addEventListener('click', prevItem);
    
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) closeLightbox();
    });
    
    document.addEventListener('keydown', function(e) {
        if (!lightbox.classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowRight') nextItem();
        if (e.key === 'ArrowLeft') prevItem();
    });
    
    document.addEventListener('click', function(e) {
        const mediaImage = e.target.closest('.media-image img');
        const eventImage = e.target.closest('.event-image img');
        const blogImage = e.target.closest('.blog-image img');
        
        if (mediaImage || eventImage || blogImage) {
            const clicked = mediaImage || eventImage || blogImage;
            let siblings = [];
            
            const container = clicked.closest('.media-grid, .events-grid, .blog-grid');
            if (container) {
                siblings = Array.from(container.querySelectorAll('img'));
            } else {
                siblings = [clicked];
            }
            
            const index = siblings.indexOf(clicked);
            openLightbox(siblings, index >= 0 ? index : 0);
        }
    });
})();

// ==================== DELETE FORM HANDLER ====================
document.addEventListener('click', function(e) {
    const deleteBtn = e.target.closest('.delete-form button') || e.target.closest('form[action*="/delete"]')?.querySelector('button');
    
    if (deleteBtn) {
        const form = deleteBtn.closest('form');
        if (form && (form.classList.contains('delete-form') || form.action.includes('/delete'))) {
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

// ==================== MOBILE SEARCH ====================
const mobileSearchInput = document.getElementById('mobileSearchInput');
if (mobileSearchInput) {
    mobileSearchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.trim();
            if (query) {
                window.location.href = '/search?q=' + encodeURIComponent(query);
            }
        }
    });
}