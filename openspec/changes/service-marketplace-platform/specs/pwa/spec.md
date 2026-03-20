# Spec: pwa

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Service Worker — Estratégia de cache

O sistema **SHALL** registrar um Service Worker que implemente estratégias de cache diferenciadas por tipo de recurso, garantindo performance e experiência offline.

### Estratégias de cache

| Tipo de recurso | Estratégia | TTL / Regra |
|---|---|---|
| Assets estáticos (JS, CSS, fontes, imagens) | **Cache-First** | Versioned por hash no build (Next.js `_next/static/`) — invalidado no deploy |
| Dados de API (`/api/*`) | **Network-First** | Fallback para cache se offline; TTL 5 min para dados não-críticos |
| Páginas HTML (navegação) | **Stale-While-Revalidate** | Serve cache, atualiza em background |
| Upload de imagens (S3/MinIO URLs) | **Cache-First** | Imutáveis por URL, cache permanente |

### Scenario 1 — Primeiro acesso (cache frio)

- **GIVEN** que o usuário acessa a aplicação pela primeira vez (sem cache)
- **WHEN** o Service Worker é registrado e ativado
- **THEN** o sistema **MUST** pre-cache o app shell (HTML, CSS, JS essenciais, ícones), retornar recursos via rede, e populá-los no cache para acessos futuros

### Scenario 2 — Acesso subsequente com rede disponível (assets)

- **GIVEN** que os assets estáticos já estão no cache e a rede está disponível
- **WHEN** o navegador requisita um asset versionado (`_next/static/chunks/...`)
- **THEN** o sistema **MUST** servir do cache (Cache-First), sem requisição de rede; **SHOULD** verificar atualizações do SW em background

### Scenario 3 — Acesso subsequente com rede disponível (dados de API)

- **GIVEN** que a rede está disponível e dados da API estão no cache
- **WHEN** o navegador faz fetch para `/api/requests` ou similares
- **THEN** o sistema **MUST** tentar rede primeiro (Network-First); se sucesso, atualizar cache; se falha de rede, servir cache

### Scenario 4 — Atualização do Service Worker

- **GIVEN** que uma nova versão do SW está disponível após deploy
- **WHEN** o navegador detecta mudança no SW durante navigation
- **THEN** o sistema **MUST** instalar o novo SW em background, aguardar ativação no próximo reload; **SHOULD** exibir toast: `"Nova versão disponível — atualize a página"`

---

## Requirement: Comportamento offline — Tela de pedidos ativos

O sistema **SHALL** permitir ao cliente visualizar seus pedidos ativos e bids recebidos mesmo quando offline, usando dados previamente cacheados.

### Scenario 1 — Visualização de pedidos offline

- **GIVEN** que o cliente acessou a tela de pedidos ativos pelo menos uma vez online
- **WHEN** o dispositivo perde conexão e o cliente navega para `/pedidos`
- **THEN** o sistema **MUST** exibir os dados cacheados da última sincronização; **MUST** mostrar banner: `"Você está offline — dados podem estar desatualizados"`; **MUST** desabilitar ações que requerem rede (aceitar bid, iniciar pagamento)

### Scenario 2 — Ação bloqueada offline

- **GIVEN** que o cliente está offline e tenta aceitar um bid
- **WHEN** o botão de ação é clicado
- **THEN** o sistema **MUST** exibir feedback visual: `"Sem conexão — tente novamente quando estiver online"`; **MUST NOT** enfileirar a ação para execução posterior (operações financeiras não são idempotentes)

### Scenario 3 — Reconexão automática

- **GIVEN** que o cliente estava offline e a conexão é restaurada
- **WHEN** o evento `online` do navigator é disparado
- **THEN** o sistema **MUST** remover o banner de offline, revalidar dados da tela atual via fetch (Network-First), e re-habilitar botões de ação

### Scenario 4 — Página nunca acessada antes (cache vazio)

- **GIVEN** que o cliente nunca acessou `/pedidos` enquanto online
- **WHEN** tenta navegar offline para `/pedidos`
- **THEN** o sistema **MUST** exibir tela de fallback offline com mensagem: `"Conecte-se à internet para carregar seus pedidos"`; **MUST NOT** exibir tela em branco

---

## Requirement: Push Notifications via Web Push API

O sistema **SHALL** enviar push notifications via Web Push API para eventos de bid e mensagem, mesmo quando o app não está aberto no navegador.

### Scenario 1 — Opt-in de notificações no cadastro/primeiro acesso

- **GIVEN** que o usuário está autenticado e nunca concedeu permissão de push
- **WHEN** acessa o dashboard pela primeira vez
- **THEN** o sistema **SHOULD** exibir prompt contextual (não-intrusivo) explicando o valor das notificações: `"Receba alertas de novas propostas e mensagens em tempo real"`; ao aceitar, **MUST** registrar subscription no backend via `POST /push/subscribe` com `{ endpoint, keys: { p256dh, auth } }`

### Scenario 2 — Push para novo bid recebido (cliente)

- **GIVEN** que o cliente tem subscription de push registrada e um profissional envia bid para seu pedido
- **WHEN** o sistema processa o bid
- **THEN** o sistema **MUST** enviar push notification com: `title: "Nova proposta recebida"`, `body: "{nome_profissional} enviou uma proposta de R$ X,XX"`, `icon: logo da plataforma`, `data: { url: "/pedidos/{request_id}" }`; ao clicar, **MUST** abrir a tela do pedido

### Scenario 3 — Push para nova mensagem no chat (ambas as partes)

- **GIVEN** que o destinatário tem subscription de push e não está com a aba do chat aberta
- **WHEN** uma mensagem é enviada no chat de um contrato
- **THEN** o sistema **MUST** enviar push com: `title: "Nova mensagem de {nome}"`, `body: preview (primeiros 100 chars)`, `data: { url: "/chat/{contract_id}" }`; **MUST NOT** enviar push se o destinatário está com a aba do chat ativa (evitar duplicata com WebSocket)

### Scenario 4 — Push para disputa aberta

- **GIVEN** que a parte contrária tem subscription de push
- **WHEN** uma disputa é aberta em um contrato
- **THEN** o sistema **MUST** enviar push: `title: "Disputa aberta"`, `body: "Uma disputa foi aberta no contrato #{id}. Você tem 72h para responder."`, `data: { url: "/contratos/{contract_id}/disputa" }`

### Scenario 5 — Usuário nega permissão de push

- **GIVEN** que o usuário nega a permissão do browser para notificações
- **WHEN** o sistema tenta registrar subscription
- **THEN** o sistema **MUST** armazenar `push_opt_out=true` no perfil; **MUST NOT** exibir o prompt novamente; **SHOULD** manter notificações in-app via WebSocket como fallback

### Scenario 6 — Subscription expirada ou inválida

- **GIVEN** que o push provider retorna `410 Gone` ou `404 Not Found` para uma subscription
- **WHEN** o sistema tenta enviar push notification
- **THEN** o sistema **MUST** remover a subscription do banco; **SHOULD** marcar o dispositivo para re-registro no próximo acesso

---

## Requirement: manifest.json completo

O sistema **SHALL** fornecer um `manifest.json` válido para instalação como PWA em dispositivos móveis e desktop.

### Campos obrigatórios

```json
{
  "name": "ServiçoJá — Marketplace de Serviços",
  "short_name": "ServiçoJá",
  "description": "Encontre profissionais verificados para serviços residenciais e comerciais",
  "start_url": "/?source=pwa",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#ffffff",
  "theme_color": "#1a1a2e",
  "lang": "pt-BR",
  "scope": "/",
  "categories": ["business", "lifestyle"],
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ],
  "screenshots": [
    { "src": "/screenshots/home.png", "sizes": "1080x1920", "type": "image/png", "form_factor": "narrow" }
  ]
}
```

### Scenario 1 — Validação do manifest por Lighthouse

- **GIVEN** que o manifest.json está configurado
- **WHEN** o Lighthouse audita a aplicação
- **THEN** **MUST** passar todos os critérios de "Installable": manifest válido, Service Worker registrado, HTTPS ativo, ícones 192 e 512px presentes

### Scenario 2 — Prompt de instalação A2HS

- **GIVEN** que o browser detecta critérios de instalação atendidos
- **WHEN** o evento `beforeinstallprompt` é disparado
- **THEN** o sistema **SHOULD** interceptar o evento e exibir banner customizado após a segunda visita: `"Instale o ServiçoJá para acesso rápido"`; **MUST NOT** exibir no primeiro acesso

### Scenario 3 — Abertura via ícone instalado

- **GIVEN** que o usuário instalou a PWA via A2HS
- **WHEN** abre o app via ícone na home screen
- **THEN** o sistema **MUST** abrir em modo `standalone` (sem barra de endereço), com `theme_color` aplicado na status bar, e navegar para `start_url` com parâmetro `source=pwa` para tracking
