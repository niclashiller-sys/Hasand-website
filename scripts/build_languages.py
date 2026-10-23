"""Build English/Norwegian pages from the approved static export and reviewed glossary.
Re-run after updating either the English source or locales/nb.json.
"""
from pathlib import Path
import re,json,hashlib,html
ROOT=Path(__file__).resolve().parents[1]
# Original approved export is retained as source; generated files have content hashes.
SOURCE_JS=ROOT/'assets/index-efa37adbecaa.js'
SOURCE_HTML=ROOT/'scripts/english-source.template'
mapping=json.loads((ROOT/'locales/nb.json').read_text())

def translated(value):
 key=value.strip()
 return value.replace(key,mapping[key],1) if key in mapping else value

def literal(match):
 try:value=json.loads(match.group())
 except (ValueError,TypeError):return match.group()
 result=translated(value)
 return json.dumps(result,ensure_ascii=False) if result!=value else match.group()

links='["EN","NO","SV"].map(d=>A.jsxDEV(d==="SV"?"span":"a",{href:d==="SV"?void 0:(d==="NO"?"/no":"/")+window.location.hash,hrefLang:d==="NO"?"nb":d==="EN"?"en":void 0,"aria-label":d==="NO"?"Norsk bokmål":d==="EN"?"English":"Svenska – kommer senere","aria-current":(d==="NO"?window.location.pathname.startsWith("/no"):d==="EN"&&!window.location.pathname.startsWith("/no"))?"page":void 0,"aria-disabled":d==="SV"?"true":void 0,title:d==="SV"?"Svenska – kommer senere":d==="NO"?"Norsk bokmål":"English",style:{fontFamily:"DM Sans, sans-serif",fontSize:"0.7rem",fontWeight:500,letterSpacing:"0.08em",textTransform:"uppercase",color:d==="SV"?"rgba(248,246,241,0.3)":"#F8F6F1",background:"none",borderBottom:(d==="NO"?window.location.pathname.startsWith("/no"):d==="EN"&&!window.location.pathname.startsWith("/no"))?"1px solid #B8975A":"1px solid transparent",padding:"0.4rem 0.5rem",textDecoration:"none",cursor:d==="SV"?"default":"pointer"},children:d},d))'
js=SOURCE_JS.read_text()
pattern=r'\["EN","NO","SV"\]\.map\(d=>A\.jsxDEV\("button",.*?,this\)\)'
js,n=re.subn(pattern,lambda _:links,js,count=1);assert n==1
mobile='A.jsxDEV("button",{"data-loc":"client/src/components/Navbar.tsx:226"'
assert js.count(mobile)==1
js=js.replace(mobile,'A.jsxDEV("div",{role:"group","aria-label":"Language",style:{display:"flex",gap:"1rem"},children:'+links+'}),'+mobile)
# Add a screen-reader label for the existing compact menu control.
js=js.replace('className:"md:hidden p-2",onClick:', 'className:"md:hidden p-2","aria-label":"Menu",onClick:')

def static_links(s,lang):
 def replace(m):
  code=m[2]
  if code=='SV':return '<span'+m[1]+' aria-disabled="true" title="Svenska – kommer senere">SV</span>'
  href='/no' if code=='NO' else '/'
  return '<a'+m[1]+' href="'+href+'" hreflang="'+('nb' if code=='NO' else 'en')+'"'+(' aria-current="page"' if code==lang else '')+'>'+code+'</a>'
 return re.sub(r'<button([^>]*)>(EN|NO|SV)</button>',replace,s)

source=SOURCE_HTML.read_text()
for language in ['en','nb']:
 bundle=js
 if language=='nb':
  bundle=re.sub(r'"(?:\\.|[^"\\])*"',literal,bundle)
  quote=next(k for k in mapping if k.startswith('"The best investment decisions'))
  bundle=bundle.replace("'"+quote+"'",json.dumps(mapping[quote],ensure_ascii=False))
  bundle=bundle.replace('`Enquiry from ${r.name} — Håsand Consultancy`','`Henvendelse fra ${r.name} – Håsand Consultancy`').replace('`Name: ${r.name}\nEmail: ${r.email}\nOrganisation: ${r.organisation}\n\n${r.message}`','`Navn: ${r.name}\nE-post: ${r.email}\nVirksomhet: ${r.organisation}\n\n${r.message}`')
  needle='path:"/",component:G7'
  assert bundle.count(needle)==1
  bundle=bundle.replace(needle,'path:/^\\/no\\/?$/,component:G7')
 filename='assets/site-'+language+'-'+hashlib.sha256(bundle.encode()).hexdigest()[:12]+'.js'
 (ROOT/filename).write_text(bundle)
 page=source.replace('/assets/index-efa37adbecaa.js','/'+filename)
 page=static_links(page,'NO' if language=='nb' else 'EN')
 alternates='\n'.join('<link rel="alternate" hreflang="'+l+'" href="'+u+'" />' for l,u in [('en','https://www.hasand.no/'),('nb','https://www.hasand.no/no'),('x-default','https://www.hasand.no/')])
 page=page.replace('</head>',alternates+'\n</head>')
 if language=='nb':
  start=page.index('<div id="root">');end=page.index('</body>')
  fragment=page[start:end]
  fragment=re.sub(r'>([^<>]+)<',lambda m:'>'+html.escape(translated(html.unescape(m[1])),quote=False)+'<',fragment)
  fragment=re.sub(r'(alt=")([^"]*)(")',lambda m:m[1]+html.escape(translated(html.unescape(m[2])),quote=True)+m[3],fragment)
  page=page[:start]+fragment+page[end:]
  page=page.replace('<html lang="en">','<html lang="nb">')
  title='Håsand Consultancy | Niclas Hiller | Investeringsrådgivning'
  desc='Uavhengig investeringsrådgivning for family offices og institusjoner. Niclas Hiller, tidligere investeringsdirektør i Formue og tidlig ansatt i NBIM. Basert i Oslo.'
  page=re.sub(r'<title>.*?</title>','<title>'+title+'</title>',page,count=1)
  for attr,name,val in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('name','twitter:title',title),('name','twitter:description',desc),('property','og:url','https://www.hasand.no/no')]:
   page=re.sub(r'(<meta '+attr+'="'+name+r'" content=")[^"]*(")',lambda m:m[1]+val+m[2],page)
  page=page.replace('<link rel="canonical" href="https://www.hasand.no/"','<link rel="canonical" href="https://www.hasand.no/no"')
  page=page.replace('"inLanguage": "en"','"inLanguage": "nb"')
  page=page.replace('<meta property="og:type"','<meta property="og:locale" content="nb_NO" />\n    <meta property="og:type"')
  target=ROOT/'no/index.html';target.parent.mkdir(exist_ok=True)
 else:target=ROOT/'index.html'
 schema_match=re.search(r'<script type="application/ld\+json">(.*?)</script>',page,re.S)
 schema=json.loads(schema_match[1])
 for item in schema['@graph']:
  if item['@type']=='WebSite':item['inLanguage']=['en','nb']
 schema['@graph'].append({'@type':'WebPage','@id':('https://www.hasand.no/no' if language=='nb' else 'https://www.hasand.no/')+'#webpage','url':'https://www.hasand.no/no' if language=='nb' else 'https://www.hasand.no/','inLanguage':language,'isPartOf':{'@id':'https://www.hasand.no/#website'},'about':{'@id':'https://www.hasand.no/#organization'}})
 page=page[:schema_match.start(1)]+json.dumps(schema,ensure_ascii=False)+page[schema_match.end(1):]
 target.write_text(page)
 print(language,filename)

(ROOT/'sitemap.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url><loc>https://www.hasand.no/</loc><xhtml:link rel="alternate" hreflang="en" href="https://www.hasand.no/"/><xhtml:link rel="alternate" hreflang="nb" href="https://www.hasand.no/no"/></url>
  <url><loc>https://www.hasand.no/no</loc><xhtml:link rel="alternate" hreflang="en" href="https://www.hasand.no/"/><xhtml:link rel="alternate" hreflang="nb" href="https://www.hasand.no/no"/></url>
  <url><loc>https://www.hasand.no/documents/niclas-hiller-executive-summary.pdf</loc></url>
</urlset>
''')
