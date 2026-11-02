"""Regression tests for the module checker and for the consistency of the requirements graph
(run: make test).

The checker must reject axioms about core terms; the requirements graph must keep its size,
every term it uses must resolve, and every formalised competency question must point to the
query file that names it.
"""
import csv
import pathlib
import re
import subprocess
import sys

from rdflib import Namespace, URIRef
from rdflib.namespace import RDF, RDFS

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import (CORE_TTL, CQ_DIR, LEX_NS, MODULE_TTL, REQUIREMENTS_TTL, TERM_MAPPING_CSV,  # noqa: E402
                    VENDOR, load_graph, reference_graph, verify_lock)

FIX = ROOT / "tests" / "fixtures"
REQ = Namespace("https://w3id.org/aidoc-ap/lex/requirements#")
AIACT = Namespace("https://w3id.org/aidoc-ap/requirements#")
REQS = load_graph([REQUIREMENTS_TTL])


def test_vendored_core_matches_lock():
    assert verify_lock() == []


def run_checker(module):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_module.py"), "--module", str(module)],
                          capture_output=True, text=True)


def test_checker_accepts_module():
    r = run_checker(MODULE_TTL)
    assert r.returncode == 0, r.stdout + r.stderr


def test_checker_rejects_rule_violations():
    r = run_checker(FIX / "bad_module.ttl")
    assert r.returncode == 1
    assert "non-module term aidoc:ModelPackaging" in r.stdout
    assert "needs exactly one rdfs:label@en" in r.stdout
    assert "not declared in module, core or reference ontologies" in r.stdout
    assert "property names use lowerCamelCase" in r.stdout


def test_requirements_size():
    reqs = set(REQS.subjects(RDF.type, REQ.Requirement))
    assert len(reqs) == 180
    frameworks = {REQS.value(r, REQ.framework) for r in reqs}
    assert frameworks == {REQ.AIAct, REQ.ALTAI, REQ.OECD, REQ.GenderD32}


def test_requirements_schema_extends_annex_iv_module():
    assert (REQ.Requirement, RDFS.subClassOf, AIACT.Requirement) in REQS
    assert (REQ.CompetencyQuestion, RDFS.subClassOf, AIACT.CompetencyQuestion) in REQS
    assert not list(REQS.triples((None, REQ.hasCompetencyQuestion, None)))


def test_every_competency_question_belongs_to_one_requirement():
    for cq in REQS.subjects(RDF.type, REQ.CompetencyQuestion):
        owners = list(REQS.subjects(AIACT.hasCompetencyQuestion, cq))
        assert len(owners) == 1, cq
        assert REQS.value(cq, RDFS.label), cq


def test_used_terms_resolve():
    known = load_graph([CORE_TTL, VENDOR / "annex_4.ttl", MODULE_TTL]) + reference_graph()
    missing = {t for t in REQS.objects(None, REQ.usesTerm) if (t, None, None) not in known}
    assert not missing, sorted(missing)


def test_term_mapping_targets_exist():
    module = load_graph([MODULE_TTL])
    for row in csv.DictReader(open(TERM_MAPPING_CSV, encoding="utf-8")):
        if row["target"].startswith("aidoc-lex:"):
            term = URIRef(LEX_NS + row["target"].split(":", 1)[1])
            assert (term, None, None) in module, row


def test_formalised_questions_match_query_files():
    linked = {str(cq).split("#")[1]: str(path) for cq, path in REQS.subject_objects(REQ.formalisedBy)}
    in_files = {}
    for f in sorted(CQ_DIR.glob("*.rq")):
        text = f.read_text(encoding="utf-8")
        q = re.search(r"^# Question: lexreq:(\S+)$", text, re.M).group(1)
        in_files[q] = f"cq/{f.name}"
        label = str(REQS.value(REQ[q], RDFS.label))
        assert re.search(rf"^# CQ: {re.escape(label)}$", text, re.M), f.name
    assert linked == in_files
