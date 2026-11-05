# Sound System Diaries

Sito statico in una sola pagina, senza build step.

- `index.html` — tutto il sito (HTML, CSS e JS inline; contenuti scritti direttamente nella pagina)
- `images/` — foto, locandine e logo usati dalla pagina
- `og-image.jpg` — anteprima per la condivisione sui social

## Deploy

Netlify, nessun comando di build, publish directory `.` (vedi `netlify.toml`). Ogni push su `main` pubblica automaticamente.

## Modificare i contenuti

Non c'è pannello admin: i testi si cambiano in `index.html` e le nuove immagini vanno in `images/`.
