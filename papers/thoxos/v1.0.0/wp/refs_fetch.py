"""Fetch exact arXiv metadata for every candidate reference and record it.

Writes wp/refs_raw.json with title, authors (in order), published and updated
dates, and the abs URL, straight from the arXiv export API. Nothing is typed
from memory. Entries that fail to resolve are recorded as unresolved.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

CANDIDATES = {
    "asterinas": "2506.03876",
    "aios": "2403.16971",
    "aiosvision": "2312.03815",
    "agentoslessons": "2607.25076",
    "agenticos": "2509.01245",
    "litmus": "2605.10779",
    "safeclaw": "2606.18356",
    "rustylinux": "2407.18431",
    "qwen25": "2412.15115",
    "modelcards": "1810.03993",
    "ragents": "2504.11703",
}


def fetch(ids: list[str]) -> dict[str, dict]:
    url = "https://export.arxiv.org/api/query?id_list=" + ",".join(ids) + f"&max_results={len(ids)}"
    req = urllib.request.Request(url, headers={"User-Agent": "thox-refs-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    out: dict[str, dict] = {}
    for entry in root.findall("a:entry", NS):
        eid = entry.findtext("a:id", default="", namespaces=NS)
        arxiv_id = eid.rsplit("/abs/", 1)[-1]
        base = arxiv_id.split("v")[0]
        title = " ".join(entry.findtext("a:title", default="", namespaces=NS).split())
        authors = [" ".join(a.findtext("a:name", default="", namespaces=NS).split())
                   for a in entry.findall("a:author", NS)]
        out[base] = {
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "published": entry.findtext("a:published", default="", namespaces=NS),
            "updated": entry.findtext("a:updated", default="", namespaces=NS),
            "journal_ref": entry.findtext("arxiv:journal_ref", default="", namespaces=NS),
            "doi": entry.findtext("arxiv:doi", default="", namespaces=NS),
            "url": f"https://arxiv.org/abs/{base}",
        }
    return out


def main() -> int:
    ids = list(CANDIDATES.values())
    got: dict[str, dict] = {}
    for i in range(0, len(ids), 10):
        chunk = ids[i:i + 10]
        for attempt in range(3):
            try:
                got.update(fetch(chunk))
                break
            except Exception as exc:  # noqa: BLE001
                print("retry", chunk, exc, file=sys.stderr)
                time.sleep(3)
        time.sleep(3)
    result = {}
    for key, aid in CANDIDATES.items():
        if aid in got and got[aid]["title"]:
            result[key] = got[aid] | {"status": "resolved"}
        else:
            result[key] = {"arxiv_id": aid, "status": "unresolved"}
    Path(__file__).with_name("refs_raw.json").write_text(json.dumps(result, indent=2))
    for key, rec in result.items():
        print(f"{key:14s} {rec['status']:10s} {rec.get('arxiv_id','')}: {rec.get('title','')[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
