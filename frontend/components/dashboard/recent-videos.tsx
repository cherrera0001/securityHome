'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useRecentVideos } from '@/hooks/useDashboard';
import { formatFileSize, formatTimestamp } from '@/lib/utils';
import { AlertCircle, CheckCircle, Clock, Loader2, Play } from 'lucide-react';
import Link from 'next/link';

export function RecentVideos() {
    const { data: videos, isLoading, error } = useRecentVideos(10);

    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Videos Recientes</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-center space-x-4 animate-pulse">
                                <div className="h-16 w-24 bg-gray-200 rounded"></div>
                                <div className="flex-1 space-y-2">
                                    <div className="h-4 w-3/4 bg-gray-200 rounded"></div>
                                    <div className="h-3 w-1/2 bg-gray-200 rounded"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Videos Recientes</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-red-600">Error al cargar videos</p>
                </CardContent>
            </Card>
        );
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-green-600" />;
            case 'processing':
                return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
            case 'failed':
                return <AlertCircle className="h-4 w-4 text-red-600" />;
            default:
                return <Clock className="h-4 w-4 text-gray-600" />;
        }
    };

    const getStatusText = (status: string) => {
        switch (status) {
            case 'completed':
                return 'Completado';
            case 'processing':
                return 'Procesando';
            case 'failed':
                return 'Error';
            default:
                return status;
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Videos Recientes</CardTitle>
            </CardHeader>
            <CardContent>
                {!videos || videos.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                        <Play className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No hay videos todavía</p>
                        <p className="text-sm">Sube tu primer video para comenzar</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {videos.map((video: any) => (
                            <Link
                                key={video.id}
                                href={`/dashboard/videos/${video.id}`}
                                className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                <div className="relative h-16 w-24 bg-gray-200 rounded overflow-hidden flex-shrink-0">
                                    {video.thumbnail_url ? (
                                        <img
                                            src={video.thumbnail_url}
                                            alt={video.filename}
                                            className="object-cover w-full h-full"
                                        />
                                    ) : (
                                        <div className="flex items-center justify-center h-full">
                                            <Play className="h-6 w-6 text-gray-400" />
                                        </div>
                                    )}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium truncate">
                                        {video.filename}
                                    </p>
                                    <div className="flex items-center space-x-2 mt-1">
                                        {getStatusIcon(video.status)}
                                        <span className="text-xs text-muted-foreground">
                                            {getStatusText(video.status)}
                                        </span>
                                        {video.status === 'processing' && video.progress && (
                                            <span className="text-xs text-blue-600">
                                                {Math.round(video.progress)}%
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {formatTimestamp(video.created_at)}
                                        {video.file_size && ` • ${formatFileSize(video.file_size)}`}
                                    </p>
                                </div>
                                {video.status === 'processing' && video.progress && (
                                    <div className="w-24">
                                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-blue-600 transition-all duration-300"
                                                style={{ width: `${video.progress}%` }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </Link>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
