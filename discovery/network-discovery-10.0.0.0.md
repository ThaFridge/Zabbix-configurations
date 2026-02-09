# Network Discovery: 10.0.0.0/24

## Wat gaan we doen?

Zabbix het netwerk `10.0.0.0/24` laten scannen om automatisch:

- Linux servers te vinden (via Zabbix agent)
- Windows servers te vinden (via Zabbix agent)
- Netwerkapparatuur te vinden (via SNMP)
- Overige apparaten te vinden (via ICMP ping)

Na het vinden worden hosts automatisch aangemaakt en aan de juiste groep + template gekoppeld.

---

## Stap 1: Host Groups Aanmaken

Ga naar: **Data collection > Host groups > Create host group**

Maak deze groepen aan:

| Groep naam | Doel |
| ---------- | ---- |
| `Discovered hosts` | Standaard groep voor alle ontdekte hosts |
| `Linux servers` | Ontdekte Linux machines |
| `Windows servers` | Ontdekte Windows machines |
| `Network devices` | Switches, routers, etc. |

---

## Stap 2: Discovery Rule Aanmaken

Ga naar: **Data collection > Discovery > Create discovery rule**

### Basis instellingen

| Veld | Waarde | Uitleg |
| ---- | ------ | ------ |
| Name | `Local network 10.0.0.0/24` | Herkenbare naam |
| Proxy | (geen proxy) | Direct vanuit Zabbix server |
| IP range | `10.0.0.0/24` | Het hele /24 subnet |
| Update interval | `1h` | Elk uur scannen |
| Checks | Zie hieronder | Meerdere checks |
| Device uniqueness criteria | IP address | Eén host per IP |
| Enabled | Ja | Activeer de rule |

### Discovery Checks toevoegen

Klik op "Add" bij Checks en maak deze checks aan (in deze volgorde):

**Check 1 - Zabbix Agent:**

| Veld | Waarde |
| ---- | ------ |
| Check type | Zabbix agent |
| Port range | 10050 |
| Key | `system.uname` |

> Dit vindt alle machines waar een Zabbix agent op draait.
> De `system.uname` key geeft OS info terug (Linux/Windows herkenning).

**Check 2 - SNMPv2 agent:**

| Veld | Waarde |
| ---- | ------ |
| Check type | SNMPv2 agent |
| Port range | 161 |
| SNMP community | `{$SNMP_COMMUNITY}` |
| SNMP OID | `sysName.0` |

> Dit vindt alle SNMP-enabled apparaten (switches, routers, printers, etc.).
> Gebruik de macro `{$SNMP_COMMUNITY}` zodat je deze centraal kunt beheren.

**Check 3 - ICMP Ping:**

| Veld | Waarde |
| ---- | ------ |
| Check type | ICMP ping |

> Vangt alle overige apparaten die reageren op ping.
> Dit is de "fallback" - als agent en SNMP niet reageren.

---

## Stap 3: Global Macro voor SNMP Community

Ga naar: **Administration > General > Macros**

| Macro | Waarde | Type |
| ----- | ------ | ---- |
| `{$SNMP_COMMUNITY}` | `public` | Secret text |

> Gebruik "Secret text" zodat de community string niet zichtbaar is in de UI.
> Pas de waarde aan als jouw apparaten een andere community string gebruiken.

---

## Stap 4: Discovery Actions Aanmaken

Ga naar: **Alerts > Actions > Discovery actions > Create action**

### Action 1: Linux servers automatisch toevoegen

**Tab "Action":**

| Veld | Waarde |
| ---- | ------ |
| Name | `Auto-discover Linux servers` |
| Enabled | Ja |

**Tab "Conditions":**

Klik "Add" en voeg toe:

| Type | Operator | Waarde |
| ---- | -------- | ------ |
| Discovery check | equals | `Local network 10.0.0.0/24: system.uname` |
| Discovery status | equals | Up |
| Received value | contains | `Linux` |

> Dit matcht alleen hosts waar `system.uname` het woord "Linux" bevat.

**Tab "Operations":**

Klik "Add" voor elke operatie:

| Operatie | Details |
| -------- | ------- |
| Add host | - |
| Add to host group | `Linux servers` |
| Link to template | `Linux by Zabbix agent active` |
| Enable host | - |

---

### Action 2: Windows servers automatisch toevoegen

**Tab "Action":**

| Veld | Waarde |
| ---- | ------ |
| Name | `Auto-discover Windows servers` |
| Enabled | Ja |

**Tab "Conditions":**

| Type | Operator | Waarde |
| ---- | -------- | ------ |
| Discovery check | equals | `Local network 10.0.0.0/24: system.uname` |
| Discovery status | equals | Up |
| Received value | contains | `Windows` |

**Tab "Operations":**

| Operatie | Details |
| -------- | ------- |
| Add host | - |
| Add to host group | `Windows servers` |
| Link to template | `Windows by Zabbix agent active` |
| Enable host | - |

---

### Action 3: Netwerkapparatuur automatisch toevoegen

**Tab "Action":**

| Veld | Waarde |
| ---- | ------ |
| Name | `Auto-discover Network devices` |
| Enabled | Ja |

**Tab "Conditions":**

| Type | Operator | Waarde |
| ---- | -------- | ------ |
| Discovery check | equals | `Local network 10.0.0.0/24: SNMPv2 agent "sysName.0"` |
| Discovery status | equals | Up |

**Tab "Operations":**

| Operatie | Details |
| -------- | ------- |
| Add host | - |
| Add to host group | `Network devices` |
| Link to template | `Generic SNMP` |
| Enable host | - |

---

## Stap 5: Verifi&euml;ren

Na maximaal 1 uur (het update interval):

1. Ga naar **Monitoring > Discovery**
   - Je ziet hier welke IP's gevonden zijn en welke checks succesvol waren
2. Ga naar **Data collection > Hosts**
   - Ontdekte hosts verschijnen hier automatisch
   - Check of ze de juiste groep en template hebben

### Troubleshooting

| Probleem | Oorzaak | Oplossing |
| -------- | ------- | --------- |
| Geen hosts gevonden | Firewall blokkeert | Open poort 10050 (agent), 161 (SNMP), ICMP |
| Agent check faalt | Agent niet geinstalleerd | Installeer Zabbix agent op de hosts |
| SNMP check faalt | Verkeerde community | Controleer `{$SNMP_COMMUNITY}` macro waarde |
| Host in verkeerde groep | Condition te breed | Verfijn de "Received value" condities |
| Dubbele hosts | Zelfde host meerdere IPs | Gebruik "Device uniqueness: DNS name" |

---

## Volgende Stappen

Na succesvolle network discovery kun je:

1. **Verfijnen**: Voeg meer specifieke actions toe (bv. voor printers, access points)
2. **LLD toevoegen**: Ontdek automatisch filesystems, interfaces, etc. op gevonden hosts
3. **Alerting**: Stel meldingen in wanneer hosts verdwijnen van het netwerk
4. **Dashboards**: Maak een overzicht van alle ontdekte apparaten
