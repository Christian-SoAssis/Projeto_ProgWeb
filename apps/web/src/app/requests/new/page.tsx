"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "sonner"
import { ChevronLeft, MapPin, Loader2, Camera } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { useAuth } from "@/context/auth-context"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const newRequestSchema = z.object({
  title: z.string().min(5, "Título deve ter no mínimo 5 caracteres.").max(200),
  description: z.string().max(2000).optional(),
  category_id: z.string().uuid("Selecione uma categoria."),
  urgency: z.enum(["immediate", "scheduled", "flexible"]),
  budget_cents: z.coerce.number().int().positive().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
})

const urgencyLabels: Record<string, string> = {
  immediate: "Urgente — Preciso hoje",
  scheduled: "Agendado — Nos próximos dias",
  flexible: "Flexível — Sem pressa",
}

export default function NewRequestPage() {
  const router = useRouter()
  const { isAuthenticated, loading } = useAuth()
  const [categories, setCategories] = useState<any[]>([])
  const [isLocating, setIsLocating] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [images, setImages] = useState<File[]>([])

  const form = useForm<z.infer<typeof newRequestSchema>>({
    resolver: zodResolver(newRequestSchema),
    defaultValues: {
      title: "",
      description: "",
      urgency: "flexible",
    },
  })

  const watchedLatitude = form.watch("latitude")
  const watchedLongitude = form.watch("longitude")

  // Redirecionar se não autenticado
  useEffect(() => {
    if (!loading && !isAuthenticated) router.push("/login")
  }, [loading, isAuthenticated, router])

  // Carregar categorias
  useEffect(() => {
    apiFetch("/categories").then(setCategories).catch(() => {})
  }, [])

  // Capturar localização automaticamente
  useEffect(() => {
    setIsLocating(true)
    navigator.geolocation?.getCurrentPosition(
      (pos) => {
        form.setValue("latitude", pos.coords.latitude)
        form.setValue("longitude", pos.coords.longitude)
        setIsLocating(false)
      },
      () => setIsLocating(false),
      { timeout: 8000 }
    )
  }, [form])

  async function onSubmit(values: z.infer<typeof newRequestSchema>) {
    if (!values.latitude || !values.longitude) {
      toast.error("Localização necessária para criar o pedido")
      return
    }

    setIsSubmitting(true)
    try {
      const token = localStorage.getItem("access_token")
      const formData = new FormData()
      formData.append("title", values.title)
      if (values.description) formData.append("description", values.description)
      formData.append("category_id", values.category_id)
      formData.append("urgency", values.urgency)
      formData.append("latitude", String(values.latitude))
      formData.append("longitude", String(values.longitude))
      if (values.budget_cents) formData.append("budget_cents", String(values.budget_cents))
      images.forEach((img) => formData.append("images", img))

      const response = await fetch(`${BASE_URL}/requests`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err.detail || "Erro ao criar pedido")
      }

      const data = await response.json()
      toast.success("Pedido criado!", { description: "Buscando profissionais próximos..." })
      router.push(`/requests/${data.id}/matches`)
    } catch (err: any) {
      toast.error("Erro ao criar pedido", { description: err.message })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-background pb-20 px-6 max-w-lg mx-auto">
      {/* Header */}
      <div className="pt-6 pb-2">
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="gap-2 text-muted-foreground">
          <ChevronLeft className="w-4 h-4" /> Voltar
        </Button>
      </div>

      <div className="mb-8">
        <h1 className="text-2xl font-extrabold tracking-tight">
          Novo <span className="text-primary italic">Pedido</span>
        </h1>
        <p className="text-sm text-muted-foreground mt-1">Descreva o que você precisa</p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Título */}
          <FormField control={form.control} name="title" render={({ field }) => (
            <FormItem>
              <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">
                O que você precisa?
              </FormLabel>
              <FormControl>
                <div className="neo-inset rounded-2xl px-4 py-1 bg-background">
                  <Input
                    placeholder="Ex: Torneira vazando na cozinha"
                    className="border-none shadow-none focus-visible:ring-0 bg-transparent h-12 text-base font-semibold"
                    {...field}
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )} />

          {/* Descrição */}
          <FormField control={form.control} name="description" render={({ field }) => (
            <FormItem>
              <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">
                Detalhes (opcional)
              </FormLabel>
              <FormControl>
                <div className="neo-inset rounded-2xl px-4 py-3 bg-background">
                  <Textarea
                    placeholder="Descreva melhor o problema, tamanho, urgência..."
                    className="border-none shadow-none focus-visible:ring-0 bg-transparent resize-none text-sm"
                    rows={3}
                    {...field}
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )} />

          {/* Categoria */}
          <FormField control={form.control} name="category_id" render={({ field }) => (
            <FormItem>
              <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">
                Categoria
              </FormLabel>
              <div className="neo-inset rounded-2xl px-4 py-1 bg-background">
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger className="border-none shadow-none focus:ring-0 bg-transparent h-12 font-semibold">
                      <SelectValue placeholder="Selecione uma categoria" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="bg-background neo-elevated border-none rounded-2xl">
                    {categories.map((cat: any) => (
                      <SelectItem key={cat.id} value={cat.id} className="font-medium">
                        {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <FormMessage />
            </FormItem>
          )} />

          {/* Urgência */}
          <FormField control={form.control} name="urgency" render={({ field }) => (
            <FormItem>
              <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">
                Urgência
              </FormLabel>
              <div className="grid grid-cols-1 gap-2">
                {Object.entries(urgencyLabels).map(([value, label]) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => field.onChange(value)}
                    className={`
                      w-full text-left px-4 py-3 rounded-2xl text-sm font-semibold transition-all
                      ${field.value === value
                        ? "neo-inset text-primary"
                        : "neo-elevated hover:translate-y-[-1px]"
                      }
                    `}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <FormMessage />
            </FormItem>
          )} />

          {/* Orçamento */}
          <FormField control={form.control} name="budget_cents" render={({ field }) => (
            <FormItem>
              <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">
                Orçamento máximo (opcional)
              </FormLabel>
              <FormControl>
                <div className="neo-inset rounded-2xl px-4 py-1 bg-background flex items-center gap-2">
                  <span className="text-muted-foreground font-bold text-sm">R$</span>
                  <Input
                    type="number"
                    placeholder="0,00"
                    className="border-none shadow-none focus-visible:ring-0 bg-transparent h-12 text-base font-semibold"
                    onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) * 100 : undefined)}
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )} />

          {/* Localização */}
          <div>
            <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">
              Localização
            </FormLabel>
            <div className={`mt-2 neo-inset rounded-2xl p-4 flex items-center gap-3 ${isLocating ? "text-primary" : watchedLatitude ? "text-green-600" : "text-destructive"}`}>
              {isLocating ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <MapPin className="w-5 h-5" />
              )}
              <span className="text-sm font-semibold">
                {isLocating
                  ? "Obtendo localização..."
                  : watchedLatitude
                  ? `${watchedLatitude.toFixed(4)}, ${watchedLongitude?.toFixed(4)}`
                  : "Localização não obtida"}
              </span>
            </div>
          </div>

          {/* Upload de imagens */}
          <div>
            <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">
              Fotos do problema (até 5)
            </FormLabel>
            <label className="mt-2 neo-inset rounded-2xl p-6 flex flex-col items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity block">
              <Camera className="w-8 h-8 text-muted-foreground" />
              <span className="text-sm font-semibold text-muted-foreground">
                {images.length > 0 ? `${images.length} foto(s) selecionada(s)` : "Toque para adicionar fotos"}
              </span>
              <input
                type="file"
                accept="image/jpeg,image/png"
                multiple
                className="hidden"
                onChange={(e) => {
                  const files = Array.from(e.target.files || []).slice(0, 5)
                  setImages(files)
                }}
              />
            </label>
          </div>

          {/* Submit */}
          <Button
            type="submit"
            variant="neo-elevated"
            className="w-full h-14 rounded-2xl text-primary font-bold text-lg mt-4"
            disabled={isSubmitting || isLocating || !watchedLatitude}
          >
            {isSubmitting ? <Loader2 className="animate-spin" /> : "Buscar Profissionais"}
          </Button>
        </form>
      </Form>
    </main>
  )
}
