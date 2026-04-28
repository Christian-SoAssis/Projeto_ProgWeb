"use client"

import { useEffect, useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { useAuth } from "@/context/auth-context"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"

export default function AuthCallbackPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { oauthLogin } = useAuth()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const accessToken = searchParams.get("access_token")
    const refreshToken = searchParams.get("refresh_token")

    if (accessToken && refreshToken) {
      oauthLogin(accessToken, refreshToken)
        .then(() => {
          toast.success("Autenticado com sucesso via Google!")
        })
        .catch((err) => {
          console.error("Erro ao autenticar", err)
          setError("Ocorreu um erro ao configurar sua sessão.")
          setTimeout(() => router.push("/login"), 3000)
        })
    } else {
      setError("Tokens de autenticação não encontrados.")
      setTimeout(() => router.push("/login"), 3000)
    }
  }, [searchParams, oauthLogin, router])

  if (error) {
    return (
      <main className="min-h-screen p-6 bg-background flex flex-col items-center justify-center gap-4">
        <h1 className="text-xl font-bold text-destructive">Falha na Autenticação</h1>
        <p className="text-muted-foreground">{error}</p>
        <p className="text-sm">Redirecionando para o login...</p>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-6 bg-background flex flex-col items-center justify-center gap-4">
      <Loader2 className="w-10 h-10 animate-spin text-primary" />
      <h1 className="text-2xl font-bold tracking-tight">Autenticando...</h1>
      <p className="text-muted-foreground">Por favor, aguarde enquanto configuramos sua conta.</p>
    </main>
  )
}
