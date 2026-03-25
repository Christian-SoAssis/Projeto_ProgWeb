## Context

O "Chat Seguro" v2 é uma interface **mobile-first** (max-width 480px) que combina mensageria em tempo real com gestão contratual. O design utiliza os princípios de Neomorfismo (sombras duplas e sem bordas) para criar uma hierarquia visual clara, separando o contexto do serviço (banner) da interação social (mensagens). A área de chat utiliza um fundo afundado para dar profundidade ao histórico de conversa.

## Goals / Non-Goals

**Goals:**
- Implementar o layout mobile-first centralizado (max-width 480px).
- Desenvolver o Header Neomórfico com perfil do profissional e status pulsante.
- Criar o Banner de Contrato Ativo com indicadores financeiros e de progresso.
- Implementar o sistema de bolhas de mensagem neomórficas (recebida vs enviada).
- Desenvolver a barra de entrada de texto e o botão de ação final.

**Non-Goals:**
- Implementação de chamadas de voz ou vídeo (serão ícones decorativos por enquanto).
- Lógica de criptografia ponta-a-ponta (foco na interface e UX).

## Decisions

### 1. Header e Contexto de Contrato
- **Header**: Elevação `elevated-sm`. Inclui avatar circular neomórfico com badge de categoria (ex: Azul para Hidráulica) e dot "Online" menta pulsante.
- **Banner Contrato**: 
    - Card elevado (`elevated-nm`) com faixa superior de 3px em menta (#1a9878).
    - Botão de ação interno: `inset` pequeno para "Ver contrato".

### 2. Sistema de Mensagens
- **Área de Chat**: Fundo afundado levemente mais escuro (#c4c0d0) para concentrar o histórico.
- **Bolhas de Mensagem**:
    - **Recebida (Profissional)**: Neomorfismo AFUNDADO (`inset-nm`), arredondamento assimétrico (4px 16px 16px 16px), cor de texto secundário.
    - **Enviada (Cliente)**: Neomorfismo ELEVADO (`elevated-sm`), arredondamento assimétrico (16px 4px 16px 16px), tint menta (`rgba(26,152,120,.08)`), cor de texto primário.

### 3. Entrada de Texto e Rodapé
- **Barra de Input**: Barra AFUNDADA (`inset`, radius 50px) com ícones de anexo elevados e botão de envio circular menta elevado.
- **CTA Final**: Botão elevado de largura total para fechamento do contrato ("Confirmar conclusão").

## Risks / Trade-offs

- **Contraste de Mensagens**: Bolhas afundadas podem ter menor legibilidade se o contraste entre a sombra interna e o texto não for bem calibrado. Usaremos o texto secundário para maior conforto visual.
- **Altura da Tela**: O banner de contrato fixo no topo e o input no rodapé reduzem a área visível do chat em telas pequenas. O banner será minimizável via scroll se necessário.
