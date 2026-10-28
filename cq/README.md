# Competency queries

One SPARQL file per formalised competency question, named after the article, ALTAI requirement, OECD principle or gender section and a topic (for example `art09_1_risk_management_system.rq`). Each file starts with four header lines:

```sparql
# CQ: What risk management system has been established for the high-risk AI system?
# Question: lexreq:aiact-art9-1-cq1
# Requirement: lexreq:aiact-art9-1
# Terms: aidoc-lex:RiskManagementSystem, aidoc-lex:accountableAgent, aidoc-lex:hasManagementSystem, aidoc-lex:includesDocument
```

The question text is copied from the requirements graph, and the question links back to the file with `lexreq:formalisedBy`; `make test` checks that both agree. `make cq` runs every query over the core, its Annex IV requirements, the module, the requirements graph and the graphs in examples/, and reports the number of rows. The worked examples page of the documentation shows each query with its answer; the requirements page links to it.
