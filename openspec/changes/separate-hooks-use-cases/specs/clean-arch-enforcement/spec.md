## ADDED Requirements

### Requirement: Desacoplamento Absoluto entre Hooks e Casos de Uso
A lógica de negócio e orquestração de aplicação SHALL ser implementada exclusivamente em classes puras de Casos de Uso. Os Hooks do React deverão servir apenas como pontos de acesso à interface do usuário ou gerenciadores de estado de renderização.

#### Scenario: Hook de Autenticação como Simples Acessor
- **WHEN** o hook `useAuth` for consumido por qualquer página ou componente
- **THEN** ele deve atuar puramente como acessor de contexto React (`useContext`), delegando todas as chamadas de método aos Casos de Uso correspondentes instanciados no container

### Requirement: Documentação de Arquitetura com Diagrama Mermaid
O repositório SHALL conter um arquivo `ARCHITECTURE.md` na raiz do módulo `apps/web/` explicando a arquitetura adotada.

#### Scenario: Visualização do Diagrama no GitHub / IDE
- **WHEN** a documentação `ARCHITECTURE.md` for aberta na IDE ou no GitHub
- **THEN** o usuário deve ver um diagrama Mermaid com os 4 círculos concêntricos e a seta de dependências apontando exclusivamente de fora para dentro
