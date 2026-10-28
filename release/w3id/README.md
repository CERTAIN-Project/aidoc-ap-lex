# w3id redirect for the LEX Extension

The redirects of AIDOC-AP live in `ids/aidoc-ap/.htaccess` of the [w3id repository](https://github.com/perma-id/w3id.org). Its last rule forwards every path below `aidoc-ap/` to `https://certain-project.github.io/aidoc-ap/`, so `https://w3id.org/aidoc-ap/lex` currently ends on a missing page of the core site.

`aidoc-ap.htaccess` in this folder is the complete proposed file: the current `ids/aidoc-ap/.htaccess` of the w3id repository (core and Lifecycle Extension rules, checked on 28 October 2026) with the rules for `lex` inserted before the default rules. The other rules are unchanged. The pull request replaces `ids/aidoc-ap/.htaccess` with it; check first that the w3id file has not changed since, and submit it once the documentation site of the extension is online, so that the redirects do not lead to missing pages.

The same pull request adds one line to `ids/aidoc-ap/README.md` of the w3id repository, after the line on the Lifecycle Extension:

```
The AIDOC-AP LEX Extension (https://w3id.org/aidoc-ap/lex, namespace https://w3id.org/aidoc-ap/lex#, requirements https://w3id.org/aidoc-ap/lex/requirements#) is documented at https://certain-project.github.io/aidoc-ap-lex/
```

The w3id directory lists Sebastian Neumaier as maintainer; the pull request should come from him or carry his approval.

Expected redirects (not yet tested in Apache):

| Request | Location |
|---|---|
| `https://w3id.org/aidoc-ap/lex` | `https://certain-project.github.io/aidoc-ap-lex/` |
| same, `Accept: text/turtle` | `.../aidoc-ap-lex/aidoc-lex.ttl` |
| same, `Accept: application/rdf+xml` or `application/owl+xml` | `.../aidoc-ap-lex/ontology.owl` |
| same, `Accept: application/ld+json` | `.../aidoc-ap-lex/ontology.jsonld` |
| `https://w3id.org/aidoc-ap/lex/requirements` | `.../aidoc-ap-lex/requirements.html` (the fragment, for example `#aiact-art9-1`, opens that requirement) |
| same, `Accept: text/turtle` | `.../aidoc-ap-lex/requirements.ttl` |
| `https://w3id.org/aidoc-ap/lex/1.0` | `.../aidoc-ap-lex/1.0/aidoc-lex.ttl` |
| `https://w3id.org/aidoc-ap/lex/example/...` | `.../aidoc-ap-lex/examples.html` |
| `https://w3id.org/aidoc-ap/`, `.../lifecycle` and other paths | unchanged |

After the merge, check the live redirects with `curl -sI` and the same `Accept` headers.
