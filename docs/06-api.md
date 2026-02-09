# Zabbix API & Automatisering

## Overzicht

De Zabbix API is een HTTP-based JSON-RPC 2.0 API waarmee je programmatisch:
- Configuraties ophalen en wijzigen
- Hosts, templates, items, triggers beheren
- Historische data opvragen
- Bulk operaties uitvoeren
- Integreren met andere systemen

## Authenticatie

```bash
# Stap 1: Inloggen en token ophalen
curl -s -X POST http://zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
      "username": "Admin",
      "password": "zabbix"
    },
    "id": 1
  }'

# Response:
# {"jsonrpc":"2.0","result":"AUTH_TOKEN_HIER","id":1}
```

Vanaf Zabbix 5.4+ kun je ook API tokens aanmaken in de UI (geen login nodig).

## Veelgebruikte API Methoden

### Hosts

```bash
# Alle hosts ophalen
curl -s -X POST http://zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
      "output": ["hostid", "host", "name", "status"],
      "selectInterfaces": ["ip"],
      "selectGroups": ["name"]
    },
    "auth": "AUTH_TOKEN",
    "id": 1
  }'

# Host aanmaken
curl -s -X POST http://zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "host.create",
    "params": {
      "host": "linux-server-01",
      "groups": [{"groupid": "2"}],
      "templates": [{"templateid": "10001"}],
      "interfaces": [{
        "type": 1,
        "main": 1,
        "useip": 1,
        "ip": "192.168.1.100",
        "dns": "",
        "port": "10050"
      }]
    },
    "auth": "AUTH_TOKEN",
    "id": 1
  }'
```

### Templates

```bash
# Templates ophalen
curl -s -X POST http://zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "template.get",
    "params": {
      "output": ["templateid", "name"],
      "filter": {
        "name": ["Linux by Zabbix agent"]
      }
    },
    "auth": "AUTH_TOKEN",
    "id": 1
  }'
```

### Problemen

```bash
# Actieve problemen ophalen
curl -s -X POST http://zabbix-server/api_jsonrpc.php \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "problem.get",
    "params": {
      "output": "extend",
      "selectTags": "extend",
      "recent": true,
      "severities": [3, 4, 5],
      "sortfield": "eventid",
      "sortorder": "DESC",
      "limit": 20
    },
    "auth": "AUTH_TOKEN",
    "id": 1
  }'
```

## Python met zabbix_utils

De officiele Python library voor Zabbix API:

```bash
pip install zabbix_utils
```

```python
from zabbix_utils import ZabbixAPI

# Verbinding maken
api = ZabbixAPI("http://zabbix-server")
api.login("Admin", "zabbix")

# Of met API token (geen login nodig):
# api = ZabbixAPI("http://zabbix-server", token="API_TOKEN")

# Alle hosts ophalen
hosts = api.host.get(
    output=["hostid", "host", "name"],
    selectInterfaces=["ip"]
)
for host in hosts:
    print(f"{host['name']}: {host['interfaces'][0]['ip']}")

# Bulk hosts aanmaken
new_hosts = [
    {"name": f"web-server-{i:02d}", "ip": f"10.0.1.{i+10}"}
    for i in range(1, 11)
]

for h in new_hosts:
    api.host.create(
        host=h["name"],
        groups=[{"groupid": "2"}],
        templates=[{"templateid": "10001"}],
        interfaces=[{
            "type": 1, "main": 1, "useip": 1,
            "ip": h["ip"], "dns": "", "port": "10050"
        }]
    )

# Template exporteren
export = api.configuration.export(
    options={"templates": ["10001"]},
    format="yaml"
)
with open("template-export.yaml", "w") as f:
    f.write(export)

# Template importeren
with open("template-export.yaml", "r") as f:
    api.configuration.import_(
        format="yaml",
        source=f.read(),
        rules={
            "templates": {"createMissing": True, "updateExisting": True},
            "items": {"createMissing": True, "updateExisting": True},
            "triggers": {"createMissing": True, "updateExisting": True},
            "discoveryRules": {"createMissing": True, "updateExisting": True}
        }
    )

api.logout()
```

## Ansible Integratie

```yaml
# Ansible playbook voor Zabbix configuratie
- hosts: localhost
  collections:
    - community.zabbix
  tasks:
    - name: Create host group
      community.zabbix.zabbix_group:
        server_url: http://zabbix-server
        login_user: Admin
        login_password: zabbix
        host_groups:
          - Linux servers
          - Web servers

    - name: Create host
      community.zabbix.zabbix_host:
        server_url: http://zabbix-server
        login_user: Admin
        login_password: zabbix
        host_name: "web-server-01"
        host_groups:
          - Linux servers
          - Web servers
        link_templates:
          - Linux by Zabbix agent
          - Nginx by HTTP
        interfaces:
          - type: agent
            main: 1
            ip: 192.168.1.100
            port: 10050
```

## Automatiseringsscenario's

| Scenario | API Methode | Beschrijving |
| -------- | ----------- | ------------ |
| Host provisioning | `host.create` | Automatisch hosts toevoegen vanuit CMDB |
| Maintenance windows | `maintenance.create` | Maintenance plannen voor deployments |
| Report generatie | `history.get` / `trend.get` | Custom rapporten genereren |
| Template sync | `configuration.export/import` | Templates synchroniseren tussen omgevingen |
| Bulk updates | `host.massupdate` | Meerdere hosts tegelijk aanpassen |
| Cleanup | `host.delete` | Verouderde hosts opruimen |

## Bronnen

- [Zabbix API Documentatie](https://www.zabbix.com/documentation/current/en/manual/api)
- [zabbix_utils Python Library](https://blog.zabbix.com/python-zabbix-utils/27056/)
- [Zabbix API Blog](https://blog.zabbix.com/zabbix-api-explained/9155/)
- [Advanced API Use Cases](https://blog.zabbix.com/advanced-zabbix-api-5-api-use-cases-to-improve-your-api-workflows/16801/)
- [Ansible Zabbix Collection](https://docs.ansible.com/ansible/latest/collections/community/zabbix/)
