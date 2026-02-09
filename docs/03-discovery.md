# Discovery Rules: Network Discovery & LLD

## Twee Soorten Discovery

Zabbix kent twee fundamenteel verschillende discovery mechanismen:

### 1. Network Discovery
- Scant netwerken om **nieuwe hosts** te vinden
- Werkt op IP-ranges
- Kan automatisch hosts aanmaken, aan groepen toevoegen, templates linken

### 2. Low-Level Discovery (LLD)
- Ontdekt **entiteiten binnen een host** (filesystems, interfaces, databases, etc.)
- Maakt automatisch items, triggers en graphs aan op basis van prototypes
- Veel krachtiger en flexibeler dan network discovery

---

## Network Discovery

### Hoe werkt het?
1. Zabbix scant een IP-range met opgegeven checks
2. Gevonden services/hosts worden gematcht tegen acties
3. Acties voeren operaties uit (host aanmaken, template linken, etc.)

### Discovery Rule configuratie
- **IP range**: bv. `192.168.1.1-254` of `10.0.0.0/24`
- **Update interval**: hoe vaak scannen
- **Checks**: SNMP, Zabbix agent, ICMP ping, HTTP, TCP poorten
- **Device uniqueness**: identificeer hosts op IP of SNMP sysName

### Discovery Actions
Bij gevonden hosts kun je automatisch:
- Host aanmaken in Zabbix
- Host aan groep toevoegen
- Template linken
- Host verwijderen als die verdwijnt
- Notificatie sturen

### Voorbeeld: Netwerk scannen
```text
IP Range:        192.168.1.1-254
Check type:      Zabbix agent (key: system.uname)
Check type:      SNMP v2 (OID: sysObjectID)
Check type:      ICMP ping
Update interval: 1h
```

---

## Low-Level Discovery (LLD)

### Hoe werkt het?
1. Een discovery item haalt JSON data op met beschikbare entiteiten
2. Filters beperken welke entiteiten verwerkt worden
3. Item/trigger/graph prototypes worden automatisch aangemaakt per entiteit

### LLD Flow
```text
Discovery Rule (key: vfs.fs.discovery)
    │
    ▼
JSON Response:
[
  {"{#FSNAME}": "/",      "{#FSTYPE}": "ext4"},
  {"{#FSNAME}": "/home",  "{#FSTYPE}": "ext4"},
  {"{#FSNAME}": "/tmp",   "{#FSTYPE}": "tmpfs"}
]
    │
    ▼
Filter: {#FSTYPE} matches ^(ext4|xfs)$
    │
    ▼
Prototypes genereren items:
  - vfs.fs.size[/,free]
  - vfs.fs.size[/,total]
  - vfs.fs.size[/home,free]
  - vfs.fs.size[/home,total]
```

### Ingebouwde Discovery Keys

| Key | Ontdekt | LLD Macros |
| --- | ------- | ---------- |
| `vfs.fs.discovery` | Filesystems | {#FSNAME}, {#FSTYPE}, {#FSDRIVETYPE} |
| `net.if.discovery` | Netwerk interfaces | {#IFNAME} |
| `system.cpu.discovery` | CPU cores | {#CPU.NUMBER}, {#CPU.STATUS} |
| `vfs.dev.discovery` | Block devices | {#DEVNAME}, {#DEVTYPE} |
| `system.hw.discovery` | Hardware info | {#TYPE}, {#NAME} |

### SNMP Discovery
- Gebruikt SNMP OID walking
- Key: `snmp.discovery` of specifieke OID's
- Macro: `{#SNMPVALUE}`, `{#SNMPINDEX}`
- Ideaal voor: switch poorten, SNMP-enabled apparaten

### Custom LLD Rules

Je kunt eigen discovery scripts schrijven die JSON teruggeven:

```bash
#!/bin/bash
# custom-db-discovery.sh - Ontdek databases
# Output moet JSON array zijn

echo '['
first=1
for db in $(mysql -N -e "SHOW DATABASES" 2>/dev/null); do
    [ "$db" = "information_schema" ] && continue
    [ "$db" = "performance_schema" ] && continue
    [ $first -eq 0 ] && echo ','
    echo "  {\"{#DBNAME}\": \"$db\"}"
    first=0
done
echo ']'
```

Configureer als UserParameter in agent config:
```ini
UserParameter=mysql.db.discovery,/usr/local/bin/custom-db-discovery.sh
```

### HTTP Agent Discovery

Discovery via REST API's (bv. Docker containers, Kubernetes pods):

```yaml
discovery_rules:
  - name: 'Docker container discovery'
    type: HTTP_AGENT
    key: 'docker.container.discovery'
    url: 'http://localhost:2375/containers/json'
    delay: '5m'
    lifetime: '7d'
    lld_macro_paths:
      - lld_macro: '{#CONTAINER.ID}'
        path: '$.Id'
      - lld_macro: '{#CONTAINER.NAME}'
        path: '$.Names[0]'
      - lld_macro: '{#CONTAINER.IMAGE}'
        path: '$.Image'
```

### LLD Filters

Filters bepalen welke ontdekte entiteiten verwerkt worden:

```yaml
filter:
  evaltype: AND_OR    # AND_OR, AND, OR, FORMULA
  conditions:
    - macro: '{#FSTYPE}'
      value: '^(ext4|xfs|btrfs)$'
      operator: MATCHES_REGEX
      formulaid: A
    - macro: '{#FSNAME}'
      value: '^/snap'
      operator: NOT_MATCHES_REGEX
      formulaid: B
```

### LLD Overrides

Overrides passen prototypes aan voor specifieke ontdekte entiteiten:

```yaml
overrides:
  - name: 'Root filesystem'
    step: '1'
    filter:
      conditions:
        - macro: '{#FSNAME}'
          value: '^/$'
    operations:
      - operationobject: TRIGGER_PROTOTYPE
        operator: LIKE
        value: 'Free disk space'
        severity: HIGH          # Verhoog severity voor root filesystem
```

### LLD Configuratieparameters

| Parameter | Beschrijving | Aanbevolen |
| --------- | ------------ | ---------- |
| Update interval | Hoe vaak discovery draait | 1h - 24h |
| Keep lost resources | Hoe lang verdwenen items bewaren | 30d |
| Lifetime | Maximum levensduur van ontdekte items | 0 (onbeperkt) of 30d |
| Enable | Discovery rule aan/uit | - |

## Best Practices

1. **Filters gebruiken**: Ontdek niet meer dan nodig (filter tmpfs, loopback, etc.)
2. **Update interval**: Discovery hoeft niet vaak (1x per uur of minder)
3. **Overrides**: Gebruik overrides voor uitzonderingen i.p.v. aparte templates
4. **Naming**: Gebruik LLD macros in item/trigger namen: `Free space on {#FSNAME}`
5. **Lifetime instellen**: Verwijder automatisch items van verdwenen entiteiten
6. **Custom discovery**: Return altijd geldige JSON, ook als er niets gevonden wordt (`[]`)
7. **Preprocessing**: Gebruik JSONPath preprocessing voor complexe API responses

## Bronnen

- [Zabbix LLD Documentatie](https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery)
- [Custom LLD Rules](https://www.zabbix.com/documentation/current/en/manual/discovery/low_level_discovery/custom_rules)
- [LLD Macros](https://www.zabbix.com/documentation/current/en/manual/config/macros/lld_macros)
- [Custom LLD Tutorial](https://sbcode.net/zabbix/custom-lld/)
