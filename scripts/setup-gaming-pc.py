#!/usr/bin/env python3
"""
Setup script: Importeert de Windows Gaming PC template in Zabbix,
maakt een host aan en koppelt de template.

Gebruik: python3 setup-gaming-pc.py
"""

import sys
import os

from zabbix_utils import ZabbixAPI

# === CONFIGURATIE ===
ZABBIX_URL = "http://10.0.0.104/zabbix"
ZABBIX_USER = "Admin"
ZABBIX_PASS = "zabbix"

GAMING_PC_HOST = "Gaming-PC"
GAMING_PC_IP = "10.0.0.156"
GAMING_PC_PORT = "10050"

HOST_GROUP_NAME = "Gaming PCs"
TEMPLATE_NAME = "Windows Gaming PC"
TEMPLATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "templates", "gaming-pc", "windows-gaming-pc.yaml"
)


def main():
    # --- Stap 1: Inloggen ---
    print(f"[1/5] Inloggen op {ZABBIX_URL}...")
    try:
        api = ZabbixAPI(ZABBIX_URL)
        api.login(user=ZABBIX_USER, password=ZABBIX_PASS)
        print(f"  OK - Ingelogd als {ZABBIX_USER}")
    except Exception as e:
        print(f"  FOUT - Kan niet inloggen: {e}")
        sys.exit(1)

    try:
        # --- Stap 2: Template importeren ---
        print(f"\n[2/5] Template importeren uit {TEMPLATE_FILE}...")
        template_path = os.path.abspath(TEMPLATE_FILE)
        with open(template_path, "r") as f:
            template_yaml = f.read()

        try:
            api.configuration.import_(
                format="yaml",
                source=template_yaml,
                rules={
                    "template_groups": {"createMissing": True, "updateExisting": False},
                    "templates": {"createMissing": True, "updateExisting": True},
                    "items": {"createMissing": True, "updateExisting": True},
                    "triggers": {"createMissing": True, "updateExisting": True},
                    "valueMaps": {"createMissing": True, "updateExisting": True},
                }
            )
            print("  OK - Template geimporteerd")
        except Exception as e:
            print(f"  WAARSCHUWING - Import fout: {e}")
            print("  Probeer verder met bestaande template...")

        # --- Stap 3: Template ID ophalen ---
        print(f"\n[3/5] Template '{TEMPLATE_NAME}' opzoeken...")
        templates = api.template.get(
            output=["templateid", "name"],
            filter={"host": [TEMPLATE_NAME]}
        )
        if not templates:
            print(f"  FOUT - Template '{TEMPLATE_NAME}' niet gevonden!")
            print("  Importeer de template handmatig via de Zabbix UI.")
            sys.exit(1)
        template_id = templates[0]["templateid"]
        print(f"  OK - Template gevonden (ID: {template_id})")

        # --- Stap 4: Host group aanmaken ---
        print(f"\n[4/5] Host group '{HOST_GROUP_NAME}' aanmaken...")
        groups = api.hostgroup.get(
            output=["groupid"],
            filter={"name": [HOST_GROUP_NAME]}
        )
        if groups:
            group_id = groups[0]["groupid"]
            print(f"  OK - Host group bestaat al (ID: {group_id})")
        else:
            result = api.hostgroup.create(name=HOST_GROUP_NAME)
            group_id = result["groupids"][0]
            print(f"  OK - Host group aangemaakt (ID: {group_id})")

        # --- Stap 5: Host aanmaken ---
        print(f"\n[5/5] Host '{GAMING_PC_HOST}' aanmaken ({GAMING_PC_IP})...")
        hosts = api.host.get(
            output=["hostid"],
            filter={"host": [GAMING_PC_HOST]}
        )
        if hosts:
            host_id = hosts[0]["hostid"]
            print(f"  OK - Host bestaat al (ID: {host_id}), template wordt bijgewerkt...")
            api.host.update(
                hostid=host_id,
                groups=[{"groupid": group_id}],
                templates=[{"templateid": template_id}],
            )
            print("  OK - Template gekoppeld aan bestaande host")
        else:
            result = api.host.create(
                host=GAMING_PC_HOST,
                name="Gaming PC",
                groups=[{"groupid": group_id}],
                templates=[{"templateid": template_id}],
                interfaces=[{
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": GAMING_PC_IP,
                    "dns": "",
                    "port": GAMING_PC_PORT
                }]
            )
            host_id = result["hostids"][0]
            print(f"  OK - Host aangemaakt (ID: {host_id})")

        # --- Klaar ---
        print("\n" + "=" * 50)
        print("KLAAR! Samenvatting:")
        print(f"  Template:   {TEMPLATE_NAME} (ID: {template_id})")
        print(f"  Host group: {HOST_GROUP_NAME} (ID: {group_id})")
        print(f"  Host:       {GAMING_PC_HOST} / {GAMING_PC_IP} (ID: {host_id})")
        print(f"\nDashboard: {ZABBIX_URL}/zabbix.php?action=host.dashboard.view&hostid={host_id}")
        print("=" * 50)

    finally:
        api.logout()


if __name__ == "__main__":
    main()
