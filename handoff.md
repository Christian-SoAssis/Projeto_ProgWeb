Handoff de Transição
Este documento detalha o estado atual do projeto, o progresso feito na funcionalidade de Payout & Agendamento de Disponibilidade de Profissionais, os problemas identificados nos testes e os passos para a próxima IA retomar o trabalho de forma eficiente.

1. Contexto e Objetivo
O objetivo da tarefa é implementar as configurações de recebimento Pix e Grade de Disponibilidade para usuários profissionais (pro), além de um mecanismo de agendamento de slots virtuais de atendimento com margem de deslocamento/travel buffer de 1 hora.

2. Progresso Realizado
Backend (API)
Modelagem e Migrações (Alembic):
Mesclada a branch mercadopago1 e executadas as migrações (incluindo a revisão 019 do Mercado Pago e a revisão ae8089c9422c das novas tabelas).
Tabela professional_pix_keys (
professional_pix_key.py
) criada com criptografia/mascaramento de dados para compliance com LGPD.
Tabela professional_availabilities (
professional_availability.py
) criada para armazenar o calendário de horários de trabalho.
Adicionados os campos de data de agendamento (scheduled_start, scheduled_end) e confirmação de pagamento (payment_confirmed_at) na tabela de contratos.
Endpoints /api/v1:
GET/POST /auth/professional/pix para gerenciar a chave Pix com mascaramento em tempo de serialização (LGPD).
GET/POST /auth/professional/availability para gerenciar a agenda semanal de trabalho do profissional.
GET /professionals/{id}/available-slots para buscar slots de atendimento gerados dinamicamente com 1h de travel buffer em relação a contratos ativos (active e payment_confirmed).
Frontend (Next.js)
Telas de Configuração (Neomorphic UI):
Implementada a tela de Dados de Payout (Pix) em 
payout/page.tsx
.
Implementada a tela de Grade de Horários Semanais em 
availability/page.tsx
.
Integração no Stepper de Contratação:
Atualizada a página de detalhes de bids do cliente (
page.tsx
) para abrir uma modal de agendamento de data e horário ao aceitar um bid, carregando dinamicamente os slots livres calculados pela API.
3. Ponto de Parada & Erros Identificados
Ao executarmos a suíte de testes (pytest tests/), identificamos uma quebra sistemática de contratos nos testes devido a uma incoerência na arquitetura limpa (Mappers e Entidades de Domínio vs Modelos de Banco de Dados) introduzida em commits anteriores na branch master:

O Problema no Modelo/Mapper de Contratos (Contract)
Model do Banco de Dados (ContractModel):
Possui a coluna started_at (Column(DateTime(timezone=True))) e completed_at, mas não possui created_at nem updated_at.
Entidade de Domínio (Contract / ContractEntity):
Possui created_at e updated_at como propriedades dataclass, mas não possui started_at.
Mapeador (ContractMapper em mappers.py):
Em to_entity, tenta ler model.created_at e model.updated_at (causando AttributeError: 'Contract' object has no attribute 'created_at').
Em to_model, passa created_at=entity.created_at e updated_at=entity.updated_at para o construtor do modelo do banco, gerando TypeError.
Use Case (UpdateBidUseCase em update_bid_use_case.py):
Instancia a entidade de domínio Contract passando started_at=datetime.now(timezone.utc) (linha 71), gerando TypeError: Contract.__init__() got an unexpected keyword argument 'started_at' porque a entidade dataclass espera created_at e não tem started_at.
4. Próximos Passos Recomendados
Passo 1: Alinhamento e Correção da Entidade / Mapper
Você precisará sincronizar os atributos do domínio com o banco:

Altere apps/api/app/infrastructure/database/mappers.py (
mappers.py
):
No to_entity: mapeie created_at=model.started_at e updated_at=None (ou o mesmo valor).
No to_model: mapeie started_at=entity.created_at.
Altere apps/api/app/application/use_cases/update_bid_use_case.py (
update_bid_use_case.py
) na instanciação de Contract (linha 64-74):
Substitua started_at=datetime.now(timezone.utc) por created_at=datetime.now(timezone.utc).
Passo 2: Escrever Testes Unitários e de Integração para Pix e Disponibilidade
Crie o arquivo apps/api/tests/v1/test_availability.py (
test_availability.py
) para validar:

Validação do Schema Pix (ProfessionalPixKeyCreate):
Chaves CPF/CNPJ limpas (apenas números).
Telefones com código do país/DDD.
Formatos UUID inválidos vs válidos.
Endpoints de Agendamento:
Registro de chave Pix e recebimento mascarado (compliance LGPD).
Cadastro de disponibilidade semanal.
Cálculo de Slots (GET /api/v1/professionals/{id}/available-slots):
Geração de slots no dia disponível com zero conflitos.
Geração de slots com conflito de contrato ativo (comprovando que o travel buffer de 1 hora remove os slots corretos).
Passo 3: Build do Frontend
Certifique-se de validar se a compilação do Next.js está íntegra executando npm run build dentro do diretório apps/web.