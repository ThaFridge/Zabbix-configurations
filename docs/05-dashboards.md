# Dashboards & Visualisatie

## Dashboard Overzicht

Dashboards zijn de visuele kern van Zabbix. Ze combineren widgets tot overzichten voor verschillende doelgroepen (operators, managers, engineers).

## Widget Types (Zabbix 7.0)

### Data Weergave
| Widget | Beschrijving |
| ------ | ------------ |
| **Graph** | Lijn/stacked/pie grafieken van item data |
| **Graph (classic)** | Traditionele Zabbix grafieken |
| **Plain text** | Ruwe item waarden als tekst |
| **Item value** | Enkele waarde groot weergegeven |
| **Gauge** | Meter/gauge weergave van een waarde |
| **Top hosts** | Ranglijst van hosts op basis van item waarden |
| **Data overview** | Tabel met item waarden voor meerdere hosts |

### Problemen & Status
| Widget | Beschrijving |
| ------ | ------------ |
| **Problems** | Lijst van actieve problemen |
| **Problem hosts** | Hosts met actieve problemen |
| **Trigger overview** | Matrix van trigger statussen per host |
| **Host availability** | Beschikbaarheid percentage van hosts |
| **SLA report** | Service Level Agreement rapportage |

### Infrastructuur
| Widget | Beschrijving |
| ------ | ------------ |
| **Map** | Netwerk map weergave |
| **Geomap** | Geografische kaart met host locaties |
| **Host navigator** | Navigatie door host groepen |
| **Discovery status** | Status van network discovery |

### Overig
| Widget | Beschrijving |
| ------ | ------------ |
| **Clock** | Klok (server/local tijd) |
| **URL** | Embedded webpagina |
| **Text** | Statische tekst / markdown |
| **Action log** | Log van uitgevoerde acties |
| **System information** | Zabbix server status |

## Dashboard Structuur

```yaml
# Dashboard export structuur
zabbix_export:
  version: '7.0'
  dashboards:
    - uuid: abc123
      name: 'Linux Server Overview'
      auto_start: 'YES'
      pages:
        - name: 'Overview'
          widgets:
            - type: problems
              name: 'Active Problems'
              x: '0'
              y: '0'
              width: '12'
              height: '5'
              fields:
                - type: INTEGER
                  name: severities
                  value: '3'    # Warning en hoger
            - type: graph
              name: 'CPU Usage'
              x: '0'
              y: '5'
              width: '6'
              height: '4'
              fields:
                - type: ITEM
                  name: itemid
                  value:
                    host: '{HOST.HOST}'
                    key: system.cpu.util
        - name: 'Disk & Memory'
          widgets:
            - type: gauge
              name: 'Memory Usage'
              width: '4'
              height: '4'
```

## Widget Data Sharing

Widgets kunnen data delen met andere widgets:
- **Host groups**: Filter andere widgets op hostgroep
- **Hosts**: Filter op specifieke host
- **Time period**: Deel tijdsperiode tussen widgets
- Configureer via "Data source" in widget instellingen

## Template Dashboards

Sinds Zabbix 7.0 ondersteunen template dashboards alle widget types. Template dashboards worden automatisch beschikbaar op elke host die de template gebruikt.

```text
Template "Linux by Zabbix agent"
└── Dashboard "Linux Overview"
    ├── Widget: CPU Graph
    ├── Widget: Memory Gauge
    ├── Widget: Disk Usage Top
    └── Widget: Active Problems
```

## Dashboard Ontwerp Best Practices

### Layout Principes
1. **Belangrijkste info linksboven**: Oog scant van links naar rechts
2. **Problemen altijd zichtbaar**: Problems widget prominent plaatsen
3. **Logische groepering**: Gerelateerde widgets bij elkaar
4. **Niet te vol**: Max 6-8 widgets per pagina, gebruik meerdere pagina's

### Voor Verschillende Doelgroepen

**Operations Dashboard**:
- Problems widget (gefilterd op severity >= Warning)
- Host availability
- Trigger overview
- Map van infrastructuur

**Performance Dashboard**:
- CPU/Memory/Disk grafieken
- Top hosts (CPU usage)
- Network traffic graphs

**Management Dashboard**:
- SLA report
- Problem host count (gauge)
- Availability percentages
- Geomap met locaties

### Tips
- Gebruik **auto-refresh** (standaard 30s)
- Gebruik **meerdere pagina's** met auto-rotate voor NOC schermen
- Gebruik **tags** om widgets te filteren
- Maak **template dashboards** voor herbruikbaarheid

## Bronnen

- [Dashboard Widgets](https://www.zabbix.com/documentation/7.0/en/manual/web_interface/frontend_sections/dashboards/widgets)
- [Dashboard Configuratie](https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/dashboards)
