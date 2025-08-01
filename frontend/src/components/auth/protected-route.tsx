'use client'

import { useAuth } from '@/hooks/use-auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: string
  requiredApprovalGroup?: number
}

export function ProtectedRoute({ 
  children, 
  requiredRole, 
  requiredApprovalGroup 
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/signin')
      return
    }

    if (user) {
      // 役割チェック
      if (requiredRole && user.role !== requiredRole) {
        router.push('/auth/error?error=AccessDenied')
        return
      }

      // 承認グループチェック
      if (requiredApprovalGroup && user.approval_group_id !== requiredApprovalGroup) {
        router.push('/auth/error?error=AccessDenied')
        return
      }
    }
  }, [user, isLoading, isAuthenticated, requiredRole, requiredApprovalGroup, router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}