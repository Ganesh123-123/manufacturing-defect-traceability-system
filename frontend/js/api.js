/**
 * Centralized API Client for Manufacturing Defect Traceability System
 */
const API_BASE_URL = (window.location.port === '5000')
    ? `${window.location.origin}/api`
    : 'http://127.0.0.1:5000/api';

class ApiClient {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(options.headers || {})
        };

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const contentType = response.headers.get("content-type");
            let data = null;

            if (contentType && contentType.includes("application/json")) {
                data = await response.json();
            } else if (response.status !== 204) {
                data = await response.text();
            }

            if (!response.ok) {
                const errorMessage = (data && data.error) ? data.error : `HTTP ${response.status}: ${response.statusText}`;
                const error = new Error(errorMessage);
                error.status = response.status;
                error.data = data;
                throw error;
            }

            return data;
        } catch (error) {
            console.error(`API Error on [${options.method || 'GET'}] ${url}:`, error);
            throw error;
        }
    }

    static get(endpoint, params = {}) {
        const queryString = new URLSearchParams(
            Object.entries(params).filter(([_, v]) => v !== undefined && v !== null && v !== '')
        ).toString();
        const fullUrl = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(fullUrl, { method: 'GET' });
    }

    static post(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    static put(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    }

    static patch(endpoint, body = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(body)
        });
    }

    static delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Ping system health
    static async checkHealth() {
        try {
            return await this.get('/system/health');
        } catch (e) {
            return { status: 'offline', database: 'disconnected' };
        }
    }
}
