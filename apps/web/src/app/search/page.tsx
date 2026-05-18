"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import {
    ChevronLeft,
    Search,
    MapPin,
    Star,
    DollarSign,
    SlidersHorizontal,
    CheckCircle,
    LocateFixed,
    Map as MapIcon,
    List as ListIcon
} from "lucide-react"
import { useGeolocation } from "@/hooks/useGeolocation"
import { useSearchProfessionals } from "@/hooks/useSearchProfessionals"
import { useCategories } from "@/hooks/useCategories"
import { formatCurrency } from "@/lib/formatters"

const RADIUS_OPTIONS = [5, 10, 20, 50, 100]

function SearchContent() {
    const router = useRouter()
    const searchParams = useSearchParams()

    const initialQ = searchParams.get("q") ?? ""
    const initialCategory = searchParams.get("categoryId") ?? ""

    const [q, setQ] = useState(initialQ)
    const [activeQ, setActiveQ] = useState(initialQ)
    const [categoryId, setCategoryId] = useState(initialCategory)
    const [radiusKm, setRadiusKm] = useState(20)
    const [showFilters, setShowFilters] = useState(false)
    const [viewMode, setViewMode] = useState<"list" | "map">("list")

    const { latitude, longitude, isLocating, error: geoError } = useGeolocation()
    const { categories } = useCategories()
    const { results, loading, error } = useSearchProfessionals({
        lat: latitude,
        lng: longitude,
        q: activeQ || undefined,
        categoryId: categoryId || undefined,
        radiusKm,
    })

    function handleSearch(e: React.FormEvent) {
        e.preventDefault()
        setActiveQ(q)
    }

    return (
        <main className="min-h-screen bg-background flex flex-col md:flex-row h-screen overflow-hidden relative">
            {/* Seção da Lista (Esquerda no Desktop, Ocupa tudo no Mobile caso viewMode=list) */}
            <div className={`flex-1 overflow-y-auto pb-24 px-6 pt-6 transition-all ${viewMode === "map" ? "hidden md:block" : "block"}`}>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => router.back()}
                    className="gap-2 text-muted-foreground mb-4"
                >
                    <ChevronLeft className="w-4 h-4" /> Voltar
                </Button>

                <form onSubmit={handleSearch} className="flex gap-2">
                    <div className="flex-1 neo-inset rounded-full flex items-center px-4 py-1 bg-background">
                        <Search className="w-4 h-4 text-muted-foreground shrink-0" />
                        <Input
                            value={q}
                            onChange={(e) => setQ(e.target.value)}
                            placeholder="Que serviço você precisa?"
                            className="border-none shadow-none focus-visible:ring-0 bg-transparent h-10 text-sm"
                        />
                    </div>
                    <Button
                        type="submit"
                        variant="neo-elevated"
                        size="sm"
                        className="h-10 px-4 rounded-full font-bold text-primary text-xs"
                    >
                        Buscar
                    </Button>
                    <Button
                        type="button"
                        variant="neo-elevated"
                        size="sm"
                        className="h-10 w-10 rounded-full p-0"
                        onClick={() => setShowFilters((v) => !v)}
                    >
                        <SlidersHorizontal className="w-4 h-4 text-muted-foreground" />
                    </Button>
                </form>
            </div>

            {showFilters && (
                <Card variant="neo-elevated" className="border-none rounded-[2rem] p-4 mb-4 space-y-4">
                    <div className="space-y-2">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                            Categoria
                        </p>
                        <div className="flex flex-wrap gap-2">
                            <button
                                type="button"
                                onClick={() => setCategoryId("")}
                                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                                    !categoryId
                                        ? "bg-primary text-primary-foreground"
                                        : "neo-inset text-muted-foreground"
                                }`}
                            >
                                Todas
                            </button>
                            {categories.map((cat) => (
                                <button
                                    key={cat.id}
                                    type="button"
                                    onClick={() => setCategoryId(cat.id)}
                                    className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                                        categoryId === cat.id
                                            ? "bg-primary text-primary-foreground"
                                            : "neo-inset text-muted-foreground"
                                    }`}
                                >
                                    {cat.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                            Raio de busca
                        </p>
                        <div className="flex gap-2 flex-wrap">
                            {RADIUS_OPTIONS.map((r) => (
                                <button
                                    key={r}
                                    type="button"
                                    onClick={() => setRadiusKm(r)}
                                    className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                                        radiusKm === r
                                            ? "bg-primary text-primary-foreground"
                                            : "neo-inset text-muted-foreground"
                                    }`}
                                >
                                    {r} km
                                </button>
                            ))}
                        </div>
                    </div>
                </Card>
            )}

            {isLocating && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4 px-1">
                    <LocateFixed className="w-4 h-4 text-primary animate-pulse" />
                    Obtendo sua localização…
                </div>
            )}

            {geoError && (
                <Card variant="neo-elevated" className="border-none rounded-[2rem] p-4 mb-4 text-sm text-destructive">
                    {geoError} — Habilite a geolocalização para ver profissionais próximos.
                </Card>
            )}

            {!isLocating && latitude && (
                <div className="flex items-center justify-between px-1 mb-4">
                    <p className="text-xs text-muted-foreground font-medium">
                        {loading
                            ? "Buscando profissionais…"
                            : `${results.length} profissional${results.length !== 1 ? "is" : ""} encontrado${results.length !== 1 ? "s" : ""}`}
                    </p>
                </div>
            )}

            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <Card key={i} variant="neo-elevated" className="border-none rounded-[2rem] p-4">
                            <div className="flex gap-4 items-center">
                                <Skeleton className="w-14 h-14 rounded-2xl" />
                                <div className="flex-1 space-y-2">
                                    <Skeleton className="h-4 w-32" />
                                    <Skeleton className="h-3 w-24" />
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            ) : error ? (
                <Card variant="neo-elevated" className="border-none rounded-[2rem] p-6 text-center text-sm text-destructive">
                    {error}
                </Card>
            ) : results.length === 0 && latitude ? (
                <Card variant="neo-elevated" className="border-none rounded-[2rem] p-8 text-center flex flex-col items-center gap-3">
                    <Search className="w-8 h-8 text-muted-foreground" />
                    <div>
                        <h3 className="font-bold">Nenhum resultado</h3>
                        <p className="text-sm text-muted-foreground mt-1">
                            Tente ampliar o raio ou usar outros termos.
                        </p>
                    </div>
                </Card>
            ) : (
                <div className="space-y-4">
                    {results.map((prof) => (
                        <Card
                            key={prof.id}
                            variant="neo-elevated"
                            className="border-none rounded-[2rem] p-4 hover:translate-y-[-2px] transition-transform cursor-pointer group"
                            onClick={() => router.push(`/professionals/${prof.id}`)}
                        >
                            <div className="flex gap-4 items-start">
                                <div className="w-14 h-14 neo-inset rounded-2xl flex items-center justify-center text-2xl bg-background/50 shrink-0">
                                    🔧
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-start gap-2">
                                        <h4 className="font-bold text-base truncate group-hover:text-primary transition-colors">
                                            {prof.bio?.slice(0, 50) || "Profissional"}
                                        </h4>
                                        <div className="flex items-center gap-1 shrink-0 text-primary">
                                            <Star className="w-3 h-3 fill-primary" />
                                            <span className="text-xs font-black font-mono">
                                                {prof.reputation_score?.toFixed(1)}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="flex items-center flex-wrap gap-3 mt-2 text-xs font-medium text-muted-foreground">
                                        {prof.distance_km != null && (
                                            <div className="flex items-center gap-1">
                                                <MapPin className="w-3 h-3 text-primary" />
                                                {prof.distance_km.toFixed(1)} km
                                            </div>
                                        )}
                                        {prof.hourly_rate_cents && (
                                            <div className="flex items-center gap-1">
                                                <DollarSign className="w-3 h-3 text-primary" />
                                                {formatCurrency(prof.hourly_rate_cents)}/h
                                            </div>
                                        )}
                                        {prof.is_verified && (
                                            <div className="flex items-center gap-1 text-green-600">
                                                <CheckCircle className="w-3 h-3" />
                                                Verificado
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
            </div>

            {/* Seção do Mapa (Direita no Desktop, Ocupa tudo no Mobile caso viewMode=map) */}
            <div className={`w-full md:w-1/2 bg-background relative neo-inset md:m-6 md:rounded-[2rem] overflow-hidden ${viewMode === "list" ? "hidden md:block" : "block fixed inset-0 z-40 md:static md:z-auto"}`}>
                {viewMode === "map" && (
                    <Button
                        variant="neo-elevated"
                        size="icon"
                        onClick={() => setViewMode("list")}
                        className="absolute top-6 left-6 z-50 md:hidden w-10 h-10 rounded-full bg-background"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </Button>
                )}
                
                {/* Mock do Mapa */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/5 via-background to-muted/20 flex flex-col items-center justify-center p-6 text-center">
                    <div className="w-24 h-24 neo-elevated rounded-full flex items-center justify-center mb-6 text-primary">
                        <MapPin className="w-10 h-10" />
                    </div>
                    <h3 className="text-lg font-black text-foreground">Visualização do Mapa</h3>
                    <p className="text-sm text-muted-foreground mt-2 max-w-xs">
                        {loading 
                            ? "Carregando profissionais no mapa..." 
                            : `${results.length} profissionais encontrados nesta região.`}
                    </p>
                    
                    {/* Mock Markers */}
                    {!loading && results.length > 0 && (
                        <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-50">
                            {results.map((r, i) => (
                                <div 
                                    key={r.id} 
                                    className="absolute w-4 h-4 bg-primary rounded-full shadow-[0_0_15px_rgba(var(--primary),0.5)] animate-pulse"
                                    style={{
                                        top: `${20 + (i * 15 % 60)}%`,
                                        left: `${20 + (i * 25 % 60)}%`
                                    }}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Floating Toggle Button (Mobile Only) */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 md:hidden">
                <Button
                    variant="neo-elevated"
                    className="h-14 rounded-full px-8 bg-background font-bold flex items-center gap-2 shadow-2xl"
                    onClick={() => setViewMode(viewMode === "list" ? "map" : "list")}
                >
                    {viewMode === "list" ? (
                        <>
                            <MapIcon className="w-4 h-4 text-primary" />
                            <span>Ver Mapa</span>
                        </>
                    ) : (
                        <>
                            <ListIcon className="w-4 h-4 text-primary" />
                            <span>Ver Lista</span>
                        </>
                    )}
                </Button>
            </div>
        </main>
    )
}

export default function SearchPage() {
    return (
        <Suspense>
            <SearchContent />
        </Suspense>
    )
}
