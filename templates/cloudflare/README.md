# Cloudflare Health - Zabbix Template

## Wat doet deze template?

Deze template monitort de beschikbaarheid en gezondheid van Cloudflare diensten. Omdat veel klantwebsites en -domeinen achter Cloudflare draaien, is een Cloudflare storing direct een probleem voor meerdere klanten. Deze template geeft vroegtijdig alarm zodat je proactief kunt handelen.

### Monitoring in drie lagen

**Laag 1 - Cloudflare Status API (passief)**
Bevraagt de publieke Cloudflare status API om te detecteren of Cloudflare zelf een storing meldt. Geen API key nodig.

- Overall status (none / minor / major / critical)
- Per-component status: CDN/Cache, Authoritative DNS, API, Dashboard

**Laag 2 - Actieve netwerk checks**
Voert vanuit de Zabbix Server eigen tests uit om onafhankelijk van Cloudflare's eigen rapportage te meten.

- ICMP ping naar 1.1.1.1 (Cloudflare DNS) + latency meting
- DNS A-record resolve van het klantdomein
- HTTP status code check van het klantdomein
- HTTP response time meting

**Laag 3 - SSL certificaat monitoring**
Controleert het SSL certificaat van het klantdomein op vervaldatum.

---

## Overzicht items

| Item key | Type | Interval | Omschrijving |
|----------|------|----------|-------------|
| `cf.status.raw` | HTTP Agent | 3m | Raw JSON van status API |
| `cf.status.indicator` | Dependent | - | Overall status: none/minor/major/critical |
| `cf.status.description` | Dependent | - | Leesbare status tekst |
| `cf.components.raw` | HTTP Agent | 3m | Raw JSON van components API |
| `cf.component.cdn` | Dependent | - | CDN/Cache status |
| `cf.component.dns` | Dependent | - | Authoritative DNS status |
| `cf.component.api` | Dependent | - | API status |
| `cf.component.dashboard` | Dependent | - | Dashboard status |
| `icmpping[1.1.1.1,4]` | Simple check | 1m | Ping naar 1.1.1.1 (1/0) |
| `icmppingsec[1.1.1.1,4]` | Simple check | 1m | Ping latency in seconden |
| `cf.http.status[{$CF.DOMAIN}]` | HTTP Agent | 2m | HTTP status code klantdomein |
| `cf.http.resptime[{$CF.DOMAIN}]` | HTTP Agent | 2m | Response time in seconden |
| `net.dns.record[,{$CF.DOMAIN},A,2,1]` | Simple check | 2m | DNS A-record lookup |
| `web.certificate.get[{$CF.DOMAIN},443]` | Simple check | 6h | SSL cert info (raw) |
| `cf.ssl.days[{$CF.DOMAIN}]` | Dependent | - | Dagen tot SSL cert verloopt |

## Overzicht triggers

| Trigger | Severity | Wanneer |
|---------|----------|---------|
| Cloudflare: Minor outage gemeld | **Warning** | Status API meldt "minor" |
| Cloudflare: Major outage gemeld | **High** | Status API meldt "major" |
| Cloudflare: Critical outage gemeld | **Disaster** | Status API meldt "critical" |
| Cloudflare: CDN/Cache niet operational | **High** | CDN component != operational |
| Cloudflare: DNS niet operational | **Disaster** | DNS component != operational |
| Cloudflare: API niet operational | **High** | API component != operational |
| Cloudflare: Dashboard niet operational | **Warning** | Dashboard component != operational |
| Cloudflare: 1.1.1.1 onbereikbaar | **High** | ICMP ping faalt |
| Cloudflare: HTTP status niet 200 | **High** | Klantdomein geeft geen 200 |
| Cloudflare: Response time hoog | **Warning** | Response time > threshold |
| Cloudflare: DNS resolve mislukt | **Disaster** | Geen DNS data in 10 minuten |
| Cloudflare: SSL verloopt < 14 dagen | **Warning** | Cert bijna verlopen |
| Cloudflare: SSL verloopt < 7 dagen | **High** | Cert kritiek bijna verlopen |

## Configureerbare macros

| Macro | Standaard | Omschrijving |
|-------|-----------|-------------|
| `{$CF.DOMAIN}` | `example.com` | Het klantdomein dat gemonitord wordt |
| `{$CF.RESPONSE_TIME_WARN}` | `3` | Response time warning drempel (seconden) |
| `{$CF.SSL_WARN_DAYS}` | `14` | SSL warning drempel (dagen) |
| `{$CF.SSL_HIGH_DAYS}` | `7` | SSL high severity drempel (dagen) |
| `{$CF.STATUS_INTERVAL}` | `3m` | Poll interval status API |
| `{$CF.HTTP_INTERVAL}` | `2m` | Poll interval HTTP checks |

## Dashboard

De template bevat een ingebouwd dashboard met:
- **Overall Status** widget - toont de huidige Cloudflare status tekst
- **Component Status** - overzicht van CDN, DNS, API, Dashboard status
- **Response Time** grafiek - response time klantdomein + ping latency
- **Actieve Problemen** - lijst van alle open triggers

---

## Importeren

### Vereisten
- Zabbix Server **6.4+** of **7.0**
- Zabbix Server moet internet toegang hebben (HTTP Agent + Simple checks)
- ICMP ping moet toegestaan zijn vanaf de Zabbix Server

### Stap 1: Template importeren

1. Open Zabbix web UI
2. Ga naar **Data collection** > **Templates**
3. Klik rechtsboven op **Import**
4. Selecteer `cloudflare-health.yaml`
5. Vink aan:
   - [x] Templates
   - [x] Items
   - [x] Triggers
   - [x] Dashboards
6. Klik **Import**

### Stap 2: Host aanmaken

1. Ga naar **Data collection** > **Hosts**
2. Klik **Create host**
3. Configureer:
   - **Host name**: `Cloudflare - KlantNaam`
   - **Groups**: `Cloud Services` (maak aan als deze niet bestaat)
   - **Interfaces**: Voeg een Agent interface toe met IP `127.0.0.1` (Zabbix vereist minimaal 1 interface)
4. Tab **Templates**: koppel **Cloudflare Health**
5. Tab **Macros**: overschrijf `{$CF.DOMAIN}` met het echte klantdomein (bijv. `klant.nl`)
6. Klik **Add**

### Stap 3: Meerdere klanten

Maak per klant een aparte host aan met dezelfde template maar een ander `{$CF.DOMAIN}`:

```
Cloudflare - Klant A  →  {$CF.DOMAIN} = klant-a.nl
Cloudflare - Klant B  →  {$CF.DOMAIN} = klant-b.com
Cloudflare - Klant C  →  {$CF.DOMAIN} = klant-c.nl
```

**Tip**: De Cloudflare status API items (overall + components) worden per host gepolled. Als je dit wilt optimaliseren, maak dan 1 host "Cloudflare Global" aan voor de status API en aparte hosts per klant met alleen de domein-specifieke checks.

### Stap 4: Controleren

Na 5-10 minuten, ga naar **Monitoring** > **Latest data** en filter op de host. Je zou moeten zien:

```
cf.status.indicator     = none
cf.component.cdn        = operational
cf.component.dns        = operational
cf.http.status[klant.nl] = 200
cf.http.resptime[klant.nl] = 0.45
cf.ssl.days[klant.nl]   = 82
```

---

## Troubleshooting

**Items krijgen geen data**
- Heeft de Zabbix Server internet? Test: `curl https://www.cloudflarestatus.com/api/v2/status.json`
- Is ICMP toegestaan? Test: `ping 1.1.1.1`

**Simple checks werken niet**
- Simple checks draaien op de Zabbix Server (of Proxy als de host aan een proxy gekoppeld is)
- `net.dns.record` vereist dat de server DNS queries kan uitvoeren

**SSL check werkt niet**
- `web.certificate.get` is beschikbaar vanaf Zabbix 6.4+
- De server moet een TLS verbinding kunnen maken op poort 443

**Component status is leeg**
- Controleer of de JSONPath preprocessing correct werkt via **Test** in de item configuratie
- Cloudflare kan component namen wijzigen; controleer de huidige namen via `curl https://www.cloudflarestatus.com/api/v2/components.json`
