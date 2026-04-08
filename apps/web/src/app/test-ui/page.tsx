"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username deve ter pelo menos 2 caracteres.",
  }),
})

export default function TestUIPage() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    toast.success("Formulário enviado!", {
      description: JSON.stringify(values),
    })
  }

  return (
    <div className="p-8 space-y-12 max-w-2xl mx-auto bg-background min-h-screen">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Showcase Neomorfismo & Form</h1>
        <p className="text-muted-foreground">Teste de variantes e setup do shadcn/ui</p>
      </header>

      {/* Seção de Botões */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Botões Neomórficos</h2>
        <div className="flex flex-wrap gap-4">
          <Button variant="neo-elevated">Elevado (Neo)</Button>
          <Button variant="neo-inset">Afundado (Neo)</Button>
          <Button variant="default">Padrão Shadcn</Button>
          <Button variant="outline">Outline</Button>
        </div>
      </section>

      {/* Seção de Cards */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Cards Neomórficos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card variant="neo-elevated">
            <CardHeader>
              <CardTitle>Elevated Card</CardTitle>
              <CardDescription>Sombra externa neomórfica.</CardDescription>
            </CardHeader>
            <CardContent>
              Conteúdo do card elevado.
            </CardContent>
          </Card>

          <Card variant="neo-inset">
            <CardHeader>
              <CardTitle>Inset Card</CardTitle>
              <CardDescription>Sombra interna neomórfica.</CardDescription>
            </CardHeader>
            <CardContent>
              Conteúdo do card afundado.
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Seção de Formulário */}
      <section className="space-y-4 p-8 neo-elevated rounded-3xl bg-background">
        <h2 className="text-xl font-semibold">Teste de Formulário (Hook Form + Zod)</h2>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome de Usuário</FormLabel>
                  <FormControl>
                    <div className="neo-inset rounded-lg px-1 bg-transparent">
                       <Input placeholder="Digite seu nome..." className="border-none shadow-none focus-visible:ring-0" {...field} />
                    </div>
                  </FormControl>
                  <FormDescription>Seu nome público.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" variant="neo-elevated" className="w-full">
              Enviar e Testar Toast
            </Button>
          </form>
        </Form>
      </section>
    </div>
  )
}
