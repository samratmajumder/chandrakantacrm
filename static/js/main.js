/**
 * Chandrakanta CRM - Main JavaScript
 * Contains common functionality used across the application
 */

// Initialize tooltips and popovers when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

/**
 * Format a number as currency (INR)
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

/**
 * Format a date string to a more readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-IN', options);
}

/**
 * Format a time string to a more readable format
 * @param {string} timeString - Time string (HH:MM:SS)
 * @returns {string} Formatted time string
 */
function formatTime(timeString) {
    if (!timeString) return '';

    const timeParts = timeString.split(':');
    if (timeParts.length < 2) return timeString;

    let hours = parseInt(timeParts[0]);
    const minutes = timeParts[1];
    const ampm = hours >= 12 ? 'PM' : 'AM';

    hours = hours % 12;
    hours = hours ? hours : 12; // Convert 0 to 12

    return hours + ':' + minutes + ' ' + ampm;
}

/**
 * Show a loading spinner in a container
 * @param {HTMLElement} container - The container to show the spinner in
 * @param {string} message - Optional message to display
 */
function showSpinner(container, message = 'Loading...') {
    container.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">${message}</p>
        </div>
    `;
}

/**
 * Show an error message in a container
 * @param {HTMLElement} container - The container to show the error in
 * @param {string} message - The error message
 */
function showError(container, message) {
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>${message}
        </div>
    `;
}

/**
 * Show a no results message in a container
 * @param {HTMLElement} container - The container to show the message in
 * @param {string} message - The message to display
 * @param {string} icon - FontAwesome icon class
 */
function showNoResults(container, message = 'No results found', icon = 'fa-search') {
    container.innerHTML = `
        <div class="text-center p-4">
            <i class="fas ${icon} fa-3x mb-3 text-muted"></i>
            <h5>${message}</h5>
            <p class="text-muted">Try different search criteria</p>
        </div>
    `;
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - The function to debounce
 * @param {number} wait - The debounce wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

/**
 * Validate form inputs
 * @param {HTMLFormElement} form - The form to validate
 * @returns {boolean} Whether the form is valid
 */
function validateForm(form) {
    const requiredInputs = form.querySelectorAll('[required]');
    let isValid = true;

    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');

            // Add error message if not already present
            const errorDiv = input.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                const invalidFeedback = document.createElement('div');
                invalidFeedback.className = 'invalid-feedback';
                invalidFeedback.textContent = 'This field is required';
                input.parentNode.insertBefore(invalidFeedback, input.nextSibling);
            }
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

/**
 * Handle API errors
 * @param {Error} error - The error object
 * @returns {string} Error message
 */
function handleApiError(error) {
    console.error('API Error:', error);

    if (error.response && error.response.data && error.response.data.error) {
        return error.response.data.error;
    }

    return error.message || 'An unexpected error occurred';
}

/**
 * Create a confirmation dialog
 * @param {string} message - The confirmation message
 * @param {Function} onConfirm - Function to call when confirmed
 * @param {string} title - Dialog title
 */
function confirmAction(message, onConfirm, title = 'Confirm Action') {
    if (confirm(message)) {
        onConfirm();
    }
}

/**
 * Get URL query parameters
 * @returns {Object} Object containing query parameters
 */
function getQueryParams() {
    const params = {};
    const queryString = window.location.search.substring(1);
    const pairs = queryString.split('&');

    for (let i = 0; i < pairs.length; i++) {
        const pair = pairs[i].split('=');
        params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
    }

    return params;
}

/**
 * Set page title with app name
 * @param {string} title - Page title
 */
function setPageTitle(title) {
    document.title = title ? `${title} - Chandrakanta CRM` : 'Chandrakanta CRM';
}

/**
 * Add event listener to dynamic elements
 * @param {HTMLElement} parent - Parent element
 * @param {string} selector - CSS selector for target elements
 * @param {string} event - Event name
 * @param {Function} handler - Event handler
 */
function addDelegatedEventListener(parent, selector, event, handler) {
    parent.addEventListener(event, function (e) {
        for (let target = e.target; target && target !== this; target = target.parentNode) {
            if (target.matches(selector)) {
                handler.call(target, e);
                break;
            }
        }
    }, false);
}
