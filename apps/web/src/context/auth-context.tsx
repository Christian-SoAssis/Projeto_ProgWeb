"use client"

import React, { createContext, useContext, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"

interface User {
  id: string
  name: string
  email: string
  role: "client" | "professional"
}

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (credentials: any) => Promise<void>
  registerClient: (data: any) => Promise<void>
  registerPro: (formData: FormData) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("access_token")
      if (token) {
        try {
          const userData = await apiFetch("/auth/me")
          setUser(userData)
        } catch (error) {
          console.error("Falha ao carregar usuário:", error)
          logout()
        }
      }
      setLoading(false)
    }
    loadUser()
  }, [])

  const login = async (credentials: any) => {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    })
    
    localStorage.setItem("access_token", data.access_token)
    localStorage.setItem("refresh_token", data.refresh_token)
    
    // Carregar dados completos do usuário
    const userData = await apiFetch("/auth/me")
    setUser(userData)
    
    // Redirecionar baseado no papel
    if (userData.role === "professional") {
      router.push("/dashboard/pro")
    } else {
      router.push("/dashboard/client")
    }
  }

  const registerClient = async (data: any) => {
    const response = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    })
    
    localStorage.setItem("access_token", response.access_token)
    localStorage.setItem("refresh_token", response.refresh_token)
    
    const userData = await apiFetch("/auth/me")
    setUser(userData)
    router.push("/dashboard/client")
  }

  const registerPro = async (formData: FormData) => {
    // Para profissionais, o backend de registro retorna o objeto ProfessionalResponse, 
    // não tokens diretamente em alguns casos dependendo do endpoint. 
    // Mas o router.post("/") em professionals.py retorna o professional.
    // O usuário profissional precisará logar após o cadastro ou o backend emitir tokens.
    // Olhando professionals.py, ele retorna o objeto professional.
    
    await apiFetch("/professionals", {
      method: "POST",
      body: formData,
    })
    
    // Como o endpoint de profissionais não retorna tokens, vamos fazer login automático
    // se tivermos a senha ou pedir para o usuário logar.
    // Por simplicidade aqui, vamos apenas avisar e jogar para o login.
    router.push("/login?registered=true")
  }

  const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setUser(null)
    router.push("/login")
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      isAuthenticated: !!user, 
      login, 
      registerClient, 
      registerPro,
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider")
  }
  return context
}
