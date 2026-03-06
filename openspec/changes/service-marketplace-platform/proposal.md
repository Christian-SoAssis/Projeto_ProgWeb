# Proposal: Service Marketplace Platform

## O Que & Por Quê

Construir uma plataforma de marketplace de serviços locais (pedreiros, encanadores, advogados, arquitetos, etc.) que conecta clientes a profissionais verificados, com diferenciação competitiva por meio de **matching inteligente via IA**, **análise de imagens do problema**, e **sistema de reputação granular**.

### Contexto Competitivo

| Player (Brasil)    | Modelo        | Fraqueza explorada                          |
|--------------------|---------------|---------------------------------------------|
| GetNinjas          | Lead-based    | CAC alto pro profissional, sem garantia     |
| Triider            | Commission    | Nicho restrito (reparos residenciais)       |
| Cronoshare         | Lead-based    | UX datada, sem diferenciação por IA         |
| Workana/99freelas  | Freelance     | Foco em serviços digitais, não locais       |

| Player (Global)    | Modelo        | Lição aprendida                             |
|--------------------|---------------|---------------------------------------------|
| Thumbtack (EUA)    | Lead-based    | Matchmaking ativo é mais rentável que passsivo |
| Angi/HomeAdvisor   | Anúncio+lead  | Diversidade de receita, mas UX complexa    |
| TaskRabbit (IKEA)  | Commission    | Booking direto + garantia geram confiança  |
| Urban Company (IN) | Managed       | Padronização de preço é barreira de entrada|

### Diferenciação Proposta

1. **Análise de imagens com IA (VLM)** — cliente fotografa o problema, IA classifica urgência e especialização necessária antes do matching.
2. **Motor de matching com Learning to Rank (LTR)** — score multi-critério (geo, reputação, competência, preço, disponibilidade) que melhora com cada contratação.
3. **Reputação granular com NLP** — reviews analisadas por IA (BERTimbau) gerando scores por dimensão (pontualidade, qualidade, limpeza) exibidos como "radar" no perfil.

## Escopo

### Incluído
- Cadastro e verificação de profissionais (CPF, CNPJ, certificações)
- Fluxo de pedido de serviço com upload de fotos
- Pipeline de análise de imagem (VLM → classificação → features de matching)
- Motor de matching com score multi-critério
- Sistema de orçamento/bid e chat in-app
- Pagamento via PIX e cartão (gateway: MercadoPago ou Stripe BR)
- Avaliações com análise NLP e exibição granular de reputação
- Painel do profissional (agenda, histórico, métricas)
- Painel do cliente (pedidos, histórico, favoritos)

### Fora do Escopo (v1)
- App nativo (iOS/Android) — web responsivo primeiro
- Serviços internacionais
- Planos de assinatura para profissionais (modelo comission puro v1)
- IA generativa para geração de orçamentos automáticos

## Modelo de Negócio

**Comissão sobre transação concluída** — plataforma retém X% do valor pago.

- Alinhamento total: só ganha se o serviço acontece.
- Reduz fricção de entrada para o profissional (sem custo de lead travado).
- Requer mecanismo anti-desintermediação (chat monitorado, pagamento obrigatório in-app).

## Non-Goals

- Não somos uma plataforma de freelancers digitais (Workana, Upwork).
- Não garantimos preços fixos por categoria (modelo Managed) na v1.
- Não construímos os modelos de IA from-scratch — usamos APIs (Gemini Vision, BERTimbau).
