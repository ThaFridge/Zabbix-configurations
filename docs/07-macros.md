# Macro's & Variabelen

## Overzicht

Macro's in Zabbix zijn variabelen die op verschillende plekken gebruikt worden om configuraties flexibel en herbruikbaar te maken.

## Soorten Macro's

### 1. Built-in Macros

Door Zabbix zelf gevuld, niet wijzigbaar:

| Macro | Waarde | Context |
| ----- | ------ | ------- |
| `{HOST.HOST}` | Technische hostnaam | Items, triggers, notifications |
| `{HOST.NAME}` | Zichtbare hostnaam | Items, triggers, notifications |
| `{HOST.IP}` | Host IP adres | Items, triggers, notifications |
| `{HOST.DNS}` | Host DNS naam | Items, triggers, notifications |
| `{HOST.CONN}` | Connectie adres (IP of DNS) | Items, triggers, notifications |
| `{ITEM.VALUE}` | Huidige item waarde | Trigger namen, notifications |
| `{ITEM.LASTVALUE}` | Laatste item waarde | Trigger namen, notifications |
| `{EVENT.NAME}` | Event/probleem naam | Notifications |
| `{EVENT.SEVERITY}` | Severity naam | Notifications |
| `{EVENT.DATE}` | Event datum | Notifications |
| `{EVENT.TIME}` | Event tijd | Notifications |
| `{TRIGGER.NAME}` | Trigger naam | Notifications |
| `{TRIGGER.STATUS}` | PROBLEM of OK | Notifications |
| `{INVENTORY.*}` | Host inventory velden | Notifications, maps |

### 2. User Macros

Door gebruikers gedefinieerd, overschrijfbaar per level:

```text
Prioriteit (hoog naar laag):
1. Host-level macro        {$CPU_CRIT} = 95    (specifiekst)
2. Template-level macro    {$CPU_CRIT} = 90
3. Global macro            {$CPU_CRIT} = 85    (meest algemeen)
```

Syntax: `{$MACRO_NAAM}`

Voorbeelden:
```text
{$CPU.UTIL.CRIT}     = 90
{$MEMORY.UTIL.WARN}  = 80
{$DISK.PUSED.MAX}    = 85
{$SNMP_COMMUNITY}    = public
{$MYSQL.PORT}        = 3306
```

### 3. LLD Macros

Gegenereerd door Low-Level Discovery:

```text
{#FSNAME}      = /home
{#FSTYPE}      = ext4
{#IFNAME}      = eth0
{#SNMPINDEX}   = 1
{#SNMPVALUE}   = GigabitEthernet0/1
{#DBNAME}      = production_db
```

Gebruikt in prototypes:
```text
Item prototype key:    vfs.fs.size[{#FSNAME},pfree]
Trigger prototype:     last(/host/vfs.fs.size[{#FSNAME},pfree]) < {$DISK.PUSED.MAX}
Graph prototype name:  Disk space on {#FSNAME}
```

## User Macro Types

| Type | Beschrijving | Voorbeeld |
| ---- | ------------ | --------- |
| Text | Gewone tekst waarde | `{$SNMP_COMMUNITY}` = `public` |
| Secret | Verborgen waarde (write-only) | `{$DB_PASSWORD}` = `******` |
| Vault | Waarde uit external vault | `{$DB_PASSWORD}` = `vault:secret/db:password` |

### Secret Macros
- Waarde wordt nooit getoond in de UI na opslaan
- Ideaal voor wachtwoorden en API keys
- Kan niet geexporteerd worden (wordt leeg geexporteerd)

### Vault Macros
- Ondersteunt HashiCorp Vault en CyberArk
- Waarde wordt real-time opgehaald uit de vault
- Formaat: `vault:path/to/secret:key`

## Macro Context

Macro's kunnen context hebben voor specifieke waarden per situatie:

```text
# Standaard disk threshold
{$DISK.PUSED.MAX} = 85

# Maar voor /tmp mag het voller
{$DISK.PUSED.MAX:"/tmp"} = 95

# En voor de database disk strenger
{$DISK.PUSED.MAX:"/var/lib/mysql"} = 75
```

In trigger expression:
```text
last(/host/vfs.fs.size[{#FSNAME},pfree]) < {$DISK.PUSED.MAX:"{#FSNAME}"}
```

## Macro's in Notificaties

```text
Subject: [{EVENT.SEVERITY}] {EVENT.NAME}

Body:
Host: {HOST.NAME} ({HOST.IP})
Problem: {EVENT.NAME}
Severity: {EVENT.SEVERITY}
Time: {EVENT.DATE} {EVENT.TIME}
Current value: {ITEM.LASTVALUE}

{TRIGGER.URL}
```

## Best Practices

1. **Naming convention**: Gebruik dots als separator: `{$COMPONENT.METRIC.TYPE}`
   - `{$CPU.UTIL.CRIT}`, `{$MEMORY.UTIL.WARN}`, `{$DISK.PUSED.MAX}`
2. **Altijd user macros voor drempelwaarden**: Nooit hardcoded waarden in triggers
3. **Descriptions invullen**: Documenteer wat de macro doet en verwachte waarden
4. **Secret macros voor gevoelige data**: Wachtwoorden, API keys, community strings
5. **Context gebruiken**: Wanneer dezelfde macro per entiteit verschilt
6. **Global defaults**: Stel globals in als baseline, overschrijf per template/host
7. **LLD macros in namen**: Altijd LLD macro in prototype namen voor herkenbaarheid

## Bronnen

- [User Macros](https://www.zabbix.com/documentation/current/en/manual/config/macros/user_macros)
- [LLD Macros](https://www.zabbix.com/documentation/current/en/manual/config/macros/lld_macros)
- [Macro Functions](https://www.zabbix.com/documentation/current/en/manual/config/macros/macro_functions)
- [Supported Macros](https://www.zabbix.com/documentation/current/en/manual/appendix/macros/supported_by_location)
