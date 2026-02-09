# Template: Windows Gaming PC

Monitor je gaming PC via Zabbix Agent 2 met service checks, performance metrics en game server latency.

## Wat wordt er gemonitord?

### GPU Services (AMD)
| Item | Service/Proces | Trigger |
|------|---------------|---------|
| AMD External Events Utility | `AMD External Events Utility` | WARNING als gestopt |

### Gaming Launchers
| Item | Service/Proces | Trigger |
|------|---------------|---------|
| Steam Client Service | `Steam Client Service` | Geen (niet altijd actief) |
| Steam proces | `steam.exe` | Geen (informatief) |
| Epic Games Launcher | `EpicGamesLauncher.exe` | Geen (informatief) |
| Xbox Gaming Services | `GamingServices` | Geen (niet altijd actief) |
| Xbox Live Auth Manager | `XblAuthManager` | Geen (niet altijd actief) |
| Xbox Live Game Save | `XblGameSave` | Geen (niet altijd actief) |
| GOG Galaxy | `GalaxyClient.exe` | Geen (informatief) |

### Windows Core Services
| Item | Service naam | Trigger |
|------|-------------|---------|
| Defender Antivirus | `WinDefend` | **HIGH** als gestopt |
| Firewall | `mpssvc` | **HIGH** als gestopt |
| Audio Service | `Audiosrv` | **WARNING** als gestopt |
| DNS Client | `Dnscache` | **WARNING** als gestopt |
| DHCP Client | `Dhcp` | Geen (informatief) |
| Windows Update | `wuauserv` | Geen (stopt regelmatig, normaal) |
| Task Scheduler | `Schedule` | Geen (informatief) |

### Systeem Performance
| Item | Key | Trigger |
|------|-----|---------|
| CPU gebruik | `system.cpu.util` | WARNING bij >{$GAMING.CPU.UTIL.WARN}% (5 min gem.) |
| RAM beschikbaar % | `vm.memory.size[pavailable]` | WARNING bij <{$GAMING.RAM.AVAIL.WARN}% |
| RAM beschikbaar bytes | `vm.memory.size[available]` | Geen |
| RAM totaal | `vm.memory.size[total]` | Geen |
| Disk vrij % | `vfs.fs.size[{$GAMING.DISK.PATH},pfree]` | WARNING <10%, HIGH <5% |
| Disk vrij bytes | `vfs.fs.size[{$GAMING.DISK.PATH},free]` | Geen |
| Disk totaal | `vfs.fs.size[{$GAMING.DISK.PATH},total]` | Geen |
| Uptime | `system.uptime` | Geen |

### Netwerk Latency (game servers)
| Item | Standaard IP | Trigger |
|------|-------------|---------|
| Ping + latency server #1 | `1.1.1.1` (Cloudflare) | WARNING onbereikbaar / latency >50ms |
| Ping + latency server #2 | `155.133.248.34` (Steam EU) | WARNING onbereikbaar / latency >50ms |
| Ping + latency server #3 | `8.8.8.8` (Google) | WARNING onbereikbaar / latency >50ms |

> **Let op:** Ping checks draaien als Simple Checks op de Zabbix Server of Proxy. Voor nauwkeurige latency-metingen vanuit je gaming PC moet je een Zabbix Proxy op hetzelfde netwerk draaien.

## Vereisten

- **Zabbix Server** 7.0 of hoger
- **Zabbix Agent 2** geinstalleerd op de Windows gaming PC
- Optioneel: **Zabbix Proxy** op hetzelfde netwerk (voor nauwkeurige ping metingen)

## Installatie stappen

### 1. Zabbix Agent 2 installeren op de gaming PC

Download Zabbix Agent 2 voor Windows van de officiele website en installeer:

```
Server=<jouw-zabbix-server-ip>
ServerActive=<jouw-zabbix-server-ip>
Hostname=Gaming-PC
```

### 2. Template importeren

1. Ga naar **Data collection** > **Templates**
2. Klik **Import** (rechtsboven)
3. Selecteer `windows-gaming-pc.yaml`
4. Klik **Import**

### 3. Host aanmaken

1. Ga naar **Data collection** > **Hosts**
2. Klik **Create host**
3. Vul in:
   - **Host name**: `Gaming-PC` (moet overeenkomen met `Hostname` in agent config)
   - **Templates**: koppel `Windows Gaming PC`
   - **Host groups**: maak bijv. `Gaming PCs` aan
   - **Interfaces**: voeg een Agent interface toe met het IP van je gaming PC, poort `10050`

### 4. Macro's aanpassen (optioneel)

Pas de standaard macro's aan op host-niveau als dat nodig is:

| Macro | Standaard | Beschrijving |
|-------|-----------|-------------|
| `{$GAMING.DISK.PATH}` | `C:` | Wijzig naar `D:` als je games op een aparte schijf staan |
| `{$GAMING.GAMESERVER.1}` | `1.1.1.1` | Pas aan naar een game server die jij veel gebruikt |
| `{$GAMING.GAMESERVER.2}` | `155.133.248.34` | Valve/Steam Amsterdam |
| `{$GAMING.GAMESERVER.3}` | `8.8.8.8` | Google DNS |
| `{$GAMING.PING.WARN}` | `0.050` | Warning drempel in seconden (50ms) |
| `{$GAMING.PING.HIGH}` | `0.100` | High drempel in seconden (100ms) |
| `{$GAMING.CPU.UTIL.WARN}` | `95` | CPU warning drempel (%) |
| `{$GAMING.RAM.AVAIL.WARN}` | `10` | RAM beschikbaar warning drempel (%) |
| `{$GAMING.DISK.FREE.WARN}` | `10` | Disk vrij warning drempel (%) |
| `{$GAMING.DISK.FREE.HIGH}` | `5` | Disk vrij high drempel (%) |

## Service namen controleren

Niet zeker of een service op jouw PC bestaat? Controleer met PowerShell:

```powershell
# Alle services tonen
Get-Service | Format-Table Name, DisplayName, Status

# Specifieke service zoeken
Get-Service -Name "Steam*"
Get-Service -Name "AMD*"
Get-Service -Name "Xbl*"
Get-Service -Name "Gaming*"

# Of via de korte naam
sc query "WinDefend"
```

## Dashboard

De template bevat een ingebouwd dashboard "Gaming PC Overview" met:
- **Windows & GPU Services** - status van kritieke Windows services en AMD GPU
- **Gaming Launchers** - welke game clients draaien er
- **CPU & Geheugen** - performance grafiek
- **Game Server Latency** - ping grafiek naar 3 game servers
- **Actieve Problemen** - overzicht van alle triggers die afgaan

## Troubleshooting

### Items worden "Not supported"
- **Service.info items**: de service bestaat niet op je PC. Controleer met `Get-Service` (zie hierboven). Dit is normaal als je bijv. Steam niet hebt geinstalleerd.
- **Proc.num items**: Zabbix Agent 2 moet draaien als service (standaard na installatie).
- **Ping items**: deze draaien op de Zabbix Server/Proxy, niet op de agent. Controleer of de server het IP kan bereiken.

### Geen data van de agent
1. Controleer of Zabbix Agent 2 service draait: `Get-Service "Zabbix Agent 2"`
2. Controleer Windows Firewall: poort 10050 (TCP inbound) moet open staan
3. Test verbinding vanaf Zabbix Server: `zabbix_get -s <gaming-pc-ip> -k agent.ping`

### Game server ping geeft geen data
- Ping checks draaien op de Zabbix Server/Proxy, niet op de gaming PC
- Controleer of ICMP (ping) niet geblokkeerd wordt door de firewall van de server

## Extra services toevoegen

Wil je meer services monitoren? Voeg items toe in Zabbix:

1. Ga naar **Data collection** > **Hosts** > jouw gaming PC > **Items**
2. Klik **Create item**
3. Vul in:
   - **Name**: beschrijvende naam
   - **Type**: Zabbix agent
   - **Key**: `service.info[<service-naam>,state]`
   - **Type of information**: Numeric (unsigned)
   - **Value mapping**: Windows service state
4. Klik **Add**

Voorbeelden van extra services die je kunt monitoren:
- `service.info[Spooler,state]` - Print Spooler
- `service.info[BITS,state]` - Background Intelligent Transfer
- `service.info[EventLog,state]` - Windows Event Log
- `proc.num[Discord.exe]` - Discord client
- `proc.num[obs64.exe]` - OBS Studio (streaming)
