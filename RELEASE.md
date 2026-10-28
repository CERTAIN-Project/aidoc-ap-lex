# Release procedure

The repository prepares releases; publishing is done by the maintainer.

## Before the release

1. `make release-check` passes: module rules with warnings as errors (every term is grounded in a requirement or a competency query), tooling tests, every competency query returns rows over `examples/`, every alignment target exists in the vendored vocabularies.
2. The CI workflow `Module checks` passes on the default branch, including the HermiT consistency check.
3. `make docs-pages` builds the worked examples page without errors; review it in `reports/site-extra/`.

## Release

1. `make release VERSION=1.0` runs the release checks, then sets the version and release date in `ontology/aidoc-lex.ttl`, `documentation/config.properties`, `CITATION.cff` and `.zenodo.json`, removes the draft note from the ontology header and writes the snapshot `versions/1.0/aidoc-lex.ttl`. Update `owl:versionInfo` and `dcterms:modified` of `requirements/requirements.ttl` by hand if the requirements changed.
2. Review the diff, commit, tag `v1.0`.
3. Push the commit and the tag.

## Publishing (maintainer)

1. Repository: make `CERTAIN-Project/aidoc-ap-lex` public.
2. GitHub Pages: Settings, Pages, source "GitHub Actions", and the repository variable `PAGES_ENABLED` set to `true` (Settings, Secrets and variables, Actions). The workflow `Build & deploy documentation (Widoco)` then publishes the term reference, the requirements, worked examples and alignments pages and the version snapshots. Without the variable it only builds the site and offers it as the downloadable artifact `documentation-site`.
3. OOPS!: run the workflow `OOPS! pitfall scan` once by hand; it sends the ontology to EasyRDF and OOPS!.
4. Zenodo: enable the GitHub integration for the repository and create the GitHub release `v1.0`; Zenodo archives it with the metadata of `.zenodo.json` and assigns a DOI. Add the DOI to `CITATION.cff` and `README.md` in the next commit.
5. w3id: once the documentation site is online, open a pull request in `perma-id/w3id.org` that replaces `ids/aidoc-ap/.htaccess` with `release/w3id/aidoc-ap.htaccess` and adds the line given in `release/w3id/README.md` to `ids/aidoc-ap/README.md`, and check the redirects listed there after the merge.
