import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value // Nota: Middleware Next.js prefere cookies
  // Para fins didáticos e simplicidade no MVP, como o AuthContext usa localStorage (que não é acessível no middleware 100% via request), 
  // poderiamos usar cookies. Mas por enquanto, vamos fazer a proteção básica no lado do cliente ou apenas via cookies se implementado.
  
  // Se você implementar cookies no AuthContext depois, o middleware fica assim:
  /*
  const { pathname } = request.nextUrl
  if (pathname.startsWith("/dashboard") && !token) {
    return NextResponse.redirect(new URL("/login", request.url))
  }
  */
  
  return NextResponse.next()
}

export const config = {
  matcher: ["/dashboard/:path*"],
}
