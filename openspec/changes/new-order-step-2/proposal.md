## Why

A segunda etapa do processo de "Novo Pedido" é onde o usuário fornece os detalhes cruciais para o sucesso do serviço. Integrar uma interface neomórfica tátil com feedback de **Inteligência Artificial** em tempo real não apenas moderniza a plataforma, mas também melhora a precisão das informações enviadas. Este passo é vital para gerar matches de alta qualidade entre clientes e profissionais.

## What Changes

- **Fluxo de Stepper Neomórfico**: Atualização do indicador de progresso para o estilo neomórfico (círculos elevados e estados ativos *inset*).
- **Formulário de Descrição Detalhada**:
    - Área de upload de mídia afundada (*inset*) com suporte a arrastar e soltar.
    - Campo de texto multilinha e seletores de localização/urgência seguindo o padrão neomórfico.
- **Card de Resultados de IA**: Implementação de um painel de feedback visual que exibe a análise da IA sobre o pedido (complexidade, urgência e confiança) usando barras de progresso e badges.

## Capabilities

### New Capabilities
- `order-description-form`: Componente de formulário com upload de fotos, área de texto e seletores de metadados.
- `ai-analysis-feedback-card`: Painel visual para exibir métricas de IA (complexidade, urgência, confiança) com barras de preenchimento e badges coloridos.
- `neomorphic-stepper`: Sistema de navegação por etapas com estados visuais neomórficos.

### Modified Capabilities
- `service-request-flow`: Extensão da lógica do fluxo de pedido para integrar a etapa de descrição detalhada e o processamento de IA.

## Impact

- **Frontend**: Desenvolvimento de novos componentes de formulário neomórficos; implementação de lógica de upload e pré-visualização; integração visual com o serviço de análise de IA.
- **UX/UI**: Melhoria significativa na percepção de "tecnologia e facilidade" durante a criação de um pedido.
