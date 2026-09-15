#!/usr/bin/env python3
"""The mock app. Stdlib only -- the fixture is not the product.

IT REPORTS TWO FACTS SEPARATELY, and that is the entire design:

    x-env    how this build BEHAVES   (development | test | production)
    x-host   where it is PLACED       (laptop | staging-1 | prod-1 | ...)
    x-build  which build

Every earlier rebuild served one header that meant both, and so could not
answer "is this staging box actually running production behaviour?" -- a
question whose answer decides whether its verdict is worth anything.

    RAILS_ENV=production APP_HOST=staging-1 PORT=3003 ./server.py
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = os.environ.get("RAILS_ENV", "development")
HOST = os.environ.get("APP_HOST", "laptop")
BUILD = os.environ.get("BUILD_SHA", "0000000")
PORT = int(os.environ.get("PORT", "3000"))


def load_env(name):
    """Read the behaviour profile. A name with no file is not an environment.

    Rails has exactly three and refuses the rest. `staging` reaching here is
    the footgun this repo exists to show: it is a HOST, and asking for it as
    an environment must fail loudly rather than fall back to development.
    """
    p = ROOT / "config" / "environments" / f"{name}.rb"
    if not p.exists():
        avail = sorted(x.stem for x in (ROOT / "config" / "environments").glob("*.rb"))
        sys.exit(
            f"RAILS_ENV={name!r} is not an environment. Available: {avail}.\n"
            f"If you meant a PLACE, that is APP_HOST -- see apps/core/hosts.tsv.\n"
            f"`staging` in particular is a host that RUNS production; it is not\n"
            f"an environment, and inventing one turns production-only code off."
        )
    cfg = {}
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line.startswith('"'):
            continue
        k, _, v = line.partition("=>")
        k = k.strip().strip('",')
        v = v.strip().rstrip(",").strip()
        cfg[k] = {"true": True, "false": False}.get(v, v.strip('"'))
    return cfg


def host_row(name):
    """What hosts.tsv says about this placement, if anything."""
    f = ROOT / "hosts.tsv"
    for line in f.read_text().splitlines():
        if line.startswith("#") or "\t" not in line:
            continue
        c = line.split("\t")
        if c[0] == name:
            return {"host": c[0], "env": c[1], "port": c[2],
                    "lifetime": c[3], "authorizing": c[4] == "yes"}
    return None


CFG = load_env(ENV)
ROW = host_row(HOST)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        # THE DISAGREEMENT IS REPORTED, NOT RESOLVED. If hosts.tsv says this
        # placement runs `production` and RAILS_ENV says `development`, the
        # app does not pick a winner -- it serves both and says they differ.
        # Something that silently reconciles two records of one fact is how
        # the two collapsed into one in the first place.
        declared = ROW["env"] if ROW else None
        agrees = (declared == ENV) if declared else None

        body = {
            "env": ENV, "host": HOST, "build": BUILD,
            "behaviour": CFG,
            "host_declared_env": declared,
            "env_matches_declaration": agrees,
            "authorizing": bool(ROW and ROW["authorizing"] and CFG.get("authorizing")),
            "why": (
                "a verdict from here can authorize: the host is trusted to stand in "
                "for production AND it runs production behaviour"
                if ROW and ROW["authorizing"] and CFG.get("authorizing") else
                "a verdict from here authorizes nothing"
            ),
        }
        out = json.dumps(body, indent=2).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("x-env", ENV)
        self.send_header("x-host", HOST)
        self.send_header("x-build", BUILD)
        if agrees is False:
            self.send_header("x-env-disagrees-with-host", f"host declares {declared}")
        self.end_headers()
        self.wfile.write(out)


if __name__ == "__main__":
    print(f"core  env={ENV}  host={HOST}  build={BUILD}  :{PORT}", flush=True)
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
