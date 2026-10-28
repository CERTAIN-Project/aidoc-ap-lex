#!/usr/bin/env python3
"""Build the extra pages of the module documentation, next to the Widoco reference.

examples.html: one section per framework (AI Act, ALTAI, OECD, gender) with the formalised
  competency questions, the SPARQL query, its result over the example graphs and the example data
  behind the result. Each query is an article whose id is the file name of the query without .rq,
  so that requirements.html can link to it.

Input: examples/*.ttl, cq/*.rq, requirements/requirements.ttl.

  python3 scripts/build_docs_pages.py --out site-extra
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import shutil
import sys

from rdflib import Graph, URIRef

from common import CORE_TTL, CQ_DIR, EXAMPLES_DIR, LEX_NS, MODULE_TTL, REPORTS, REQUIREMENTS_TTL, ROOT, VENDOR, load_graph

EX_NS = "https://w3id.org/aidoc-ap/lex/example/"
PREFIXES = {
    "aidoc": "https://w3id.org/aidoc-ap#", "aidoc-lex": LEX_NS, "ex": EX_NS, "prov": "http://www.w3.org/ns/prov#",
    "dqv": "http://www.w3.org/ns/dqv#", "mls": "http://www.w3.org/ns/mls#", "dcterms": "http://purl.org/dc/terms/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#", "xsd": "http://www.w3.org/2001/XMLSchema#",
    "dpv-aiact": "https://w3id.org/dpv/legal/eu/aiact#", "skos": "http://www.w3.org/2004/02/skos/core#",
}
REQ_NS = "https://w3id.org/aidoc-ap/lex/requirements#"
PREFIXES["lexreq"] = REQ_NS
PREFIXES["aiact"] = "https://w3id.org/aidoc-ap/requirements#"
PREFIXES["airo"] = "https://w3id.org/airo#"
PREFIXES["dpv-ai"] = "https://w3id.org/dpv/ai#"
FRAMEWORKS = [("aiact", "EU AI Act"), ("altai", "ALTAI"), ("oecd", "OECD AI Principles"), ("gender", "Gender requirements (CERTAIN D3.2)")]


def short(v) -> str:
    if v is None:
        return ""
    s = str(v)
    for p, ns in PREFIXES.items():
        if isinstance(v, URIRef) and s.startswith(ns):
            return f"{p}:{s[len(ns):]}"
    return s


def header(text: str) -> dict:
    out = {}
    for key in ("CQ", "Question", "Requirement", "Terms"):
        m = re.search(rf"^#\s*{key}:\s*(.+)$", text, re.M)
        out[key] = m.group(1).strip() if m else ""
    return out


def turtle_of(data: Graph, nodes: list) -> str:
    sub = Graph()
    for p, ns in PREFIXES.items():
        sub.bind(p, ns)
    for n in nodes:
        for t in data.triples((n, None, None)):
            sub.add(t)
    text = sub.serialize(format="turtle")
    return "\n".join(l for l in text.splitlines() if not l.startswith("@prefix")).strip()


def page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="assets/pages.css">
</head>
<body>
<header><nav><a href="index.html">AIDOC-AP LEX Extension</a> · <a href="requirements.html">Requirements</a> · <a href="examples.html">Worked examples</a> · <a href="alignments.html">Alignments</a></nav></header>
<main>
{body}
</main>
<footer>AIDOC-AP LEX Extension · CERTAIN project (Horizon Europe, grant agreement 101189650) · CC BY 4.0</footer>
</body>
</html>
"""


def examples_page() -> str:
    files = sorted(EXAMPLES_DIR.glob("*.ttl"))
    data = Graph()
    for f in files:
        data.parse(f)
    g = load_graph([CORE_TTL, VENDOR / "annex_4.ttl", MODULE_TTL, REQUIREMENTS_TTL, *files])
    req = load_graph([REQUIREMENTS_TTL])
    by_fw = {}
    for f in sorted(CQ_DIR.glob("*.rq")):
        text = f.read_text(encoding="utf-8")
        rid = header(text)["Requirement"].split(":", 1)[-1]
        by_fw.setdefault(rid.split("-", 1)[0], []).append((f, text, rid))

    parts = ["<h1>Worked examples</h1>",
             "<p class=\"lead\">How the module documents that an AI system meets legal and ethical requirements, shown on an "
             "example graph of a high-risk CV screening system (AI Act Annex III, point 4(a)). Each competency question "
             "comes from the <a href=\"requirements.html\">requirements</a>; below it are the SPARQL query, its answer over "
             "the example and the example data behind the answer. Organisations, persons, figures and dates in the example are invented.</p>",
             "<p>Example graphs: " + ", ".join(f'<a href="examples/{f.name}">{f.name}</a>' for f in files) + ".</p>",
             "<nav class=\"toc\">" + " ".join(f'<a href="#{k}">{html.escape(t)}</a>' for k, t in FRAMEWORKS if k in by_fw) + "</nav>"]
    for key, title in FRAMEWORKS:
        if key not in by_fw:
            continue
        parts.append(f'<section id="{key}"><h2>{html.escape(title)}</h2>')
        for f, text, rid in by_fw[key]:
            h = header(text)
            label = req.value(URIRef(REQ_NS + rid), URIRef("http://www.w3.org/2000/01/rdf-schema#label"))
            res = g.query(text)
            cols = [str(v) for v in res.vars]
            rows = list(res)
            parts.append(f'<article id="{f.stem}"><h3>{html.escape(h["CQ"])}</h3>')
            parts.append(f'<p class="hint">Requirement: <a href="requirements.html#show-{rid}">{html.escape(str(label or rid))}</a></p>')
            parts.append("<p class=\"terms\">Module terms: " + ", ".join(f"<code>{html.escape(t.strip())}</code>"
                                                                   for t in h["Terms"].split(",") if t.strip()) + "</p>")
            table = ["<table><thead><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in cols) + "</tr></thead><tbody>"]
            for r in rows[:12]:
                table.append("<tr>" + "".join(f"<td>{html.escape(short(v))}</td>" for v in r) + "</tr>")
            table.append("</tbody></table>")
            if len(rows) > 12:
                table.append(f"<p class=\"hint\">{len(rows) - 12} further rows.</p>")
            parts.append("".join(table))
            nodes = []
            for r in rows[:3]:
                for v in r:
                    if isinstance(v, URIRef) and str(v).startswith(EX_NS) and v not in nodes \
                            and any(str(p).startswith(LEX_NS) for p in data.predicates(v, None)):
                        nodes.append(v)
            if nodes:
                parts.append("<details><summary>Example data</summary><pre>" + html.escape(turtle_of(data, nodes[:2])) + "</pre></details>")
            query = "\n".join(l for l in text.splitlines() if not l.startswith("#")).strip()
            parts.append(f"<details><summary>SPARQL query ({f.name})</summary><pre>" + html.escape(query) + "</pre></details></article>")
        parts.append("</section>")
    return page("Worked examples · AIDOC-AP LEX Extension", "\n".join(parts))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPORTS / "site-extra"))
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    (out / "assets").mkdir(parents=True, exist_ok=True)
    (out / "examples").mkdir(exist_ok=True)
    (out / "examples.html").write_text(examples_page(), encoding="utf-8")
    shutil.copy(ROOT / "documentation" / "assets" / "pages.css", out / "assets" / "pages.css")
    for f in EXAMPLES_DIR.glob("*.ttl"):
        shutil.copy(f, out / "examples" / f.name)
    print(f"wrote {out}/examples.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
