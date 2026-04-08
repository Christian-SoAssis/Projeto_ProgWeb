"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps extends React.ComponentProps<"input"> {
  mask?: "phone" | "cpf"
}

const maskValue = (value: string, mask?: "phone" | "cpf") => {
  if (!mask) return value
  
  const numbers = value.replace(/\D/g, "")
  
  if (mask === "phone") {
    if (numbers.length <= 11) {
      return numbers
        .replace(/(\d{2})(\d)/, "($1) $2")
        .replace(/(\d{5})(\d)/, "$1-$2")
        .substring(0, 15)
    }
    return value.substring(0, 15)
  }
  
  if (mask === "cpf") {
    return numbers
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d)/, "$1.$2")
      .replace(/(\d{3})(\d{1,2})/, "$1-$2")
      .substring(0, 14)
  }
  
  return value
}

function Input({ className, type, mask, onChange, value, ...props }: InputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (mask) {
      e.target.value = maskValue(e.target.value, mask)
    }
    onChange?.(e)
  }

  return (
    <input
      type={type}
      data-slot="input"
      value={value}
      onChange={handleChange}
      className={cn(
        "h-11 w-full min-w-0 rounded-2xl border-none bg-background px-4 py-3 text-base transition-all outline-none placeholder:text-muted-foreground/50",
        "focus-visible:shadow-neo-inset focus-visible:scale-[0.99]",
        "disabled:pointer-events-none disabled:opacity-50 aria-invalid:ring-1 aria-invalid:ring-destructive/50 md:text-sm",
        className
      )}
      {...props}
    />
  )
}

export { Input }
