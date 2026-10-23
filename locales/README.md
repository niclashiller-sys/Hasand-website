# Norwegian Bokmål preview

The Norwegian copy in `nb.json` has received a separate editorial pass for fluent Norwegian investment terminology and fidelity to the approved English content. This is an assistant editorial review, not certification by an external human translator.

English and Norwegian live at `/` and `/no`; both language selectors preserve the current section. The mobile menu also provides language links. Swedish is labelled unavailable until translated. The executive summary remains the approved English PDF and is labelled accordingly on the Norwegian page.

Build with `python scripts/build_languages.py`. The approved English sources are `scripts/english-source.template` (static HTML) and `assets/index-efa37adbecaa.js` (application). Update those sources and the glossary for future copy edits, then rebuild both languages. Generated application bundles have content hashes to avoid stale caches.

Norwegian text uses "kapitalallokering", "porteføljekonstruksjon", "diskresjonær forvaltning" and "investeringskomité". "Family office" remains an industry term. Official institution and qualification names remain in their original form. The AUM sentence makes clear that Formue's assets grew during the tenure and does not attribute the entire increase to one individual. The contact confirmation makes clear that the enquiry must be sent from the visitor's email application.

No production release is authorised yet: this branch is for Niclas's review.

## Swedish preview

Swedish copy lives in `sv.json`, served at `/sv`. The generator now builds English, Norwegian Bokmål and Swedish together. All three selectors are active on desktop and in the compact menu. All pages have reciprocal language alternatives, distinct canonical URLs, and sitemap entries.

The Swedish text received a separate editorial pass for Swedish idiom and investment terminology (including diskretionär förvaltning, tillgångsallokering and investeringskommitté). Capital amounts are explicitly in Norwegian kronor; the firm continues to be described as based in Norway. Official institution names and the established term family office are retained. The PDF language is labelled English. This is an assistant editorial review, not external human certification.

Swedish remains preview-only until Niclas approves release.
