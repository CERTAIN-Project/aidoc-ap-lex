# AIDOC-AP LEX Extension (aidoc-lex): Legal and Ethical Requirements

Extension module of the [AIDOC-AP](https://w3id.org/aidoc-ap) application profile, developed in the CERTAIN project (Horizon Europe, grant agreement 101189650). The AIDOC-AP core describes the technical documentation of AI systems required by Annex IV of the EU AI Act. The extension adds the terms needed to document how an AI system meets legal and ethical requirements: the obligations of providers and deployers in Articles 9 to 17, 72 and 73 of the EU AI Act, and the ethical requirements of the Assessment List for Trustworthy AI (ALTAI), the OECD AI Principles and the gender requirements of CERTAIN deliverable D3.2. It covers management systems, assessments, measures, compliance documents, incidents and the organisations and persons involved, and publishes the requirements themselves with their competency questions and the evidence an organisation is expected to keep. It imports the core without changing any of its definitions and is aligned to DPV, the DPV AI Act extension, DPV-AI, AIRO and VAIR.

Status: draft of version 1.0, not released.

| | |
|---|---|
| Namespace | `https://w3id.org/aidoc-ap/lex#` (prefix `aidoc-lex`) |
| Ontology | [ontology/aidoc-lex.ttl](ontology/aidoc-lex.ttl): 77 classes, 27 object properties, 10 datatype properties, 6 concept schemes |
| Requirements | [requirements/requirements.ttl](requirements/requirements.ttl) (namespace `https://w3id.org/aidoc-ap/lex/requirements#`, prefix `lexreq`): 180 requirements, 476 competency questions, 45 of them formalised as SPARQL |
| Imports | AIDOC-AP core 1.2 |
| Documentation | [w3id.org/aidoc-ap/lex](https://certain-project.github.io/aidoc-ap-lex/): term reference, [requirements](https://certain-project.github.io/aidoc-ap-lex/requirements.html), [worked examples](https://certain-project.github.io/aidoc-ap-lex/examples.html), [alignments](https://certain-project.github.io/aidoc-ap-lex/alignments.html) |
| Licence | CC BY 4.0 for the ontology, requirements and documentation ([LICENSE-CC-BY.txt](LICENSE-CC-BY.txt)), Apache-2.0 for code ([LICENSE](LICENSE)) |
| Citation | [CITATION.cff](CITATION.cff) |

## Requirements

| Framework | Requirements | Scope |
|---|---|---|
| EU AI Act (Regulation (EU) 2024/1689) | 119 | Articles 9 to 17 and 72, 73, by paragraph and point; obligations of providers and deployers only |
| ALTAI | 49 | the seven requirements of the Assessment List for Trustworthy AI |
| OECD AI Principles | 5 | values-based principles 1.1 to 1.5 |
| [CERTAIN D3.2](https://certain-project.eu/wp-content/uploads/2026/02/CERTAIN_WP3_D3.2_Ethical-considerations-of-AI-compliance_V1.0-delivered.pdf) (Ethical considerations of AI compliance) | 7 | gender audit, QETAM, GIA and SGIA, gender risk register, gender balance, monitoring |

Each requirement has its text, competency questions, the ontology terms needed to answer them (`lexreq:usesTerm`) and the expected evidence (`lexreq:expectedEvidence`). The legal text follows the AI Act Service Desk of the European Commission at the time of the analysis. Terms proposed in the analysis were merged where they overlapped or mapped to existing AIDOC-AP, AIRO or DPV terms; [requirements/term-mapping.csv](requirements/term-mapping.csv) records the decision and rationale for each of the 364 proposed terms.

## Example

Any artefact, measure or activity can point to the requirement it is evidence for:

```turtle
@prefix aidoc-lex: <https://w3id.org/aidoc-ap/lex#> .
@prefix lexreq: <https://w3id.org/aidoc-ap/lex/requirements#> .
@prefix ex: <https://w3id.org/aidoc-ap/lex/example/> .

ex:Measure_Reweighting a aidoc-lex:BiasMitigationMeasure ;
    aidoc-lex:controlFunction aidoc-lex:Mitigation ;
    aidoc-lex:addressesRisk ex:Risk_GenderBias ;
    aidoc-lex:addressesRequirement lexreq:aiact-art10-2-g .
```

[examples/](examples/README.md) holds the compliance documentation of an invented high-risk CV screening system; [cq/](cq/README.md) holds the formalised competency questions, each answered over the example.

## Working with the repository

```bash
make setup      # Python virtual environment; fetches the pinned AIDOC-AP core
make all        # module checks, tooling tests, competency queries, alignments
```

| Command | Purpose |
|---|---|
| `make check` | module rules (`make check-strict` before a release) |
| `make test` | tooling tests and consistency of the requirements graph |
| `make cq` | competency queries over the examples |
| `make alignments` | check the SKOS alignment proposals in `alignments/` and write the alignment records |
| `make docs-pages` | worked examples page of the documentation |
| `make site`, `make serve` | build the documentation site locally with Widoco (needs Java 17 or later) and serve it on http://localhost:8000/ |
| `make merged` | core and module in one file without imports, for reasoners |
| `make release VERSION=1.0` | release files; see [RELEASE.md](RELEASE.md) |

| Path | Content |
|---|---|
| `ontology/` | the module |
| `requirements/` | requirements graph and the mapping of proposed terms |
| `cq/`, `examples/` | competency queries and example graph |
| `alignments/` | SKOS alignment proposals and their records |
| `documentation/` | Widoco configuration, introduction, requirements and alignments pages |
| `scripts/`, `tests/` | tooling and its tests |
| `release/` | w3id redirect rules |

Authors: Fabian Kovac (University of Applied Sciences St. Pölten), Konstantinos Amplianitis (University College Dublin), Sebastian Neumaier and Tobias Dam (University of Applied Sciences St. Pölten).
