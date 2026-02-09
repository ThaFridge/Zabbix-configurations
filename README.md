# Zabbix Configurations

Centrale repository voor Zabbix monitoring configuraties, templates, discovery rules, alerts en dashboards.

## Projectstructuur

```
Zabbix-configurations/
├── docs/                  # Kennisbasis & documentatie
│   ├── 01-zabbix-overview.md      # Zabbix overzicht & architectuur
│   ├── 02-templates.md            # Templates: structuur & best practices
│   ├── 03-discovery.md            # Discovery rules (Network & LLD)
│   ├── 04-triggers-alerts.md      # Triggers, severity & alerting
│   ├── 05-dashboards.md           # Dashboards & visualisatie
│   ├── 06-api.md                  # Zabbix API & automatisering
│   └── 07-macros.md               # Macro's & variabelen
├── templates/             # Zabbix templates (YAML export)
├── discovery/             # Custom discovery scripts & regels
├── alerts/                # Alert configuraties & media types
├── dashboards/            # Dashboard exports & configuraties
├── scripts/               # Hulpscripts (preprocessing, external checks)
└── api-examples/          # API automatisering scripts
```

## Zabbix Versies

| Versie | Type | Status |
|--------|------|--------|
| **7.0** | LTS | Huidige stabiele versie (aanbevolen voor productie) |
| 7.2 / 7.4 | Feature release | Tussenreleases met nieuwe features |
| **8.0** | LTS | Verwacht Q2 2026 - OpenTelemetry, Complex Event Processing, Mobile App |

## Snelstart

1. Lees de docs in `docs/` voor de kennisbasis
2. Templates staan klaar in `templates/` (YAML formaat, importeerbaar in Zabbix)
3. Custom discovery scripts in `discovery/`
4. API voorbeelden in `api-examples/`

## Conventies

- Templates worden geexporteerd in **YAML** formaat (Zabbix standaard sinds 5.4+)
- Bestanden zijn UTF-8 encoded
- Naming convention: `kebab-case` voor bestanden, `Template Naam` voor Zabbix template namen
