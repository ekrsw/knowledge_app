import 'next-auth'
import { DefaultSession } from 'next-auth'
import { JWT } from 'next-auth/jwt'

declare module 'next-auth' {
  interface Session {
    accessToken?: string
    user: {
      id: string
      username: string
      name: string
      role: string
      approval_group_id: number
    } & DefaultSession['user']
  }

  interface User {
    id: string
    username: string
    name: string
    role: string
    approval_group_id: number
    accessToken: string
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken?: string
    role?: string
    approval_group_id?: number
  }
}