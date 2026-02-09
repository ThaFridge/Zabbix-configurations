# Cove Data Protection - Zabbix Template

## Wat doet deze template?

Deze template monitort **N-able Cove Data Protection** (voorheen SolarWinds Backup) via de JSON-RPC API. De template ontdekt automatisch alle backup devices en monitort per device de backup status, fouten, en of backups op tijd draaien.

### Waarom via Zabbix?

De Cove management console geeft al overzicht, maar met Zabbix kun je:
- Backup failures **combineren met server health** alerts (1 dashboard)
- **Triggers en escalaties** instellen (bijv. na 48h geen backup → bel engineer)
- Backup status per klant koppelen aan klant-specifieke host groups
- **Historische trends** bijhouden (opslag groei, failure rates)

### Wat wordt gemonitord?

**Per device (automatisch ontdekt via LLD):**

| Item | Beschrijving | Trigger |
|------|-------------|---------|
| Laatste backup status | Status code (Failed, Completed, etc.) | High bij Failed/Aborted |
| Aantal fouten | Foutcount laatste sessie | - |
| Aantal waarschuwingen | Waarschuwingen laatste sessie | - |
| Laatste succesvolle backup | Unix timestamp | Warning > 26h, High > 48h |
| Gebruikte opslag | Cloud storage in bytes | - |
| OS type | Besturingssysteem | - |
| Computer naam | Hostname van het device | - |
| Actieve data sources | Files, SystemState, VMware, etc. | - |

**Globaal:**

| Item | Beschrijving |
|------|-------------|
| Totaal aantal devices | Hoeveel devices in Cove |
| Totale opslag | Totaal gebruikte cloud storage |

### Status codes

| Code | Betekenis | Trigger |
|------|-----------|---------|
| 1 | In progress | - |
| 2 | **Failed** | **High** |
| 3 | **Aborted** | **High** |
| 5 | Completed | - (OK) |
| 6 | Interrupted | - |
| 7 | Not started | **Warning** |
| 8 | Completed with errors | **Warning** |
| 9 | In progress (image) | - |
| 10 | Over quota | **Warning** |
| 11 | No selection | - |
| 12 | Restarted | - |

---

## Overzicht triggers

| Trigger | Severity | Wanneer |
|---------|----------|---------|
| Backup FAILED | **High** | Laatste sessie status = 2 (Failed) |
| Backup ABORTED | **High** | Laatste sessie status = 3 (Aborted) |
| Backup completed with errors | **Warning** | Laatste sessie status = 8 |
| Backup not started | **Warning** | Laatste sessie status = 7 |
| Over quota | **Warning** | Laatste sessie status = 10 |
| Geen succesvolle backup in 26h | **Warning** | Timestamp laatste succes > 26 uur geleden |
| Geen succesvolle backup in 48h | **High** | Timestamp laatste succes > 48 uur geleden |

## Configureerbare macros

| Macro | Standaard | Omschrijving |
|-------|-----------|-------------|
| `{$COVE.PARTNER}` | *(leeg)* | Cove partner/company naam |
| `{$COVE.USER}` | *(leeg)* | API gebruiker email |
| `{$COVE.PASSWORD}` | *(leeg, secret)* | API gebruiker wachtwoord |
| `{$COVE.API.URL}` | `https://api.backup.management/jsonapi` | API endpoint |
| `{$COVE.INTERVAL}` | `15m` | Poll interval |
| `{$COVE.BACKUP.MAX_AGE_HOURS}` | `26` | Warning drempel (uren) |
| `{$COVE.BACKUP.CRITICAL_AGE_HOURS}` | `48` | High severity drempel (uren) |

## Dashboard

De template bevat een ingebouwd dashboard met:
- **Totaal devices** teller
- **Totale opslag** widget
- **Backup Problemen** lijst (alle actieve triggers)

---

## Vereisten

- Zabbix Server **6.4+** of **7.0**
- Zabbix Server moet `api.backup.management` kunnen bereiken (HTTPS)
- Een Cove Data Protection account met **API access**

## Stap 1: Cove API gebruiker aanmaken

1. Log in op de [Cove Management Console](https://backup.management)
2. Ga naar je partner account
3. Maak een nieuwe gebruiker aan (of bewerk een bestaande)
4. Zorg dat **API Authentication** is aangevinkt
5. Noteer:
   - **Partner naam** (exact zoals weergegeven in de console)
   - **Email adres** van de gebruiker
   - **Wachtwoord** van de gebruiker

**Let op**: De API gebruiker heeft toegang tot alle devices onder de partner. Maak een dedicated API-only user aan voor Zabbix.

## Stap 2: Template importeren

1. Open Zabbix web UI
2. Ga naar **Data collection** > **Templates**
3. Klik **Import**
4. Selecteer `cove-backup-health.yaml`
5. Vink aan: Templates, Items, Triggers, Discovery rules, Dashboards
6. Klik **Import**

## Stap 3: Host aanmaken

1. Ga naar **Data collection** > **Hosts**
2. Klik **Create host**
3. Configureer:
   - **Host name**: `Cove Backup` (of `Cove - KlantNaam`)
   - **Groups**: `Backup Services`
   - **Interfaces**: Agent interface met IP `127.0.0.1`
4. Tab **Templates**: koppel **Cove Data Protection**
5. Tab **Macros**: vul in:
   - `{$COVE.PARTNER}` = jouw partner naam (exact, hoofdlettergevoelig)
   - `{$COVE.USER}` = API gebruiker email
   - `{$COVE.PASSWORD}` = API gebruiker wachtwoord
6. Klik **Add**

## Stap 4: Controleren

Na 15-20 minuten:

1. Ga naar **Monitoring** > **Latest data** en filter op host `Cove Backup`
2. Je zou moeten zien:
   - `cove.auth.visa` = (lange token string)
   - `cove.devices.count` = bijv. `42`
   - `cove.storage.total` = bijv. `1.2 TB`
3. Ga naar **Configuration** > **Hosts** > `Cove Backup` > **Discovery**
   - Check of de discovery rule devices heeft gevonden
4. Na de discovery (kan tot 1 uur duren) verschijnen per device items zoals:
   - `cove.device.status[12345]` = `5` (Completed)
   - `cove.device.errors[12345]` = `0`
   - `cove.device.last_success[12345]` = (timestamp)

---

## Multi-tenant setup

### Optie A: Eén Cove partner account per klant
Maak per klant een aparte host aan met eigen credentials:

```
Cove - Klant A  →  {$COVE.PARTNER} = "Klant A BV", {$COVE.USER} = api@klant-a.nl
Cove - Klant B  →  {$COVE.PARTNER} = "Klant B BV", {$COVE.USER} = api@klant-b.nl
```

### Optie B: Eén superadmin account
Als je een partner-level account hebt met toegang tot alle klanten, kun je 1 host aanmaken die alle devices ontdekt. De device namen bevatten dan devices van alle klanten.

---

## Hoe werkt de template technisch?

```
1. Login (elke 10 min)
   POST → api.backup.management/jsonapi
   Method: Login
   → Ontvangt: visa token (geldig 15 min)

2. EnumerateAccountStatistics (elke 15 min)
   POST → api.backup.management/jsonapi
   Method: EnumerateAccountStatistics
   Headers: visa token
   → Ontvangt: JSON met alle devices + statistieken

3. LLD Discovery
   Parseert de JSON response
   → Maakt per device een {#DEVICE.ID} + {#DEVICE.NAME}

4. Dependent items per device
   Extraheert per device via JSONPath:
   → Status, fouten, waarschuwingen, timestamp, opslag, OS
```

De template gebruikt **1 master API call** om alle data op te halen, en verwerkt alles via **dependent items** en **LLD**. Dit minimaliseert het aantal API calls.

---

## Troubleshooting

**Login mislukt / geen visa**
- Controleer of partner naam exact klopt (hoofdlettergevoelig!)
- Controleer of de gebruiker API Authentication heeft aanstaan
- Test handmatig:
  ```bash
  curl -X POST https://api.backup.management/jsonapi \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"Login","params":{"partner":"JouwPartner","username":"user@email.com","password":"wachtwoord"},"id":"1"}'
  ```

**Geen devices ontdekt**
- Wacht minimaal 1 uur na host aanmaken (LLD discovery interval)
- Controleer of `cove.devices.raw` data bevat in Latest data
- Controleer of `cove.devices.count` > 0

**Visa expired errors**
- De visa is 15 min geldig, de template refresht elke 10 min
- Bij problemen, verlaag `{$COVE.INTERVAL}` niet onder 10 minuten (anders verloopt de visa tussen login en data call)

**PartnerId -1 geeft geen resultaten**
- PartnerId `-1` betekent "alle partners". Als dit niet werkt, heb je mogelijk niet de juiste rechten
- Vraag het juiste PartnerId op via de Cove management console

---

## API Column codes referentie

| Code | Beschrijving | Type |
|------|-------------|------|
| I0 | Device ID | Integer |
| I1 | Device Name | String |
| I14 | Used Storage | Bytes |
| I16 | OS Version | String |
| I18 | Computer Name | String |
| I32 | OS Type | String |
| I78 | Active Data Sources | String |
| F00 | Last Session Status | Integer (1-12) |
| F06 | Error Count | Integer |
| F07 | Warning Count | Integer |
| F09 | Last Successful Timestamp | Unix timestamp |

Volledige lijst: [N-able Column Codes](https://developer.n-able.com/n-able-cove/docs/column-codes)

## Bronnen

- [Cove JSON-RPC API Guide](https://documentation.n-able.com/covedataprotection/USERGUIDE/QSG/Content/service-management/json-api/home.htm)
- [N-able Developer Portal - Cove](https://developer.n-able.com/n-able-cove/docs/getting-started)
- [Column Codes Reference](https://developer.n-able.com/n-able-cove/docs/column-codes)
- [Backup Scripts (Community)](https://github.com/BackupNerd/Backup-Scripts)
