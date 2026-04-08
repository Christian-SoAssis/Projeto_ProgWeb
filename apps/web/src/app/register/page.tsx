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
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "sonner"
import { ChevronLeft, User, Briefcase } from "lucide-react"

const registerSchema = z.object({
  name: z.string().min(2, { message: "Nome deve ter no mínimo 2 caracteres." }),
  email: z.string().email({ message: "E-mail inválido." }),
  phone: z.string().min(10, { message: "Telefone inválido." }),
  cpf: z.string().optional().refine((val) => !val || val.length === 14, {
    message: "CPF deve ter 11 dígitos.",
  }),
  password: z.string().min(6, { message: "Senha deve ter no mínimo 6 caracteres." }),
  role: z.enum(["client", "professional"]),
})

export default function RegisterPage() {
  const form = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      cpf: "",
      password: "",
      role: "client",
    },
  })

  function onSubmit(values: z.infer<typeof registerSchema>) {
    toast.success("Conta criada!", {
      description: `Bem-vindo, ${values.name} (${values.role === "client" ? "Cliente" : "Profissional"})`,
    })
    console.log(values)
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

      <Card variant="neo-elevated" className="w-full border-none rounded-[2.5rem] p-4">
        <CardHeader className="text-center space-y-2 pb-2">
          <CardTitle className="text-3xl font-extrabold tracking-tight">Criar Conta</CardTitle>
          <CardDescription className="text-sm font-medium uppercase tracking-widest text-muted-foreground/60 font-mono">
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
                    <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">Telefone</FormLabel>
                    <FormControl>
                      <Input placeholder="(11) 98888-7777" mask="phone" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              {form.watch("role") === "professional" && (
                <FormField
                  control={form.control}
                  name="cpf"
                  render={({ field }) => (
                    <FormItem className="animate-in fade-in slide-in-from-top-1 duration-300">
                      <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">CPF</FormLabel>
                      <FormControl>
                        <Input placeholder="000.000.000-00" mask="cpf" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="ml-1 text-[10px] font-bold uppercase tracking-wider opacity-60">Senha</FormLabel>
                    <FormControl>
                      <Input placeholder="••••••••" type="password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" variant="neo-elevated" className="w-full h-14 rounded-2xl text-primary font-bold text-lg mt-4 animate-in fade-in zoom-in duration-300">
                Criar Conta
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
