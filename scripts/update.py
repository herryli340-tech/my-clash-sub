import base64
import json
from pathlib import Path
from urllib.parse import unquote

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources.txt"
OUT = ROOT / "dist" / "clash.yaml"

UA = "clash-auto-update/2.0"
TIMEOUT = 20
MAX_NODES = 120


def decode_text(data):
    data = data.strip()

    if any(x in data for x in (
        "proxies:",
        "proxy-groups:",
        "ss://",
        "vmess://",
        "vless://",
        "trojan://",
        "hysteria2://"
    )):
        return data

    try:
        decoded = base64.b64decode(
            data + "=" * (-len(data) % 4)
        ).decode("utf-8", "ignore")

        if decoded.strip():
            return decoded
    except Exception:
        pass

    return data


def fetch(url):
    r = requests.get(
        url,
        headers={"User-Agent": UA},
        timeout=TIMEOUT
    )
    r.raise_for_status()
    return decode_text(r.text)


def parse_yaml(text):
    try:
        obj = yaml.safe_load(text)

        if isinstance(obj, dict) and isinstance(
            obj.get("proxies"), list
        ):
            return [
                p for p in obj["proxies"]
                if isinstance(p, dict)
            ]

    except Exception:
        pass

    return []


def parse_vmess(line):
    try:
        raw = base64.b64decode(
            line[8:] + "=" * (-len(line[8:]) % 4)
        ).decode()

        d = json.loads(raw)

        server = d.get("add")

        if not server:
            return None

        return {
            "name": d.get("ps") or server,
            "type": "vmess",
            "server": server,
            "port": int(d.get("port", 443)),
            "uuid": d.get("id"),
            "cipher": "auto",
            "tls": d.get("tls") in ("tls", "1", True),
            "network": d.get("net", "tcp"),
        }

    except Exception:
        return None


def parse_lines(text):
    nodes = []

    for line in text.splitlines():

        line = unquote(line.strip())

        if line.startswith("vmess://"):

            node = parse_vmess(line)

            if node:
                nodes.append(node)

    return nodes


def normalize(nodes):

    result = []
    seen = set()

    for node in nodes:

        if not isinstance(node, dict):
            continue

        name = str(
            node.get("name")
            or node.get("server")
            or ""
        ).strip()

        server = str(
            node.get("server") or ""
        ).strip()

        port = node.get("port")

        if not name or not server or not port:
            continue

        try:
            port = int(port)
        except Exception:
            continue

        node = dict(node)

        node["name"] = name[:70]
        node["server"] = server
        node["port"] = port

        key = (
            node.get("type"),
            server,
            port,
            node.get("uuid"),
            node.get("password")
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(node)

        if len(result) >= MAX_NODES:
            break

    return result


def main():

    urls = [
        x.strip()
        for x in SOURCES.read_text(
            encoding="utf-8"
        ).splitlines()
        if x.strip()
        and not x.lstrip().startswith("#")
    ]

    nodes = []

    for url in urls:

        try:

            text = fetch(url)

            parsed = parse_yaml(text)

            if not parsed:
                parsed = parse_lines(text)

            nodes.extend(parsed)

            print(
                f"OK {url}: {len(parsed)} nodes"
            )

        except Exception as e:

            print(
                f"ERROR {url}: {e}"
            )

    nodes = normalize(nodes)

    names = [
        node["name"]
        for node in nodes
    ]

    config = {

        "mixed-port": 7890,

        "allow-lan": True,

        "mode": "rule",

        "log-level": "info",

        "ipv6": False,

        "dns": {
            "enable": True,
            "enhanced-mode": "fake-ip",
            "nameserver": [
                "https://1.1.1.1/dns-query",
                "https://dns.google/dns-query"
            ]
        },

        "proxies": nodes,

        "proxy-groups": [

            {
                "name": "🚀 自动选择",
                "type": "url-test",
                "proxies": names,
                "url": "https://www.gstatic.com/generate_204",
                "interval": 300,
                "tolerance": 100
            },

            {
                "name": "🤖 ChatGPT",
                "type": "select",
                "proxies": [
                    "🚀 自动选择",
                    "DIRECT"
                ]
            },

            {
                "name": "🔎 Google",
                "type": "select",
                "proxies": [
                    "🚀 自动选择",
                    "DIRECT"
                ]
            },

            {
                "name": "📺 YouTube",
                "type": "select",
                "proxies": [
                    "🚀 自动选择",
                    "DIRECT"
                ]
            }
        ],

        "rules": [

            "DOMAIN-SUFFIX,openai.com,🤖 ChatGPT",
            "DOMAIN-SUFFIX,chatgpt.com,🤖 ChatGPT",
            "DOMAIN-SUFFIX,oaistatic.com,🤖 ChatGPT",

            "DOMAIN-SUFFIX,google.com,🔎 Google",
            "DOMAIN-SUFFIX,googleapis.com,🔎 Google",
            "DOMAIN-SUFFIX,gstatic.com,🔎 Google",

            "DOMAIN-SUFFIX,youtube.com,📺 YouTube",
            "DOMAIN-SUFFIX,youtube-nocookie.com,📺 YouTube",
            "DOMAIN-SUFFIX,googlevideo.com,📺 YouTube",
            "DOMAIN-SUFFIX,ytimg.com,📺 YouTube",

            "GEOIP,CN,DIRECT",

            "MATCH,🚀 自动选择"
        ]
    }

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUT.write_text(
        yaml.safe_dump(
            config,
            allow_unicode=True,
            sort_keys=False
        ),
        encoding="utf-8"
    )

    print(
        f"TOTAL={len(nodes)}"
    )

    if not nodes:
        raise SystemExit(
            "No usable nodes parsed."
        )


if __name__ == "__main__":
    main()
