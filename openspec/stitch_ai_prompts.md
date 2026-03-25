# Stitch AI Design Prompts: ServiçoJá — Tema Verde (Lavanda Pó)

Este documento contém os prompts atualizados para uso no Stitch AI / Antigravity para criação de telas consistentes do ServiçoJá. Cada prompt deve ser precedido pelo Bloco Global abaixo.

---

## 🎨 Bloco Global — Incluir em TODOS os prompts

IDENTIDADE VISUAL GLOBAL — ServiçoJá (Tema Verde Lavanda)

Plataforma: ServiçoJá — marketplace de serviços locais no Brasil.
Stack: Next.js 14 + shadcn/ui + Tailwind CSS. Todo texto em PT-BR.

DESIGN SYSTEM: Neomorphism puro. Todos os elementos emergem da mesma superfície
sólida (#d0ccdc). Profundidade criada exclusivamente por sombras duplas.
SEM glassmorphism. SEM gradientes decorativos. SEM bordas visíveis em cards.

MODO CLARO (padrão):
  --bg: #d0ccdc | --sa: #aca8b8 | --sb: #f4f0ff
  Texto primário: #140e20 | Texto secundário: #584870 | Texto terciário: #9080b0
  Acento: #1a9878 (menta) | Glow: rgba(26,152,120,.22)

MODO ESCURO (ativado pelo usuário em Configurações):
  --bg: #252030 | --sa: #181422 | --sb: #322c3e
  Texto primário: #ddd8f0 | Texto secundário: #8878b0 | Texto terciário: #4e4870
  Acento: #30c898 (menta vibrante) | Glow: rgba(48,200,152,.28)

SOMBRAS NEOMÓRFICAS:
  Elevado (cards): -6px -6px 14px #f4f0ff, 6px 6px 14px #aca8b8 | radius: 22px
  Elevado sm (botões): -3px -3px 8px #f4f0ff, 3px 3px 8px #aca8b8 | radius: 12px
  Afundado (inputs): inset -3px -3px 7px #f4f0ff, inset 3px 3px 7px #aca8b8
  Nav ativa: inset -3px -3px 7px #f4f0ff, inset 3px 3px 7px #aca8b8 + cor acento
  CTA: background #1a9878, box-shadow: 0 0 0 2px rgba(26,152,120,.22), radius: 14px

TIPOGRAFIA:
  Interface: DM Sans (300 400 500 600)
  Números e métricas: DM Mono

CORES DE CATEGORIA (invariáveis em todos os temas):
  Hidráulica #2e7bc4 | Elétrica #d4a00a | Gás #e06820 | Construção #b04020
  Jardinagem #2a8c50 | Limpeza #18a0a0 | Pintura #9050c0 | Marcenaria #8a5c28
  Ar-cond. #4898d8 | Segurança #384880 | Tecnologia #20a870 | Reformas #c06840
  Saúde/Beleza #d04080 | Jurídico #485870 | Educação #e08820 | Pet #d85020

---

## 📄 Tela 1 — Landing Page

[INCLUIR BLOCO GLOBAL]

Crie a landing page do ServiçoJá no MODO CLARO PADRÃO (Lavanda Pó, fundo #d0ccdc).

Header neomórfico elevado: logo "ServiçoJá ⚡" com ⚡ em #1a9878, nav com links
"Como funciona", "Categorias", "Seja Profissional", botões "Entrar" (ghost elevado)
e "Cadastrar" (CTA #1a9878).

Hero: headline "Encontre profissionais verificados perto de você", subtítulo em
texto secundário. Barra de busca AFUNDADA (inset) com ícone de lupa e placeholder
"Que serviço você precisa?". 4 category pills elevadas abaixo: 🔧 Hidráulica,
⚡ Elétrica, 🧹 Limpeza, ➕ Ver todas.

3 cards de diferenciais elevados: "IA analisa sua foto", "Match em 80ms",
"LGPD Certificado". Ícone em #1a9878, título e subtítulo.

Grid 4×4 de categorias: cards neomórficos elevados com ícone tintado na cor da
categoria, nome em texto primário, contagem em DM Mono.

Footer com links em texto terciário.

OBRIGATÓRIO: fundo #d0ccdc. Neomorphism puro. DM Sans. DM Mono para números. PT-BR.
Sombra clara: #f4f0ff. Sombra escura: #aca8b8. Sem bordas. Sem gradientes.

---

## 🔍 Tela 2 — Busca e Descoberta

[INCLUIR BLOCO GLOBAL]

Crie a tela "Busca e Descoberta" no MODO CLARO PADRÃO (fundo #d0ccdc).

Layout split desktop: 40% lista esquerda, 60% mapa direita.

Painel esquerdo: barra de busca AFUNDADA. Filtros em pills neomórficas — ativo:
inset + texto #1a9878. Cards de profissional elevados com faixa 3px no topo na
cor da categoria, avatar, nome, especialidade, ★ rating (âmbar) + jobs + tempo
em DM Mono, tags coloridas, preço em DM Mono, botão "Ver perfil".

Painel direito: mapa vetorial fundo #dcd8e8. Pins na cor da categoria. Pin ativo
with halo pulsante menta. Popup neomórfico elevado.

OBRIGATÓRIO: fundo #d0ccdc. Neomorphism puro. DM Sans + DM Mono. PT-BR.
Sombra clara: #f4f0ff. Sombra escura: #aca8b8.

---

## 🤖 Tela 3 — Novo Pedido (Passo 2 de 3)

[INCLUIR BLOCO GLOBAL]

Crie "Novo Pedido — Passo 2 de 3" no MODO CLARO PADRÃO (fundo #d0ccdc).

Stepper: "1 Categoria ✓" (circle preenchido menta) → "2 Descreva" (circle inset
+ borda menta) → "3 Confirmar" (circle elevado neutro).

Card central elevado grande (22px): upload AFUNDADO 200px com ícone câmera menta,
campo texto AFUNDADO multilinha, dois campos AFUNDADOS side-by-side (Localização
+ Urgência).

Card IA elevado abaixo: 🤖 + "Análise IA — resultado" + badge "94% confiança".
3 badges AFUNDADOS por categoria/urgência/complexidade. 3 barras AFUNDADAS (inset)
com preenchimento: Complexidade 55% âmbar, Urgência 85% terracota, Confiança 94% menta.

CTA elevado "Buscar profissionais →" em menta, largura total.

OBRIGATÓRIO: fundo #d0ccdc. Neomorphism puro. DM Sans + DM Mono. PT-BR.
Sombra clara: #f4f0ff. Sombra escura: #aca8b8.

---

## 📊 Tela 4 — Painel do Profissional

[INCLUIR BLOCO GLOBAL]

Crie o "Painel do Profissional" no MODO CLARO PADRÃO (fundo #d0ccdc).

Sidebar 240px elevada: logo, nav vertical ("Início" ativo inset + menta, demais
elevados). Rodapé com avatar circular, nome, "Plano Premium" DM Mono menta, dot
online menta.

3 stat cards elevados: Ganhos R$ 4.280 DM Mono (+12% verde), Lances 7 (+3 hoje
menta), Reputação 4.97 ★ âmbar. Card gráfico elevado com área interna AFUNDADA,
linha menta, eixos DM Mono. Grid 2 colunas: "Próximos trabalhos" (faixa 3px por
categoria + nome + horário DM Mono) e "Reputação granular" (4 barras AFUNDADAS
menta: Pontualidade 98%, Qualidade 95%, Limpeza 92%, Comunicação 97%).

OBRIGATÓRIO: fundo #d0ccdc. Neomorphism puro. DM Sans + DM Mono. PT-BR.
Sombra clara: #f4f0ff. Sombra escura: #aca8b8.

---

## 📱 Tela 5 — Dashboard do Cliente

[INCLUIR BLOCO GLOBAL]

Crie o "Dashboard do Cliente" no MODO CLARO PADRÃO (fundo #d0ccdc). Mobile-first
(max-width 480px).

Header elevado: logo ⚡ menta, "Olá, João!" texto primário, badge notificação.
Nav pills horizontal: "Início" (ativo inset menta), "Pedidos", "Contratos",
"Chat", "Perfil". Pills neomórficas border-radius 50px.

Cards de pedidos elevados: faixa 3px categoria + pill colorida + status pill
("Aberto" verde, "Em andamento" âmbar, "Concluído" cinza) + título + botão "Ver
detalhes".

Atividade recente: ícones emoji elevados 36px + texto bold + detalhe secundário +
timestamp DM Mono. Stats: 3 mini-cards elevados (📋 3 abertos, 💰 R$ 1.240,
⭐ 4.9) com valores DM Mono.

OBRIGATÓRIO: fundo #d0ccdc. Neomorphism puro. DM Sans + DM Mono. PT-BR.
Sombra clara: #f4f0ff. Sombra escura: #aca8b8.

---

## 💬 Tela 6 — Chat Seguro

[INCLUIR BLOCO GLOBAL]

Crie o "Chat Seguro" no MODO CLARO PADRÃO (fundo #d0ccdc). Mobile (max-width 480px).

Header elevado: avatar com badge de categoria colorido, nome primário, especialidade
secundário, dot online menta pulsante, ícones info + chamada.

Banner contrato elevado (faixa menta 3px topo): "Contrato Ativo" menta bold,
"Em andamento", "R$ 270,00" DM Mono, botão inset "Ver contrato".

Área de mensagens AFUNDADA (fundo #c4c0d0): bolhas recebidas AFUNDADAS (4px 16px
16px 16px, texto secundário, esquerda), bolhas enviadas ELEVADAS (16px 4px 16px
16px, tint menta rgba(26,152,120,.08), direita). Timestamps DM Mono terciário.

Input AFUNDADO (border-radius 50px): ícones câmera e clipe elevados, placeholder,
botão circular elevado menta. CTA elevado "Confirmar conclusão e avaliar →" menta.

OBRIGATÓRIO: fundo #d0ccdc. Neomorphism puro. DM Sans + DM Mono. PT-BR.
Sombra clara: #f4f0ff. Sombra escura: #aca8b8.

---

## ⚙️ Tela 7 — Configurações / Aparência

[INCLUIR BLOCO GLOBAL]

Crie "Configurações — Aparência" no MODO CLARO PADRÃO (fundo #d0ccdc).

Header elevado: botão voltar "←" elevado, "Configurações" centralizado.

Seção "Aparência" — card elevado grande: label "APARÊNCIA" 11px uppercase terciário.
Segmented control de tema: container AFUNDADO (inset, 14px radius, padding 4px).
"☀️ Claro" (ativo, padrão): elevado dentro do container, texto menta, peso 600.
"🌙 Escuro" (inativo): flush, texto secundário. Preview ao vivo abaixo: card
elevado médio com miniatura esquemática do modo ativo.
Toggle "Sincronizar com dispositivo": track AFUNDADO + dot elevado (menta quando
ligado). Padrão: desligado.

Seção "Notificações" — card elevado separado: 3 toggles neomórficos.
Seção "Conta" — card elevado separado: rows com "›" terciário.
Botão "Sair da conta" ghost elevado, texto #b04020 (terracota), sem fundo colorido.

OBRIGATÓRIO: fundo #d0ccdc. Neomorphism puro. DM Sans. PT-BR.
Sombra clara: #f4f0ff. Sombra escura: #aca8b8.
Toggles: track afundado + dot elevado. Segmented control: ativo elevado, inativo flush.
