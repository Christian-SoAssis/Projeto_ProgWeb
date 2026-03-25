## Context

O "Painel do Profissional" v2 adota uma arquitetura de **Sidebar Fixa + Main Content Area**, proporcionando uma navegação estável e foco em métricas de desempenho. O design utiliza as regras de profundidade do Neomorfismo para separar as seções de controle da área de dados, garantindo uma estética premium e executiva.

## Goals / Non-Goals

**Goals:**
- Implementar a Sidebar Neomórfica de 240px com navegação vertical.
- Desenvolver os 3 Stat Cards (Ganhos, Lances, Reputação) com tipografia `DM Mono`.
- Criar o widget de gráfico de desempenho com área visual afundada.
- Implementar o grid de trabalhos agendados e barras de reputação granular.

**Non-Goals:**
- Implementação de lógica de cálculo de ganhos no frontend (esperamos dados processados do backend).
- Funcionalidades de edição de perfil (serão tratadas em outra proposta).

## Decisions

### 1. Sidebar Neomórfica (240px)
- **Elevação**: `elevated-lg` aplicada a todo o bloco lateral.
- **Navegação**: Items com `inset-nm` e cor de acento (#1a9878) quando selecionados.
- **Perfil (Rodapé)**: Avatar circular neomórfico elevado e indicador de presença menta.

### 2. Analytics Widgets
- **Stat Cards**: Elevação `elevated-sm`. Valores principais em `DM Mono` grande.
- **Gráfico de Linha**:
    - Área interna: `inset-nm` com fundo `#dcd8e8`.
    - Eixos e Labels: Texto terciário em `DM Mono`.
    - Linha de Dados: Cor sólida #1a9878 com sombra de brilho sutil.

### 3. Listagens e Indicadores de Progresso
- **Próximos Trabalhos**: Lista com faixa vertical de 3px à esquerda na cor da categoria identificada.
- **Reputação Granular**:
    - Trilhas: `inset-nm`.
    - Preenchimento: Cor sólida Menta (#1a9878).
    - Valores: `DM Mono`.

## Risks / Trade-offs

- **Espaço em Telas Pequenas**: A sidebar fixa de 240px pode ser restritiva em laptops menores. Implementaremos um estado recolhido (*collapsed*) se necessário.
- **Rendering de Gráficos**: Garantir que as bibliotecas de gráficos não introduzam bordas ou sombras conflitantes com o estilo neomórfico.
