# Zabbix Monitoring - Onderzoek & Plan

## Doel
Multi-tenant monitoring voor meerdere klanten, elk met eigen netwerk.

---

## 1. Zabbix Server Setup

- **Zabbix Server**: Centrale installatie (Docker of bare-metal)
- **Database**: PostgreSQL of MySQL
- **Frontend**: Zabbix web UI (nginx + PHP)

## 2. Multi-tenant / Multi-klant opzet

| Concept | Beschrijving |
|---------|-------------|
| **Host Groups** | Per klant een eigen host group (bijv. `Klant-A`, `Klant-B`) |
| **Templates** | Herbruikbare templates per type server/dienst |
| **User Groups** | Per klant een user group met alleen zicht op eigen hosts |
| **Proxies** | Per klantnetwerk een Zabbix Proxy voor bereikbaarheid |

### Zabbix Proxy per klant
- Draait in het netwerk van de klant
- Communiceert outbound naar Zabbix Server (poort 10051)
- Geen inbound firewall rules nodig bij klant
- Verzamelt lokaal data en stuurt door naar centrale server

## 3. Server Health Monitoring (Zabbix Agent)

**Zabbix Agent 2** installeren op elke server:

- CPU load & usage
- Memory usage
- Disk usage & I/O
- Network traffic
- Process monitoring
- Log file monitoring
- Windows services / Linux systemd units
- Uptime

**Agent communicatie**:
- Agent -> Proxy (in klantnetwerk)
- Proxy -> Zabbix Server (centraal)

## 4. Externe Diensten Monitoren (zonder agent)

### Simple Checks (vanuit Zabbix Server/Proxy)
- **ICMP Ping**: beschikbaarheid + latency
- **TCP Port check**: is een poort open?
- **HTTP check**: website bereikbaar?

### HTTP Agent (ingebouwd)
- HTTP/HTTPS requests naar externe diensten
- Response time meten
- Status code checken
- Content matching (bevat pagina verwachte tekst?)

### Voorbeelden externe monitoring

| Dienst | Methode | Wat te meten |
|--------|---------|-------------|
| **Cloudflare** | HTTP Agent | Status page, DNS response time, API health |
| **Microsoft 365** | HTTP Agent | Service health endpoint |
| **DNS** | Simple check | DNS lookup response time |
| **VPN endpoints** | ICMP/TCP | Bereikbaarheid + latency |
| **Websites klanten** | HTTP Agent | Uptime, response time, SSL expiry |

## 5. Cloudflare Monitoring - Specifiek

### 5.1 Overall Status (GRATIS, geen API key)

**Endpoint**: `https://www.cloudflarestatus.com/api/v2/status.json`

Retourneert:
```json
{
  "status": {
    "indicator": "none|minor|major|critical",
    "description": "All Systems Operational"
  }
}
```

**Zabbix configuratie**:
- Item type: **HTTP Agent**
- URL: `https://www.cloudflarestatus.com/api/v2/status.json`
- Request type: GET
- Interval: 1m-5m
- **JSONPath preprocessing**: `$.status.indicator`

**Triggers**:
| Severity | Conditie | Beschrijving |
|----------|----------|-------------|
| Warning | `indicator = "minor"` | Cloudflare minor outage - controleer klant impact |
| High | `indicator = "major"` | Cloudflare major outage - klanten waarschijnlijk getroffen |
| Disaster | `indicator = "critical"` | Cloudflare critical outage - alle klanten getroffen |

### 5.2 Per Component Monitoring (GRATIS, geen API key)

**Endpoint**: `https://www.cloudflarestatus.com/api/v2/components.json`

Belangrijkste componenten om te monitoren:

| Component | Waarom relevant |
|-----------|----------------|
| **CDN/Cache** | Websites klanten laden niet als dit offline is |
| **Authoritative DNS** | Domeinen van klanten resolven niet meer |
| **DDoS Protection** | Klanten zijn onbeschermd |
| **SSL** | HTTPS werkt niet meer voor klanten |
| **Dashboard / API** | Wij kunnen niks configureren |
| **Workers** | Als klanten Workers gebruiken |
| **Regio: Europe** | Relevant als klanten in EU zitten |

**Zabbix aanpak** - Dependent items:
1. **Master item**: HTTP Agent haalt volledige components.json op (1x per 3 min)
2. **Dependent items**: Per component een item met JSONPath filter
   - JSONPath voorbeeld CDN: `$.components[?(@.name=="CDN/Cache")].status.first()`
   - Mogelijke waarden: `operational`, `degraded_performance`, `partial_outage`, `major_outage`

**Triggers per component**:
```
Trigger: Cloudflare CDN degraded
  Expression: last(/Cloudflare/cf.component.cdn)<>"operational"
  Severity: High

Trigger: Cloudflare DNS outage
  Expression: last(/Cloudflare/cf.component.dns)<>"operational"
  Severity: Disaster
```

### 5.3 Actieve Tests vanuit Zabbix (eigen metingen)

Naast de status API ook zelf testen of Cloudflare werkt:

| Test | Zabbix Item Type | Details |
|------|-----------------|---------|
| **DNS resolve** | Simple Check `net.dns.record` | Resolve een klantdomein, meet response time |
| **HTTPS response** | HTTP Agent | GET naar klantwebsite, check status 200 + response time |
| **SSL cert expiry** | HTTP Agent + preprocessing | Dagen tot SSL verlopen |
| **Ping latency** | Simple Check `icmpping` | Latency naar Cloudflare edge (1.1.1.1) |

**Trigger voorbeelden**:
```
Trigger: Klantwebsite response time > 3s
  Expression: last(/Cloudflare/http.response.time[klantsite.nl]) > 3
  Severity: Warning

Trigger: Klantwebsite onbereikbaar
  Expression: last(/Cloudflare/http.status[klantsite.nl]) <> 200
  Severity: High

Trigger: SSL certificaat verloopt binnen 14 dagen
  Expression: last(/Cloudflare/ssl.expiry[klantsite.nl]) < 14
  Severity: Warning

Trigger: Cloudflare DNS resolve mislukt
  Expression: last(/Cloudflare/net.dns.record[,klantsite.nl]) = 0
  Severity: Disaster
```

### 5.4 Cloudflare API Monitoring (optioneel, API token nodig)

Als je een Cloudflare API token hebt kun je ook meten:
- Requests per zone (per klantdomein)
- Geblokkeerde threats
- Bandwidth usage
- Cache hit ratio
- Firewall events

Dit is **nice-to-have**, niet nodig voor basis health monitoring.

### 5.5 Aanbevolen Template: "Cloudflare Health"

Samenvatting van het template dat we gaan bouwen:

```
Template: "Template Cloudflare Health"

Items:
  - cf.status.overall          (HTTP Agent, 3m interval)
  - cf.component.cdn           (Dependent item)
  - cf.component.dns           (Dependent item)
  - cf.component.ddos          (Dependent item)
  - cf.component.ssl           (Dependent item)
  - cf.component.api           (Dependent item)
  - cf.component.europe        (Dependent item)
  - cf.ping.1111               (Simple check, 1m interval)
  - cf.dns.resolve[{$DOMAIN}]  (Simple check, 2m interval)
  - cf.http.status[{$DOMAIN}]  (HTTP Agent, 2m interval)
  - cf.http.resptime[{$DOMAIN}](HTTP Agent, 2m interval)
  - cf.ssl.expiry[{$DOMAIN}]   (HTTP Agent, 6h interval)

Triggers:
  - Cloudflare overall status != none         -> Warning/High/Disaster
  - Cloudflare CDN niet operational            -> High
  - Cloudflare DNS niet operational            -> Disaster
  - Ping naar 1.1.1.1 faalt                   -> High
  - DNS resolve klantdomein faalt              -> Disaster
  - HTTP status != 200                         -> High
  - Response time > 3s                         -> Warning
  - SSL expiry < 14 dagen                     -> Warning
  - SSL expiry < 7 dagen                      -> High

Macros:
  {$DOMAIN} = in te vullen per host (klantdomein)

Dashboard widgets:
  - Cloudflare overall status (singlestat)
  - Component status overzicht (tabel)
  - Response time grafiek per klantdomein
  - Actieve problemen lijst
```

## 6. Dashboard Mogelijkheden

- **Per klant dashboard**: overzicht van alle hosts + services
- **Global dashboard**: overzicht alle klanten (alleen voor beheerders)
- **Maps**: visuele netwerktopologie per klant
- **SLA reports**: uptime rapportages per klant
- **Widgets**: grafieken, problemen, top-N, kaarten

## 7. Alerting

- Email notificaties
- Slack / Teams integratie
- Escalatie regels (bijv. eerst engineer, dan manager)
- Per klant eigen notificatie-instellingen

---

## Open Vragen

- [ ] Hoeveel klanten / servers initieel?
- [ ] Waar draait de Zabbix Server? (eigen DC, cloud?)
- [ ] Hebben klanten al agents draaien of is alles nieuw?
- [ ] Welke OS'en bij klanten? (Windows/Linux mix?)
- [ ] Budget voor Zabbix? (open source vs enterprise)
- [ ] Welke externe diensten naast Cloudflare nog meer monitoren?
- [ ] Moeten klanten zelf toegang tot Zabbix dashboard?

---

## Volgende Stappen

1. Open vragen beantwoorden
2. Architectuur tekening maken
3. Proof of Concept opzetten (1 server + 1 proxy + 1 agent)
4. Templates bouwen voor standaard monitoring
5. Externe checks configureren (Cloudflare etc.)
6. Dashboards inrichten
