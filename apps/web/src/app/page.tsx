import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchBar } from "@/components/SearchBar";
import Link from "next/link";

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
              <Link href="/login">Entrar</Link>
            </Button>
            <Button variant="neo-elevated" size="sm" asChild className="text-xs font-bold text-primary">
              <Link href="/register">Cadastrar</Link>
            </Button>
          </div>
        </div>
      </header>

      <section className="w-full">
        <SearchBar />
      </section>

      <section className="grid grid-cols-1 gap-6 w-full">
        <Link href="/search">
          <Card className="neo-elevated border-none bg-background rounded-3xl p-2 transition-transform active:scale-95 cursor-pointer hover:translate-y-[-2px]">
            <CardHeader>
              <CardTitle className="text-lg font-sans">Encontrar Profissional</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Acesso rápido aos melhores prestadores da sua região com selo de verificação manual.
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/dashboard/client">
          <Card className="neo-elevated border-none bg-background rounded-3xl p-2 hover:translate-y-[-2px] transition-transform cursor-pointer">
            <CardHeader>
              <CardTitle className="text-lg font-sans">Meus Pedidos</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Acompanhe o status dos seus pedidos e veja os lances recebidos.
              </p>
            </CardContent>
          </Card>
        </Link>
      </section>

      <footer className="w-full flex justify-center gap-4 pt-4">
        <Button asChild className="neo-elevated rounded-2xl h-14 w-full bg-background hover:bg-background text-primary font-bold shadow-none border-none">
          <Link href="/requests/new">
            Criar Novo Pedido
          </Link>
        </Button>
      </footer>
    </main>
  );
}
