import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Tutorial Helper',
    description: 'Video tutorial upload and processing',
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
        <body>
            {children}
        </body>
        </html>
    );
}