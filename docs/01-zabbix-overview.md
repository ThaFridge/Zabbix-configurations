# Zabbix Overzicht & Architectuur

## Wat is Zabbix?

Zabbix is een open-source enterprise monitoring platform voor netwerken, servers, cloud, applicaties en services. Het biedt real-time monitoring, alerting, visualisatie en automatisering zonder licentiekosten.

## Architectuur

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Zabbix      │────▶│  Zabbix      │────▶│  Database        │
│  Agents      │     │  Server      │     │  (PostgreSQL/    │
│  (op hosts)  │     │              │     │   MySQL/Oracle)  │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
┌─────────────┐     ┌──────▼───────┐
│  SNMP        │────▶│  Zabbix      │
│  Devices     │     │  Frontend    │
└─────────────┘     │  (Web UI)    │
                    └──────────────┘
┌─────────────┐
│  Zabbix      │──── Optioneel: voor gedistribueerde monitoring
│  Proxy       │     en remote locaties
└─────────────┘
```

## Kerncomponenten

### 1. Zabbix Server
- Centrale component die data ontvangt en verwerkt
- Evalueert triggers, stuurt notificaties
- Slaat alle configuratie en historische data op

### 2. Zabbix Agent (Classic & Agent 2)
- **Agent Classic**: C-gebaseerd, bewezen en stabiel
- **Agent 2**: Go-gebaseerd, plugin-architectuur, moderne features
  - Native plugins voor: Docker, MongoDB, PostgreSQL, MySQL, Redis, Memcached, etc.
  - Ondersteunt custom plugins
  - Kan als Windows service draaien

### 3. Zabbix Proxy
- Verzamelt data namens de server (voor remote/distributed monitoring)
- Buffer modes: **Disk**, **Memory**, **Hybrid**
- Proxy load balancing & HA (nieuw in 7.0)

### 4. Zabbix Frontend
- Web-based UI (PHP)
- Dashboards, grafieken, maps, rapportage
- Volledig configureerbaar via GUI of API

### 5. Database
- Ondersteund: PostgreSQL (aanbevolen), MySQL/MariaDB, Oracle, TimescaleDB
- TimescaleDB voor betere performance bij grote installaties

## Data Collection Methoden

| Methode | Beschrijving | Gebruik |
| ------- | ------------ | ------- |
| Zabbix Agent | Actief/passief agent op host | OS metrics, logs, processen |
| SNMP | v1/v2c/v3 polling & traps | Netwerkapparatuur, printers |
| IPMI | Intelligent Platform Management | Hardware health (servers) |
| JMX | Java Management Extensions | Java applicaties |
| HTTP Agent | HTTP/HTTPS requests | REST APIs, webservices |
| SSH/Telnet | Remote commands | Apparaten zonder agent |
| Calculated | Berekende items | Afgeleide metrics |
| Dependent | Afgeleid van master item | Eenmalig ophalen, meervoudig parsen |
| Script | Custom scripts (Agent 2) | Alles wat je kunt scripten |
| Prometheus | Prometheus metrics scraping | Cloud-native applicaties |
| Browser | Headless browser checks (7.0+) | Web monitoring met screenshots |

## Zabbix 7.0 LTS - Belangrijkste Features

- **Async pollers**: 10-100x betere performance, tot 1000 gelijktijdige checks per poller
- **Proxy HA & load balancing**: Automatische failover en schaling
- **Browser monitoring**: Multi-step browser scenarios met screenshots
- **Configureerbare timeouts**: Per item-type, per proxy, per item
- **MFA**: TOTP en Duo Universal Prompt
- **LDAP/AD JIT provisioning**: Automatisch gebruikers aanmaken bij eerste login
- **Nieuwe dashboard widgets**: Uitgebreidere visualisatie opties
- **Template dashboards**: Alle widget types nu ondersteund

## Zabbix 8.0 LTS (verwacht Q2 2026)

- **OpenTelemetry integratie**: Volledige OTEL ondersteuning
- **Complex Event Processing**: Automatische event correlatie, deduplicatie
- **NetFlow support**: Netwerkverkeer analyse
- **Nieuwe storage engine**: Geoptimaliseerd voor grote volumes
- **Mobile App**: iOS en Android met push notifications
- **Zero-config network discovery**: Automatische netwerk mapping

## Bronnen

- [Zabbix 7.0 What's New](https://www.zabbix.com/whats_new_7_0)
- [Zabbix Documentatie](https://www.zabbix.com/documentation/current/en/manual)
- [Zabbix 7.0 Blog](https://blog.zabbix.com/zabbix-7-0-everything-you-need-to-know/28210/)
- [Zabbix Roadmap](https://www.zabbix.com/roadmap)
