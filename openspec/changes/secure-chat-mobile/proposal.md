## Why

O "Chat Seguro" é o ambiente onde a confiança é consolidada entre clientes e profissionais no ServiçoJá. Integrar os detalhes do contrato diretamente na conversa e utilizar uma interface **neomórfica** tátil e moderna reforça a segurança e o profissionalismo da plataforma. Esta proposta visa criar uma experiência de mensageria fluida e contextual, facilitando a comunicação e a finalização de serviços.

## What Changes

- **Interface de Chat Mobile-First**: Otimização completa para telas de até 480px, priorizando a legibilidade e o acesso rápido a ações de contrato.
- **Header e Banner Contexual**:
    - Header elevado com perfil do profissional e indicador de status "Online" pulsante.
    - Banner de "Contrato Ativo" elevado com acesso rápido aos detalhes financeiros e status do serviço.
- **Área de Mensagens Especializada**:
    - Fundo da conversa levemente afundado (#c4c0d0).
    - Bolhas de mensagens com estilos distintos: AFUNDADAS para o profissional e ELEVADAS para o cliente (com tint menta).
- **Input e Controles de Ação**:
    - Barra de mensagem afundada (*inset*) com controles de anexo elevados.
    - Botão CTA fixo no rodapé para confirmação de conclusão e avaliação do serviço.

## Capabilities

### New Capabilities
- `secure-chat-shell`: Estrutura base do chat com header de perfil e banner de contrato ativo.
- `neomorphic-bubbles-system`: Sistema de componentes para mensagens enviadas e recebidas com elevações e arredondamentos assimétricos.
- `chat-input-bar`: Barra de entrada de texto neomórfica com suporte a anexos e botão de envio circular.

### Modified Capabilities
- `chat-messaging`: Atualização do sistema de chat existente para o novo padrão visual neomórfico e mobile-first.

## Impact

- **Frontend**: Desenvolvimento de componentes de chat responsivos; implementação de lógica de estados de mensagem (envio/leitura); aplicação rigorosa dos tokens de Neomorfismo em bolhas e inputs.
- **UX/UI**: Transforma a conversa em um fluxo de trabalho estruturado, mantendo o contexto do contrato sempre visível.
