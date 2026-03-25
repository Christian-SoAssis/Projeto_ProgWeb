## Context

A tela "Novo Pedido — Passo 2" é uma interface de formulário rica que utiliza **Neomorphism** para criar uma experiência tátil. O destaque é a integração visual com o motor de IA, que fornece feedback imediato sobre a descrição do usuário. O layout é centralizado e focado em converter a entrada do usuário em dados estruturados.

## Goals / Non-Goals

**Goals:**
- Implementar o `Stepper` neomórfico (3 etapas).
- Criar a área de upload e o campo de texto com sombra interna (*inset*).
- Desenvolver o card de "Análise IA" com barras de progresso e badges dinâmicos.
- Utilizar a paleta Lavanda Pó e o Acento Menta (#1a9878).

**Non-Goals:**
- Implementação da lógica de processamento de imagem no servidor (foco na UI de upload).
- Integração real com a API de IA (usaremos estados de mock/front para esta proposta).

## Decisions

### 1. Stepper Neomórfico
- **Círculos**: `elevated-sm`.
- **Estado Ativo**: `inset-nm` com `border: 2px solid #1a9878`.
- **Concluído**: Preenchimento total em Menta com ícone de check (√).

### 2. Card Central de Descrição
- **Elevação**: `elevated-lg` (22px radius).
- **Upload Area**: `inset-nm`, altura fixa de 200px. Ícone de câmera em menta.
- **Fields**: Input de localização e seletor de urgência lado a lado, ambos `inset-nm`.

### 3. Card de Análise IA (Feedback)
- **Elevação**: `elevated-sm`, posicionado logo abaixo do card principal.
- **Badges**: Estilo afundado (`inset-nm`) com fundos translúcidos baseados na cor da categoria identificada.
- **Barras de Progresso**:
    - Trilhas (*tracks*): `inset-nm`.
    - Preenchimento (*fill*): Cores sólidas (Âmbar para complexidade, Terracota para urgência, Menta para confiança).
- **Tipografia**: `DM Mono` para valores numéricos (ex: "94%", "Alta").

### 4. Navegação
- Botão CTA inferior em Menta, largura total, `elevated-sm` com brilho de acento.

## Risks / Trade-offs

- **Feedback Visual da IA**: Mostrar resultados de IA enquanto o usuário digita pode ser distrativo. Implementaremos um *debounce* ou acionamento via botão "Analisar" se o feedback em tempo real for muito instável.
- **Complexidade de Sombras**: O aninhamento de elementos *inset* dentro de cards *elevados* deve ser testado para garantir que a percepção de profundidade não seja confusa.
