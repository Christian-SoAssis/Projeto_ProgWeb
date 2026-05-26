"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronLeft, MapPin, Loader2, Camera } from "lucide-react"
import { useState } from "react"
import { useAuth } from "@/presentation/hooks/use-auth"
import { useCategories } from "@/hooks/useCategories"
import { useGeolocation } from "@/hooks/useGeolocation"
import { useCreateRequest } from "@/hooks/useCreateRequest"

const newRequestSchema = z.object({
  title: z.string().min(5, "Título deve ter no mínimo 5 caracteres.").max(200),
  description: z.string().max(2000).optional(),
  category_id: z.string().uuid("Selecione uma categoria."),
  urgency: z.enum(["immediate", "scheduled", "flexible"]),
  budget_cents: z.coerce.number().int().positive().optional(),
})

const URGENCY_LABELS: Record<string, string> = {
  immediate: "Urgente — Preciso hoje",
  scheduled: "Agendado — Nos próximos dias",
  flexible: "Flexível — Sem pressa",
}

export default function NewRequestPage() {
  const router = useRouter()
  const { isAuthenticated, loading } = useAuth()
  const { categories } = useCategories()
  const { latitude, longitude, isLocating, error: locationError } = useGeolocation()
  const { createRequest, isSubmitting } = useCreateRequest()
  const [step, setStep] = useState(1)
  const [images, setImages] = useState<File[]>([])

  const form = useForm<z.infer<typeof newRequestSchema>>({
    resolver: zodResolver(newRequestSchema),
    defaultValues: { title: "", description: "", urgency: "flexible" },
  })

  useEffect(() => {
    if (!loading && !isAuthenticated) router.push("/login")
  }, [loading, isAuthenticated, router])

  async function onSubmit(values: z.infer<typeof newRequestSchema>) {
    if (!latitude || !longitude) return
    await createRequest({ ...values, latitude, longitude, images })
  }

  const nextStep = async (fieldsToValidate: (keyof z.infer<typeof newRequestSchema>)[]) => {
    const isStepValid = await form.trigger(fieldsToValidate)
    if (isStepValid) setStep((s) => s + 1)
  }

  return (
    <main className="min-h-screen bg-background pb-20 px-6 max-w-lg mx-auto flex flex-col">
      <div className="pt-6 pb-2">
        <Button variant="ghost" size="sm" onClick={() => step > 1 ? setStep(step - 1) : router.back()} className="gap-2 text-muted-foreground">
          <ChevronLeft className="w-4 h-4" /> Voltar
        </Button>
      </div>

      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black tracking-tight">
            Novo <span className="text-primary italic">Pedido</span>
          </h1>
          <p className="text-sm font-medium text-muted-foreground mt-1">Passo {step} de 3</p>
        </div>
        {/* Step Indicators */}
        <div className="flex gap-1.5 pb-1">
            {[1, 2, 3].map(i => (
                <div key={i} className={`h-1.5 rounded-full transition-all ${step >= i ? 'w-6 bg-primary' : 'w-2 bg-muted/50'}`} />
            ))}
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 flex-1 flex flex-col">
          
          {/* STEP 1: AI Prompt */}
          <div className={`space-y-6 flex-1 transition-all duration-300 ${step === 1 ? 'block opacity-100' : 'hidden opacity-0'}`}>
            <div className="neo-inset rounded-3xl p-6 bg-primary/5 text-center mb-6">
                <div className="w-12 h-12 neo-elevated bg-background rounded-full flex items-center justify-center mx-auto mb-4 text-primary">
                    ✨
                </div>
                <h3 className="font-bold text-lg">Me conte o que precisa</h3>
                <p className="text-xs text-muted-foreground mt-1">Nossa IA ajuda a categorizar o problema para encontrar os melhores profissionais.</p>
            </div>

            <FormField control={form.control} name="title" render={({ field }) => (
              <FormItem>
                <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">Resumo (Título)</FormLabel>
                <FormControl>
                  <div className="neo-inset rounded-2xl px-4 py-1 bg-background focus-within:ring-2 ring-primary/20 transition-all">
                    <Input placeholder="Ex: Torneira vazando na cozinha" className="border-none shadow-none focus-visible:ring-0 bg-transparent h-14 text-base font-bold" {...field} />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )} />

            <FormField control={form.control} name="description" render={({ field }) => (
              <FormItem>
                <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">Detalhes (opcional)</FormLabel>
                <FormControl>
                  <div className="neo-inset rounded-2xl px-4 py-3 bg-background focus-within:ring-2 ring-primary/20 transition-all">
                    <Textarea placeholder="Descreva melhor o problema..." className="border-none shadow-none focus-visible:ring-0 bg-transparent resize-none text-sm" rows={4} {...field} />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )} />

            <Button type="button" variant="neo-elevated" onClick={() => nextStep(['title', 'description'])} className="w-full h-14 rounded-2xl text-primary font-bold text-lg mt-8">
              Avançar <ChevronLeft className="w-5 h-5 rotate-180 ml-2" />
            </Button>
          </div>

          {/* STEP 2: Category & Budget */}
          <div className={`space-y-6 flex-1 transition-all duration-300 ${step === 2 ? 'block opacity-100' : 'hidden opacity-0'}`}>
            <FormField control={form.control} name="category_id" render={({ field }) => (
              <FormItem>
                <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">Categoria do Serviço</FormLabel>
                <div className="neo-inset rounded-2xl px-4 py-1 bg-background">
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger className="border-none shadow-none focus:ring-0 bg-transparent h-14 font-bold text-base">
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="bg-background neo-elevated border-none rounded-2xl">
                      {categories.map((cat) => (
                        <SelectItem key={cat.id} value={cat.id} className="font-medium py-3">{cat.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <FormMessage />
              </FormItem>
            )} />

            <FormField control={form.control} name="budget_cents" render={({ field }) => (
              <FormItem>
                <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">Orçamento máximo (opcional)</FormLabel>
                <FormControl>
                  <div className="neo-inset rounded-2xl px-4 py-1 bg-background flex items-center gap-2">
                    <span className="text-muted-foreground font-black text-lg pl-2">R$</span>
                    <Input type="number" placeholder="0,00" className="border-none shadow-none focus-visible:ring-0 bg-transparent h-14 text-xl font-bold"
                      onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) * 100 : undefined)} />
                  </div>
                </FormControl>
                <p className="text-[10px] text-muted-foreground ml-2">Deixe em branco para receber orçamentos livres.</p>
                <FormMessage />
              </FormItem>
            )} />

            <Button type="button" variant="neo-elevated" onClick={() => nextStep(['category_id', 'budget_cents'])} className="w-full h-14 rounded-2xl text-primary font-bold text-lg mt-8">
              Avançar <ChevronLeft className="w-5 h-5 rotate-180 ml-2" />
            </Button>
          </div>

          {/* STEP 3: Urgency, Photos & Location */}
          <div className={`space-y-6 flex-1 transition-all duration-300 ${step === 3 ? 'block opacity-100' : 'hidden opacity-0'}`}>
            <FormField control={form.control} name="urgency" render={({ field }) => (
              <FormItem>
                <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">Urgência</FormLabel>
                <div className="grid grid-cols-1 gap-3">
                  {Object.entries(URGENCY_LABELS).map(([value, label]) => (
                    <button key={value} type="button" onClick={() => field.onChange(value)}
                      className={`w-full text-left px-5 py-4 rounded-2xl text-sm font-bold transition-all ${field.value === value ? "neo-inset text-primary ring-2 ring-primary/20" : "neo-elevated hover:translate-y-[-2px] text-muted-foreground"}`}>
                      {label}
                    </button>
                  ))}
                </div>
                <FormMessage />
              </FormItem>
            )} />

            <div>
              <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">Localização (Obrigatório)</FormLabel>
              <div className={`mt-2 neo-inset rounded-2xl p-5 flex items-center gap-4 ${isLocating ? "text-primary" : latitude ? "text-green-600" : "text-destructive"}`}>
                {isLocating ? <Loader2 className="w-6 h-6 animate-spin" /> : <MapPin className="w-6 h-6" />}
                <div>
                    <p className="text-sm font-bold">
                        {isLocating ? "Buscando localização..." : latitude ? "Localização confirmada" : "Erro ao buscar GPS"}
                    </p>
                    {latitude && <p className="text-[10px] opacity-70 mt-0.5">O profissional verá apenas uma estimativa.</p>}
                </div>
              </div>
            </div>

            <div>
              <FormLabel className="ml-1 text-xs font-bold uppercase tracking-wider opacity-70">Fotos do problema (até 5)</FormLabel>
              <label className="mt-2 neo-inset rounded-2xl p-6 flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-black/5 transition-colors block border-2 border-dashed border-muted">
                <Camera className="w-8 h-8 text-muted-foreground/50" />
                <span className="text-sm font-bold text-muted-foreground">
                  {images.length > 0 ? `${images.length} foto(s) selecionada(s)` : "Toque para adicionar fotos"}
                </span>
                <input type="file" accept="image/jpeg,image/png" multiple className="hidden"
                  onChange={(e) => setImages(Array.from(e.target.files || []).slice(0, 5))} />
              </label>
            </div>

            <Button type="submit" variant="neo-elevated" className="w-full h-14 rounded-2xl bg-primary text-primary-foreground shadow-xl font-black text-lg mt-8"
              disabled={isSubmitting || isLocating || !latitude}>
              {isSubmitting ? <Loader2 className="animate-spin w-6 h-6 mx-auto" /> : "Publicar Pedido"}
            </Button>
          </div>
        </form>
      </Form>
    </main>
  )
}
