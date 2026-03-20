# Spec: nextjs-architecture

> Arquitetura de rotas Next.js 14 App Router para o ServiçoJá. Define tipo de componente (Server/Client), sub-componentes interativos, e estratégia de data fetching por rota.

---

## Regra Geral

> [!IMPORTANT]
> **Server Component por padrão.** Usar `'use client'` **apenas** quando há uma razão concreta:
> - Formulários com estado local (`useState`, `useForm`)
> - Event handlers do navegador (`onClick`, `onChange`, `onSubmit`)
> - Hooks de ciclo de vida (`useEffect`, `useRef`)
> - WebSocket / real-time (`useSocket`)
> - APIs do browser (`navigator.geolocation`, `Notification.requestPermission`)

### Data Fetching

| Tipo | Quando usar | Ferramenta |
|------|------------|-----------|
| **Server fetch** | Dados estáticos ou que mudam pouco, SEO necessário | `fetch()` direto em Server Components, com `cache` / `revalidate` |
| **SWR (cliente)** | Dados que mudam em tempo real ou após ações do usuário | `useSWR` com `fetcher` e `revalidateOnFocus` |
| **React Query** | Mutations com optimistic updates | `useMutation` para POST/PATCH/DELETE |

---

## Árvore de Rotas

```
app/
├── layout.tsx                    (Server) — Shell global, providers, fontes
├── page.tsx                      (Server) — Landing page / marketing
├── (auth)/
│   ├── login/page.tsx            (Client) — Formulário
│   ├── register/page.tsx         (Client) — Formulário
│   └── register/profissional/page.tsx (Client) — Formulário multi-step
├── (dashboard)/
│   ├── layout.tsx                (Server) — Sidebar, auth check
│   ├── pedidos/
│   │   ├── page.tsx              (Server) — Lista de pedidos
│   │   ├── novo/page.tsx         (Client) — Formulário + geo + upload
│   │   └── [id]/
│   │       ├── page.tsx          (Server) — Detalhes do pedido
│   │       └── propostas/page.tsx (Server) — Lista de bids
│   ├── contratos/
│   │   └── [id]/
│   │       ├── page.tsx          (Server) — Detalhes do contrato
│   │       ├── pagamento/page.tsx (Client) — Checkout MercadoPago
│   │       ├── disputa/page.tsx  (Client) — Formulário de disputa
│   │       ├── avaliacao/page.tsx (Client) — Formulário de review
│   │       └── chat/page.tsx     (Client) — WebSocket real-time
│   ├── favoritos/page.tsx        (Server) — Lista de favoritos
│   ├── perfil/page.tsx           (Client) — Edição de perfil
│   └── notificacoes/page.tsx     (Server) — Lista de notificações
├── profissional/
│   ├── layout.tsx                (Server) — Sidebar profissional
│   ├── dashboard/page.tsx        (Server) — Métricas
│   ├── agenda/page.tsx           (Server) — Bids pendentes
│   └── perfil/page.tsx           (Client) — Edição de perfil
├── busca/page.tsx                (Client) — Mapa + filtros interativos
├── p/[slug]/page.tsx             (Server) — Perfil público (SEO)
├── admin/
│   ├── layout.tsx                (Server) — Auth admin check
│   ├── dashboard/page.tsx        (Server) — KPIs gerais
│   ├── profissionais/page.tsx    (Server) — Aprovação
│   ├── disputas/page.tsx         (Server) — Listagem
│   └── disputas/[id]/page.tsx    (Server) — Detalhe + resolução
└── offline/page.tsx              (Server) — Fallback PWA
```

---

## Rotas Detalhadas

### `/` — Landing Page

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: categorias populares, stats da plataforma — `revalidate: 3600` (1h) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `SearchHero` | `onChange` para input de busca, `onClick` para CTA, `navigator.geolocation` |
| `InstallBanner` | `useEffect` para `beforeinstallprompt` (A2HS) |

---

### `/login`

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário com `useForm` (react-hook-form), `useState` para erros, `onClick` para OAuth |
| **Dados** | Nenhum server fetch; login via `useMutation` (POST /auth/login) |

---

### `/register`

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário com validação Zod, `useState`, `useForm` |
| **Dados** | `useMutation` (POST /auth/register) |

---

### `/register/profissional`

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário multi-step (dados pessoais → categorias → documentos → localização), `useState` para step, `useRef` para file input, `navigator.geolocation` |
| **Dados** | Server fetch (em `layout.tsx`): categorias. `useMutation` (POST /professionals) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `StepIndicator` | `useState` para step ativo |
| `DocumentUpload` | `useRef` para file input, drag-and-drop events |
| `LocationPicker` | `useEffect` + `navigator.geolocation`, mapa interativo |
| `CategorySelector` | `useState` para seleção múltipla, `onClick` |

---

### `/pedidos` — Lista de Pedidos

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /requests (paginado, filtrado por status) — `revalidate: 0` (dinâmico, cookies) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `StatusFilter` | `useState` para filtro ativo, `onClick` para tabs |
| `OfflineBanner` | `useEffect` + `navigator.onLine`, evento `online`/`offline` |

---

### `/pedidos/novo` — Criar Pedido

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário complexo: uploads de imagem, geolocalização, seleção de categoria |
| **Dados** | SWR: categorias (cached). `useMutation` (POST /requests + upload imagens) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `ImageUploader` | `useRef` file input, drag-and-drop, preview com `URL.createObjectURL` |
| `LocationInput` | `navigator.geolocation`, mapa pin, `useState` para coords |
| `UrgencySelector` | `useState` para seleção |
| `BudgetInput` | `onChange` para formatação de moeda |

---

### `/pedidos/[id]` — Detalhes do Pedido

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /requests/:id (com imagens, ai_* fields) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `ImageGallery` | `useState` para modal lightbox, `onClick` para navegação |
| `AiAnalysisBadge` | Puro presentational — **Server Component** (sem `'use client'`) |

---

### `/pedidos/[id]/propostas` — Bids Recebidos

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /requests/:id/bids |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `BidCard` | **Server Component** — presentational |
| `AcceptRejectButtons` | `onClick` + `useMutation` (PATCH /bids/:id), `useState` para loading/confirm |
| `SortSelector` | `useState` para ordenação |

---

### `/contratos/[id]` — Detalhes do Contrato

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /contracts/:id (com profissional, disputa aninhada) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `StatusTimeline` | **Server Component** — presentational |
| `ActionButtons` | `onClick` para navegar a pagamento/disputa/avaliação |

---

### `/contratos/[id]/pagamento` — Checkout

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | SDK do MercadoPago (Brick de pagamento), redirect pós-checkout |
| **Dados** | `useMutation` (POST /contracts/:id/payment) → recebe URL do checkout |

---

### `/contratos/[id]/disputa` — Abrir/Ver Disputa

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário de abertura, formulário de resposta, `useState` para modo (abrir vs responder) |
| **Dados** | SWR: GET /disputes/:id (se existir). `useMutation` (POST /contracts/:id/dispute, POST /disputes/:id/response) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `DisputeForm` | `useForm` + validação Zod, upload de evidências |
| `ResponseForm` | `useForm`, `useState` para proposed_resolution |
| `EvidenceUploader` | `useRef` file input, preview |
| `CountdownTimer` | `useEffect` + `setInterval` para deadline 72h |

---

### `/contratos/[id]/avaliacao` — Review

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário com star rating interativo, textarea |
| **Dados** | `useMutation` (POST /reviews) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `StarRating` | `useState` para hover preview, `onClick` para selecionar |
| `ReviewTextarea` | `onChange`, counter de caracteres |

---

### `/contratos/[id]/chat` — Chat In-App

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | WebSocket (Socket.io), scroll automático, input de mensagem, `useEffect` para conexão/desconexão |
| **Dados** | SWR: histórico inicial GET /contracts/:id/messages. Real-time: WebSocket `onMessage` |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `MessageList` | `useRef` para scroll-to-bottom, `useEffect` para auto-scroll |
| `MessageInput` | `useState` para conteúdo, `onKeyDown` Enter para enviar |
| `ConnectionStatus` | `useState` para status do socket |
| `MessageBubble` | **Server Component** (estático) — passado como children |

---

### `/favoritos` — Lista de Favoritos

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /favorites |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `RemoveFavoriteButton` | `onClick` + `useMutation` (DELETE /favorites/:id) |

---

### `/perfil` — Edição de Perfil (Cliente)

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário de edição, upload de avatar |
| **Dados** | SWR: GET /auth/me. `useMutation` (PATCH /users/me) |

---

### `/notificacoes` — Notificações

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /notifications (paginado) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `MarkReadButton` | `onClick` + `useMutation` (PATCH /notifications/mark-read) |
| `NotificationBadge` | SWR: `GET /notifications?unread=true` com `refreshInterval: 30000` |

---

### `/profissional/dashboard` — Painel Profissional

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /professionals/me/metrics |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `EarningsChart` | Biblioteca de charts (recharts), `useEffect` para resize |
| `PeriodSelector` | `useState` para período ativo (7d, 30d, 90d) |

---

### `/profissional/agenda` — Bids Pendentes

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /bids?status=pending (profissional) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `BidActionButtons` | `onClick` + `useMutation` para cancelar bid |

---

### `/profissional/perfil` — Edição de Perfil Prof.

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Formulário multi-campo, upload docs, mapa de localização, seleção de categorias |
| **Dados** | SWR: GET /professionals/me. `useMutation` (PATCH /professionals/me) |

---

### `/busca` — Busca e Mapa

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Client Component |
| **Motivo** | Mapa interativo (Leaflet/Mapbox), filtros dinâmicos, geolocalização, debounce de input |
| **Dados** | SWR: GET /search/professionals com filtros (q, lat/lng, radius_km, category) — re-fetch a cada filtro alterado |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `SearchMap` | Mapa interativo, `useRef` para instância do mapa, `useEffect` para pins |
| `FilterSidebar` | `useState` para filtros, `onChange` |
| `SearchInput` | `useState` + debounce (`useEffect` com timer), `onChange` |
| `ProfessionalCardList` | **Server Component** via streaming — renderizado no servidor e passado como children |
| `RadiusSlider` | `useState`, `onChange` |

---

### `/p/[slug]` — Perfil Público do Profissional (SEO)

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Motivo** | SEO: `generateMetadata()` com nome, bio, rating para meta tags e OG |
| **Dados** | Server fetch: GET /professionals/:slug — `revalidate: 300` (5 min) |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `ReputationRadar` | Biblioteca de charts (recharts), canvas rendering |
| `FavoriteButton` | `onClick` + `useMutation` (POST /favorites), `useState` para toggle |
| `ContactCTA` | `onClick` para iniciar pedido |

---

### `/admin/dashboard` — KPIs Admin

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /admin/metrics |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `KpiChart` | recharts, resize |
| `DateRangePicker` | `useState`, calendar popup |

---

### `/admin/profissionais` — Aprovação de Profissionais

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /admin/professionals?status=pending |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `ApproveRejectButtons` | `onClick` + `useMutation` (PATCH /admin/professionals/:id) |
| `DocumentViewer` | Modal lightbox, `useState` |

---

### `/admin/disputas` — Listagem de Disputas

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /admin/disputes?status=opened |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `StatusFilter` | `useState` para filtro ativo |

---

### `/admin/disputas/[id]` — Resolução de Disputa

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component |
| **Dados** | Server fetch: GET /admin/disputes/:id |

**Sub-componentes `'use client'`:**

| Componente | Motivo |
|-----------|--------|
| `ResolveForm` | `useForm` + Zod, `useState` para resolution type, range slider para refund_percent |
| `EvidenceGallery` | `useState` para lightbox modal |

---

### `/offline` — Fallback PWA

| Aspecto | Detalhe |
|---------|---------|
| **page.tsx** | Server Component (pre-cached pelo Service Worker) |
| **Dados** | Nenhum — tela estática com mensagem e botão de retry |

---

## Resumo: Server vs Client

| Tipo | Rotas | % |
|------|-------|--:|
| **Server Component** | `/`, `/pedidos`, `/pedidos/[id]`, `/pedidos/[id]/propostas`, `/contratos/[id]`, `/favoritos`, `/notificacoes`, `/profissional/dashboard`, `/profissional/agenda`, `/p/[slug]`, `/admin/*`, `/offline` | **~60%** |
| **Client Component** | `/login`, `/register`, `/register/profissional`, `/pedidos/novo`, `/contratos/[id]/pagamento`, `/contratos/[id]/disputa`, `/contratos/[id]/avaliacao`, `/contratos/[id]/chat`, `/perfil`, `/profissional/perfil`, `/busca` | **~40%** |

### Motivos recorrentes para `'use client'`

| Motivo | Exemplos |
|--------|---------|
| Formulários (`useForm`, `useState`, `onChange`) | Login, Register, Pedido Novo, Disputa, Review |
| WebSocket / real-time | Chat |
| APIs do browser | Geolocalização (Busca, Pedido Novo), Notifications (PWA) |
| Bibliotecas client-only | MercadoPago SDK (Pagamento), Leaflet (Busca), recharts (Dashboard) |
| Interatividade intensa | Filtros dinâmicos (Busca), Star rating (Review) |

---

## Layout Hierarchy

```
app/layout.tsx (Server)
├── Providers (Client) — ThemeProvider, SWRConfig, AuthContext
├── Header (Server)
│   ├── Logo (Server)
│   ├── NavLinks (Server)
│   └── UserMenu (Client) — useState para dropdown, onClick
├── main → {children}
└── Footer (Server)

app/(dashboard)/layout.tsx (Server)
├── Sidebar (Server)
│   ├── NavItems (Server)
│   └── NotificationBadge (Client) — SWR polling
└── main → {children}
```

---

## Shared Client Components (components/)

| Componente | Usado em | Motivo `'use client'` |
|-----------|---------|----------------------|
| `UserMenu` | Layout global | Dropdown state, onClick |
| `NotificationBadge` | Sidebar | SWR polling 30s |
| `FavoriteButton` | Perfil público, cards | onClick + mutation |
| `ImageUploader` | Pedido novo, Disputa, Perfil | File input, drag-drop |
| `LocationPicker` | Cadastro profissional, Pedido novo | Geolocation API |
| `ConfirmDialog` | Aceitar bid, Excluir conta | useState, onClick |
| `Toast` | Global (via Provider) | Animated notification |
| `OfflineBanner` | Dashboard layout | navigator.onLine |
