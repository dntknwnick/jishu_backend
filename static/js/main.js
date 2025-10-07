// Main JavaScript utilities for API interactions
// This file provides a JavaScript SDK for interacting with the Jishu Backend API
// Can be used in React frontend or any other JavaScript application

// Base API configuration
const API_BASE_URL = window.location.origin;

// Helper function to make API requests
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    // Add authorization header if token exists
    const token = localStorage.getItem('access_token');
    if (token) {
        defaultOptions.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        return {
            success: response.ok,
            status: response.status,
            data: data,
        };
    } catch (error) {
        return {
            success: false,
            status: 0,
            data: { message: 'Network error occurred' },
        };
    }
}

// Authentication functions
const auth = {
    // Register new user
    async register(userData) {
        return await apiRequest('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },
    
    // Login user
    async login(credentials) {
        const result = await apiRequest('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
        
        if (result.success && result.data.data && result.data.data.access_token) {
            localStorage.setItem('access_token', result.data.data.access_token);
            localStorage.setItem('user', JSON.stringify(result.data.data.user));
        }
        
        return result;
    },
    
    // Google OAuth login/registration
    async googleAuth(token) {
        const result = await apiRequest('/api/auth/google', {
            method: 'POST',
            body: JSON.stringify({ token }),
        });

        if (result.success && result.data.data && result.data.data.access_token) {
            localStorage.setItem('access_token', result.data.data.access_token);
            localStorage.setItem('user', JSON.stringify(result.data.data.user));

            // Return additional info about whether this is a new user
            return {
                ...result,
                isNewUser: result.data.data.is_new_user || false,
                needsProfileCompletion: result.data.data.user.source === 'google' && !result.data.data.user.mobile_no
            };
        }

        return result;
    },
    
    // Verify token
    async verifyToken() {
        return await apiRequest('/api/auth/verify-token', {
            method: 'POST',
        });
    },
    
    // Logout
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    },
    
    // Check if user is authenticated
    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },

    // Get current user
    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    },

    // Check if user needs to complete profile (Google users without mobile)
    needsProfileCompletion() {
        const user = this.getCurrentUser();
        return user && user.source === 'google' && !user.mobile_no;
    },

    // Check if user is admin
    isAdmin() {
        const user = this.getCurrentUser();
        return user && user.is_admin;
    },

    // Check if user is premium
    isPremium() {
        const user = this.getCurrentUser();
        return user && user.is_premium;
    },
};

// User management functions
const user = {
    // Get user profile
    async getProfile() {
        return await apiRequest('/api/user/profile', {
            method: 'GET',
        });
    },
    
    // Update user profile
    async updateProfile(profileData) {
        const result = await apiRequest('/api/user/profile', {
            method: 'PUT',
            body: JSON.stringify(profileData),
        });
        
        if (result.success && result.data.data && result.data.data.user) {
            localStorage.setItem('user', JSON.stringify(result.data.data.user));
        }
        
        return result;
    },
    
    // Change password
    async changePassword(passwordData) {
        return await apiRequest('/api/user/change-password', {
            method: 'POST',
            body: JSON.stringify(passwordData),
        });
    },
};

// Admin functions
const admin = {
    // Get all users
    async getUsers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/api/admin/users?${queryString}` : '/api/admin/users';
        
        return await apiRequest(endpoint, {
            method: 'GET',
        });
    },
    
    // Update user status
    async updateUserStatus(userId, status) {
        return await apiRequest(`/api/admin/users/${userId}/status`, {
            method: 'PUT',
            body: JSON.stringify({ status }),
        });
    },
};

// Utility functions
const utils = {
    // Show alert message
    showAlert(type, message, duration = 5000) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto dismiss
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    },
    
    // Clear form errors
    clearFormErrors() {
        document.querySelectorAll('.is-invalid').forEach(element => {
            element.classList.remove('is-invalid');
        });
        document.querySelectorAll('.invalid-feedback').forEach(element => {
            element.textContent = '';
        });
    },
    
    // Show form errors
    showFormErrors(errors) {
        Object.keys(errors).forEach(field => {
            const input = document.getElementById(field);
            if (input) {
                input.classList.add('is-invalid');
                const feedback = input.nextElementSibling;
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.textContent = errors[field];
                }
            }
        });
    },
    
    // Validate email format
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Validate mobile number (Indian format)
    validateMobile(mobile) {
        const re = /^[6-9]\d{9}$/;
        return re.test(mobile);
    },
    
    // Validate password strength
    validatePassword(password) {
        const minLength = password.length >= 8;
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasNumber = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        
        return {
            isValid: minLength && hasUpper && hasLower && hasNumber && hasSpecial,
            errors: {
                minLength: !minLength ? 'Password must be at least 8 characters long' : null,
                hasUpper: !hasUpper ? 'Password must contain at least one uppercase letter' : null,
                hasLower: !hasLower ? 'Password must contain at least one lowercase letter' : null,
                hasNumber: !hasNumber ? 'Password must contain at least one digit' : null,
                hasSpecial: !hasSpecial ? 'Password must contain at least one special character' : null,
            }
        };
    },
    
    // Format date
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    },
    
    // Format datetime
    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString();
    },
};

// Export for use in other scripts
window.JishuAPI = {
    auth,
    user,
    admin,
    utils,
    apiRequest,
};
