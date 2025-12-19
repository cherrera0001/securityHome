'use client';

import { ProtectedRoute } from '@/components/auth/protected-route';
import { RecentVideos } from '@/components/dashboard/recent-videos';
import { StatsCards } from '@/components/dashboard/stats-cards';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { LogOut, Upload, User } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
    const { user, logout } = useAuth();

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
                {/* Header */}
                <header className="bg-white border-b">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex justify-between items-center h-16">
                            <div className="flex items-center">
                                <h1 className="text-2xl font-bold text-gray-900">
                                    ForensicVideo AI
                                </h1>
                            </div>
                            <div className="flex items-center space-x-4">
                                <Link href="/dashboard/upload">
                                    <Button>
                                        <Upload className="h-4 w-4 mr-2" />
                                        Subir Video
                                    </Button>
                                </Link>
                                <div className="flex items-center space-x-2 text-sm">
                                    <User className="h-4 w-4" />
                                    <span>{user?.full_name || user?.username}</span>
                                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                        {user?.role}
                                    </span>
                                </div>
                                <Button variant="outline" size="sm" onClick={logout}>
                                    <LogOut className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Main Content */}
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {/* Welcome Section */}
                    <div className="mb-8">
                        <h2 className="text-3xl font-bold text-gray-900">
                            Bienvenido, {user?.full_name?.split(' ')[0] || user?.username}
                        </h2>
                        <p className="text-gray-600 mt-1">
                            Resumen de tu actividad forense
                        </p>
                    </div>

                    {/* Stats Cards */}
                    <div className="mb-8">
                        <StatsCards />
                    </div>

                    {/* Recent Videos */}
                    <div className="grid gap-6 md:grid-cols-2">
                        <RecentVideos />

                        {/* Quick Actions */}
                        <div className="space-y-4">
                            <div className="bg-white p-6 rounded-lg border">
                                <h3 className="text-lg font-semibold mb-4">Acciones Rápidas</h3>
                                <div className="space-y-3">
                                    <Link href="/dashboard/upload">
                                        <Button className="w-full justify-start" variant="outline">
                                            <Upload className="h-4 w-4 mr-2" />
                                            Subir nuevo video
                                        </Button>
                                    </Link>
                                    <Link href="/dashboard/videos">
                                        <Button className="w-full justify-start" variant="outline">
                                            Ver todos los videos
                                        </Button>
                                    </Link>
                                    <Link href="/dashboard/faces">
                                        <Button className="w-full justify-start" variant="outline">
                                            Galería de rostros
                                        </Button>
                                    </Link>
                                    <Link href="/dashboard/reports">
                                        <Button className="w-full justify-start" variant="outline">
                                            Generar reporte
                                        </Button>
                                    </Link>
                                </div>
                            </div>

                            {/* System Status */}
                            <div className="bg-white p-6 rounded-lg border">
                                <h3 className="text-lg font-semibold mb-4">Estado del Sistema</h3>
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">API</span>
                                        <span className="flex items-center text-sm text-green-600">
                                            <span className="h-2 w-2 bg-green-600 rounded-full mr-2"></span>
                                            Operativo
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">Workers</span>
                                        <span className="flex items-center text-sm text-green-600">
                                            <span className="h-2 w-2 bg-green-600 rounded-full mr-2"></span>
                                            Activos
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">Storage</span>
                                        <span className="flex items-center text-sm text-green-600">
                                            <span className="h-2 w-2 bg-green-600 rounded-full mr-2"></span>
                                            Disponible
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </ProtectedRoute>
    );
}
