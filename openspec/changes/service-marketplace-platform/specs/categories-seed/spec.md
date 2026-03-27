# Spec: categories-seed

> Lista oficial das 16 categorias iniciais do ServiçoJá v1 com cores atribuídas.

---

## Categorias Iniciais (v1)

| # | Nome | Slug | Cor (Hex) | Descrição |
|---|------|------|-----------|-----------|
| 1 | Hidráulica | `hidraulica` | `#2e7bc4` | Encanamento, vazamentos, instalações |
| 2 | Elétrica | `eletrica` | `#d4a00a` | Instalações elétricas, reparos |
| 3 | Gás | `gas` | `#e06820` | Instalação e manutenção de gás |
| 4 | Construção | `construcao` | `#b04020` | Obras, alvenaria, reformas estruturais |
| 5 | Jardinagem | `jardinagem` | `#2a8c50` | Paisagismo, poda, manutenção de jardins |
| 6 | Limpeza | `limpeza` | `#18a0a0` | Limpeza residencial e comercial |
| 7 | Pintura | `pintura` | `#9050c0` | Pintura interna e externa |
| 8 | Marcenaria | `marcenaria` | `#8a5c28` | Móveis sob medida, carpintaria |
| 9 | Ar-condicionado | `ar-condicionado` | `#4898d8` | Instalação e manutenção de climatização |
| 10 | Segurança | `seguranca` | `#384880` | Câmeras, alarmes, controle de acesso |
| 11 | Tecnologia | `tecnologia` | `#20a870` | Informática, redes, suporte técnico |
| 12 | Reformas | `reformas` | `#c06840` | Renovações completas, design de interiores |
| 13 | Saúde/Beleza | `saude-beleza` | `#d04080` | Serviços estéticos e terapêuticos |
| 14 | Jurídico | `juridico` | `#485870` | Consultoria jurídica, documentação |
| 15 | Educação | `educacao` | `#e08820` | Aulas particulares, cursos, tutoria |
| 16 | Pets | `pets` | `#d85020` | Banho, tosa, veterinária, adestramento |

## Observações

- **Cores invariantes**: Definidas no design system neomórfico, não alterar sem aprovação de UX
- **Sistema escalável**: Novas categorias podem ser adicionadas via painel admin no futuro
- **Hierarquia**: Suporte a subcategorias via `parent_id` (não usado na v1, reservado para v2)
- **Soft delete**: Usar `is_active=false` ao invés de exclusão física

## Migration Seed Script (Referência)

```python
# apps/api/scripts/seed_categories.py (a implementar no futuro)
INITIAL_CATEGORIES = [
    {"name": "Hidráulica",      "slug": "hidraulica",      "color": "#2e7bc4", "sort_order": 1},
    {"name": "Elétrica",        "slug": "eletrica",        "color": "#d4a00a", "sort_order": 2},
    {"name": "Gás",             "slug": "gas",             "color": "#e06820", "sort_order": 3},
    {"name": "Construção",      "slug": "construcao",      "color": "#b04020", "sort_order": 4},
    {"name": "Jardinagem",      "slug": "jardinagem",      "color": "#2a8c50", "sort_order": 5},
    {"name": "Limpeza",         "slug": "limpeza",         "color": "#18a0a0", "sort_order": 6},
    {"name": "Pintura",         "slug": "pintura",         "color": "#9050c0", "sort_order": 7},
    {"name": "Marcenaria",      "slug": "marcenaria",      "color": "#8a5c28", "sort_order": 8},
    {"name": "Ar-condicionado", "slug": "ar-condicionado", "color": "#4898d8", "sort_order": 9},
    {"name": "Segurança",       "slug": "seguranca",       "color": "#384880", "sort_order": 10},
    {"name": "Tecnologia",      "slug": "tecnologia",      "color": "#20a870", "sort_order": 11},
    {"name": "Reformas",        "slug": "reformas",        "color": "#c06840", "sort_order": 12},
    {"name": "Saúde/Beleza",    "slug": "saude-beleza",    "color": "#d04080", "sort_order": 13},
    {"name": "Jurídico",        "slug": "juridico",        "color": "#485870", "sort_order": 14},
    {"name": "Educação",        "slug": "educacao",        "color": "#e08820", "sort_order": 15},
    {"name": "Pets",            "slug": "pets",            "color": "#d85020", "sort_order": 16},
]
```
