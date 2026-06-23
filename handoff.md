# 🚀 Guia de Implantação e Handoff para Terminar em Casa (ServiçoJá)

Este documento contém todas as informações e os passos necessários para você salvar o seu trabalho atual na faculdade/laboratório e concluir a implantação e os testes da aplicação do seu próprio computador em casa.

---

## 📌 PARTE 0: SALVAR O SEU TRABALHO AGORA (Urgente!)
Como você está em um computador do laboratório (`/home/alunos`), se você fechar a sessão ou desligar o computador, **todas as suas modificações locais serão perdidas**.
Antes de sair, abra o terminal no diretório `/home/alunos/Desktop/www/dasdasd/Projeto_ProgWeb` e execute os seguintes comandos para subir todas as alterações para o seu repositório Git remoto (GitHub/GitLab):

```bash
# 1. Adicionar todas as alterações locais (start.sh, botões de voltar nos perfis, novos scripts de teste, etc.)
git add .

# 2. Fazer o commit
git commit -m "feat: configuração de deploy em container, botões de navegação de perfil e scripts auxiliares"

# 3. Enviar as alterações para o repositório remoto
git push origin master
```

---

## 🐳 PARTE 1: IMAGEM DOCKER (Construção e Envio)

Você precisará da imagem Docker do backend contendo a otimização que junta a **API** e o **Worker** em um único container para economizar no plano do Render. Você pode fazer isso direto no laboratório (antes de ir) ou fazer em casa depois de clonar o repositório.

### Opção A: Gerar e enviar a imagem agora no laboratório (Recomendado)
Se você já estiver logado no Docker Hub nesta máquina, execute os seguintes comandos no terminal:
```bash
# 1. Faça o login na sua conta do Docker Hub (se ainda não fez)
docker login

# 2. Taggear a imagem local para o seu repositório do Docker Hub
# (Substitua 'tagname' por algo como 'latest' ou 'v1')
docker tag chrissoassis/servicoja:latest chrissoassis/servicoja:tagname

# 3. Enviar para o Docker Hub
docker push chrissoassis/servicoja:tagname
```

### Opção B: Clonar o repositório e gerar a imagem em casa
Se preferir compilar tudo em casa, siga estes comandos no seu computador doméstico após clonar o repositório:
```bash
# 1. Vá para a raiz do projeto clonado
cd Projeto_ProgWeb

# 2. Construir a imagem Docker do backend localmente
docker build -t chrissoassis/servicoja:latest ./apps/api

# 3. Fazer login no Docker Hub
docker login

# 4. Criar a tag da imagem
docker tag chrissoassis/servicoja:latest chrissoassis/servicoja:tagname

# 5. Enviar a imagem
docker push chrissoassis/servicoja:tagname
```

---

## 🗄️ PARTE 2: BANCO DE DADOS (Neon Postgres)

O banco de dados Neon já está configurado com a estrutura e os dados iniciais. A URL de conexão direta é:
```text
postgresql://neondb_owner:npg_vKT4ulJE3aGF@ep-weathered-pond-acxkymxt-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

> [!IMPORTANT]
> **Ajuste para SQLAlchemy e Asyncpg:**
> No backend do FastAPI, o driver `asyncpg` não reconhece o parâmetro `sslmode=require`. Por isso, ao configurar a variável de ambiente `DATABASE_URL` no Render, utilize o formato assíncrono exato abaixo:
> `postgresql+asyncpg://neondb_owner:npg_vKT4ulJE3aGF@ep-weathered-pond-acxkymxt-pooler.sa-east-1.aws.neon.tech/neondb?ssl=require`

---

## ☁️ PARTE 3: IMPLANTAÇÃO DO BACKEND NO RENDER (Gratuito)

No painel do [Render](https://dashboard.render.com/):

### A. Criar o Redis Gratuito (Key Value)
1. Clique no botão **New** (ou no topo direito) e selecione **Key Value** (antigo Redis).
2. Configure:
   * **Name:** `servicoja-redis`
   * **Region:** Selecione a mesma região que você escolheu no Neon (ex: `sa-east-1` ou a mais próxima do Brasil).
3. Após criar, vá até a página do Redis criado e copie o campo **Internal Redis Connection String** (será algo como `redis://red-xxxxxxxxxx:6379`).

### B. Criar o Web Service da API
1. Clique em **New** e selecione **Web Service**.
2. Escolha a opção **Deploy an existing image from a registry** (localizada logo abaixo do campo de busca de repositório Git).
3. No campo da imagem, insira o seu repositório Docker Hub completo:
   `docker.io/chrissoassis/servicoja:tagname` *(substitua pela sua imagem e tag real)*.
4. Clique em **Next**.
5. Configure:
   * **Name:** `servicoja-api`
   * **Region:** A mesma região do Redis e do Neon.
   * **Instance Type:** `Free` (Gratuito).
6. Expanda a seção **Advanced** e adicione as seguintes **Environment Variables**:

| Chave | Valor | Observação |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://neondb_owner:npg_vKT4ulJE3aGF@ep-weathered-pond-acxkymxt-pooler.sa-east-1.aws.neon.tech/neondb?ssl=require` | Conexão com o Neon (formato assíncrono). |
| `REDIS_URL` | *Colar a string copiada do passo anterior* | Ex: `redis://red-xxxxxxxxxx:6379` |
| `JWT_SECRET` | *Uma string longa e secreta de sua escolha* | Ex: `meu_segredo_super_seguro_e_longo_para_jwt` |
| `ENVIRONMENT` | `production` | Modo produção da API |
| `LOG_LEVEL` | `info` | Nível de logs mínimos |
| `GOOGLE_API_KEY` | *Sua chave da API do Gemini* | Chave de acesso à IA para análise de fotos e pedidos |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Modelo de IA para classificação |

7. Role até o fim da página e clique em **Create Web Service**.
8. *Nota:* O Render iniciará o container. O nosso script modificado `start.sh` subirá tanto o servidor FastAPI (`uvicorn`) quanto o processador de tarefas em segundo plano (`arq`) de forma concorrente no mesmo container gratuito!

---

## 🎨 PARTE 4: IMPLANTAÇÃO DO FRONTEND NO VERCEL (Gratuito)

No painel do [Vercel](https://vercel.com/):

1. Clique em **Add New > Project** e faça login com a sua conta do GitHub/GitLab.
2. Importe o repositório do seu projeto `Projeto_ProgWeb`.
3. Na tela de configuração de build, ajuste as seguintes opções:
   * **Framework Preset:** Selecione `Next.js`.
   * **Root Directory:** Clique em Edit e aponte para `apps/web`.
   * **Build Command:** Deixe o padrão (`npm run build`).
   * **Output Directory:** Deixe o padrão (`.next`).
4. Abra a seção **Environment Variables** e adicione:
   * `NEXT_PUBLIC_API_URL` = `https://servicoja-api.onrender.com/api/v1` *(Substitua pelo endereço HTTPS público que o Render gerar para a sua API após o deploy iniciar)*.
   * `API_INTERNAL_URL` = `https://servicoja-api.onrender.com/api/v1` *(Substitua pelo mesmo endereço público do Render)*.
5. Clique em **Deploy**. O Vercel fará a compilação estática do Next.js e gerará um link público de acesso (ex: `servicoja.vercel.app`).

---

## 🧪 PARTE 5: FLUXO DE TESTES EM CASA
Quando ambos os deploys estiverem finalizados, você poderá validar o sistema completo:

1. Acesse a URL do frontend gerada pela Vercel.
2. Acesse a página de Login e entre com uma das contas de teste padrão já criadas no banco do Neon:
   * **Cliente:** `cliente.teste@ficticio.com` | Senha: `senha123`
   * **Profissional:** `profissional.teste@ficticio.com` | Senha: `senha123`
3. **Validar Navegação de Perfil:** Entre no painel e vá na página de visualização de perfil. Clique no botão de voltar (ícone de seta azul com efeito hover moderno que adicionamos no canto superior esquerdo) e verifique se você é redirecionado corretamente ao painel correspondente (Client ou Pro).
4. **Validar Worker & IA:** Entre como Cliente, faça um novo pedido de serviço anexando uma foto e clique em salvar.
   * O fluxo enviará o pedido ao backend.
   * O Worker rodando em background no container da API processará a foto usando a API do Gemini.
   * Aguarde alguns segundos e atualize a tela ou visualize o pedido para ver as tags sugeridas, urgência e nível de complexidade detectados pela IA.

---

Boa viagem de volta para casa! Qualquer dúvida, basta rodar o projeto localmente para testar usando o comando `docker compose up --build`.