## 1. Estrutura de Layout Split-Screen

- [ ] 1.1 Criar a página de Busca (`/busca`) com container principal dividido em 40% (lista) e 60% (mapa) no Desktop.
- [ ] 1.2 Implementar o comportamento de scroll independente para o painel de resultados (lista).
- [ ] 1.3 Garantir que o painel do mapa permaneça fixo ou utilize `sticky` durante a rolagem no desktop.
- [ ] 1.4 Adaptar o layout para dispositivos móveis (painéis empilhados ou troca via tab).

## 2. Painel de Busca e Filtros Neomórficos

- [ ] 2.1 Implementar o componente `InsetSearchBar` com a classe `inset-nm` e ícone de lupa.
- [ ] 2.2 Desenvolver o carrossel horizontal de filtros usando pills neomórficas (`Pill`).
- [ ] 2.3 Implementar a lógica de estado para os filtros (transição `elevated-sm` -> `inset-nm` ao selecionar).
- [ ] 2.4 Vincular os filtros à lógica de listagem (exibindo apenas categorias selecionadas).

## 3. Cards de Profissionais e Listagem

- [ ] 3.1 Desenvolver o componente `ProfessionalCard` com elevação `elevated-lg` e borda superior de 3px na cor da categoria.
- [ ] 3.2 Implementar o avatar neomórfico elevado com emoji e o badge de categoria translúcido.
- [ ] 3.3 Formatar as estatísticas (Rating, Jobs, Tempo) usando a fonte `DM Mono` e cores específicas.
- [ ] 3.4 Adicionar o botão "Ver perfil" com estilo ghost elevado.

## 4. Integração de Mapa Vetorial

- [ ] 4.1 Configurar o provedor de mapa (ex: Mapbox) com o estilo visual customizado (fundo `#dcd8e8`).
- [ ] 4.2 Implementar pins personalizados na cor da categoria do profissional.
- [ ] 4.3 Desenvolver o popup de pin com estilo neomórfico elevado contendo resumo do profissional.
- [ ] 4.4 Implementar o efeito de halo pulsante menta para o pin do profissional selecionado na lista.

## 5. Polimento e Testes

- [ ] 5.1 Realizar auditoria visual de Neomorfismo: verificar se todas as sombras seguem a regra `--sb` / `--sa`.
- [ ] 5.2 Testar a performance da renderização do mapa com múltiplos pins (> 50).
- [ ] 5.3 Validar a acessibilidade dos textos menta sobre o fundo lavanda.
