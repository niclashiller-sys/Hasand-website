"""Build language pages from the approved export and reviewed nb/sv glossaries."""
from pathlib import Path
import re,json,hashlib,html
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCE_JS=ROOT/'assets/index-efa37adbecaa.js'
SOURCE_HTML=ROOT/'scripts/english-source.template'
BASE='https://www.hasand.no'
CONFIG={
 'en':{'code':'EN','path':'/','locale':'en_GB'},
 'nb':{'code':'NO','path':'/no','locale':'nb_NO','title':'Håsand Consultancy | Niclas Hiller | Investeringsrådgivning','description':'Uavhengig investeringsrådgivning for family offices og institusjoner. Niclas Hiller, tidligere investeringsdirektør i Formue og tidlig ansatt i NBIM. Basert i Oslo.','subject':'Henvendelse fra','fields':['Navn','E-post','Virksomhet']},
 'sv':{'code':'SV','path':'/sv','locale':'sv_SE','title':'Håsand Consultancy | Niclas Hiller | Investeringsrådgivning','description':'Oberoende investeringsrådgivning för family offices och institutioner. Niclas Hiller, tidigare investeringschef på Formue och tidig medarbetare på NBIM. Baserad i Oslo.','subject':'Förfrågan från','fields':['Namn','E-post','Organisation']}}
LANG_BY_CODE={v['code']:k for k,v in CONFIG.items()}
links='["EN","NO","SV"].map(d=>A.jsxDEV("a",{href:(d==="NO"?"/no":d==="SV"?"/sv":"/")+window.location.hash,hrefLang:d==="NO"?"nb":d==="SV"?"sv":"en","aria-label":d==="NO"?"Norsk bokmål":d==="SV"?"Svenska":"English","aria-current":(d==="NO"?window.location.pathname.startsWith("/no"):d==="SV"?window.location.pathname.startsWith("/sv"):!/^\\/(no|sv)(\\/|$)/.test(window.location.pathname))?"page":void 0,title:d==="NO"?"Norsk bokmål":d==="SV"?"Svenska":"English",style:{fontFamily:"DM Sans, sans-serif",fontSize:"0.7rem",fontWeight:500,letterSpacing:"0.08em",textTransform:"uppercase",color:"#F8F6F1",background:"none",borderBottom:(d==="NO"?window.location.pathname.startsWith("/no"):d==="SV"?window.location.pathname.startsWith("/sv"):!/^\\/(no|sv)(\\/|$)/.test(window.location.pathname))?"1px solid #B8975A":"1px solid transparent",padding:"0.4rem 0.5rem",textDecoration:"none",cursor:"pointer"},children:d},d))'
js=SOURCE_JS.read_text()
js,n=re.subn(r'\["EN","NO","SV"\]\.map\(d=>A\.jsxDEV\("button",.*?,this\)\)',lambda _:links,js,count=1);assert n==1
mobile='A.jsxDEV("button",{"data-loc":"client/src/components/Navbar.tsx:226"'
assert js.count(mobile)==1
js=js.replace(mobile,'A.jsxDEV("div",{role:"group","aria-label":"Language",style:{display:"flex",gap:"1rem"},children:'+links+'}),'+mobile)
js=js.replace('className:"md:hidden p-2",onClick:','className:"md:hidden p-2","aria-label":"Menu",onClick:')
source=SOURCE_HTML.read_text()
for language,cfg in CONFIG.items():
 mapping=json.loads((ROOT/('locales/'+language+'.json')).read_text()) if language!='en' else {}
 def translated(value):
  key=value.strip()
  return value.replace(key,mapping[key],1) if key in mapping else value
 def literal(match):
  try:value=json.loads(match.group())
  except (ValueError,TypeError):return match.group()
  result=translated(value)
  return json.dumps(result,ensure_ascii=False) if result!=value else match.group()
 bundle=js
 if language!='en':
  bundle=re.sub(r'"(?:\\.|[^"\\])*"',literal,bundle)
  quote=next(k for k in mapping if k.startswith('"The best investment decisions'))
  bundle=bundle.replace("'"+quote+"'",json.dumps(mapping[quote],ensure_ascii=False))
  bundle=bundle.replace('`Enquiry from ${r.name} — Håsand Consultancy`','`'+cfg['subject']+' ${r.name} – Håsand Consultancy`')
  fields=cfg['fields']
  bundle=bundle.replace('`Name: ${r.name}\nEmail: ${r.email}\nOrganisation: ${r.organisation}\n\n${r.message}`','`'+fields[0]+': ${r.name}\n'+fields[1]+': ${r.email}\n'+fields[2]+': ${r.organisation}\n\n${r.message}`')
  needle='path:"/",component:G7';assert bundle.count(needle)==1
  bundle=bundle.replace(needle,'path:/^\\/'+cfg['path'].strip('/')+'\\/?$/,component:G7')
 filename='assets/site-'+language+'-'+hashlib.sha256(bundle.encode()).hexdigest()[:12]+'.js'
 (ROOT/filename).write_text(bundle)
 page=source.replace('/assets/index-efa37adbecaa.js','/'+filename)
 def static_link(m):
  code=m[2];lang=LANG_BY_CODE[code];url=CONFIG[lang]['path']
  return '<a'+m[1]+' href="'+url+'" hreflang="'+lang+'"'+(' aria-current="page"' if code==cfg['code'] else '')+'>'+code+'</a>'
 page=re.sub(r'<button([^>]*)>(EN|NO|SV)</button>',static_link,page)
 alternates='\n'.join('<link rel="alternate" hreflang="'+l+'" href="'+BASE+c['path']+'" />'for l,c in CONFIG.items())+'\n<link rel="alternate" hreflang="x-default" href="'+BASE+'/" />'
 page=page.replace('</head>',alternates+'\n</head>')
 if language=='sv':page=page.replace('</head>','<link rel="stylesheet" href="/assets/swedish-layout-v1.css" />\n</head>')
 if language!='en':
  start=page.index('<div id="root">');end=page.index('</body>');fragment=page[start:end]
  fragment=re.sub(r'>([^<>]+)<',lambda m:'>'+html.escape(translated(html.unescape(m[1])),quote=False)+'<',fragment)
  fragment=re.sub(r'(alt=")([^"]*)(")',lambda m:m[1]+html.escape(translated(html.unescape(m[2])),quote=True)+m[3],fragment)
  page=page[:start]+fragment+page[end:]
  page=page.replace('<html lang="en">','<html lang="'+language+'">')
  page=re.sub(r'<title>.*?</title>','<title>'+cfg['title']+'</title>',page,count=1)
  for attr,name,val in [('name','description',cfg['description']),('property','og:title',cfg['title']),('property','og:description',cfg['description']),('name','twitter:title',cfg['title']),('name','twitter:description',cfg['description']),('property','og:url',BASE+cfg['path'])]:
   page=re.sub(r'(<meta '+attr+'="'+name+r'" content=")[^"]*(")',lambda m:m[1]+val+m[2],page)
  page=page.replace('<link rel="canonical" href="'+BASE+'/"','<link rel="canonical" href="'+BASE+cfg['path']+'"')
  page=page.replace('<meta property="og:type"','<meta property="og:locale" content="'+cfg['locale']+'" />\n    <meta property="og:type"')
 target=ROOT/(cfg['path'].strip('/')+'/index.html' if language!='en' else 'index.html');target.parent.mkdir(exist_ok=True)
 match=re.search(r'<script type="application/ld\+json">(.*?)</script>',page,re.S);schema=json.loads(match[1])
 for item in schema['@graph']:
  if item['@type']=='WebSite':item['inLanguage']=list(CONFIG)
 schema['@graph'].append({'@type':'WebPage','@id':BASE+cfg['path']+'#webpage','url':BASE+cfg['path'],'inLanguage':language,'isPartOf':{'@id':BASE+'/#website'},'about':{'@id':BASE+'/#organization'}})
 page=page[:match.start(1)]+json.dumps(schema,ensure_ascii=False)+page[match.end(1):]
 target.write_text(page)
 print(language,filename)

NS='http://www.sitemaps.org/schemas/sitemap/0.9';XHTML='http://www.w3.org/1999/xhtml';ET.register_namespace('',NS);ET.register_namespace('xhtml',XHTML)
sitemap=ET.Element('{'+NS+'}urlset')
for cfg in CONFIG.values():
 url=ET.SubElement(sitemap,'{'+NS+'}url');ET.SubElement(url,'{'+NS+'}loc').text=BASE+cfg['path']
 for lang,other in CONFIG.items():ET.SubElement(url,'{'+XHTML+'}link',{'rel':'alternate','hreflang':lang,'href':BASE+other['path']})
url=ET.SubElement(sitemap,'{'+NS+'}url');ET.SubElement(url,'{'+NS+'}loc').text=BASE+'/documents/niclas-hiller-executive-summary.pdf'
ET.indent(sitemap);ET.ElementTree(sitemap).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
