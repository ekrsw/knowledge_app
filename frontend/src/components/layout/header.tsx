'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'

export function Header() {
  return (
    <header className="border-b bg-white shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="bg-blue-600 text-white rounded-lg p-2">
              <span className="text-xl font-bold">KRS</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">
              Knowledge Revision System
            </span>
          </Link>
          
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/revisions" className="text-gray-600 hover:text-gray-900">
              修正案
            </Link>
            <Link href="/approvals" className="text-gray-600 hover:text-gray-900">
              承認
            </Link>
            <Link href="/notifications" className="text-gray-600 hover:text-gray-900">
              通知
            </Link>
          </nav>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              ログイン
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}