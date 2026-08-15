/**
 * Apex Scaife Lapping & Coating - Frontend JavaScript Core
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation Scroll Effect
    const header = document.querySelector('.site-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // 2. Mobile Menu Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            // Toggle hamburger icon animation
            const spans = menuToggle.querySelectorAll('span');
            spans[0].style.transform = navMenu.classList.contains('active') ? 'rotate(45deg) translate(5px, 6px)' : 'none';
            spans[1].style.opacity = navMenu.classList.contains('active') ? '0' : '1';
            spans[2].style.transform = navMenu.classList.contains('active') ? 'rotate(-45deg) translate(5px, -6px)' : 'none';
        });
    }

    // 3. FAQ Accordion Logic
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const item = question.parentElement;
            const isActive = item.classList.contains('active');
            
            // Close all FAQ items
            document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));
            
            // Toggle current FAQ item
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // 4. Toast Notification Manager
    setupToasts();

    // 5. Dashboard Sidebar Mobile Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.db-sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== sidebarToggle) {
                sidebar.classList.remove('active');
            }
        });
    }

    // 6. Dynamic Scaife Cost Autocalculation
    setupCostAutoCalc();
});

/**
 * Setup and handle Toast Notifications dismissals
 */
function setupToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            dismissToast(toast);
        }, 5000);

        // Click to dismiss
        const closeBtn = toast.querySelector('.toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                dismissToast(toast);
            });
        }
    });
}

function dismissToast(toast) {
    toast.style.animation = 'fadeOut 0.5s ease-out forwards';
    setTimeout(() => {
        toast.remove();
    }, 500);
}

/**
 * Helper to show toast messages programmatically (for JS events)
 */
function showToast(title, message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-title">${title}</span>
            <span class="toast-msg">${message}</span>
        </div>
        <span class="toast-close">&times;</span>
    `;

    container.appendChild(toast);
    
    // Wire up events
    setTimeout(() => {
        dismissToast(toast);
    }, 5000);

    toast.querySelector('.toast-close').addEventListener('click', () => {
        dismissToast(toast);
    });
}

/**
 * Auto calculation of price on the Scaife Entry Form based on Diameter and selected Lapping/Coating
 */
function setupCostAutoCalc() {
    const diameterInput = document.getElementById('id_diameter');
    const lappingSelect = document.getElementById('id_lapping_type');
    const coatingSelect = document.getElementById('id_coating_type');
    const costInput = document.getElementById('id_cost');

    if (diameterInput && lappingSelect && coatingSelect && costInput) {
        const pricing = window.pricingConfig || {
            lapping_rate: 150.00,
            coating_rate: 200.00
        };

        const calculate = () => {
            const diameter = parseFloat(diameterInput.value) || 0;
            const lappingType = lappingSelect.value;
            const coatingType = coatingSelect.value;

            const lapCost = (lappingType === 'yes' || lappingType === 'standard' || lappingType === 'precision' || lappingType === 'ultra') ? (pricing.lapping_rate || 150.00) : 0;
            const coatCost = (coatingType === 'yes' || coatingType === 'standard' || coatingType === 'premium' || coatingType === 'dlc') ? (pricing.coating_rate || 200.00) : 0;

            const total = (lapCost + coatCost) * diameter;
            costInput.value = total.toFixed(2);
        };

        diameterInput.addEventListener('input', calculate);
        lappingSelect.addEventListener('change', calculate);
        coatingSelect.addEventListener('change', calculate);
    }
}
