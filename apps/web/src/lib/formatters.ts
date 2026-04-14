export function formatCurrency(cents: number): string {
    return (cents / 100).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
    })
}

export function formatDate(isoString: string): string {
    return new Date(isoString).toLocaleDateString("pt-BR")
}
