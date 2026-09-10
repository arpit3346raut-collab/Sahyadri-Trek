// Custom JavaScript for Maharashtra Government - Sahyadri Trekking Portal

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Set minimum date for trek booking to today
if (document.getElementById('trekDate')) {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('trekDate').setAttribute('min', today);
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        return form.checkValidity();
    }
    return false;
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Dynamic year in footer
if (document.getElementById('currentYear')) {
    document.getElementById('currentYear').textContent = new Date().getFullYear();
}

// Mobile menu toggle (if needed)
function toggleMobileMenu() {
    const navbarCollapse = document.querySelector('.navbar-collapse');
    if (navbarCollapse) {
        navbarCollapse.classList.toggle('show');
    }
}

// Weather status indicator
function updateWeatherStatus(status) {
    const weatherElement = document.getElementById('weatherStatus');
    if (weatherElement) {
        weatherElement.className = ''; // Clear existing classes
        switch(status) {
            case 'safe':
                weatherElement.classList.add('text-success');
                weatherElement.innerHTML = '<i class="fas fa-check-circle"></i> Safe for trekking';
                break;
            case 'moderate':
                weatherElement.classList.add('text-warning');
                weatherElement.innerHTML = '<i class="fas fa-cloud-rain"></i> Moderate rain - trek with caution';
                break;
            case 'heavy':
                weatherElement.classList.add('text-danger');
                weatherElement.innerHTML = '<i class="fas fa-bolt"></i> Heavy rain - trekking prohibited';
                break;
            default:
                weatherElement.innerHTML = 'Weather status unavailable';
        }
    }
}

// Example usage of weather status (would be called from backend in real app)
// updateWeatherStatus('safe');

// Slot availability checker
function checkSlotAvailability(trekId, date, slot) {
    // In a real application, this would make an AJAX call to check availability
    console.log(`Checking availability for trek ${trekId} on ${date} for ${slot} slot`);
    
    // Simulate response
    setTimeout(() => {
        const isAvailable = Math.random() > 0.3; // 70% chance of availability
        const availabilityElement = document.getElementById('slotAvailability');
        if (availabilityElement) {
            if (isAvailable) {
                availabilityElement.innerHTML = '<span class="text-success"><i class="fas fa-check"></i> Slots available</span>';
            } else {
                availabilityElement.innerHTML = '<span class="text-danger"><i class="fas fa-times"></i> No slots available</span>';
            }
        }
    }, 500);
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Example usage: showNotification('Your trek has been booked successfully!', 'success');