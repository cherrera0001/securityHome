import axios, { AxiosError, AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle errors
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        if (error.response?.status === 401) {
            // Token expired or invalid - clear auth and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// API methods
export const authAPI = {
    login: async (email: string, password: string) => {
        const formData = new FormData();
        formData.append('username', email); // OAuth2 uses 'username' field
        formData.append('password', password);

        const response = await api.post('/api/auth/login', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    register: async (data: {
        email: string;
        username: string;
        password: string;
        full_name: string;
    }) => {
        const response = await api.post('/api/auth/register', data);
        return response.data;
    },

    me: async () => {
        const response = await api.get('/api/users/me');
        return response.data;
    },
};

export const dashboardAPI = {
    getStats: async () => {
        const response = await api.get('/api/dashboard/stats');
        return response.data;
    },

    getActivity: async (days: number = 7) => {
        const response = await api.get(`/api/dashboard/activity?days=${days}`);
        return response.data;
    },
};

export const videosAPI = {
    getAll: async (page: number = 1, limit: number = 20) => {
        const response = await api.get(`/api/videos?page=${page}&limit=${limit}`);
        return response.data;
    },

    getRecent: async (limit: number = 10) => {
        const response = await api.get(`/api/videos/recent?limit=${limit}`);
        return response.data;
    },

    getById: async (id: number) => {
        const response = await api.get(`/api/videos/${id}`);
        return response.data;
    },

    upload: async (file: File, onProgress?: (progress: number) => void) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/api/videos/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
                if (progressEvent.total && onProgress) {
                    const percentCompleted = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    onProgress(percentCompleted);
                }
            },
        });
        return response.data;
    },

    getStatus: async (id: number) => {
        const response = await api.get(`/api/videos/${id}/status`);
        return response.data;
    },

    getDetections: async (id: number) => {
        const response = await api.get(`/api/videos/${id}/detections`);
        return response.data;
    },

    getFaces: async (id: number) => {
        const response = await api.get(`/api/videos/${id}/faces`);
        return response.data;
    },
};

export const facesAPI = {
    getAll: async (videoId?: number, page: number = 1, limit: number = 20) => {
        let url = `/api/faces?page=${page}&limit=${limit}`;
        if (videoId) {
            url += `&video_id=${videoId}`;
        }
        const response = await api.get(url);
        return response.data;
    },

    search: async (faceId: number, threshold: number = 0.7, maxResults: number = 10) => {
        const response = await api.post('/api/faces/search', {
            face_embedding_id: faceId,
            threshold,
            max_results: maxResults,
        });
        return response.data;
    },

    markAsPOI: async (faceId: number, label: string, notes?: string) => {
        const response = await api.post('/api/faces/mark-poi', {
            face_embedding_id: faceId,
            poi_label: label,
            notes,
        });
        return response.data;
    },
};

export const reportsAPI = {
    generate: async (videoId: number, options: {
        report_type: string;
        include_faces?: boolean;
        include_chain_of_custody?: boolean;
    }) => {
        const response = await api.post('/api/reports/generate', {
            video_id: videoId,
            ...options,
        });
        return response.data;
    },

    getAll: async () => {
        const response = await api.get('/api/reports');
        return response.data;
    },

    getById: async (id: number) => {
        const response = await api.get(`/api/reports/${id}`);
        return response.data;
    },

    download: async (id: number) => {
        const response = await api.get(`/api/reports/${id}/download`, {
            responseType: 'blob',
        });
        return response.data;
    },
};

export default api;
