# Sound System Diaries — soundsystemdiaries.it

L'archivio dei sound system italiani.

## Come si aggiorna

Dal pannello **https://soundsystemdiaries.it/admin/**:

- **Eventi** — aggiungi una serata con flyer, data, città, locale e sound. Dopo la data passa da sola in «Eventi passati».
- **Sound system** — schede, foto, storia in italiano e inglese, link social.
- **Home** — quali sound compaiono in «Aggiunti di recente» e nella griglia «Ogni sound ha una storia».

Quando premi «Pubblica», il pannello salva su GitHub e Netlify ricostruisce il sito in un paio di minuti.

I messaggi dei moduli «Aggiungi il tuo sound / evento» arrivano su Netlify → progetto → **Forms** (e per email, se attivi le notifiche).

## Com'è fatto

- `data/` — i contenuti (`sounds.json`, `events.json`, `home.json`), modificati dal pannello
- `build/build.py` — costruisce il sito in `dist/` (solo Python, nessuna dipendenza)
- `build/template.html` — la pagina del sito con i segnaposto per i contenuti
- `static/` — immagini ottimizzate, font, anteprime social (`og/`), privacy, `_headers`, `_redirects`
- `images/uploads/` — foto caricate dal pannello (servite ridimensionate dal CDN di Netlify)
- `admin/` — pannello Decap CMS

Per provarlo in locale: `python3 build/build.py` e poi apri `dist/` con un server (es. `python3 -m http.server -d dist`).
