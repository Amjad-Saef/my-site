#!/usr/bin/env python3
"""Build a browser-ready HTML edition from the same Quarto/Markdown sources.

Only used to bundle an immediately viewable example. For regular publishing,
`quarto render` is the authoritative build process.
Requires: pandoc, Python, PyYAML, BeautifulSoup4.
"""
from pathlib import Path
import copy, re, html, json, shutil, subprocess, datetime
from bs4 import BeautifulSoup
import yaml
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'docs'

DOCS=[ROOT/'essays/fourier-series.qmd',ROOT/'essays/compactness.qmd',ROOT/'notes/euler-identity.qmd',ROOT/'notes/gaussian-integral.qmd']


def document(path):
    s=path.read_text()
    assert s.startswith('---\n'),path
    parts=s.split('---\n',2)
    meta=yaml.safe_load(parts[1])
    return meta, parts[2].strip()

POSTS=[]
for p in DOCS:
    m,b=document(p)
    date=m['date']
    if isinstance(date,datetime.date): date=date.isoformat()
    POSTS.append({'file':p,'meta':m,'body':b,'date':date,'url':str(p.relative_to(ROOT).with_suffix('.html')),'kind':'Essay' if p.parent.name=='essays' else 'Note','minutes':max(2,round(len(b.split())/210))})
POSTS.sort(key=lambda o:o['date'],reverse=True)

def format_date(date):return datetime.date.fromisoformat(date).strftime('%B %-d, %Y')
def esc(s):return html.escape(str(s),quote=True)

def icon(name):
    if name=='search':return '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>'
    if name=='menu':return '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 7h18M3 12h18M3 17h18"/></svg>'


def shell(contents,title,description,root_rel='',active='',body_class=''):
    nav=''.join(f'<a class="{"active" if name==active else ""}" href="{root_rel}{url}" {"aria-current=\"page\"" if name==active else ""}>{name}</a>' for name,url in [('Essays','essays/index.html'),('Notes','notes/index.html'),('About','about.html')])
    links=f'<div class="header-links" id="header-links">{nav}</div>'
    search=f'''<button type="button" class="header-search" id="search-launch" aria-label="Search articles">{icon('search')}<span>Search</span><kbd>⌘ K</kbd></button>'''
    head=f'''<!doctype html><html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="description" content="{esc(description)}"/>
<meta name="theme-color" content="#f9f8f5"/>
<link rel="icon" type="image/svg+xml" href="{root_rel}assets/favicon.svg"/>
<link rel="stylesheet" href="{root_rel}styles/site.css"/>
<title>{esc(title)} · Your Name</title></head>'''
    header=f'''<div class="site-shell {body_class}"><header class="site-header"><div class="header-inner"><a class="site-brand" href="{root_rel}index.html" aria-label="Home"><span class="brand-symbol">∑</span><span class="brand-wordmark">Your Name</span></a><div class="header-right">{links}{search}<button class="mobile-nav-toggle" id="mobile-nav-toggle" type="button" aria-controls="header-links" aria-expanded="false" aria-label="Toggle navigation">{icon('menu')}</button></div></div></header>'''
    footer=f'''<footer class="site-footer"><div class="footer-inner"><span>© 2026 Your Name · Built for careful reading.</span><div class="footer-links"><a href="{root_rel}essays/index.html">Essays</a><a href="{root_rel}notes/index.html">Notes</a><a href="{root_rel}about.html">About</a></div></div></footer></div>'''
    search_modal='''<div class="search-backdrop" id="search-backdrop" role="presentation"><div class="search-dialog" role="dialog" aria-modal="true" aria-label="Search the notebook"><div class="search-top">'''+icon('search')+'''<input id="search-input" type="search" placeholder="Search essays and notes…" aria-label="Search query"/><button type="button" class="search-close" id="search-close">ESC</button></div><div class="search-results" id="search-results"><div class="search-empty">Start typing a topic, title, or keyword.</div></div></div></div>'''
    # Global index paths are prepended for nested pages; escape JSON to avoid any '<' in script content.
    data=[{'title':p['meta']['title'],'description':p['meta']['description'],'categories':p['meta']['categories'],'kind':p['kind'],'date':p['date'],'url':root_rel+p['url']} for p in POSTS]
    script='''<script>const SEARCH_ITEMS='''+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+''';
(()=>{const overlay=document.getElementById('search-backdrop'),entry=document.getElementById('search-input'),results=document.getElementById('search-results'),launch=document.getElementById('search-launch'),close=document.getElementById('search-close'),toggle=document.getElementById('mobile-nav-toggle'),nav=document.getElementById('header-links');let returnFocus=null;
function show(){returnFocus=document.activeElement;overlay.classList.add('open');document.body.style.overflow='hidden';entry.value='';results.innerHTML='<div class="search-empty">Start typing a topic, title, or keyword.</div>';entry.focus()}
function hide(){overlay.classList.remove('open');document.body.style.overflow='';returnFocus?.focus()}
function render(){const q=entry.value.trim().toLocaleLowerCase();results.replaceChildren();if(!q){results.innerHTML='<div class="search-empty">Start typing a topic, title, or keyword.</div>';return}const words=q.split(/\\s+/);const found=SEARCH_ITEMS.filter(p=>words.every(w=>(p.title+' '+p.description+' '+p.categories.join(' ')).toLocaleLowerCase().includes(w)));if(!found.length){results.innerHTML='<div class="search-empty">No matching writing found.</div>';return}for(const p of found){const a=document.createElement('a');a.href=p.url;a.className='search-hit';const b=document.createElement('b');b.textContent=p.title;const s=document.createElement('span');s.textContent=p.kind+' · '+p.categories.join(', ');a.append(b,s);results.append(a)}}
launch.addEventListener('click',show);close.addEventListener('click',hide);entry.addEventListener('input',render);overlay.addEventListener('click',e=>{if(e.target===overlay)hide()});document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();show()}else if(e.key==='Escape'&&overlay.classList.contains('open'))hide()});toggle.addEventListener('click',()=>{const open=nav.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open))});})();
</script>'''
    return head+'<body>'+header+'<main id="main-content">'+contents+'</main>'+footer+search_modal+script+'</body></html>'

def write(path,content):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf8')

def row(p,idx,root_rel=''):
    m=p['meta']
    img=Path(m['image']).name
    return f'''<a class="post-row" href="{root_rel}{p['url']}"><span class="post-index">{idx:02d} /</span><div class="post-main"><div class="post-meta">{p['kind']} &nbsp;·&nbsp; {esc(format_date(p['date']))} &nbsp;·&nbsp; {p['minutes']} MIN READ</div><h3>{esc(m['title'])}</h3><p class="post-desc">{esc(m['description'])}</p></div><img class="post-image" src="{root_rel}assets/{img}" loading="lazy" alt="{esc(m['image-alt'])}"/></a>'''

def make_home():
    _,b=document(ROOT/'index.qmd')
    # Raw HTML front-and-back surround the listing marker, which is Quarto-specific.
    b=b.replace('::: {#recent-writing .landing}\n:::','<div class="landing"><div class="post-list">'+''.join(row(p,i+1) for i,p in enumerate(POSTS[:4]))+'</div></div>')
    b=b.replace('<div class="formula" aria-label="Euler\'s identity">', '<div class="formula" aria-label="Euler\'s identity">')
    write('index.html',shell(b,'Home','Mathematical essays, patient explanations, and notes from the margins of a notebook.',body_class='home'))

def make_collection(kind):
    p=ROOT/kind/'index.qmd';m,b=document(p)
    marker='<div id="essay-listing"></div>' if kind=='essays' else '<div id="note-listing"></div>'
    selected=[p for p in POSTS if p['kind']==('Essay' if kind=='essays' else 'Note')]
    b=b.replace(marker,'<div class="post-list">'+''.join(row(p,i+1,'../') for i,p in enumerate(selected))+'</div>')
    write(f'{kind}/index.html',shell(b,kind.capitalize(),m['description'],'../',kind.capitalize()))

def clean_qmd_for_pandoc(body):
    # Quarto equation numbering/crossrefs, reproduced for the standalone edition.
    pattern=r'(?ms)^\$\$\n(.*?)^\$\$ \{#(eq-[\w-]+)\}$'
    matches=list(re.finditer(pattern,body))
    ids={m.group(2):index+1 for index,m in enumerate(matches)}
    for label,number in ids.items():
        body=body.replace('@'+label, f'[equation ({number})](#{label})')
    def add_number(m):
        number=ids[m.group(2)]
        return ('::: {#'+m.group(2)+' .numbered-equation}\n\n$$\n'
            +m.group(1)+'$$\n\n<span class="eq-tag">('+str(number)+')</span>\n\n:::' )
    body=re.sub(pattern,add_number,body)
    body=re.sub(r'\b@thm-[\w-]+','the theorem',body)
    return body

def pandoc_html(body,post):
    body=clean_qmd_for_pandoc(body)
    command=['pandoc','-f','markdown+tex_math_dollars+fenced_divs+citations','-t','html5','--mathml','--citeproc','--bibliography',str(ROOT/'references.bib')]
    run=subprocess.run(command,input=body,text=True,capture_output=True,check=True)
    return run.stdout

def make_article(p):
    m=p['meta'];relative='../';body=pandoc_html(p['body'],p)
    soup=BeautifulSoup(body,'html.parser')
    toc=[]
    for el in soup.find_all(['h2','h3']):
        if el.name=='h2' and el.get_text(' ',strip=True).lower()=='references':continue
        if el.get('id'):toc.append((el.name,el['id'],el.get_text(' ',strip=True)))
    toc_html=''.join(f'<a href="#{esc(heading_id)}">{esc(text)}</a>' for _,heading_id,text in toc)
    label='ESSAY / MATHEMATICS' if p['kind']=='Essay' else 'NOTE / MATHEMATICS'
    deck=m.get('description','')
    content=f'''<div class="article-frame"><a class="article-back" href="../{p['file'].parent.name}/index.html">← &nbsp; All {p['file'].parent.name}</a><div class="article-head"><div class="article-kicker">{label}</div><h1>{esc(m['title'])}</h1><p class="article-deck">{esc(deck)}</p><div class="article-meta"><span>{esc(format_date(p['date']))}</span><span>{p['minutes']} minute read</span><span>{esc(' · '.join(m['categories']))}</span></div></div><div class="article-layout"><article class="article-content">{str(soup)}<div class="article-end"><a href="../{p['file'].parent.name}/index.html">← Back to {p['file'].parent.name}</a><a href="../index.html">Home ↗</a></div></article><aside class="article-side" aria-label="Table of contents"><div class="toc-label">On this page</div><nav>{toc_html}</nav></aside></div></div>'''
    write(p['url'],shell(content,m['title'],deck,'../',p['file'].parent.name.capitalize(),'article'))

def make_about():
    _,b=document(ROOT/'about.qmd')
    write('about.html',shell(b,'About','About the author and the purpose of this mathematical notebook.',active='About'))

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for directory in ['assets','styles']:
        shutil.copytree(ROOT/directory,OUT/directory,dirs_exist_ok=True)
    (OUT/'.nojekyll').touch()
    make_home();make_collection('essays');make_collection('notes');make_about()
    for p in POSTS:make_article(p)
    print('Built',len(list(OUT.rglob('*.html'))),'HTML pages and assets in docs/')
