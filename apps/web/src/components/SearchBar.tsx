"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"

export function SearchBar() {
    const router = useRouter()
    const [q, setQ] = useState("")

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault()
        const trimmed = q.trim()
        if (trimmed) {
            router.push(`/search?q=${encodeURIComponent(trimmed)}`)
        } else {
            router.push("/search")
        }
    }

    return (
        <form onSubmit={handleSubmit} className="w-full">
            <button type="submit" className="w-full text-left">
                <div className="relative group neo-inset rounded-full flex items-center px-6 py-2 bg-background cursor-text">
                    <Search className="w-6 h-6 text-muted-foreground shrink-0 mr-2" />
                    <Input
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        placeholder="O que você precisa hoje?"
                        className="border-none shadow-none focus-visible:ring-0 bg-transparent h-14 text-lg font-sans placeholder:text-muted-foreground/70"
                    />
                </div>
            </button>
        </form>
    )
}
