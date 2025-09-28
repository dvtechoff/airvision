import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Navbar from '@/components/Navbar'
import { AppDataProvider } from '@/lib/AppDataContext'
import { CityProvider } from '@/contexts/CityContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AirVision - From Earth Data to Safer Skies',
  description: 'Professional air quality monitoring powered by NASA TEMPO satellite data',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-white min-h-screen text-black`}>
        <CityProvider>
          <AppDataProvider>
            <Navbar />
            <main className="pt-16">
              {children}
            </main>
          </AppDataProvider>
        </CityProvider>
      </body>
    </html>
  )
}
