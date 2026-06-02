"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, Calendar, Check, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { apiFetch } from "@/infrastructure/http/http-client"
import { toast } from "sonner"

interface AvailabilityDay {
  day_of_week: number
  day_name: string
  start_time: string
  end_time: string
  is_active: boolean
}

const DEFAULT_DAYS = [
  { day_of_week: 0, day_name: "Domingo", start_time: "08:00", end_time: "18:00", is_active: false },
  { day_of_week: 1, day_name: "Segunda", start_time: "08:00", end_time: "18:00", is_active: true },
  { day_of_week: 2, day_name: "Terça", start_time: "08:00", end_time: "18:00", is_active: true },
  { day_of_week: 3, day_name: "Quarta", start_time: "08:00", end_time: "18:00", is_active: true },
  { day_of_week: 4, day_name: "Quinta", start_time: "08:00", end_time: "18:00", is_active: true },
  { day_of_week: 5, day_name: "Sexta", start_time: "08:00", end_time: "18:00", is_active: true },
  { day_of_week: 6, day_name: "Sábado", start_time: "08:00", end_time: "18:00", is_active: false },
]

export default function AvailabilitySettingsPage() {
  const router = useRouter()
  const [days, setDays] = useState<AvailabilityDay[]>(DEFAULT_DAYS)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  // Load existing availability
  useEffect(() => {
    async function loadAvailability() {
      try {
        const response = await apiFetch("/auth/professional/availability")
        if (response && response.availabilities && response.availabilities.length > 0) {
          const loadedMap = new Map<number, any>()
          response.availabilities.forEach((item: any) => {
            loadedMap.set(item.day_of_week, item)
          })

          const mergedDays = DEFAULT_DAYS.map((d) => {
            const loaded = loadedMap.get(d.day_of_week)
            if (loaded) {
              // Convert "08:00:00" to "08:00"
              const start = loaded.start_time.substring(0, 5)
              const end = loaded.end_time.substring(0, 5)
              return {
                ...d,
                start_time: start,
                end_time: end,
                is_active: loaded.is_active,
              }
            }
            return d
          })
          setDays(mergedDays)
        }
      } catch (err) {
        console.error("Erro ao carregar a grade horária:", err)
      } finally {
        setFetching(false)
      }
    }
    loadAvailability()
  }, [])

  const handleToggleDay = (dayIndex: number) => {
    setDays((prev) =>
      prev.map((d, index) => (index === dayIndex ? { ...d, is_active: !d.is_active } : d))
    )
  }

  const handleTimeChange = (dayIndex: number, field: "start_time" | "end_time", value: string) => {
    setDays((prev) =>
      prev.map((d, index) => (index === dayIndex ? { ...d, [field]: value } : d))
    )
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation: make sure start time is before end time for active days
    for (const day of days) {
      if (day.is_active) {
        if (day.start_time >= day.end_time) {
          toast.error(`No dia ${day.day_name}, o horário de início deve ser antes do fim.`)
          return
        }
      }
    }

    setLoading(true)
    try {
      const payload = {
        availabilities: days.map((d) => ({
          day_of_week: d.day_of_week,
          start_time: `${d.start_time}:00`,
          end_time: `${d.end_time}:00`,
          is_active: d.is_active,
        })),
      }

      await apiFetch("/auth/professional/availability", {
        method: "POST",
        body: JSON.stringify(payload),
      })

      toast.success("Agenda de horários salva com sucesso!", {
        className: "neo-elevated rounded-2xl border-none text-foreground font-bold",
      })
    } catch (err: any) {
      toast.error(err.message || "Erro ao salvar a agenda")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex justify-center items-start sm:py-6 relative font-sans">
      <div className="w-full max-w-[480px] bg-background min-h-screen sm:min-h-[840px] sm:rounded-[2.5rem] sm:neo-elevated overflow-hidden flex flex-col relative border-none pb-12">
        
        {/* Header */}
        <header className="px-5 py-4 bg-background neo-elevated flex items-center gap-3 shrink-0">
          <button 
            onClick={() => router.push("/profile/pro")}
            className="w-10 h-10 rounded-full neo-elevated hover:bg-muted/5 flex items-center justify-center transition-all"
          >
            <ChevronLeft className="w-5 h-5 text-muted-foreground" />
          </button>
          <h2 className="text-base font-black text-foreground/90">Grade de Horários</h2>
        </header>

        {/* Content */}
        <div className="flex-1 px-5 py-6 space-y-6 overflow-y-auto">
          <section className="space-y-4">
            <h3 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/80 px-1">
              Definir Disponibilidade Semanal
            </h3>
            
            <Card className="border-none rounded-[2rem] p-5 space-y-6 neo-elevated text-left">
              <div className="flex items-center gap-3 text-primary mb-2">
                <div className="w-10 h-10 rounded-xl neo-inset flex items-center justify-center bg-background/50">
                  <Calendar className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold">Dias e Horários de Trabalho</h4>
                  <p className="text-[10px] text-muted-foreground font-medium">Os clientes só poderão reservar horários dentro desta grade.</p>
                </div>
              </div>

              {fetching ? (
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-14 bg-muted/20 animate-pulse rounded-xl" />
                  ))}
                </div>
              ) : (
                <form onSubmit={handleSave} className="space-y-6">
                  
                  {/* Days list */}
                  <div className="space-y-4">
                    {days.map((day, idx) => (
                      <div key={day.day_of_week} className="flex flex-col gap-2 p-3 rounded-2xl neo-inset bg-background/30">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-black text-foreground/90">{day.day_name}</span>
                          
                          {/* Toggle button */}
                          <button
                            type="button"
                            onClick={() => handleToggleDay(idx)}
                            className={`
                              w-12 h-6 rounded-full p-0.5 transition-all duration-300 focus:outline-none relative shrink-0
                              ${day.is_active ? "neo-inset bg-background" : "neo-inset"}
                            `}
                          >
                            <div 
                              className={`
                                w-5 h-5 rounded-full transition-all duration-300 flex items-center justify-center
                                ${day.is_active 
                                  ? "translate-x-6 bg-[#1a9878] shadow-[0_0_10px_rgba(26,152,120,.5)] text-primary-foreground" 
                                  : "translate-x-0 bg-background neo-elevated text-muted-foreground"
                                }
                              `}
                            >
                              {day.is_active && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                            </div>
                          </button>
                        </div>

                        {/* Start and end times inputs */}
                        {day.is_active && (
                          <div className="flex items-center gap-3 mt-1.5 animate-in fade-in slide-in-from-top-1 duration-200">
                            <div className="flex-1 flex items-center gap-2 px-3 h-10 rounded-xl bg-background neo-elevated">
                              <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                              <span className="text-[10px] font-bold text-muted-foreground uppercase">De:</span>
                              <input
                                type="time"
                                value={day.start_time}
                                onChange={(e) => handleTimeChange(idx, "start_time", e.target.value)}
                                className="bg-transparent border-none text-xs font-bold text-foreground focus:outline-none w-full"
                              />
                            </div>
                            <div className="flex-1 flex items-center gap-2 px-3 h-10 rounded-xl bg-background neo-elevated">
                              <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                              <span className="text-[10px] font-bold text-muted-foreground uppercase">Até:</span>
                              <input
                                type="time"
                                value={day.end_time}
                                onChange={(e) => handleTimeChange(idx, "end_time", e.target.value)}
                                className="bg-transparent border-none text-xs font-bold text-foreground focus:outline-none w-full"
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Save button */}
                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full h-14 bg-background text-primary font-black text-sm rounded-xl neo-elevated hover:bg-muted/5 transition-all border-none"
                  >
                    {loading ? "Salvando..." : "Salvar Agenda"}
                  </Button>
                </form>
              )}
            </Card>
          </section>
        </div>

      </div>
    </main>
  )
}
