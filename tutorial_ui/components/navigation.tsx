'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
    const pathname = usePathname();

    const isActive = (path: string) => pathname === path;

    return (
        <nav className="bg-white shadow-md fixed top-0 left-0 right-0 z-50">
        <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
        <div className="flex space-x-8 items-center">
        <Link href="/" className="text-xl font-bold text-blue-600">
        Samplr
        </Link>
    <Link
    href="/dashboard"
    className={`px-3 py-2 rounded-md text-sm font-medium ${
        isActive('/dashboard')
            ? 'bg-blue-100 text-blue-700'
            : 'text-gray-600 hover:text-gray-900'
    }`}
>
    Dashboard
    </Link>
    </div>
    </div>
    </div>
    </nav>
);
}