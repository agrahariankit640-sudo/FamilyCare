// FamilyCare API Client
const API = {
    baseUrl: '/api',
    
    // Get CSRF token from meta tag
    getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    },
    
    // Core request method
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            },
            credentials: 'same-origin',
            ...options
        };
        
        // Don't set Content-Type for FormData (file uploads)
        if (options.body instanceof FormData) {
            delete config.headers['Content-Type'];
        }
        
        try {
            const response = await fetch(url, config);
            
            // Handle auth redirect for protected endpoints (exclude login/register/logout)
            if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
                window.location.href = '/login';
                return null;
            }
            
            // Handle non-JSON responses (file downloads)
            const contentType = response.headers.get('content-type');
            if (contentType && !contentType.includes('application/json')) {
                if (!response.ok) throw new Error('Request failed');
                return response;
            }
            
            const data = await response.json();
            if (!response.ok) {
                throw new APIError(data.error || 'Request failed', response.status, data);
            }
            if (data && typeof data === 'object' && 'data' in data && data.success !== undefined) {
                return data.data;
            }
            return data;
        } catch (error) {
            if (error instanceof APIError) throw error;
            throw new APIError('Network error. Please try again.', 0);
        }
    },
    
    // Query string builder
    buildQuery(params) {
        if (!params) return '';
        if (typeof params === 'string') {
            return params.startsWith('?') ? params : '?' + params;
        }
        if (typeof params === 'object') {
            const cleanParams = {};
            for (const [k, v] of Object.entries(params)) {
                if (v !== undefined && v !== null && v !== '') {
                    cleanParams[k] = v;
                }
            }
            const qs = new URLSearchParams(cleanParams).toString();
            return qs ? '?' + qs : '';
        }
        return '';
    },
    
    // Convenience methods
    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },
    
    // File upload
    upload(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            body: formData
        });
    },
    
    // File download
    async download(endpoint, filename) {
        const response = await this.request(endpoint);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    },
    
    // === Module-specific API methods ===
    
    // Auth
    auth: {
        login: (data) => API.post('/auth/login', data),
        register: (data) => API.post('/auth/register', data),
        logout: () => API.post('/auth/logout'),
        me: () => API.get('/auth/me'),
        updateProfile: (data) => API.put('/auth/profile', data),
        changePassword: (data) => API.put('/auth/password', data),
        uploadPhoto: (formData) => API.upload('/auth/profile-photo', formData)
    },
    
    // Dashboard
    dashboard: {
        summary: () => API.get('/dashboard/summary'),
        recentActivity: () => API.get('/dashboard/recent-activity'),
        upcoming: () => API.get('/dashboard/upcoming')
    },
    
    // Family Members
    familyMembers: {
        list: () => API.get('/family-members'),
        get: (id) => API.get(`/family-members/${id}`),
        create: (data) => API.post('/family-members', data),
        update: (id, data) => API.put(`/family-members/${id}`, data),
        delete: (id) => API.delete(`/family-members/${id}`),
        summary: (id) => API.get(`/family-members/${id}/summary`),
        uploadPhoto: (id, formData) => API.upload(`/family-members/${id}/photo`, formData)
    },
    
    // Medical Records
    records: {
        list: (params = '') => API.get(`/records${API.buildQuery(params)}`),
        get: (id) => API.get(`/records/${id}`),
        create: (data) => API.post('/records', data),
        update: (id, data) => API.put(`/records/${id}`, data),
        delete: (id) => API.delete(`/records/${id}`)
    },
    
    // Documents
    documents: {
        upload: (formData) => API.upload('/documents/upload', formData),
        get: (id) => API.get(`/documents/${id}`),
        delete: (id) => API.delete(`/documents/${id}`)
    },
    
    // Prescriptions
    prescriptions: {
        list: (params = '') => API.get(`/prescriptions${API.buildQuery(params)}`),
        get: (id) => API.get(`/prescriptions/${id}`),
        create: (data) => API.post('/prescriptions', data),
        update: (id, data) => API.put(`/prescriptions/${id}`, data),
        delete: (id) => API.delete(`/prescriptions/${id}`)
    },
    
    // Medicines
    medicines: {
        list: (params = '') => API.get(`/medicines${API.buildQuery(params)}`),
        get: (id) => API.get(`/medicines/${id}`),
        create: (data) => API.post('/medicines', data),
        update: (id, data) => API.put(`/medicines/${id}`, data),
        delete: (id) => API.delete(`/medicines/${id}`),
        updateStatus: (id, status) => API.put(`/medicines/${id}/status`, { status })
    },
    
    // Reminders
    reminders: {
        list: (params = '') => API.get(`/reminders${API.buildQuery(params)}`),
        create: (data) => API.post('/reminders', data),
        updateStatus: (id, status) => API.put(`/reminders/${id}/status`, { status }),
        delete: (id) => API.delete(`/reminders/${id}`)
    },
    
    // Appointments
    appointments: {
        list: (params = '') => API.get(`/appointments${API.buildQuery(params)}`),
        get: (id) => API.get(`/appointments/${id}`),
        create: (data) => API.post('/appointments', data),
        update: (id, data) => API.put(`/appointments/${id}`, data),
        delete: (id) => API.delete(`/appointments/${id}`)
    },
    
    // Tests
    tests: {
        list: (params = '') => API.get(`/tests${API.buildQuery(params)}`),
        get: (id) => API.get(`/tests/${id}`),
        create: (data) => API.post('/tests', data),
        update: (id, data) => API.put(`/tests/${id}`, data),
        delete: (id) => API.delete(`/tests/${id}`)
    },
    
    // Vaccinations
    vaccinations: {
        list: (params = '') => API.get(`/vaccinations${API.buildQuery(params)}`),
        get: (id) => API.get(`/vaccinations/${id}`),
        create: (data) => API.post('/vaccinations', data),
        update: (id, data) => API.put(`/vaccinations/${id}`, data),
        delete: (id) => API.delete(`/vaccinations/${id}`)
    },
    
    // Health Parameters
    healthParams: {
        list: (params = '') => API.get(`/health-parameters${API.buildQuery(params)}`),
        create: (data) => API.post('/health-parameters', data),
        delete: (id) => API.delete(`/health-parameters/${id}`),
        trends: (params = '') => API.get(`/health-parameters/trends${API.buildQuery(params)}`)
    },
    
    // Expenses
    expenses: {
        list: (params = '') => API.get(`/expenses${API.buildQuery(params)}`),
        get: (id) => API.get(`/expenses/${id}`),
        create: (data) => API.post('/expenses', data),
        update: (id, data) => API.put(`/expenses/${id}`, data),
        delete: (id) => API.delete(`/expenses/${id}`),
        summary: (params = '') => API.get('/expenses/summary' + (params ? API.buildQuery(params) : ''))
    },
    
    // Insurance
    insurance: {
        listPolicies: () => API.get('/insurance/policies'),
        getPolicy: (id) => API.get(`/insurance/policies/${id}`),
        createPolicy: (data) => API.post('/insurance/policies', data),
        updatePolicy: (id, data) => API.put(`/insurance/policies/${id}`, data),
        deletePolicy: (id) => API.delete(`/insurance/policies/${id}`),
        listClaims: (params = '') => API.get(`/insurance/claims${API.buildQuery(params)}`),
        getClaim: (id) => API.get(`/insurance/claims/${id}`),
        createClaim: (data) => API.post('/insurance/claims', data),
        updateClaim: (id, data) => API.put(`/insurance/claims/${id}`, data),
        deleteClaim: (id) => API.delete(`/insurance/claims/${id}`)
    },
    
    // Timeline
    timeline: {
        get: (params = '') => API.get(`/timeline${API.buildQuery(params)}`)
    },
    
    // Search
    search: {
        query: (params = '') => API.get(`/search${API.buildQuery(params)}`)
    },
    
    // Emergency
    emergency: {
        getMember: (id) => API.get(`/emergency/${id}`),
        getAll: () => API.get('/emergency/all')
    },
    
    // Notifications
    notifications: {
        list: () => API.get('/notifications'),
        markRead: (id) => API.put(`/notifications/${id}/read`),
        markAllRead: () => API.put('/notifications/read-all'),
        delete: (id) => API.delete(`/notifications/${id}`),
        unreadCount: () => API.get('/notifications/unread-count')
    },
    
    // Export
    export: {
        backup: () => API.download('/export/backup', 'familycare_backup.json'),
        csv: (module) => API.download(`/export/csv/${module}`, `familycare_${module}.csv`),
        familySummary: (id) => API.download(`/export/family-summary/${id}`, 'family_summary.json')
    },
    
    // Users & Profile
    users: {
        getProfile: () => API.get('/users/me'),
        updateSettings: (data) => API.put('/users/settings', data),
        uploadPhoto: (formData) => API.upload('/users/photo', formData),
        deletePhoto: () => API.delete('/users/photo'),
        deleteAccount: (confirmData) => API.delete('/users/account', confirmData)
    },
    
    // Admin
    admin: {
        stats: () => API.get('/admin/stats'),
        users: () => API.get('/admin/users'),
        setUserStatus: (id, isActive) => API.put(`/admin/users/${id}/status`, { is_active: isActive }),
        activityLog: () => API.get('/admin/activity-log')
    }
};

// Custom API Error class
class APIError extends Error {
    constructor(message, status, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}
