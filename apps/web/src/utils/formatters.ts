export function formatRelative(iso: string) {
    const diff = Date.now() - new Date(iso).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return "agora"
    if (mins < 60) return `${mins}min atrás`
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h atrás`
    return `${Math.floor(hrs / 24)}d atrás`
}
