"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function ChatIndexPage() {
  const router = useRouter()

  useEffect(() => {
    router.replace("/chat/demo-contract-123")
  }, [router])

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-muted-foreground font-bold tracking-wide">
          Carregando ambiente de chat...
        </span>
      </div>
    </div>
  )
}
