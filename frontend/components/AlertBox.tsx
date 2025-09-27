'use client'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { motion } from 'framer-motion'
import { AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react'

interface AlertBoxProps {
  type: 'warning' | 'info' | 'success' | 'error'
  title: string
  description: string
  className?: string
}

export default function AlertBox({ type, title, description, className }: AlertBoxProps) {
  const icons = {
    warning: AlertTriangle,
    info: Info,
    success: CheckCircle,
    error: XCircle
  }

  const colors = {
    warning: 'text-orange-500',
    info: 'text-blue-500',
    success: 'text-green-500',
    error: 'text-red-500'
  }

  const Icon = icons[type]

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      <Alert className={`border-l-4 ${
        type === 'warning' ? 'border-orange-500 bg-orange-50' :
        type === 'info' ? 'border-blue-500 bg-blue-50' :
        type === 'success' ? 'border-green-500 bg-green-50' :
        'border-red-500 bg-red-50'
      }`}>
        <Icon className={`h-4 w-4 ${colors[type]}`} />
        <AlertTitle className={colors[type]}>{title}</AlertTitle>
        <AlertDescription className="text-gray-700">
          {description}
        </AlertDescription>
      </Alert>
    </motion.div>
  )
}
