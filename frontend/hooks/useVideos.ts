'use client';

import { videosAPI } from '@/lib/api';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

export function useVideos(page: number = 1, limit: number = 20) {
    return useQuery({
        queryKey: ['videos', page, limit],
        queryFn: () => videosAPI.getAll(page, limit),
    });
}

export function useVideo(id: number) {
    return useQuery({
        queryKey: ['video', id],
        queryFn: () => videosAPI.getById(id),
        enabled: !!id,
    });
}

export function useVideoStatus(id: number, enabled: boolean = true) {
    return useQuery({
        queryKey: ['video', id, 'status'],
        queryFn: () => videosAPI.getStatus(id),
        enabled: enabled && !!id,
        refetchInterval: (data) => {
            // Stop polling if video is completed or failed
            if (data?.status === 'completed' || data?.status === 'failed') {
                return false;
            }
            return 2000; // Poll every 2 seconds while processing
        },
    });
}

export function useVideoUpload() {
    const [progress, setProgress] = useState(0);
    const queryClient = useQueryClient();

    const mutation = useMutation({
        mutationFn: (file: File) => videosAPI.upload(file, setProgress),
        onSuccess: () => {
            // Invalidate videos queries to refetch
            queryClient.invalidateQueries({ queryKey: ['videos'] });
            setProgress(0);
        },
        onError: () => {
            setProgress(0);
        },
    });

    return {
        upload: mutation.mutate,
        uploading: mutation.isPending,
        progress,
        error: mutation.error,
        data: mutation.data,
    };
}
