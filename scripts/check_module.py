#!/usr/bin/env python3
"""Check ontology/aidoc-lex.ttl against the rules of the LEX Extension.

Errors (exit code 1):
  - vendored core differs from vendor/LOCK.json (the core must not be modified)
  - module does not parse, or its ontology header is incomplete
  - a triple has a subject outside the aidoc-lex namespace (no axioms about core or reference terms)
  - a term lacks an English rdfs:label or rdfs:comment, or breaks the naming convention
  - an object or datatype property lacks rdfs:domain or rdfs:range; a class lacks rdfs:subClassOf
  - a referenced IRI (domain, range, superclass, superproperty, ...) is not declared in the
    module, the core or the vendored reference ontologies
Warnings (errors with --strict):
  - a term is not grounded: neither a requirement in requirements/requirements.ttl uses it
    (lexreq:usesTerm) nor a competency query in cq/ mentions it; a class is also grounded
    through a grounded subclass
  - rdfs:isDefinedBy missing; local name also used in the core; style findings in labels/comments
"""
from __future__ import annotations

import argparse
import re
import sys

from rdflib import BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD, DCTERMS, Namespace

from common import (CORE_ONTOLOGY_IRIS, CORE_NS, CORE_TTL, CQ_DIR, LEX_NS, LEX_ONTOLOGY_IRIS,
                    LEX_PREFIX, MODULE_TTL, REQ_NS, REQUIREMENTS_TTL, load_graph, qname,
                    reference_graph, verify_lock)
from style import findings as style_findings

VANN = Namespace("http://purl.org/vocab/vann/")
TERM_TYPES = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty}
REF_PREDICATES = [RDFS.domain, RDFS.range, RDFS.subClassOf, RDFS.subPropertyOf,
                  OWL.equivalentClass, OWL.equivalentProperty, OWL.inverseOf, OWL.disjointWith]
BUILTIN = (str(XSD), str(RDF), str(RDFS), str(OWL))
CORE_VERSION_IRI_PREFIX = "https://w3id.org/aidoc-ap/"


class Report:
    def __init__(self, strict: bool):
        self.strict, self.errors, self.warnings = strict, [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        (self.errors if self.strict else self.warnings).append(msg)


def lang_values(g, s, p, lang="en"):
    return [o for o in g.objects(s, p) if isinstance(o, Literal) and o.language == lang]


def union_members(g, node):
    if isinstance(node, BNode):
        lst = g.value(node, OWL.unionOf) or g.value(node, OWL.intersectionOf)
        if lst is not None:
            out = []
            while lst is not None and lst != RDF.nil:
                first = g.value(lst, RDF.first)
                if first is not None:
                    out.append(first)
                lst = g.value(lst, RDF.rest)
            return out
    return [node]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", default=str(MODULE_TTL))
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors (use before a release)")
    args = ap.parse_args()
    rep = Report(args.strict)

    for p in verify_lock():
        rep.error(p)

    try:
        g = load_graph([args.module])
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: module does not parse: {exc}")
        return 1
    core = load_graph([CORE_TTL])
    refs = reference_graph()

    # 1. ontology header
    onts = [s for s in g.subjects(RDF.type, OWL.Ontology)]
    if len(onts) != 1 or str(onts[0]) not in LEX_ONTOLOGY_IRIS:
        rep.error(f"expected exactly one owl:Ontology with IRI in {sorted(LEX_ONTOLOGY_IRIS)}, found {onts}")
    ont = onts[0] if onts else None
    if ont is not None:
        imports = [str(o) for o in g.objects(ont, OWL.imports)]
        core_version_iri = re.compile(re.escape(CORE_VERSION_IRI_PREFIX) + r"\d+(\.\d+)*$")
        if not any(i in CORE_ONTOLOGY_IRIS or core_version_iri.match(i) for i in imports):
            rep.error("module must owl:imports the AIDOC-AP core (ontology IRI or a version IRI)")
        for p, name in [(OWL.versionIRI, "owl:versionIRI"), (OWL.versionInfo, "owl:versionInfo"),
                        (DCTERMS.title, "dcterms:title"), (DCTERMS.license, "dcterms:license"),
                        (DCTERMS.description, "dcterms:description")]:
            if g.value(ont, p) is None:
                rep.error(f"ontology header lacks {name}")
        if str(g.value(ont, VANN.preferredNamespacePrefix)) != LEX_PREFIX:
            rep.error(f"vann:preferredNamespacePrefix must be '{LEX_PREFIX}'")
        if str(g.value(ont, VANN.preferredNamespaceUri)) != LEX_NS:
            rep.error(f"vann:preferredNamespaceUri must be '{LEX_NS}'")

    # 2. subject rule: only module terms (and blank nodes) may appear as subjects
    for s in sorted({s for s in g.subjects() if isinstance(s, URIRef)}, key=str):
        if ont is not None and s == ont:
            continue
        if not str(s).startswith(LEX_NS):
            n = len(list(g.triples((s, None, None))))
            rep.error(f"{n} triple(s) about non-module term {qname(s)}: the module may only describe its own terms")

    # 3. term-level checks
    terms = sorted({s for t in TERM_TYPES for s in g.subjects(RDF.type, t) if str(s).startswith(LEX_NS)}, key=str)
    core_locals = {str(s)[len(CORE_NS):] for s in core.subjects() if str(s).startswith(CORE_NS)}

    def declared(iri: URIRef) -> bool:
        s = str(iri)
        return (s.startswith(BUILTIN) or (iri, None, None) in g or (iri, None, None) in core
                or (iri, None, None) in refs)

    for t in terms:
        local = str(t)[len(LEX_NS):]
        types = set(g.objects(t, RDF.type))
        is_class = OWL.Class in types
        labels = lang_values(g, t, RDFS.label)
        comments = lang_values(g, t, RDFS.comment)
        if len(labels) != 1:
            rep.error(f"{qname(t)}: needs exactly one rdfs:label@en (found {len(labels)})")
        if not comments:
            rep.error(f"{qname(t)}: needs an rdfs:comment@en")
        if is_class and not re.fullmatch(r"[A-Z][A-Za-z0-9]*", local):
            rep.error(f"{qname(t)}: class names use UpperCamelCase")
        if not is_class and not re.fullmatch(r"[a-z][A-Za-z0-9]*", local):
            rep.error(f"{qname(t)}: property names use lowerCamelCase")
        if not is_class and labels and str(labels[0])[:1].isupper():
            rep.warn(f"{qname(t)}: property labels start in lower case, as in the core")
        if is_class and g.value(t, RDFS.subClassOf) is None:
            rep.error(f"{qname(t)}: class must be placed in the hierarchy (rdfs:subClassOf)")
        if types & {OWL.ObjectProperty, OWL.DatatypeProperty}:
            if g.value(t, RDFS.domain) is None:
                rep.error(f"{qname(t)}: property needs rdfs:domain")
            if g.value(t, RDFS.range) is None:
                rep.error(f"{qname(t)}: property needs rdfs:range")
        if OWL.DatatypeProperty in types:
            for r in g.objects(t, RDFS.range):
                if isinstance(r, URIRef) and not (str(r).startswith(str(XSD)) or r in (RDFS.Literal, RDF.langString)):
                    rep.warn(f"{qname(t)}: datatype property range {qname(r)} is not an XSD datatype or rdfs:Literal")
        if g.value(t, RDFS.isDefinedBy) is None:
            rep.warn(f"{qname(t)}: add rdfs:isDefinedBy <https://w3id.org/aidoc-ap/lex#>")
        if local in core_locals:
            rep.warn(f"{qname(t)}: local name '{local}' is also used in the core; consider a distinct name")
        for lit in labels + comments:
            f = style_findings(str(lit))
            if f:
                rep.warn(f"{qname(t)}: style ({', '.join(f)}) in '{str(lit)[:60]}'")

    # 4. every referenced IRI resolves
    for t in terms:
        for p in REF_PREDICATES:
            for o in g.objects(t, p):
                for m in union_members(g, o):
                    if isinstance(m, URIRef) and not declared(m):
                        rep.error(f"{qname(t)} {qname(p)} {qname(m)}: target is not declared in module, core or reference ontologies")

    # 5. grounding: a requirement uses the term, or a competency query mentions it
    used = set()
    if REQUIREMENTS_TTL.exists():
        used = set(load_graph([REQUIREMENTS_TTL]).objects(None, URIRef(REQ_NS + "usesTerm")))
    cq_text = "\n".join(p.read_text(encoding="utf-8") for p in sorted(CQ_DIR.glob("*.rq"))) if CQ_DIR.exists() else ""
    def mentioned(t):
        local = str(t)[len(LEX_NS):]
        return t in used or re.search(rf"({LEX_PREFIX}:{re.escape(local)}\b|<{re.escape(str(t))}>)", cq_text)

    grounded = {t for t in terms if mentioned(t)}
    # an upper class is grounded through a grounded subclass
    grounded |= {t for t in terms if any(s in grounded for s in g.transitive_subjects(RDFS.subClassOf, t))}
    for t in terms:
        if OWL.AnnotationProperty in set(g.objects(t, RDF.type)):
            continue
        if t not in grounded:
            rep.warn(f"{qname(t)}: not grounded (no requirement uses it or a subclass of it, and no competency query in cq/ mentions it)")

    for w in rep.warnings:
        print("WARN: ", w)
    for e in rep.errors:
        print("ERROR:", e)
    print(f"{len(terms)} module term(s); {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
