// FoodFlex Desktop Application - Main JavaScript File

document.addEventListener('DOMContentLoaded', () => {
    // Initialize animations
    initAnimations();
    
    // Initialize window controls
    initWindowControls();
    
    // Initialize sidebar
    initSidebar();
    
    // Initialize search functionality
    initSearch();
});

// Animation functions with GSAP
function initAnimations() {
    // Check if GSAP is loaded
    if (typeof gsap !== 'undefined') {
        // Fade in elements with the animate-in class
        gsap.from('.animate-in', {
            opacity: 0,
            y: 20,
            stagger: 0.1,
            duration: 0.6,
            ease: 'power2.out'
        });
        
        // Animate hero section
        gsap.from('.hero-section', {
            opacity: 0,
            scale: 0.95,
            duration: 0.8,
            ease: 'power2.out'
        });
        
        // Animate cards on scroll
        const cards = document.querySelectorAll('.food-card, .paladium-card');
        cards.forEach(card => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top bottom-=100',
                    toggleActions: 'play none none none'
                },
                opacity: 0,
                y: 30,
                duration: 0.5,
                ease: 'power2.out'
            });
        });
    }
}

// Window controls for desktop app behavior
function initWindowControls() {
    const minimizeBtn = document.querySelector('.window-control.minimize');
    const maximizeBtn = document.querySelector('.window-control.maximize');
    const closeBtn = document.querySelector('.window-control.close');
    const titlebar = document.querySelector('.titlebar');
    
    if (minimizeBtn && maximizeBtn && closeBtn) {
        // Make titlebar draggable
        let isDragging = false;
        let dragStartX, dragStartY;
        
        titlebar.addEventListener('mousedown', (e) => {
            isDragging = true;
            dragStartX = e.clientX;
            dragStartY = e.clientY;
        });
        
        window.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const dx = e.clientX - dragStartX;
                const dy = e.clientY - dragStartY;
                
                // In a real Electron app, you would use:
                // window.moveTo(window.screenX + dx, window.screenY + dy);
                // For now we'll just simulate this behavior
                console.log(`Window moved by ${dx}px horizontally and ${dy}px vertically`);
            }
        });
        
        window.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        // Button click handlers
        minimizeBtn.addEventListener('click', () => {
            console.log('Window minimized');
        });
        
        maximizeBtn.addEventListener('click', () => {
            console.log('Window maximized/restored');
        });
        
        closeBtn.addEventListener('click', () => {
            console.log('Window closed');
        });
    }
}

// Sidebar interaction
function initSidebar() {
    const sidebar = document.querySelector('.app-sidebar');
    
    if (sidebar) {
        const sidebarLinks = sidebar.querySelectorAll('a');
        
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Remove active class from all links
                sidebarLinks.forEach(l => l.classList.remove('active'));
                
                // Add active class to clicked link
                link.classList.add('active');
            });
        });
        
        // Toggle sidebar expansion on hover
        sidebar.addEventListener('mouseenter', () => {
            sidebar.classList.add('expanded');
        });
        
        sidebar.addEventListener('mouseleave', () => {
            sidebar.classList.remove('expanded');
        });
    }
}

// Search functionality
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    
    if (searchInput) {
        searchInput.addEventListener('focus', () => {
            document.querySelector('.search-container').classList.add('focused');
        });
        
        searchInput.addEventListener('blur', () => {
            document.querySelector('.search-container').classList.remove('focused');
        });
        
        searchInput.addEventListener('input', (e) => {
            // Implement search functionality
            console.log(`Searching for: ${e.target.value}`);
        });
    }
} 