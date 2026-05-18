"use client"

import Link from "next/link"
import { 
  Droplet, 
  Zap, 
  Flame, 
  HardHat, 
  TreePine, 
  Sparkles, 
  Paintbrush, 
  Hammer, 
  Wind, 
  ShieldCheck, 
  Laptop, 
  Wrench, 
  Heart, 
  Scale, 
  GraduationCap, 
  PawPrint 
} from "lucide-react"

const CATEGORIES = [
  { name: "Hidráulica", slug: "hidraulica", icon: Droplet, color: "#2e7bc4" },
  { name: "Elétrica", slug: "eletrica", icon: Zap, color: "#d4a00a" },
  { name: "Gás", slug: "gas", icon: Flame, color: "#e06820" },
  { name: "Construção", slug: "construcao", icon: HardHat, color: "#b04020" },
  { name: "Jardinagem", slug: "jardinagem", icon: TreePine, color: "#2a8c50" },
  { name: "Limpeza", slug: "limpeza", icon: Sparkles, color: "#18a0a0" },
  { name: "Pintura", slug: "pintura", icon: Paintbrush, color: "#9050c0" },
  { name: "Marcenaria", slug: "marcenaria", icon: Hammer, color: "#8a5c28" },
  { name: "Ar-cond.", slug: "ar-condicionado", icon: Wind, color: "#4898d8" },
  { name: "Segurança", slug: "seguranca", icon: ShieldCheck, color: "#384880" },
  { name: "Tecnologia", slug: "tecnologia", icon: Laptop, color: "#20a870" },
  { name: "Reformas", slug: "reformas", icon: Wrench, color: "#c06840" },
  { name: "Saúde/Beleza", slug: "saude-beleza", icon: Heart, color: "#d04080" },
  { name: "Jurídico", slug: "juridico", icon: Scale, color: "#485870" },
  { name: "Educação", slug: "educacao", icon: GraduationCap, color: "#e08820" },
  { name: "Pets", slug: "pets", icon: PawPrint, color: "#d85020" },
]

export function CategoryPills() {
  return (
    <div className="grid grid-cols-4 gap-4 w-full">
      {CATEGORIES.map((cat) => {
        const Icon = cat.icon
        return (
          <Link
            key={cat.slug}
            href={`/search?category=${cat.slug}`}
            className="flex flex-col items-center justify-center gap-3 p-4 rounded-3xl neo-elevated bg-background hover:translate-y-[-2px] active:translate-y-[1px] transition-transform group"
          >
            <div 
              className="w-10 h-10 rounded-full flex items-center justify-center neo-inset"
            >
              <Icon 
                style={{ color: cat.color }} 
                className="w-5 h-5 opacity-90 group-hover:opacity-100 transition-opacity" 
              />
            </div>
            <span className="text-[10px] sm:text-xs font-semibold text-center font-sans tracking-tight leading-tight text-foreground/80 group-hover:text-foreground">
              {cat.name}
            </span>
          </Link>
        )
      })}
    </div>
  )
}
