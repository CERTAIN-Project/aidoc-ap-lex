# Examples

Instance graphs that show the LEX Extension on realistic data. `make cq` loads every `*.ttl` file in this folder together with the AIDOC-AP core, its Annex IV requirements, the module and the requirements graph, and runs the competency queries in cq/ over them. Instance IRIs use the namespace `https://w3id.org/aidoc-ap/lex/example/`.

The graphs are examples, not records: organisations, persons, figures and dates are invented.

## hr_screening_system.ttl

TalentScreen, a CV screening system of an SME provider deployed by a logistics company: a high-risk AI system under Annex III, point 4(a) of the AI Act.

| Requirements | What the example shows |
|---|---|
| Article 9 | risk management system with policy, procedure and register; risk assessment with categorised risks; risk control measures with control functions; compliance test |
| Article 10 | data governance framework, design choice, data set with original purpose, assumptions, special category data and retention period; data gap and its remediation; processing record; bias assessment and gender audit |
| Article 11 | technical documentation linked to Annex IV requirements; simplified documentation of an SME |
| Article 12 | log entries with event types and the person who verified a result |
| Articles 13, 15 | instructions for use with declared metrics; measurements per group of applicants; predetermined change; security, resilience and maintenance measures |
| Article 14 | provider and deployer oversight measures, stop and override mechanisms, assigned overseers, training |
| Articles 16, 17 | quality management system with typed procedures; accountability framework; conformity assessment, CE marking, EU registration, accessibility |
| Articles 72, 73 | post-market monitoring system; serious incident with initial and complete report, investigation, corrective action and communication with the authority and the notified body |
| AIDOC-AP core | data sets and their preparation, model and evaluation, interfaces, applied standards, hardware, change log, post-market monitoring |
| ALTAI, OECD, D3.2 | fundamental rights, data protection, gender, work and environmental impact assessments; technology acceptance study; trade-off assessment; audit; worker consultation; redress, reporting channel and data subject rights |
