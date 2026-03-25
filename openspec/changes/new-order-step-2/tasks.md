## 1. Navegação e Stepper Neomórfico

- [ ] 1.1 Criar o componente `NeomorphicStepper` com 3 etapas.
- [ ] 1.2 Implementar os estados visuais: concluído (menta + check), ativo (inset + borda menta) e inativo (elevado neutro).
- [ ] 1.3 Integrar o stepper no topo da página de "Novo Pedido".

## 2. Formulário de Descrição do Pedido

- [ ] 2.1 Desenvolver o card central `OrderDescriptionCard` com elevação `elevated-lg`.
- [ ] 2.2 Criar a `UploadArea` afundada (`inset-nm`) com 200px de altura e ícone de câmera menta.
- [ ] 2.3 Implementar o `TextArea` neomórfico afundado para a descrição do problema (6 linhas).
- [ ] 2.4 Adicionar os campos de Localização e Urgência side-by-side utilizando a classe `inset-nm`.

## 3. Painel de Análise por IA

- [ ] 3.1 Desenvolver o card `AIAnalysisCard` com elevação `elevated-sm` secundária.
- [ ] 3.2 Implementar as barras de métricas (Trilha `inset-nm` + Preenchimento colorido).
- [ ] 3.3 Configurar as cores das barras: Âmbar (Complexidade), Terracota (Urgência), Menta (Confiança).
- [ ] 3.4 Implementar os badges de categoria identificada com fundo translúcido `rgba(cor, 0.12)`.
- [ ] 3.5 Garantir que os rótulos e valores de porcentagem utilizem a fonte `DM Mono`.

## 4. Integração e CTA

- [ ] 4.1 Montar o layout da página combinando o Card Central e o Card de IA em uma coluna centralizada.
- [ ] 4.2 Adicionar o botão CTA "Buscar profissionais →" em Menta com largura total e brilho de acento.
- [ ] 4.3 Implementar a lógica de transição visual do formulário para o estado de "analisando" (ex: skeleton ou loading neomórfico).

## 5. Revisão Visual e UX

- [ ] 5.1 Verificar a consistência das sombras em todos os níveis de elevação e profundidade.
- [ ] 5.2 Testar a interação de upload e o feedback visual imediato das barras de métrica.
- [ ] 5.3 Validar a acessibilidade das cores das categorias identificadas.
