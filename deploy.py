#!/usr/bin/env python3
"""Deploy the NCR app (single index.html) to Vercel project protokol-ncr."""
import json, subprocess, sys

VERCEL = "/opt/hatch/bin/vercel"
TEAM = "team_nlqFD2dq4q704gftJuIbzq6g"
PROJECT_ID = "prj_etmop3CL5vHvUBp1vLwgcsjWN3PN"
PROJECT_NAME = "protokol-ncr"
SRC = "/home/hatch/workspace/goals/protokol-peru-real-estate-production-readiness/files/ncr-gdc-nc-2026/index.html"

def call_tool(name, args):
    proc = subprocess.run(
        [VERCEL, "call-tool", "--name", name, "--arguments-json", json.dumps(args)],
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        print(f"!! {name} failed (exit {proc.returncode}): {proc.stdout} {proc.stderr}", file=sys.stderr)
        sys.exit(1)
    outer = json.loads(proc.stdout)
    if not outer.get("ok"):
        print(f"!! {name} returned not-ok: {proc.stdout[:2000]}", file=sys.stderr)
        sys.exit(1)
    return json.loads(outer["result"]["content"][0]["text"])

def main():
    data = open(SRC, encoding="utf-8").read()
    print(f"deploying {PROJECT_NAME} ({len(data)} bytes) ...", flush=True)
    res = call_tool("create_deployment", {
        "requestBody": {
            "name": PROJECT_NAME,
            "project": PROJECT_ID,
            "target": "production",
            "files": [{"file": "index.html", "data": data, "encoding": "utf-8"}],
        },
        "teamId": TEAM,
        "forceNew": "1",
        "skipAutoDetectionConfirmation": "1",
    })
    result = res.get("result", res)
    print(f"  deployment id: {result.get('id')}")
    print(f"  url: {result.get('url')}")
    print(f"  state: {result.get('readyState')}")

if __name__ == "__main__":
    main()
