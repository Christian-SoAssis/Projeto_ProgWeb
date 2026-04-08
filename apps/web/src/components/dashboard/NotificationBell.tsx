"use client"

import { Bell } from "lucide-react"
import { useState } from "react"

interface NotificationBellProps {
  hasNotifications?: boolean
}

export function NotificationBell({ hasNotifications = true }: NotificationBellProps) {
  const [active, setActive] = useState(false)

  return (
    <button
      onClick={() => setActive(!active)}
      className={`
        relative w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-200
        ${active 
          ? "neo-inset text-primary scale-95" 
          : "neo-elevated text-muted-foreground hover:text-primary active:scale-90"
        }
      `}
    >
      <Bell className={`w-5 h-5 ${active ? "fill-primary/20" : ""}`} />
      
      {hasNotifications && !active && (
        <span className="absolute top-3 right-3 w-2 h-2 bg-primary rounded-full ring-2 ring-background animate-pulse" />
      )}
    </button>
  )
}
