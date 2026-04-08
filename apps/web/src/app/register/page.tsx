"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { ChevronLeft, User, Briefcase, MapPin, Loader2 } from "lucide-react"
import { useAuth } from "@/context/auth-context"
import { useState, useEffect } from "react"

const registerSchema = z.object({
  name: z.string().min(2, { message: "Nome deve ter no mínimo 2 caracteres." }),
  email: z.string().email({ message: "E-mail inválido." }),
  phone: z.string().regex(/^\+55\d{10,11}$/, { message: "Formato: +5511999998888" }),
  password: z.string().min(8, { message: "Senha deve ter no mínimo 8 caracteres." }),
  role: z.enum(["client", "professional"]),
  consent_terms: z.boolean().refine(val => val === true, { message: "Aceite os termos." }),
  consent_privacy: z.boolean().refine(val => val === true, { message: "Aceite a política." }),
  // Campos extras para Profissional
  bio: z.string().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
})

export default function RegisterPage() {
  const { registerClient, registerPro } = useAuth()
  const [isLocating, setIsLocating] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "+55",
      password: "",
      role: "client",
      consent_terms: false,
      consent_privacy: false,
      bio: "",
    },
  })

  // Capturar geolocalização se for profissional
  const role = form.watch("role")
  useEffect(() => {
    if (role === "professional" && !form.getValues("latitude")) {
      setIsLocating(true)
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          form.setValue("latitude", pos.coords.latitude)
          form.setValue("longitude", pos.coords.longitude)
          setIsLocating(false)
          toast.success("Localização capturada!")
        },
        (err) => {
          console.error(err)
          setIsLocating(false)
          toast.error("Não foi possível obter sua localização.")
        }
      )
    }
  }, [role, form])

  async function onSubmit(values: z.infer<typeof registerSchema>) {
    setIsSubmitting(true)
    try {
      if (values.role === "client") {
        await registerClient({
          name: values.name,
          email: values.email,
          phone: values.phone,
          password: values.password,
          consent_terms: values.consent_terms,
          consent_privacy: values.consent_privacy,
        })
        toast.success("Cadastro realizado com sucesso!")
      } else {
        // Preparar FormData para Profissional (Multipart)
        const formData = new FormData()
        formData.append("name", values.name)
        formData.append("email", values.email)
        formData.append("phone", values.phone || "")
        formData.append("password", values.password)
        formData.append("consent_terms", String(values.consent_terms))
        formData.append("consent_privacy", String(values.consent_privacy))
        formData.append("bio", values.bio || "Profissional qualificado em busca de oportunidades.")
        formData.append("latitude", String(values.latitude || 0))
        formData.append("longitude", String(values.longitude || 0))
        formData.append("service_radius_km", "15")
        formData.append("hourly_rate_cents", "5000") // Mock: R$ 50,00
        formData.append("category_ids_json", JSON.stringify([])) // Mock: Nenhuma categoria inicial
        formData.append("document_type", "cpf")
        
        // Criar arquivo Dummy conforme solicitado pelo usuário
        const dummyFile = new File(["dummy-content"], "documento.pdf", { type: "application/pdf" })
        formData.append("document", dummyFile)

        await registerPro(formData)
        toast.success("Cadastro realizado! Faça login para continuar.")
      }
    } catch (error: any) {
      toast.error("Erro ao cadastrar", { description: error.message })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen p-6 bg-background flex flex-col items-center justify-center gap-8 max-w-lg mx-auto">
      <div className="w-full">
        <Button variant="ghost" size="sm" asChild className="gap-2 text-muted-foreground hover:text-foreground">
          <a href="/">
            <ChevronLeft className="w-4 h-4" />
            Voltar
          </a>
        </Button>
      </div>

      <Card variant="neo-elevated" className="w-full border-none rounded-[2.5rem] p-3 pt-0">
        <CardHeader className="text-center space-y-2 pb-2">
          <CardTitle className="text-3xl font-extrabold tracking-tight">Criar Conta</CardTitle>
          <CardDescription className="text-xs font-medium uppercase tracking-widest text-muted-foreground/60 font-mono">
            Junte-se à plataforma
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <Tabs 
            defaultValue="client" 
            onValueChange={(val) => form.setValue("role", val as "client" | "professional")}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2 neo-inset bg-transparent h-14 p-1 rounded-2xl border-none">
              <TabsTrigger 
                value="client" 
                className="rounded-xl flex gap-2 data-[state=active]:neo-elevated data-[state=active]:bg-background data-[state=active]:text-primary transition-all duration-300"
              >
                <User className="w-4 h-4" />
                Sou Cliente
              </TabsTrigger>
              <TabsTrigger 
                value="professional" 
                className="rounded-xl flex gap-2 data-[state=active]:neo-elevated data-[state=active]:bg-background data-[state=active]:text-primary transition-all duration-300"
              >
                <Briefcase className="w-4 h-4" />
                Profissional
              </TabsTrigger>
            </TabsList>
          </Tabs>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 gap-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">Nome Completo</FormLabel>
                      <FormControl>
                        <Input placeholder="Seu nome" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">E-mail</FormLabel>
                      <FormControl>
                        <Input placeholder="seu@email.com" type="email" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">Telefone (+55...)</FormLabel>
                      <FormControl>
                        <Input placeholder="+5511988887777" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {role === "professional" && (
                  <>
                    <FormField
                      control={form.control}
                      name="bio"
                      render={({ field }) => (
                        <FormItem className="animate-in fade-in slide-in-from-top-1 duration-300">
                          <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">Sobre Você (Bio)</FormLabel>
                          <FormControl>
                            <Textarea placeholder="Descreva suas habilidades..." className="neo-inset bg-transparent border-none min-h-[100px]" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <div className="neo-inset rounded-2xl p-4 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MapPin className={`w-4 h-4 ${form.watch("latitude") ? "text-primary" : "text-muted-foreground"}`} />
                        <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Localização</span>
                      </div>
                      <span className="text-[10px] font-mono font-bold">
                        {isLocating ? <Loader2 className="w-3 h-3 animate-spin"/> : form.watch("latitude") ? "Capturada" : "Pendente"}
                      </span>
                    </div>
                  </>
                )}

                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">Senha (mín 8 chars)</FormLabel>
                      <FormControl>
                        <Input placeholder="••••••••" type="password" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="space-y-3 pt-2">
                <FormField
                  control={form.control}
                  name="consent_terms"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md p-2">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel className="text-[10px] font-medium leading-none cursor-pointer">
                          Aceito os Termos de Uso do ServiçoJá
                        </FormLabel>
                      </div>
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="consent_privacy"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md p-2">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel className="text-[10px] font-medium leading-none cursor-pointer">
                          Aceito a Política de Privacidade (LGPD)
                        </FormLabel>
                      </div>
                    </FormItem>
                  )}
                />
              </div>

              <Button 
                type="submit" 
                variant="neo-elevated" 
                className="w-full h-14 rounded-2xl text-primary font-bold text-lg mt-4 animate-in fade-in zoom-in duration-300"
                disabled={isSubmitting || (role === "professional" && !form.watch("latitude"))}
              >
                {isSubmitting ? <Loader2 className="animate-spin" /> : "Criar Conta"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      <p className="text-sm text-center text-muted-foreground font-medium">
        Já tem uma conta?{" "}
        <a href="/login" className="text-primary font-bold hover:underline">
          Fazer Login
        </a>
      </p>
    </main>
  )
}
