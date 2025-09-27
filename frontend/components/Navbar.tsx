'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Wind, BarChart3, Bell, Info } from 'lucide-react'

export default function Navbar() {
  return (
    <motion.nav 
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 w-full bg-white/95 backdrop-blur-sm border-b border-gray-200 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <Wind className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">AirVision</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/" className="text-gray-700 hover:text-blue-600 font-medium smooth-transition flex items-center space-x-1">
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
            <Link href="/forecast" className="text-gray-700 hover:text-blue-600 font-medium smooth-transition">
              Forecast
            </Link>
            <Link href="/alerts" className="text-gray-700 hover:text-blue-600 font-medium smooth-transition flex items-center space-x-1">
              <Bell className="w-4 h-4" />
              <span>Alerts</span>
            </Link>
            <Link href="/about" className="text-gray-700 hover:text-blue-600 font-medium smooth-transition flex items-center space-x-1">
              <Info className="w-4 h-4" />
              <span>About</span>
            </Link>
          </div>
        </div>
      </div>
    </motion.nav>
  )
}
