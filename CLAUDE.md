# Zabbix Configurations Project

## Doel
Repository voor het ontwikkelen, documenteren en beheren van Zabbix monitoring configuraties.
We werken samen aan templates, discovery rules, alerts, dashboards en automatisering.

## Taal
Documentatie en communicatie in het **Nederlands**. Code comments in het Engels.

## Projectstructuur
- `docs/` - Kennisbasis (01-07, genummerd per onderwerp)
- `templates/` - Zabbix templates in YAML formaat
- `discovery/` - Custom LLD scripts en configuraties
- `alerts/` - Alert configuraties en webhook definities
- `dashboards/` - Dashboard exports
- `scripts/` - Hulpscripts (preprocessing, external checks)
- `api-examples/` - Python/bash API automatisering scripts

## Conventies
- Templates: YAML formaat (Zabbix standaard)
- Bestandsnamen: kebab-case
- Template namen: "Template [Type] [Wat] by [Methode]"
- Macro naming: `{$COMPONENT.METRIC.TYPE}` (dots als separator)
- Encoding: UTF-8
- Trigger severity: Volg best practices uit docs/04-triggers-alerts.md

## Omgeving
- Zabbix versie: **7.2 / 7.4** (feature release)
- Ervaring: **Beginner** - alles stap voor stap uitleggen
- Monitoring targets:
  - Linux servers
  - Windows servers
  - Netwerkapparatuur (SNMP)
  - Applicaties & Services (databases, webservers, Docker, etc.)
- Eerste prioriteit: **Discovery rules**

## Werkwijze
- Gebruiker is beginner: leg concepten helder uit met voorbeelden
- Nederlands voor documentatie en uitleg
- Stap voor stap opbouwen, niet te veel tegelijk
- Praktische voorbeelden geven die direct bruikbaar zijn
