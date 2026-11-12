"""Build soundsystemdiaries.it from data/*.json + build/template.html -> dist/.

Runs on Netlify at every push (no dependencies, Python standard library only).
Everything the admin panel (/admin) edits lives in data/:
  data/sounds.json  - every sound system (photo, city, story IT/EN, socials)
  data/events.json  - upcoming events (flyer, date, place, lineup)
  data/home.json    - which sounds appear in "Aggiunti di recente" and in the home grid
"""
import json, os, re, shutil, html as H, unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist')
BASE = 'https://soundsystemdiaries.it'
P = lambda *a: os.path.join(ROOT, *a)
esc = lambda x: H.escape(str(x or ''), quote=True)

def load(name):
    with open(P('data', name), encoding='utf-8') as f:
        return json.load(f)

def slug(x):
    x = unicodedata.normalize('NFKD', str(x)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', x).strip('-') or 'item'

def paras(text):
    return [p.strip() for p in re.split(r'\n\s*\n', text or '') if p.strip()]

# approximate centre of each region: used when a new sound or event has no coordinates
REGION_CENTER = {
    'Abruzzo': (42.23, 13.85), 'Basilicata': (40.50, 16.08), 'Calabria': (39.07, 16.35), 'Campania': (40.86, 14.84),
    'Emilia-Romagna': (44.53, 11.03), 'Friuli-Venezia Giulia': (46.07, 13.13), 'Lazio': (41.98, 12.77), 'Liguria': (44.32, 8.70),
    'Lombardia': (45.58, 9.77), 'Marche': (43.35, 13.13), 'Molise': (41.68, 14.60), 'Piemonte': (45.05, 7.92),
    'Puglia': (41.00, 16.60), 'Sardegna': (40.05, 9.05), 'Sicilia': (37.55, 14.15), 'Toscana': (43.45, 11.10),
    'Trentino-Alto Adige': (46.43, 11.17), 'Umbria': (42.95, 12.48), "Valle d'Aosta": (45.73, 7.37), 'Veneto': (45.65, 11.85),
    'San Marino': (43.94, 12.45),
}
MIT = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre']
MEN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MON3 = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
IC = {
    'cal': '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="16.5" rx="2"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/></svg>',
    'pin': '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.6"/></svg>',
    'spk': '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2.5" width="14" height="19" rx="2"/><circle cx="12" cy="14.5" r="4"/><circle cx="12" cy="6.8" r="1.4"/></svg>',
}

def img_url(path, width=1100):
    """Photos uploaded from the panel can be huge phone pictures: serve them resized through Netlify's image CDN."""
    path = (path or '').strip()
    if not path:
        return ''
    if path.startswith('http'):
        return path
    if not path.startswith('/'):
        path = '/' + path
    if path.startswith('/images/uploads/'):
        return f'/.netlify/images?url={path}&w={width}&fm=webp&q=78'
    return path

# ------------------------------------------------------------------ sounds
sounds, seen = [], set()
known_city = {}
for x in load('sounds.json')['items']:
    x = dict(x)
    x['name'] = (x.get('name') or '').strip()
    if not x['name']:
        continue
    sid = slug(x.get('id') or x['name'])
    while sid in seen:
        sid += '-2'
    seen.add(sid)
    x['id'] = sid
    x['city'] = (x.get('city') or '').strip()
    x['region'] = (x.get('region') or '').strip()
    if x.get('lat') not in (None, '') and x.get('lon') not in (None, '') and x['city']:
        known_city[x['city'].lower()] = (float(x['lat']), float(x['lon']))
    sounds.append(x)
for x in sounds:
    if x.get('lat') in (None, '') or x.get('lon') in (None, ''):
        c = known_city.get(x['city'].lower()) or REGION_CENTER.get(x['region'])
        x['lat'], x['lon'] = (c if c else (None, None))
        x['_approx'] = not known_city.get(x['city'].lower())
    x['place'] = ', '.join(v for v in (x['city'], x['region']) if v)
    x['story_it'] = paras(x.get('story'))
    x['story_en_l'] = paras(x.get('story_en'))
BYID = {x['id']: x for x in sounds}
BYNAME = {x['name'].lower(): x for x in sounds}
find = lambda v: BYNAME.get(str(v).strip().lower()) or BYID.get(slug(v))

map_data = []
for x in sounds:
    map_data.append({'id': x['id'], 'name': x['name'], 'city': x['city'] or None, 'region': x['region'] or None,
                     'founded': int(x['founded']) if str(x.get('founded') or '').isdigit() else None,
                     'lat': x['lat'], 'lon': x['lon'],
                     'genres': {'roots': False, 'dub': False, 'steppers': False}, 'vinyl': None, 'selfBuilt': None,
                     'instagram': x.get('instagram') or None, 'facebook': x.get('facebook') or None, 'color': None,
                     'hasPhoto': bool(x.get('photo')), **({'story': x['story_it']} if x['story_it'] else {})})
story_en = {x['id']: x['story_en_l'] for x in sounds if x['story_en_l']}

D = ['', ' d1', ' d2', ' d3', ' d4', ' d5']
sound_cards = ''
for i, x in enumerate(sounds):
    ph = img_url(x.get('photo'))
    pic = (f'<img loading="lazy" decoding="async" class="ph real-photo" src="{esc(ph)}" alt="{esc(x["name"])}">' if ph
           else '<div class="ph pal-red"></div>')
    sound_cards += f'''        <div data-sound-id="{x['id']}" class="sound-card tilt reveal{D[i % 6]}">
          {pic}
          <div class="grad"></div><div class="tint"></div>
          <div class="sound-info">
            <p class="place">{esc(x['place'] or 'Italia')}</p>
            <h3>{esc(x['name'].upper())}</h3>
          </div>
        </div>
'''

home = load('home.json')
home_sounds = ''
for sid in home.get('home_sounds') or []:
    x = find(sid)
    if not x or not x.get('photo'):
        continue
    home_sounds += (f'\n          <a href="#sound/{x["id"]}" class="sq tilt"><img class="ph real-photo" src="{esc(img_url(x["photo"], 600))}" '
                    f'alt="{esc(x["name"])}" loading="lazy"><div class="grad"></div><span class="nm">{esc(x["name"])}</span></a>')
recent, n_recent = '', 0
for sid in home.get('recent') or []:
    x = find(sid)
    if not x:
        continue
    n_recent += 1
    recent += (f'<a class="nsc" href="#sound/{x["id"]}"><div class="nsc-img"><img src="{esc(img_url(x.get("photo"), 800))}" alt="{esc(x["name"])}" loading="lazy">'
               f'<span class="nsc-tag" data-i18n="ns.tag">Aggiunto di recente</span></div><div class="nsc-body"><h3>{esc(x["name"])}</h3>'
               + (f'<div class="evc-row"><span class="ic">{IC["cal"]}</span><span><span data-i18n="ns.since">dal</span> {esc(x["founded"])}</span></div>' if x.get('founded') else '')
               + f'<div class="evc-row"><span class="ic">{IC["pin"]}</span><span>{esc(x["place"] or "Italia")}</span></div></div></a>')

# ------------------------------------------------------------------ events
events = []
for e in load('events.json')['items']:
    e = dict(e)
    try:
        y, m, d = [int(v) for v in str(e.get('date', ''))[:10].split('-')]
        date(y, m, d)
    except Exception:
        print('skip event without a valid date:', e.get('title'))
        continue
    e['iso'] = f'{y}-{m:02d}-{d:02d}'
    e['it'], e['en'], e['mon'] = f'{d} {MIT[m - 1]} {y}', f'{MEN[m - 1]} {d}, {y}', MON3[m - 1]
    e['id'] = slug(e.get('id') or (e['iso'] + '-' + (e.get('title') or 'evento')))
    if e.get('lat') in (None, '') or e.get('lon') in (None, ''):
        c = known_city.get((e.get('city') or '').lower()) or REGION_CENTER.get(e.get('region') or '')
        e['lat'], e['lon'] = c if c else ('', '')
    events.append(e)
events.sort(key=lambda e: e['iso'])

def ev_card(e, home=False):
    title = e.get('title') or ''
    pic = img_url(e.get('flyer'), 900)
    img = (f'<a class="evc-img" href="#events"><img src="{esc(pic)}" alt="{esc(title)}" loading="lazy"></a>' if home else
           f'<button type="button" class="evc-img" data-flyer><img src="{esc(pic)}" alt="{esc(title)}" loading="lazy"></button>')
    place = ', '.join(v for v in (e.get('city'), e.get('region')) if v)
    loc = (e.get('city') or '') + (' — ' + e['venue'] if e.get('venue') else '')
    lineup = e.get('lineup') or ''
    attrs = '' if home else (f' data-event-card data-location="{esc(loc)}" data-month="{e["mon"]}" '
                             f'data-search="{esc((title + " " + loc + " " + (e.get("address") or "") + " " + lineup).lower())}" '
                             f'data-sounds="{esc("|".join(v.strip() for v in re.split(r"[·,]", lineup) if v.strip()))}" '
                             f'data-lat="{e["lat"]}" data-lon="{e["lon"]}"')
    return (f'<article class="event-card evc reveal" data-date="{e["iso"]}"{attrs}>{img}<div class="evc-body">'
            f'<h3>{esc(title)}</h3>'
            f'<div class="evc-row"><span class="ic">{IC["cal"]}</span><b data-i18n="ev-{e["id"]}.fdate">{e["it"]}</b></div>'
            f'<div class="evc-row"><span class="ic">{IC["pin"]}</span><span>{esc(place)}</span></div>'
            + (f'<div class="evc-snd"><span class="ic">{IC["spk"]}</span><b>{esc(lineup)}</b></div>' if lineup else '')
            + '</div></article>')

ev_i18n = ('Object.assign(I18N.it, ' + json.dumps({f'ev-{e["id"]}.fdate': e['it'] for e in events}, ensure_ascii=False) + ');\n'
           '  Object.assign(I18N.en, ' + json.dumps({f'ev-{e["id"]}.fdate': e['en'] for e in events}, ensure_ascii=False) + ');')

# ------------------------------------------------------------------ assemble
t = open(P('build', 'template.html'), encoding='utf-8').read()
js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
t = (t.replace('__SOUNDS_DATA__', js(map_data))
      .replace('__STORY_EN__', js(story_en))
      .replace('<!--@SOUND_CARDS-->', sound_cards)
      .replace('<!--@HOME_SOUNDS-->', home_sounds)
      .replace('<!--@RECENT-->', recent)
      .replace('<!--@RECENT_DOTS-->', '<i></i>' * n_recent)
      .replace('<!--@HOME_EVENTS-->', ''.join(ev_card(e, True) for e in events))
      .replace('<!--@EVENT_CARDS-->', ''.join(ev_card(e) for e in events))
      .replace('/*@EVENT_I18N*/', ev_i18n))
assert '__SOUNDS_DATA__' not in t and '<!--@' not in t

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
shutil.copytree(P('static'), OUT)
os.makedirs(os.path.join(OUT, 'images'), exist_ok=True)
if os.path.isdir(P('images', 'uploads')):
    shutil.copytree(P('images', 'uploads'), os.path.join(OUT, 'images', 'uploads'))
shutil.copytree(P('admin'), os.path.join(OUT, 'admin'))

def set_head(doc, title, desc, url, image):
    doc = re.sub(r'<title>.*?</title>', lambda m: '<title>' + H.escape(title) + '</title>', doc, count=1, flags=re.S)
    doc = re.sub(r'<meta name="description" content="[^"]*">', lambda m: '<meta name="description" content="' + esc(desc) + '">', doc, count=1)
    for prop, val in (('og:title', title), ('og:description', desc), ('og:url', url), ('og:image', image)):
        doc = re.sub(r'<meta property="' + prop + r'" content="[^"]*">', lambda m: f'<meta property="{prop}" content="{esc(val)}">', doc, count=1)
    for nm, val in (('twitter:title', title), ('twitter:description', desc), ('twitter:image', image)):
        doc = re.sub(r'<meta name="' + nm + r'" content="[^"]*">', lambda m: f'<meta name="{nm}" content="{esc(val)}">', doc, count=1)
    doc = re.sub(r'<link rel="canonical" href="[^"]*">', lambda m: '<link rel="canonical" href="' + url + '">', doc, count=1)
    return doc

def write(rel, doc):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(doc)

write('index.html', t)
urls = [BASE + '/']
for x in sounds:
    if x['story_it']:
        desc = x['story_it'][0]
        if len(desc) > 200:
            desc = desc[:desc.rfind(' ', 0, 195)] + '…'
    else:
        desc = x['name'] + (f", sound system da {x['place']}" if x['place'] else '') + ". La scheda nell'archivio dei sound system italiani di Sound System Diaries."
    og = f'/og/{x["id"]}.jpg'
    image = BASE + og if os.path.exists(P('static', 'og', x['id'] + '.jpg')) else (BASE + img_url(x.get('photo'), 1200) if x.get('photo') else BASE + '/og-image.jpg')
    url = f'{BASE}/sound/{x["id"]}/'
    write(f'sound/{x["id"]}/index.html', set_head(t, f'{x["name"]} — Sound System Diaries', desc, url, image))
    urls.append(url)
for path, title, desc in (
        ('aggiungi', 'Aggiungi il tuo sound — Sound System Diaries', "Fai parte di un sound system italiano? Manda foto, storia e contatti: lo aggiungiamo all'archivio di Sound System Diaries."),
        ('aggiungi/evento', 'Aggiungi il tuo evento — Sound System Diaries', 'Organizzi una serata sound system? Mandaci il flyer con data, luogo e sound: la pubblichiamo nel calendario di Sound System Diaries.')):
    write(f'{path}/index.html', set_head(t, title, desc, f'{BASE}/{path}/', BASE + '/og-image.jpg'))
    urls.append(f'{BASE}/{path}/')
urls.append(BASE + '/privacy/')
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
write('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {BASE}/sitemap.xml\n')
n_home = home_sounds.count('class="sq')
print(f'built: {len(sounds)} sounds, {len(events)} events, {n_recent} recent, home grid {n_home}')
approx = [x['name'] for x in sounds if x.get('_approx')]
if approx:
    print('position from region centre (add lat/lon in the panel for a precise pin):', ', '.join(approx))
