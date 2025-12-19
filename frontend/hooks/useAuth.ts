'use client';

import { authService, User } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export function useAuth() {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Check if user is authenticated on mount
        const currentUser = authService.getUser();
        setUser(currentUser);
        setLoading(false);
    }, []);

    const login = async (email: string, password: string) => {
        try {
            const user = await authService.login(email, password);
            setUser(user);
            router.push('/dashboard');
            return user;
        } catch (error) {
            throw error;
        }
    };

    const register = async (data: {
        email: string;
        username: string;
        password: string;
        full_name: string;
    }) => {
        try {
            const user = await authService.register(data);
            router.push('/login');
            return user;
        } catch (error) {
            throw error;
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    return {
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
    };
}
