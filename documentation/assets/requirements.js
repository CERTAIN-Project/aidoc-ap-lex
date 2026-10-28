(async function(){

  // --- helpers --------------------------------------------------------------
  const $ = sel => document.querySelector(sel);
  const byId = id => document.getElementById(id);
  const esc = s => (s||'').replace(/[&<>"]/g,c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c]));

  const RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type';
  const RDFS = 'http://www.w3.org/2000/01/rdf-schema#';
  const DCTERMS = 'http://purl.org/dc/terms/';
  const SKOS = 'http://www.w3.org/2004/02/skos/core#';
  const FOAF = 'http://xmlns.com/foaf/0.1/';
  const OWL = 'http://www.w3.org/2002/07/owl#';
  const REQ = 'https://w3id.org/aidoc-ap/lex/requirements#';
  const ONTO = 'https://w3id.org/aidoc-ap/lex/requirements';
  const PREFIXES = [
    ['aidoc-lex:', 'https://w3id.org/aidoc-ap/lex#'], ['aidoc:', 'https://w3id.org/aidoc-ap#'],
    ['aiact:', 'https://w3id.org/aidoc-ap/requirements#'], ['dpv-aiact:', 'https://w3id.org/dpv/legal/eu/aiact#'],
    ['airo:', 'https://w3id.org/airo#'], ['prov:', 'http://www.w3.org/ns/prov#']
  ];
  const qname = iri => { for (const [p, ns] of PREFIXES) if (iri.startsWith(ns)) return p + iri.slice(ns.length); return iri; };

  // --- load data ------------------------------------------------------------
  async function loadScript(src){
    return new Promise((ok,ko)=>{ const s=document.createElement('script'); s.src=src; s.onload=ok; s.onerror=ko; document.head.appendChild(s); });
  }

  async function load(){
    await loadScript('https://unpkg.com/n3@1.17.4/browser/n3.min.js');
    const txt = await (await fetch(window.REQUIREMENTS_TTL || 'requirements.ttl', {cache:'no-store'})).text();
    const byS = new Map();
    for (const q of new N3.Parser().parse(txt)) {
      if (!byS.has(q.subject.id)) byS.set(q.subject.id, []);
      byS.get(q.subject.id).push(q);
    }
    const all = (s, p) => (byS.get(s) || []).filter(q => q.predicate.id === p).map(q => q.object);
    const one = (s, p) => { const o = all(s, p)[0]; return o ? o.value : null; };

    // metadata
    const authors = all(ONTO, DCTERMS+'creator').map(b => {
      const name = one(b.id, FOAF+'name'), org = one(b.id, FOAF+'organization');
      return org ? `${name} (${org})` : name;
    });
    byId('meta-created').textContent = one(ONTO, DCTERMS+'created') || 'N/A';
    byId('meta-modified').textContent = one(ONTO, DCTERMS+'modified') || 'N/A';
    byId('meta-version').textContent = one(ONTO, OWL+'versionInfo') || 'N/A';
    byId('meta-authors').textContent = authors.join(', ') || 'N/A';
    const lic = one(ONTO, DCTERMS+'license');
    byId('meta-license').innerHTML = lic ? `<a href="${esc(lic)}" target="_blank">${esc(lic)}</a>` : 'N/A';

    // requirements
    const reqs = [];
    for (const [s, qs] of byS) {
      if (!qs.some(q => q.predicate.id === RDF && q.object.id === REQ+'Requirement')) continue;
      const fw = one(s, REQ+'framework');
      const cqs = all(s, REQ+'hasCompetencyQuestion').map(o => ({
        id: o.id.split('#')[1], text: one(o.id, RDFS+'label'), query: one(o.id, REQ+'formalisedBy')
      })).sort((a, b) => Number(a.id.split('-cq')[1]) - Number(b.id.split('-cq')[1]));
      reqs.push({
        id: s.split('#')[1], uri: s,
        label: one(s, RDFS+'label') || s,
        framework: one(fw, SKOS+'notation') || fw,
        frameworkUri: fw,
        section: one(s, REQ+'section') || '',
        description: one(s, DCTERMS+'description') || '',
        source: one(s, DCTERMS+'source') || '',
        seeAlso: one(s, RDFS+'seeAlso'),
        sortKey: one(s, REQ+'sortKey') || s,
        normative: all(s, REQ+'normativeSource').map(o => o.value),
        evidence: all(s, REQ+'expectedEvidence').map(o => o.value),
        terms: all(s, REQ+'usesTerm').map(o => o.id),
        cqs
      });
    }
    reqs.sort((a, b) => a.sortKey.localeCompare(b.sortKey));
    return reqs;
  }

  // --- render ---------------------------------------------------------------
  const requirements = await load();
  const state = { q:'', fw:'', sec:'', formalised:false };

  const fill = (sel, values) => values.forEach(v => { const o=document.createElement('option'); o.value=v; o.textContent=v; sel.appendChild(o); });
  fill(byId('fwSel'), [...new Set(requirements.map(r => r.framework))]);
  const fillSections = () => {
    byId('secSel').length = 1;
    fill(byId('secSel'), [...new Set(requirements.filter(r => !state.fw || r.framework === state.fw).map(r => r.section))]);
  };
  fillSections();

  byId('q').oninput = e => { state.q = e.target.value.toLowerCase(); draw(); };
  byId('fwSel').onchange = e => { state.fw = e.target.value; state.sec = ''; fillSections(); draw(); };
  byId('secSel').onchange = e => { state.sec = e.target.value; draw(); };
  byId('formalisedOnly').onchange = e => { state.formalised = e.target.checked; draw(); };
  byId('closeDetails').onclick = () => byId('details').classList.add('hidden');

  function filter(list){
    return list.filter(r => {
      if (state.fw && r.framework !== state.fw) return false;
      if (state.sec && r.section !== state.sec) return false;
      if (state.formalised && !r.cqs.some(c => c.query)) return false;
      if (state.q) {
        const hay = [r.id, r.label, r.section, r.description, ...r.evidence, ...r.cqs.map(c => c.text), ...r.terms.map(qname)].join(' ').toLowerCase();
        if (!hay.includes(state.q)) return false;
      }
      return true;
    });
  }

  function draw(){
    const list = filter(requirements);
    const nCq = list.reduce((n, r) => n + r.cqs.length, 0);
    const nQ = list.reduce((n, r) => n + r.cqs.filter(c => c.query).length, 0);
    const nTerms = new Set(list.flatMap(r => r.terms)).size;
    $('#summary').innerHTML = `<p>${list.length} of ${requirements.length} requirement(s) shown, with ${nCq} competency questions
      (${nQ} formalised as SPARQL queries) and ${nTerms} distinct ontology terms.</p>`;
    $('#rows').innerHTML = list.map(r => {
      const nf = r.cqs.filter(c => c.query).length;
      return `<tr class="requirement-row" data-reqid="${esc(r.id)}">
          <td><strong>${esc(r.label)}</strong><br><span class="muted">${esc(r.section)}</span></td>
          <td><span class="badge ns fw">${esc(r.framework)}</span></td>
          <td>${esc(r.description.substring(0, 160))}${r.description.length > 160 ? '…' : ''}</td>
          <td>${r.cqs.length}${nf ? `<span class="formalised" title="formalised as SPARQL">(${nf} ✓)</span>` : ''}</td>
          <td>${r.evidence.length}</td>
          <td>${r.terms.length}</td>
        </tr>`;
    }).join('');
    document.querySelectorAll('tbody tr').forEach(tr => { tr.onclick = () => showDetails(tr.getAttribute('data-reqid')); });
  }

  function showDetails(reqId){
    const r = requirements.find(x => x.id === reqId);
    if (!r) return;
    const text = r.description.split('\n').map(p => `<p>${esc(p)}</p>`).join('');
    const cqs = r.cqs.map(c => `<li>${esc(c.text)}${c.query
      ? ` <a class="formalised" href="examples.html#${esc(c.query.replace(/^cq\//, '').replace(/\.rq$/, ''))}">SPARQL query and answer →</a>` : ''}</li>`).join('');
    // module terms link to their entry in this documentation (Widoco anchors are local names); other terms to their IRI
    const LEX = 'https://w3id.org/aidoc-ap/lex#';
    const href = t => t.startsWith(LEX) ? `index.html#${t.slice(LEX.length)}` : t;
    const terms = r.terms.map(t => `<a href="${esc(href(t))}"${t.startsWith(LEX) ? '' : ' target="_blank"'}><code>${esc(qname(t))}</code></a>`).join(' ');
    const list = xs => xs.length ? `<ul>${xs.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : '<p class="muted">None given</p>';
    byId('detailsBody').innerHTML = `
      <h3>${esc(r.label)}</h3>
      <p><span class="badge ns">${esc(r.framework)}</span> ${esc(r.section)}</p>
      <h4>Text</h4>${text}
      ${r.normative.length ? `<h4>Normative and methodological sources</h4>${list(r.normative)}` : ''}
      <h4>Competency questions (${r.cqs.length})</h4>${cqs ? `<ul>${cqs}</ul>` : '<p class="muted">None given</p>'}
      <h4>Ontology terms (${r.terms.length})</h4><p class="terms">${terms || '<span class="muted">None given</span>'}</p>
      <h4>Expected evidence and artefacts (${r.evidence.length})</h4>${list(r.evidence)}
      <hr>
      <p><strong>URI:</strong> <code>${esc(r.uri)}</code></p>
      ${r.source ? `<p><strong>Reference:</strong> ${esc(r.source)}</p>` : ''}
      ${r.seeAlso ? `<p><strong>Source text:</strong> <a target="_blank" href="${esc(r.seeAlso)}">${esc(r.seeAlso)} →</a></p>` : ''}
      <p><a href="#show-${esc(r.id)}">Link to this requirement</a></p>`;
    byId('details').classList.remove('hidden');
  }

  window.showDetails = showDetails;
  draw();
  window.dispatchEvent(new Event('requirements:rendered'));
})();
