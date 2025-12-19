'use client';

import { dashboardAPI, videosAPI } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';

export function useDashboardStats() {
    return useQuery({
        queryKey: ['dashboard', 'stats'],
        queryFn: dashboardAPI.getStats,
        refetchInterval: 5000, // Refetch every 5 seconds
    });
}

export function useDashboardActivity(days: number = 7) {
    return useQuery({
        queryKey: ['dashboard', 'activity', days],
        queryFn: () => dashboardAPI.getActivity(days),
        refetchInterval: 30000, // Refetch every 30 seconds
    });
}

export function useRecentVideos(limit: number = 10) {
    return useQuery({
        queryKey: ['videos', 'recent', limit],
        queryFn: () => videosAPI.getRecent(limit),
        refetchInterval: 10000, // Refetch every 10 seconds
    });
}
