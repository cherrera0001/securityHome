import { authAPI } from './api';

export interface User {
    id: number;
    email: string;
    username: string;
    full_name: string;
    role: 'admin' | 'investigator' | 'client';
    is_active: boolean;
}

export interface AuthTokens {
    access_token: string;
    token_type: string;
}

export const authService = {
    login: async (email: string, password: string): Promise<User> => {
        const data: AuthTokens = await authAPI.login(email, password);

        // Store token
        localStorage.setItem('access_token', data.access_token);

        // Fetch and store user info
        const user = await authAPI.me();
        localStorage.setItem('user', JSON.stringify(user));

        return user;
    },

    register: async (data: {
        email: string;
        username: string;
        password: string;
        full_name: string;
    }): Promise<User> => {
        const user = await authAPI.register(data);
        return user;
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    },

    getToken: (): string | null => {
        return localStorage.getItem('access_token');
    },

    getUser: (): User | null => {
        const userStr = localStorage.getItem('user');
        if (!userStr) return null;
        try {
            return JSON.parse(userStr);
        } catch {
            return null;
        }
    },

    isAuthenticated: (): boolean => {
        return !!localStorage.getItem('access_token');
    },

    hasRole: (role: string): boolean => {
        const user = authService.getUser();
        return user?.role === role;
    },
};
