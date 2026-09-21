# Sound System Diaries

Sito statico, nessun build step. Struttura:

- `index.html` — pagina principale (CSS e JS inline, contenuti caricati da `data/*.json` via fetch)
- `data/sounds.json`, `data/events.json`, `data/diaries.json`, `data/people.json` — contenuti modificabili dal pannello `/admin`
- `images/` — foto e flyer (le nuove foto caricate dal pannello finiscono in `images/uploads/`)
- `admin/` — pannello Decap CMS (config in `admin/config.yml`, backend `turbo-github`)

## Deploy

Netlify, nessun comando di build, publish directory `.` (vedi `netlify.toml`). Ogni push su `main` pubblica automaticamente.

## Pannello di gestione

`https://<tuo-dominio>/admin/` — richiede un account gratuito su decapcms.org/turbo collegato a questo repository (vedi `admin/config.yml` per il `turbo_site_id`).
