'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardStats } from '@/hooks/useDashboard';
import { Activity, AlertCircle, Users, Video } from 'lucide-react';

export function StatsCards() {
    const { data: stats, isLoading, error } = useDashboardStats();

    if (isLoading) {
        return (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {[1, 2, 3, 4].map((i) => (
                    <Card key={i} className="animate-pulse">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <div className="h-4 w-24 bg-gray-200 rounded"></div>
                            <div className="h-4 w-4 bg-gray-200 rounded"></div>
                        </CardHeader>
                        <CardContent>
                            <div className="h-8 w-16 bg-gray-200 rounded mb-2"></div>
                            <div className="h-3 w-32 bg-gray-200 rounded"></div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600">Error al cargar estadísticas</p>
            </div>
        );
    }

    const cards = [
        {
            title: 'Total Videos',
            value: stats?.total_videos || 0,
            description: 'Videos procesados',
            icon: Video,
            color: 'text-blue-600',
            bgColor: 'bg-blue-100',
        },
        {
            title: 'En Procesamiento',
            value: stats?.videos_processing || 0,
            description: 'Videos en análisis',
            icon: Activity,
            color: 'text-yellow-600',
            bgColor: 'bg-yellow-100',
        },
        {
            title: 'Rostros Hoy',
            value: stats?.faces_today || 0,
            description: 'Rostros detectados hoy',
            icon: Users,
            color: 'text-green-600',
            bgColor: 'bg-green-100',
        },
        {
            title: 'Alertas Activas',
            value: stats?.active_alerts || 0,
            description: 'Alertas sin resolver',
            icon: AlertCircle,
            color: 'text-red-600',
            bgColor: 'bg-red-100',
        },
    ];

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {cards.map((card) => {
                const Icon = card.icon;
                return (
                    <Card key={card.title} className="hover:shadow-lg transition-shadow">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">
                                {card.title}
                            </CardTitle>
                            <div className={`${card.bgColor} p-2 rounded-lg`}>
                                <Icon className={`h-4 w-4 ${card.color}`} />
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {card.value.toLocaleString('es-ES')}
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                {card.description}
                            </p>
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}
