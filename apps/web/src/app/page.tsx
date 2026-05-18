import { Button } from "@/components/ui/button";
import { SearchBar } from "@/components/SearchBar";
import { CategoryPills } from "@/components/CategoryPills";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen p-6 md:p-8 flex flex-col items-center gap-10 max-w-2xl mx-auto">
      {/* Header / Nav */}
      <header className="w-full flex justify-between items-center px-2 pt-2">
        <div className="flex flex-col">
          <h1 className="text-xl md:text-2xl font-extrabold tracking-tight font-sans">
            Serviço<span className="text-primary italic">Já</span>
          </h1>
        </div>
        <div className="flex gap-4 items-center">
          <Link href="/dashboard/client" className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors">
            Meus Pedidos
          </Link>
          <Button variant="neo-elevated" size="sm" asChild className="text-xs font-bold text-primary rounded-xl">
            <Link href="/login">Entrar</Link>
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="w-full flex flex-col items-center text-center mt-6 md:mt-12 gap-6 px-2">
        <div className="space-y-4">
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight font-sans leading-tight text-foreground">
            Encontre os melhores <br/>
            <span className="text-primary">profissionais</span> perto de você.
          </h2>
          <p className="text-base md:text-lg text-muted-foreground font-medium max-w-md mx-auto">
            Da hidráulica à tecnologia, conectamos você aos especialistas mais bem avaliados da sua região.
          </p>
        </div>

        {/* Busca Afundada */}
        <div className="w-full max-w-lg mt-4">
          <SearchBar />
        </div>
      </section>

      {/* Categorias Neomórficas */}
      <section className="w-full flex flex-col gap-6 mt-4">
        <div className="flex items-center justify-between px-2">
          <h3 className="text-lg font-bold font-sans text-foreground">Explorar Categorias</h3>
        </div>
        <CategoryPills />
      </section>

      {/* Footer / CTA */}
      <footer className="w-full flex flex-col items-center gap-6 pt-12 pb-8">
        <Button asChild className="neo-elevated rounded-3xl h-16 w-full max-w-md bg-background hover:bg-background text-primary font-bold shadow-none border-none group">
          <Link href="/requests/new" className="flex items-center justify-center gap-2 text-lg">
            Criar Novo Pedido
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </Button>
        <p className="text-xs text-muted-foreground font-mono tracking-widest uppercase">
          ServiçoJá © 2024
        </p>
      </footer>
    </main>
  );
}
