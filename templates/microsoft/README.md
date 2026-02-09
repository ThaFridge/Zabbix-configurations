# Microsoft Cloud Health - Zabbix Template

## Wat doet deze template?

Deze template monitort de gezondheid van Microsoft 365 en Azure diensten via de **Microsoft Graph API**. Wanneer Microsoft een storing meldt voor bijvoorbeeld Exchange, Teams of Azure Virtual Desktop, krijg je direct een alert in Zabbix. Daarnaast voert de template eigen actieve checks uit op kritieke Microsoft endpoints.

### Gemonitorde diensten

| Dienst | Zabbix key | Trigger severity | Impact bij storing |
|--------|-----------|-----------------|-------------------|
| **Exchange Online** | `ms.health.exchange` | High | Email verstoord |
| **Microsoft Teams** | `ms.health.teams` | High | Communicatie verstoord |
| **SharePoint Online** | `ms.health.sharepoint` | High | Documenten onbereikbaar |
| **Microsoft Entra ID** (Azure AD) | `ms.health.entra` | Disaster | Authenticatie voor alles verstoord |
| **Microsoft Intune** | `ms.health.intune` | High | Device management verstoord |
| **Microsoft 365 Apps** | `ms.health.m365apps` | Warning | Word, Excel etc. verstoord |
| **OneDrive for Business** | `ms.health.onedrive` | Warning | Bestandssync verstoord |
| **Azure Virtual Desktop** | `ms.health.avd` | Disaster | AVD gebruikers kunnen niet werken |
| **Microsoft Defender XDR** | `ms.health.defender` | High | Security monitoring verstoord |

### Monitoring in drie lagen

**Laag 1 - Microsoft Graph Service Health API**
Bevraagt de officiële Microsoft Graph API voor service health status. Vereist een Azure AD App Registration.

- Health status per dienst (serviceOperational, serviceDegradation, serviceInterruption, etc.)
- Actieve service issues (onopgeloste incidenten)
- Aantal actieve issues teller

**Laag 2 - Actieve HTTP endpoint checks**
Eigen tests vanuit Zabbix, onafhankelijk van wat Microsoft rapporteert:

- `login.microsoftonline.com` - Azure AD login endpoint (status + response time)
- `outlook.office365.com` - Outlook Web App healthcheck
- `portal.azure.com` - Azure Portal bereikbaarheid

**Laag 3 - Issue tracking**
Telt het aantal actieve (onopgeloste) service issues en triggert een warning als er issues zijn.

---

## Overzicht items

| Item key | Type | Interval | Omschrijving |
|----------|------|----------|-------------|
| `ms.auth.token` | HTTP Agent | 50m | OAuth2 bearer token (auto-refresh) |
| `ms.health.raw` | HTTP Agent | 5m | Raw JSON service health overviews |
| `ms.health.exchange` | Dependent | - | Exchange Online status |
| `ms.health.teams` | Dependent | - | Microsoft Teams status |
| `ms.health.sharepoint` | Dependent | - | SharePoint Online status |
| `ms.health.entra` | Dependent | - | Microsoft Entra ID status |
| `ms.health.intune` | Dependent | - | Microsoft Intune status |
| `ms.health.m365apps` | Dependent | - | Microsoft 365 Apps status |
| `ms.health.onedrive` | Dependent | - | OneDrive for Business status |
| `ms.health.avd` | Dependent | - | Azure Virtual Desktop status |
| `ms.health.defender` | Dependent | - | Microsoft Defender XDR status |
| `ms.issues.raw` | HTTP Agent | 5m | Raw JSON actieve issues |
| `ms.issues.count` | Dependent | - | Aantal actieve issues |
| `ms.http.login.status` | HTTP Agent | 2m | Login endpoint HTTP status |
| `ms.http.login.resptime` | HTTP Agent | 2m | Login endpoint response time |
| `ms.http.outlook.status` | HTTP Agent | 2m | Outlook Web HTTP status |
| `ms.http.portal.status` | HTTP Agent | 5m | Azure Portal HTTP status |

## Overzicht triggers

| Trigger | Severity | Wanneer |
|---------|----------|---------|
| Exchange Online niet operational | **High** | Exchange meldt probleem |
| Teams niet operational | **High** | Teams meldt probleem |
| SharePoint niet operational | **High** | SharePoint meldt probleem |
| Entra ID niet operational | **Disaster** | Azure AD/Entra meldt probleem |
| Intune niet operational | **High** | Intune meldt probleem |
| M365 Apps niet operational | **Warning** | Office apps melden probleem |
| OneDrive niet operational | **Warning** | OneDrive meldt probleem |
| Azure Virtual Desktop niet operational | **Disaster** | AVD meldt probleem |
| Defender niet operational | **High** | Defender meldt probleem |
| Actieve service issues | **Warning** | 1 of meer onopgeloste issues |
| Login endpoint onbereikbaar | **Disaster** | login.microsoftonline.com down |
| Login response time hoog | **Warning** | Login endpoint > 3s |
| Outlook Web onbereikbaar | **High** | Outlook healthcheck faalt |
| Azure Portal onbereikbaar | **High** | portal.azure.com down |

## Configureerbare macros

| Macro | Standaard | Omschrijving |
|-------|-----------|-------------|
| `{$MS.TENANT.ID}` | *(leeg)* | Azure AD Tenant ID |
| `{$MS.APP.ID}` | *(leeg)* | App Registration Client ID |
| `{$MS.APP.SECRET}` | *(leeg, secret)* | App Registration Client Secret |
| `{$MS.GRAPH.URL}` | `https://graph.microsoft.com/v1.0` | Graph API base URL |
| `{$MS.LOGIN.URL}` | `https://login.microsoftonline.com` | Azure AD login URL |
| `{$MS.STATUS.INTERVAL}` | `5m` | Poll interval service health |
| `{$MS.TOKEN.INTERVAL}` | `50m` | Token refresh interval |

## Dashboard

De template bevat een ingebouwd dashboard met:
- **Service Health Status** - overzicht van alle 9 diensten
- **Actieve Issues** teller
- **Login Response Time** grafiek
- **Actieve Problemen** lijst

---

## Vereisten

- Zabbix Server **6.4+** of **7.0**
- Zabbix Server moet internet toegang hebben
- Azure AD App Registration met juiste permissions

## Stap 1: Azure AD App Registration aanmaken

1. Ga naar [Azure Portal](https://portal.azure.com) > **Microsoft Entra ID** > **App registrations**
2. Klik **New registration**
   - Name: `Zabbix Monitoring`
   - Supported account types: **Single tenant**
   - Redirect URI: laat leeg
3. Klik **Register**
4. Noteer:
   - **Application (client) ID** → dit wordt `{$MS.APP.ID}`
   - **Directory (tenant) ID** → dit wordt `{$MS.TENANT.ID}`

## Stap 2: API Permissions instellen

1. In de App Registration, ga naar **API permissions**
2. Klik **Add a permission** > **Microsoft Graph** > **Application permissions**
3. Zoek en voeg toe:
   - `ServiceHealth.Read.All`
4. Klik **Grant admin consent for [tenant naam]**
5. Controleer dat de status op **Granted** staat

## Stap 3: Client Secret aanmaken

1. Ga naar **Certificates & secrets** > **Client secrets**
2. Klik **New client secret**
   - Description: `Zabbix`
   - Expires: kies een geschikte periode (bijv. 24 maanden)
3. Klik **Add**
4. **Kopieer direct de Value** → dit wordt `{$MS.APP.SECRET}`
   - Let op: de value is na het verlaten van de pagina niet meer zichtbaar!

## Stap 4: Template importeren in Zabbix

1. Open Zabbix web UI
2. Ga naar **Data collection** > **Templates**
3. Klik **Import**
4. Selecteer `microsoft-health.yaml`
5. Vink aan: Templates, Items, Triggers, Dashboards
6. Klik **Import**

## Stap 5: Host aanmaken

1. Ga naar **Data collection** > **Hosts**
2. Klik **Create host**
3. Configureer:
   - **Host name**: `Microsoft Cloud`
   - **Groups**: `Cloud Services`
   - **Interfaces**: Agent interface met IP `127.0.0.1`
4. Tab **Templates**: koppel **Microsoft Cloud Health**
5. Tab **Macros**: vul in:
   - `{$MS.TENANT.ID}` = jouw Azure AD Tenant ID
   - `{$MS.APP.ID}` = jouw App Registration Client ID
   - `{$MS.APP.SECRET}` = jouw Client Secret
6. Klik **Add**

## Stap 6: Controleren

Na 5-10 minuten, ga naar **Monitoring** > **Latest data** en filter op host `Microsoft Cloud`:

```
ms.auth.token           = (lange token string)
ms.health.exchange      = serviceOperational
ms.health.teams         = serviceOperational
ms.health.entra         = serviceOperational
ms.health.avd           = serviceOperational
ms.issues.count         = 0
ms.http.login.status    = 200
ms.http.login.resptime  = 0.12
ms.http.outlook.status  = 200
```

---

## Multi-tenant setup

Als je meerdere klanten hebt met elk een eigen Microsoft tenant, maak dan per klant een aparte host aan met eigen tenant credentials:

```
Microsoft - Klant A  →  {$MS.TENANT.ID} = tenant-id-a, {$MS.APP.ID} = app-id-a, ...
Microsoft - Klant B  →  {$MS.TENANT.ID} = tenant-id-b, {$MS.APP.ID} = app-id-b, ...
```

Elke klant heeft een eigen App Registration nodig in hun Azure AD.

---

## Mogelijke service status waarden

De Microsoft Graph API retourneert deze status waarden:

| Status | Betekenis |
|--------|-----------|
| `serviceOperational` | Dienst werkt normaal |
| `investigating` | Microsoft onderzoekt een probleem |
| `restoringService` | Microsoft werkt aan herstel |
| `verifyingService` | Microsoft verifieert dat het probleem opgelost is |
| `serviceRestored` | Dienst is hersteld |
| `postIncidentReviewPublished` | Post-incident review gepubliceerd |
| `serviceDegradation` | Dienst werkt maar met verminderde prestaties |
| `serviceInterruption` | Dienst is onderbroken |
| `extendedRecovery` | Herstel duurt langer dan verwacht |
| `falsePositive` | Eerder gemeld probleem bleek vals alarm |
| `investigationSuspended` | Onderzoek gepauzeerd |

---

## Troubleshooting

**Token ophalen mislukt**
- Controleer of Tenant ID, App ID en Secret correct zijn
- Controleer of de Zabbix Server `login.microsoftonline.com` kan bereiken
- Test: `curl -X POST "https://login.microsoftonline.com/TENANT_ID/oauth2/v2.0/token" -d "grant_type=client_credentials&client_id=APP_ID&client_secret=SECRET&scope=https://graph.microsoft.com/.default"`

**Health data is leeg of "unknown"**
- Controleer of `ServiceHealth.Read.All` permission is granted met admin consent
- Controleer of het token succesvol opgehaald wordt (check `ms.auth.token` item)
- De service naam in de JSONPath filter moet exact matchen met wat Microsoft retourneert

**AVD status is "unknown"**
- Niet alle tenants hebben AVD. Als de tenant geen AVD licentie heeft, zal deze service niet in de health overview staan
- De JSONPath fallback retourneert dan "unknown" en de trigger gaat niet af (by design)

**Client secret verlopen**
- Maak een nieuwe secret aan in Azure Portal
- Update `{$MS.APP.SECRET}` in de Zabbix host macros
- Zet een reminder in je agenda voor de volgende verlooptdatum

---

## Bronnen

- [Microsoft Graph Service Communications API](https://learn.microsoft.com/en-us/graph/service-communications-concept-overview)
- [Azure Resource Health REST API](https://learn.microsoft.com/en-us/rest/api/resourcehealth/)
- [Zabbix MS365 Integration](https://www.zabbix.com/integrations/ms365)
