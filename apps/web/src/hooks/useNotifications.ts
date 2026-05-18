"use client"

import { useState, useEffect, useCallback } from "react"
import { apiFetch } from "@/lib/api"
import { Notification } from "@/domain/models/notification"

function mapNotification(data: any): Notification {
    return {
        id: data.id,
        type: data.type,
        payload: data.payload ?? {},
        readAt: data.read_at,
        createdAt: data.created_at,
    }
}

export function useNotifications() {
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [loading, setLoading] = useState(true)

    const reload = useCallback(() => {
        apiFetch("/notifications")
            .then((data: any[]) => setNotifications(data.map(mapNotification)))
            .catch(() => {})
            .finally(() => setLoading(false))
    }, [])

    useEffect(() => {
        reload()
    }, [reload])

    const unreadCount = notifications.filter((n) => n.readAt === null).length

    async function markRead(ids: string[]) {
        if (ids.length === 0) return
        try {
            const updated: any[] = await apiFetch("/notifications/mark-read", {
                method: "PATCH",
                body: JSON.stringify({ notification_ids: ids }),
            })
            setNotifications((prev) =>
                prev.map((n) => {
                    const found = updated.find((u) => u.id === n.id)
                    return found ? mapNotification(found) : n
                })
            )
        } catch {}
    }

    return { notifications, unreadCount, loading, markRead, reload }
}
