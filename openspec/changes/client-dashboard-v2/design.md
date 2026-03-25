## Context

O "Dashboard do Cliente" v2 é uma interface **mobile-first** (max-width 480px) projetada para oferecer uma experiência tátil e intuitiva. O layout prioriza o acompanhamento de pedidos ativos e a visualização rápida de notificações. O design utiliza os princípios de Neomorfismo (sombras duplas e sem bordas) para criar uma hierarquia visual clara em uma tela compacta.

## Goals / Non-Goals

**Goals:**
- Implementar o layout mobile-first centralizado (max-width 480px).
- Desenvolver o Header Neomórfico com badge de notificação elevado.
- Criar as Nav Pills horizontais com scroll e estados visuais ativos/inativos.
- Implementar o sistema de cards de pedidos e widgets de atividade/stats.

**Non-Goals:**
- Implementação de fluxos de chat detalhados (serão tratados em outra proposta).
- Funcionalidades de gerenciamento de perfil completo.

## Decisions

### 1. Header e Navegação Mobile
- **Header**: Elevação `elevated-sm`. Inclui saudação e um badge de notificação (`elevated-sm` pequeno) com contador.
- **Nav Pills**: 
    - Container com `overflow-x: auto` e `scrollbar-hide`.
    - Pills com `border-radius: 50px`.
    - Ativo: `inset-nm` com cor de acento (#1a9878). Inativo: `elevated-sm`.

### 2. Cards de Pedidos Ativos
- **Layout**: Lista empilhada verticalmente.
- **Elevação**: `elevated-lg` (22px radius).
- **Indicadores**: Faixa superior de 3px na cor da categoria identificada.
- **Status Badges**:
    - Aberto: Verde (#2a8c50).
    - Em andamento: Âmbar (#d4a00a).
    - Concluído: Cinza (#9080b0).

### 3. Atividade e Stats Rápidos
- **Atividade Recente**: Itens de lista com ícone emoji em círculo `elevated-sm`.
- **Stats Rápidos**: Row de 3 mini-cards `elevated-sm`. Valores em `DM Mono`.

## Risks / Trade-offs

- **Densidade de Informação**: O Neomorfismo consome mais espaço devido às sombras. Em telas de 320px, teremos que reduzir os paddings para evitar que os cards fiquem muito estreitos.
- **Scroll Horizontal**: As Nav Pills devem ter um indicador visual claro de que há mais itens para rolar (ex: gradiente sutil ou corte parcial do último item).
