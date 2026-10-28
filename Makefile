# AIDOC-AP LEX Extension: tooling entry points.
PY ?= $(shell [ -x .venv/bin/python ] && echo .venv/bin/python || echo python3)
MODULE := ontology/aidoc-lex.ttl

.PHONY: setup check check-strict cq test lint-text merged alignments docs-pages site serve set-version release all release-check fetch-core

setup:
	python3 -m venv .venv
	.venv/bin/pip install --quiet --upgrade pip
	.venv/bin/pip install --quiet -r requirements.txt
	@[ -f vendor/aidoc-ap/aidoc-ap.ttl ] || PY="$(CURDIR)/.venv/bin/python" bash scripts/fetch_core.sh
	@echo "venv ready: .venv"

check:
	$(PY) scripts/check_module.py --module $(MODULE)

check-strict:
	$(PY) scripts/check_module.py --module $(MODULE) --strict

reports:
	mkdir -p reports

cq: | reports
	$(PY) scripts/run_cqs.py

test:
	$(PY) -m pytest -q tests

alignments:
	$(PY) scripts/alignments.py

docs-pages:
	$(PY) scripts/build_docs_pages.py --out reports/site-extra
	$(PY) scripts/alignments.py --split-dir reports/site-extra/resources
	cp alignments/proposed-reified.ttl reports/site-extra/resources/aidoc-lex-alignments.ttl

# Local build of the documentation site, same steps as .github/workflows/widoco.yml
WIDOCO_VERSION := 1.4.25

widoco.jar:
	curl -sSL -o widoco.jar "https://github.com/dgarijo/Widoco/releases/download/v$(WIDOCO_VERSION)/widoco-$(WIDOCO_VERSION)-jar-with-dependencies_JDK-17.jar"

site: widoco.jar docs-pages
	rm -rf site
	java -Xmx1G -jar widoco.jar -ontFile $(MODULE) -outFolder site -confFile documentation/config.properties \
		-includeAnnotationProperties -rewriteAll -webVowl -excludeProvenance -noPlaceHolderText -uniteSections
	cp site/index-en.html site/index.html
	cp -R reports/site-extra/. site/
	mkdir -p site/assets
	cp $(MODULE) requirements/requirements.ttl documentation/requirements.html documentation/alignments.html site/
	cp documentation/assets/* site/assets/
	@if [ -d versions ]; then cp -R versions/. site/; fi

# The requirements and alignments pages fetch Turtle files, which browsers block for file:// URLs
serve: site
	@echo "http://localhost:8000/"
	$(PY) -m http.server -d site 8000

set-version:
	@test -n "$(VERSION)" || (echo "usage: make set-version VERSION=0.3" && exit 1)
	$(PY) scripts/set_version.py --version $(VERSION)

release: release-check
	@test -n "$(VERSION)" || (echo "usage: make release VERSION=1.0" && exit 1)
	$(PY) scripts/set_version.py --version $(VERSION) --release
	@echo "Release files updated. Review the diff, commit, tag v$(VERSION); publishing steps: RELEASE.md"

lint-text:
	$(PY) scripts/style.py $(wildcard documentation/*.html README.md)

merged: | reports
	$(PY) scripts/merge.py --out reports/framework_merged.ttl

all: check test cq alignments

release-check: check-strict test cq alignments

fetch-core:
	bash scripts/fetch_core.sh
