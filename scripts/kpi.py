#!/usr/bin/env python3
"""Compute KPI 1.2, Integration Success Rate, over requirements/requirements.ttl.

A requirement counts as integrated when
  1. every term it uses (lexreq:usesTerm) is declared in the core, the module or a reused vocabulary,
  2. it has at least one competency question, and
  3. at least one of its competency questions is formalised as a query in cq/ that returns
     rows over the example graphs.
The rate is the share of integrated requirements; the target is 0.90. The report lists the
counts after each condition, per framework.
"""
from __future__ import annotations

import argparse
import collections
import pathlib

from rdflib import Namespace
from rdflib.namespace import RDF

from common import (CORE_TTL, EXAMPLES_DIR, MODULE_TTL, REPORTS, REQUIREMENTS_TTL, ROOT, VENDOR,
                    load_graph, reference_graph)

REQ = Namespace("https://w3id.org/aidoc-ap/lex/requirements#")
AIACT = Namespace("https://w3id.org/aidoc-ap/requirements#")
TARGET = 0.90
STEPS = ["requirements", "terms declared", "with competency question", "formalised", "answered"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--md", default=str(REPORTS / "kpi-1-2.md"))
    args = ap.parse_args()

    reqs = load_graph([REQUIREMENTS_TTL])
    known = load_graph([CORE_TTL, VENDOR / "annex_4.ttl", MODULE_TTL]) + reference_graph()
    data = load_graph([CORE_TTL, VENDOR / "annex_4.ttl", MODULE_TTL, REQUIREMENTS_TTL,
                       *sorted(EXAMPLES_DIR.glob("*.ttl"))])

    answered_files = {}
    for path in {str(o) for o in reqs.objects(None, REQ.formalisedBy)}:
        try:
            answered_files[path] = len(list(data.query((ROOT / path).read_text(encoding="utf-8")))) > 0
        except Exception:  # noqa: BLE001
            answered_files[path] = False

    counts = collections.defaultdict(collections.Counter)
    for r in reqs.subjects(RDF.type, REQ.Requirement):
        fw = str(reqs.value(r, REQ.framework)).split("#")[-1]
        cqs = list(reqs.objects(r, AIACT.hasCompetencyQuestion))
        files = [str(f) for q in cqs for f in reqs.objects(q, REQ.formalisedBy)]
        steps = [True,
                 all((t, None, None) in known for t in reqs.objects(r, REQ.usesTerm)),
                 bool(cqs),
                 bool(files),
                 any(answered_files.get(f) for f in files)]
        for i, name in enumerate(STEPS):
            if all(steps[:i + 1]):
                counts[fw][name] += 1
                counts["total"][name] += 1

    total = counts["total"]
    rate = total["answered"] / total["requirements"] if total["requirements"] else 0.0
    head = "| Framework | " + " | ".join(STEPS) + " |"
    lines = [head, "|" + "---|" * (len(STEPS) + 1)]
    for fw in sorted(k for k in counts if k != "total") + ["total"]:
        lines.append(f"| {fw} | " + " | ".join(str(counts[fw][s]) for s in STEPS) + " |")
    summary = f"KPI 1.2 Integration Success Rate: {total['answered']}/{total['requirements']} = {rate:.3f} (target {TARGET:.2f})"
    REPORTS.mkdir(exist_ok=True)
    pathlib.Path(args.md).write_text("# KPI 1.2\n\n" + summary + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
