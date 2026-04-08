import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen p-8 flex flex-col items-center gap-12 max-w-lg mx-auto">
      <header className="w-full flex flex-col items-center gap-6">
        <div className="w-full flex justify-between items-center px-2">
          <div className="flex flex-col">
            <h1 className="text-2xl font-extrabold tracking-tight font-sans">
              Serviço<span className="text-primary italic">Já</span>
            </h1>
            <p className="text-muted-foreground font-medium uppercase text-[8px] tracking-[0.2em] font-mono">
              Pure Neomorphism v2.0
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="ghost" size="sm" asChild className="text-xs font-semibold">
              <a href="/login">Entrar</a>
            </Button>
            <Button variant="neo-elevated" size="sm" asChild className="text-xs font-bold text-primary">
              <a href="/register">Cadastrar</a>
            </Button>
          </div>
        </div>
      </header>

      {/* Search Section - Inset */}
      <section className="w-full">
        <div className="relative group">
          <div className="neo-inset rounded-full flex items-center px-4 py-1 bg-background">
            <Search className="w-5 h-5 text-muted-foreground" />
            <Input 
              placeholder="Que serviço você precisa hoje?" 
              className="border-none shadow-none focus-visible:ring-0 bg-transparent h-12 text-base font-sans"
            />
          </div>
        </div>
      </section>

      {/* Action Cards - Elevated */}
      <section className="grid grid-cols-1 gap-6 w-full">
        <Card className="neo-elevated border-none bg-background rounded-3xl p-2 transition-transform active:scale-95 cursor-pointer">
          <CardHeader>
            <CardTitle className="text-lg font-sans">Encontrar Profissional</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Acesso rápido aos melhores prestadores da sua região com selo de verificação manual.
            </p>
          </CardContent>
        </Card>

        <Card className="neo-elevated border-none bg-background rounded-3xl p-2">
          <CardHeader>
            <CardTitle className="text-lg font-sans">Meus Pedidos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="neo-inset rounded-2xl p-4 flex justify-between items-center bg-transparent">
              <span className="text-sm font-sans font-medium">Reforma Banheiro</span>
              <span className="text-[10px] font-mono bg-primary/20 text-primary px-2 py-1 rounded-full">
                EM ANÁLISE VLM
              </span>
            </div>
            <div className="neo-inset rounded-2xl p-4 flex justify-between items-center bg-transparent">
              <span className="text-sm font-sans font-medium">Pintura Fachada</span>
              <span className="text-[10px] font-mono bg-secondary/80 text-secondary-foreground px-2 py-1 rounded-full">
                FINALIZADO
              </span>
            </div>
          </CardContent>
        </Card>
      </section>

      <footer className="w-full flex justify-center gap-4 pt-4">
        <Button className="neo-elevated rounded-2xl h-14 w-full bg-background hover:bg-background text-primary font-bold shadow-none border-none">
          Criar Novo Pedido
        </Button>
      </footer>
    </main>
  );
}
