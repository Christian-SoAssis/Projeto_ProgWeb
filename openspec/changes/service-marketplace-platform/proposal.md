# Proposal: Service Marketplace Platform

## Por Quê

O Brasil carece de uma plataforma de serviços locais que una **matching inteligente por IA**, **análise automatizada de imagens do problema** e **reputação granular verificada**. Os players atuais (GetNinjas, Triider, Cronoshare) operam com UX datada, sem diferenciação por IA e sem garantias ao cliente, gerando alta taxa de abandono e desintermediação.

## O Que Muda

- **[NOVO]** Plataforma web responsiva (PWA) conectando clientes a profissionais locais verificados
- **[NOVO]** Pipeline de análise de imagem com VLM (Gemini Vision) — cliente fotografa o problema, IA classifica urgência e especialização
- **[NOVO]** Motor de Matching LTR (LightGBM) — score multi-critério que melhora com cada contratação
- **[NOVO]** Sistema de reputação granular com NLP (BERTimbau) — scores por dimensão (pontualidade, qualidade, limpeza, comunicação)
- **[NOVO]** Fluxo completo: pedido → bid → contrato → pagamento PIX/cartão → review
- **[NOVO]** Chat in-app com monitoramento anti-desintermediação
- **[NOVO]** Painéis de cliente, profissional e admin

## Capacidades

### Novas Capacidades
- `user-auth` — Autenticação JWT + OAuth2 (Google), cadastro e verificação de profissionais
- `service-request` — Fluxo de pedido de serviço com upload de imagens e análise VLM
- `matching-engine` — Motor de matching LTR com ranking de profissionais
- `bid-contract` — Orçamento (bid), aceite, criação de contrato e pagamento integrado
- `chat-messaging` — Chat in-app com WebSocket e detecção de desintermediação
- `reviews-reputation` — Avaliações com NLP, scores granulares e cálculo de reputação
- `professional-dashboard` — Painel do profissional (agenda, bids, métricas, earnings)
- `client-dashboard` — Painel do cliente (pedidos ativos, histórico, favoritos)
- `admin-dashboard` — Painel admin (aprovação de profissionais, flags de fraude)
- `search-discovery` — Busca geo + full-text com Typesense e mapa interativo

### Capacidades Modificadas
_(nenhuma — projeto novo)_

## Impacto

- **Stack**: Next.js 14 + Node.js/Fastify (BFF) + Python/FastAPI (matching microservice)
- **Banco**: PostgreSQL 16 + PostGIS + pgvector (schema novo completo)
- **Infra**: Docker Compose com Redis, MinIO/S3, Typesense
- **APIs externas**: Gemini Vision, BERTimbau/HuggingFace, MercadoPago/Stripe BR, Resend, Twilio
- **Público-alvo**: Brasil (PT-BR), foco inicial em serviços residenciais e profissionais liberais

## Non-Goals

- App nativo iOS/Android (v1 é web responsivo/PWA)
- Serviços internacionais
- Planos de assinatura para profissionais (comissão pura v1)
- IA generativa para geração de orçamentos automáticos
- Modelos de IA treinados from-scratch (usamos APIs)
- Preços fixos por categoria (modelo "Managed")
