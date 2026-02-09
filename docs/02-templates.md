# Templates: Structuur & Best Practices

## Wat is een Template?

Een template is een herbruikbare set van monitoring-configuraties die je kunt toepassen op meerdere hosts. Templates bevatten:

- **Items** (metrics die verzameld worden)
- **Triggers** (condities die problemen detecteren)
- **Graphs** (visualisaties)
- **Dashboards** (overzichtspagina's)
- **Discovery rules** (automatische detectie)
- **Web scenarios** (website monitoring)
- **Macros** (variabelen)

## Template Hierarchie (Nesting/Linking)

```text
Template OS Linux by Zabbix agent
├── Template Module Linux CPU by Zabbix agent
├── Template Module Linux memory by Zabbix agent
├── Template Module Linux filesystems by Zabbix agent
├── Template Module Linux network interfaces by Zabbix agent
└── Template Module Linux block devices by Zabbix agent
```

Templates kunnen aan andere templates gelinkt worden (nesting). Dit maakt modulaire opbouw mogelijk.

## Export Formaten

| Formaat | Extensie | Standaard |
| ------- | -------- | --------- |
| YAML | .yaml / .yml | Ja (sinds 5.4) |
| XML | .xml | Legacy |
| JSON | .json | Alternatief |

**Let op**: Import vereist UTF-8 encoding (met of zonder BOM).

## Template YAML Structuur

```yaml
zabbix_export:
  version: '7.0'
  template_groups:
    - uuid: abc123
      name: 'Templates/Custom'
  templates:
    - uuid: def456
      template: 'Custom Linux Monitoring'
      name: 'Custom Linux Monitoring'
      description: 'Aangepaste Linux monitoring template'
      groups:
        - name: 'Templates/Custom'
      items:
        - uuid: ghi789
          name: 'CPU utilization'
          type: ZABBIX_ACTIVE
          key: 'system.cpu.util'
          delay: '1m'
          value_type: FLOAT
          units: '%'
          description: 'CPU gebruik percentage'
          tags:
            - tag: component
              value: cpu
          triggers:
            - uuid: jkl012
              expression: 'min(/Custom Linux Monitoring/system.cpu.util,5m)>90'
              name: 'High CPU utilization (over 90% for 5m)'
              priority: WARNING
      discovery_rules:
        - uuid: mno345
          name: 'Filesystem discovery'
          type: ZABBIX_ACTIVE
          key: 'vfs.fs.discovery'
          delay: '1h'
          filter:
            conditions:
              - macro: '{#FSTYPE}'
                value: '^(ext4|xfs|btrfs)$'
                formulaid: A
          item_prototypes:
            - uuid: pqr678
              name: 'Free disk space on {#FSNAME}'
              type: ZABBIX_ACTIVE
              key: 'vfs.fs.size[{#FSNAME},free]'
              delay: '5m'
              value_type: UNSIGNED
              units: B
      macros:
        - macro: '{$CPU.UTIL.CRIT}'
          value: '90'
          description: 'CPU critical threshold'
```

## Template Componenten in Detail

### Items
- Definieer WAT er gemonitord wordt
- Elk item heeft een unieke `key` (bv. `system.cpu.util`)
- Types: Zabbix Agent, SNMP, HTTP Agent, Calculated, Dependent, etc.

### Triggers
- Definieer WANNEER er een probleem is
- Gebruikt expressions met functies: `min()`, `max()`, `avg()`, `last()`, `diff()`, etc.
- Severity levels: Not classified, Information, Warning, Average, High, Disaster

### Discovery Rules
- Automatisch items/triggers/graphs aanmaken op basis van wat er gevonden wordt
- Bevat item prototypes, trigger prototypes, graph prototypes

### Macros
- Variabelen die je per host kunt overschrijven
- Syntax: `{$MACRO_NAAM}`
- Ideaal voor drempelwaarden die per host anders kunnen zijn

## Best Practices

1. **Modulair opbouwen**: Maak kleine, gerichte templates en link ze
2. **Macros voor drempelwaarden**: Gebruik `{$CPU.UTIL.CRIT}` i.p.v. hardcoded waarden
3. **Tags gebruiken**: Tag items en triggers voor filtering en correlatie
4. **Naming conventions**:
   - Template naam: `Template [Type] [Wat] by [Methode]`
   - Voorbeeld: `Template OS Linux by Zabbix agent`
5. **Documenteer**: Vul descriptions in voor items, triggers en macros
6. **Versiebeheer**: Exporteer templates als YAML en sla op in Git
7. **Test eerst**: Test templates op een test-host voordat je ze breed uitrolt

## Import/Export

### Exporteren (GUI)
1. Ga naar Data collection > Templates
2. Selecteer template(s)
3. Klik "Export" (standaard YAML)

### Importeren (GUI)
1. Ga naar Data collection > Templates
2. Klik "Import" rechtsboven
3. Selecteer bestand en configureer import regels

### Exporteren (API)
```bash
curl -s -X POST http://zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "configuration.export",
    "params": {
      "options": {
        "templates": ["10001"]
      },
      "format": "yaml"
    },
    "auth": "TOKEN",
    "id": 1
  }'
```

## Bronnen

- [Zabbix Templates Documentatie](https://www.zabbix.com/documentation/current/en/manual/xml_export_import/templates)
- [Zabbix Template Guidelines](https://www.zabbix.com/documentation/guidelines/en/thosts/configuration)
- [Template Converter Tool](https://github.com/monitoringartist/zabbix-template-converter)
