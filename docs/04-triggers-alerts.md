# Triggers, Severity & Alerting

## Triggers

Een trigger is een logische expressie die de status van verzamelde data evalueert. Wanneer de conditie waar wordt, ontstaat er een **probleem**.

### Trigger Expression Syntax

```text
functie(/host/key,parameters) operator waarde
```

Voorbeelden:
```text
# CPU hoger dan 90% gedurende 5 minuten
min(/Linux server/system.cpu.util,5m) > 90

# Minder dan 10% vrije diskruimte
last(/Linux server/vfs.fs.size[/,pfree]) < 10

# Host is onbereikbaar (geen data voor 5 minuten)
nodata(/Linux server/agent.ping,5m) = 1

# Meer dan 100 processen
last(/Linux server/proc.num) > 100

# Verandering in configuratie bestand
diff(/Linux server/vfs.file.cksum[/etc/passwd]) = 1
```

### Veelgebruikte Trigger Functies

| Functie | Beschrijving | Voorbeeld |
| ------- | ------------ | --------- |
| `last()` | Laatste waarde | `last(/host/key) > 100` |
| `min()` | Minimum over periode | `min(/host/key,5m) > 90` |
| `max()` | Maximum over periode | `max(/host/key,1h) > 95` |
| `avg()` | Gemiddelde over periode | `avg(/host/key,10m) > 80` |
| `diff()` | Verschil met vorige waarde | `diff(/host/key) = 1` |
| `change()` | Verschil (numeriek) | `change(/host/key) > 10` |
| `nodata()` | Geen data ontvangen | `nodata(/host/key,5m) = 1` |
| `count()` | Aantal waarden in periode | `count(/host/key,1h,"gt","100") > 5` |
| `trend_avg()` | Trend gemiddelde | `trend_avg(/host/key,1d:now/d) > 80` |
| `forecast()` | Voorspelling | `forecast(/host/key,1h,30m) > 95` |

### Trigger Dependencies

Voorkom alert-storms door afhankelijkheden te defini&euml;ren:

```text
Switch poort down
  └── Alle hosts achter die poort: triggers afhankelijk van switch trigger
      └── Alle services op die hosts: afhankelijk van host trigger
```

Als de parent-trigger actief is, worden child-triggers onderdrukt.

---

## Severity Levels

| Level | Kleur | Gebruik |
| ----- | ----- | ------- |
| Not classified | Grijs | Niet gecategoriseerd |
| Information | Lichtblauw | Informatief, geen actie nodig |
| Warning | Geel | Aandacht nodig, geen directe impact |
| Average | Oranje | Significante impact, actie vereist |
| High | Rood | Kritieke component down |
| Disaster | Donkerrood | Hele service/systeem down |

### Best Practices voor Severity

- **Information**: Gebruik alleen voor testen/development
- **Warning**: "Er is iets veranderd" - ge&iuml;soleerd geen impact
  - Voorbeeld: CPU > 70% voor 15 minuten, disk > 80%
- **Average**: Sub-component met beperkte impact
  - Voorbeeld: Een van meerdere webservers down, disk > 90%
- **High**: Kritieke service/component is down
  - Voorbeeld: Enige webserver down, database replicatie stopt
- **Disaster**: Complete service/omgeving onbereikbaar
  - Voorbeeld: Hele netwerk segment onbereikbaar, database cluster down

---

## Alerting & Notificaties

### Media Types

| Type | Beschrijving | Gebruik |
| ---- | ------------ | ------- |
| Email | SMTP email | Standaard notificaties |
| SMS | SMS berichten | Urgente alerts (High/Disaster) |
| Webhook | HTTP callbacks | Slack, Teams, PagerDuty, Telegram, etc. |
| Script | Custom scripts | Alles wat je kunt scripten |

### Webhook Voorbeelden

**Slack webhook**:
```json
{
  "channel": "#monitoring",
  "username": "Zabbix",
  "text": "Problem: {EVENT.NAME}\nHost: {HOST.NAME}\nSeverity: {EVENT.SEVERITY}"
}
```

**Microsoft Teams**:
```json
{
  "@type": "MessageCard",
  "summary": "Zabbix Alert",
  "sections": [{
    "activityTitle": "{EVENT.NAME}",
    "facts": [
      {"name": "Host", "value": "{HOST.NAME}"},
      {"name": "Severity", "value": "{EVENT.SEVERITY}"},
      {"name": "Time", "value": "{EVENT.DATE} {EVENT.TIME}"}
    ]
  }]
}
```

### Actions

Actions verbinden triggers aan notificaties:

```text
Action: "Linux server alerts"
├── Conditions:
│   ├── Trigger severity >= Warning
│   ├── Host group = Linux servers
│   └── NOT in maintenance
├── Operations:
│   ├── Stap 1 (direct): Email naar Linux team
│   ├── Stap 2 (na 30 min): SMS naar on-call engineer
│   └── Stap 3 (na 1 uur): Email naar management
└── Recovery operations:
    └── Email naar Linux team: "RESOLVED: {EVENT.NAME}"
```

### Escalaties

Escalaties zorgen ervoor dat onopgeloste problemen naar hogere levels gaan:

1. **Stap 1** (0 min): Email naar team
2. **Stap 2** (30 min): SMS naar on-call
3. **Stap 3** (60 min): Bel manager
4. **Stap 4** (120 min): Bel directeur

### Maintenance Windows

Voorkom valse alerts tijdens gepland onderhoud:
- **Met data collection**: Data wordt nog verzameld, maar geen alerts
- **Zonder data collection**: Alles stopt (niet aanbevolen)
- Plan vooruit met start/eindtijd of recurring schedule

## Tags voor Trigger Organisatie

```yaml
triggers:
  - name: 'High CPU utilization'
    tags:
      - tag: scope
        value: performance
      - tag: component
        value: cpu
      - tag: team
        value: linux-ops
```

Tags maken het mogelijk om:
- Actions te filteren op specifieke tags
- Dashboard widgets te filteren
- Event correlatie uit te voeren
- Trigger problemen te groeperen

## Bronnen

- [Trigger Expressions](https://www.zabbix.com/documentation/current/en/manual/config/triggers/expression)
- [Trigger Severity](https://www.zabbix.com/documentation/current/en/manual/config/triggers/severity)
- [Actions](https://www.zabbix.com/documentation/current/en/manual/config/notifications/action)
- [Severity Best Practices](https://platon.sikt.no/tjenester/zabbix/best_practice_severity)
