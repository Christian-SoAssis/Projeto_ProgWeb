"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, Key, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { apiFetch } from "@/infrastructure/http/http-client"
import { toast } from "sonner"

type PixKeyType = "cpf" | "cnpj" | "email" | "phone" | "random"

export default function PayoutSettingsPage() {
  const router = useRouter()
  const [keyType, setKeyType] = useState<PixKeyType>("cpf")
  const [keyValue, setKeyValue] = useState("")
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)
  const [hasExistingKey, setHasExistingKey] = useState(false)

  // Load existing key
  useEffect(() => {
    async function loadPixKey() {
      try {
        const response = await apiFetch("/auth/professional/pix")
        if (response && response.key_value) {
          setKeyType(response.key_type as PixKeyType)
          setKeyValue(response.key_value)
          setHasExistingKey(true)
        }
      } catch (err) {
        // If 404, it means no key is registered yet, which is expected
        console.log("Nenhuma chave cadastrada ainda.")
      } finally {
        setFetching(false)
      }
    }
    loadPixKey()
  }, [])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyValue.trim()) {
      toast.error("Por favor, preencha o valor da chave Pix")
      return
    }

    setLoading(false)
    try {
      setLoading(true)
      const response = await apiFetch("/auth/professional/pix", {
        method: "POST",
        body: JSON.stringify({
          key_type: keyType,
          key_value: keyValue,
        }),
      })

      if (response && response.key_value) {
        setKeyValue(response.key_value)
        setHasExistingKey(true)
        toast.success("Chave Pix salva com sucesso!", {
          className: "neo-elevated rounded-2xl border-none text-foreground font-bold"
        })
      }
    } catch (err: any) {
      toast.error(err.message || "Erro ao salvar a chave Pix")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex justify-center items-start sm:py-6 relative font-sans">
      <div className="w-full max-w-[480px] bg-background min-h-screen sm:min-h-[840px] sm:rounded-[2.5rem] sm:neo-elevated overflow-hidden flex flex-col relative border-none pb-12">
        
        {/* Header */}
        <header className="px-5 py-4 bg-background neo-elevated flex items-center gap-3 shrink-0">
          <button 
            onClick={() => router.push("/profile/pro")}
            className="w-10 h-10 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all"
          >
            <ChevronLeft className="w-5 h-5 text-muted-foreground" />
          </button>
          <h2 className="text-base font-black text-foreground/90">Dados de Payout</h2>
        </header>

        {/* Content */}
        <div className="flex-1 px-5 py-6 space-y-6 overflow-y-auto">
          <section className="space-y-4">
            <h3 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/80 px-1">
              Recebimento de Repasses (Pix)
            </h3>
            
            <Card className="border-none rounded-[2rem] p-6 space-y-6 neo-elevated text-left">
              <div className="flex items-center gap-3 text-primary mb-2">
                <div className="w-10 h-10 rounded-xl neo-inset flex items-center justify-center bg-background/50">
                  <Key className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold">Chave Pix para Split</h4>
                  <p className="text-[10px] text-muted-foreground font-medium">Os valores dos serviços serão enviados para esta conta.</p>
                </div>
              </div>

              {fetching ? (
                <div className="space-y-3">
                  <div className="h-10 bg-muted/20 animate-pulse rounded-xl" />
                  <div className="h-12 bg-muted/20 animate-pulse rounded-xl" />
                </div>
              ) : (
                <form onSubmit={handleSave} className="space-y-5">
                  {/* Select Key Type */}
                  <div className="space-y-2">
                    <label className="text-[11px] font-black uppercase tracking-wider text-muted-foreground">
                      Tipo de Chave
                    </label>
                    <div className="relative">
                      <select
                        value={keyType}
                        onChange={(e) => {
                          setKeyType(e.target.value as PixKeyType)
                          if (hasExistingKey) {
                            setKeyValue("")
                            setHasExistingKey(false)
                          }
                        }}
                        className="w-full h-12 px-4 rounded-xl bg-background border-none text-xs font-bold neo-inset focus:outline-none appearance-none"
                      >
                        <option value="cpf">CPF</option>
                        <option value="cnpj">CNPJ</option>
                        <option value="email">E-mail</option>
                        <option value="phone">Telefone (Celular com DDD)</option>
                        <option value="random">Chave Aleatória (UUID)</option>
                      </select>
                      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground text-xs font-bold">
                        ▼
                      </div>
                    </div>
                  </div>

                  {/* Input Key Value */}
                  <div className="space-y-2">
                    <label className="text-[11px] font-black uppercase tracking-wider text-muted-foreground">
                      Valor da Chave
                    </label>
                    <input
                      type="text"
                      value={keyValue}
                      onChange={(e) => setKeyValue(e.target.value)}
                      placeholder={
                        keyType === "cpf" ? "000.000.000-00" :
                        keyType === "cnpj" ? "00.000.000/0000-00" :
                        keyType === "phone" ? "11999999999" :
                        keyType === "email" ? "nome@exemplo.com" : "Chave aleatória"
                      }
                      className="w-full h-12 px-4 rounded-xl bg-background border-none text-xs font-bold neo-inset focus:outline-none"
                    />
                  </div>

                  {hasExistingKey && (
                    <div className="p-3 bg-primary/10 rounded-xl flex items-center gap-2">
                      <Check className="w-4 h-4 text-primary shrink-0" />
                      <span className="text-[10px] font-bold text-primary">
                        Já existe uma chave cadastrada. Digite um novo valor acima caso queira atualizá-la.
                      </span>
                    </div>
                  )}

                  {/* Save Button */}
                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-14 bg-background text-primary font-black text-sm rounded-xl neo-elevated hover:bg-muted/5 transition-all border-none"
                  >
                    {loading ? "Salvando..." : "Salvar Chave Pix"}
                  </Button>
                </form>
              )}
            </Card>
          </section>
        </div>

      </div>
    </main>
  )
}
