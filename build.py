#!/usr/bin/env python3
"""Build the verox static blog. Usage: python build.py.
Posts are optional: an empty posts/ directory produces a clean, empty website.
After importing Markdown posts, run `pip install -r requirements.txt` once.
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
POST_DIR = ROOT / 'posts'
SITE = 'https://abdullah-5j.github.io'
ASSET_VERSION = 'verox-20261024-tryhackme-refine'
SECTIONS = {
    'hackthebox': 'Hack The Box',
    'research': 'Research',
    'tryhackme': 'TryHackMe',
    'thoughts': 'Thoughts',
}
ORDER = ['hackthebox', 'research', 'tryhackme']
TOPICS = [
    'web-security', 'binary-exploitation', 'reverse-engineering',
    'digital-forensics', 'malware-analysis', 'windows-security',
    'linux', 'network-security', 'ctf', 'privilege-escalation',
    'xss', 'sql-injection',
]


def h(value):
    return html.escape(str(value), quote=True)


def svg(name, size=19):
    paths = {
        'feather': '<path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L3 12.5V21h8.5z"/><path d="m16 8-2 2"/><path d="M3 21l9-9"/>',
        'brain': '<path d="M12 18V5a3 3 0 0 0-5.5-1.6A4 4 0 0 0 4 10a4 4 0 0 0 2 7 4 4 0 0 0 6 1"/><path d="M12 18V5a3 3 0 0 1 5.5-1.6A4 4 0 0 1 20 10a4 4 0 0 1-2 7 4 4 0 0 1-6 1"/><path d="M9 9c-2 0-3 1-3 3m9-3c2 0 3 1 3 3"/>',
        'archive': '<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v12h14V8M10 12h4"/>',
        'list': '<path d="M4 6h16M4 12h16M4 18h16"/>',
        'tag': '<path d="M20 12l-8 8-9-9V4h7z"/><circle cx="7.5" cy="8" r="1"/>',
        'folder': '<path d="M3 7V5a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v11H3z"/>',
        'chevron': '<path d="m9 18 6-6-6-6"/>',
        'search': '<circle cx="10.7" cy="10.7" r="7.5"/><path d="m16.5 16.5 4.6 4.6"/>',
        'moon': '<path d="M20 15.2A8 8 0 0 1 8.8 4 8 8 0 1 0 20 15.2Z"/>',
        'calendar': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18"/>',
        'github': '<path d="M9 19c-4.3 1.3-4.3-2.2-6-2.5M9 22v-3.3c-4.5 1-6-1.8-6-5.3a5 5 0 0 1 1.3-3.5c-.1-.8-.5-2.4.2-3.7 0 0 1.4-.4 4 1.6a13 13 0 0 1 7 0c2.6-2 4-1.6 4-1.6.7 1.3.3 2.9.2 3.7a5 5 0 0 1 1.3 3.5c0 3.5-1.5 6.3-6 5.3V22"/>',
        'discord': '<path d="M18 5c-2-1-3-1.2-4-1.4l-.5 1.1a13 13 0 0 0-3 0L10 3.6C9 3.8 8 4 6 5 4 8 3 11 3 17c2 1.5 3.5 2.3 5 2.7l1-1.6m8 0 1 1.6c1.5-.4 3-1.2 5-2.7 0-6-1-9-3-12z"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/>',
        'monitor': '<rect x="2" y="3" width="20" height="15" rx="2"/><path d="M8 22h8m-4-4v4"/>',
        'cube': '<path d="m12 2 9 5v10l-9 5-9-5V7zM3 7l9 5 9-5m-9 5v10"/>',
        'target': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
        'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
        'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
        'x': '<path d="M3 3l18 18M3 21 21 3M3 3h4l14 18h-4L3 3z"/>',
        'medium': '<circle cx="5.5" cy="12" r="4.6" fill="currentColor" stroke="none"/><ellipse cx="15.5" cy="12" rx="2.7" ry="4.4" fill="currentColor" stroke="none"/><ellipse cx="21" cy="12" rx="1.2" ry="4.1" fill="currentColor" stroke="none"/>',
    }
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'


def page_path(section):
    return '/thoughts/' if section == 'thoughts' else f'/writeups/{section}/'


def nav_item(label, icon, href, active=False):
    return f'<a class="nav-item{" active" if active else ""}" href="{href}" {"aria-current=\"page\"" if active else ""}>{svg(icon)}<span>{h(label.upper())}</span></a>'


def sidebar(active):
    links = [
        ('Writeups','feather','/writeups/','writeups'),
        ('Thoughts','brain','/thoughts/','thoughts'),
        ('Archives','archive','/archives/','archives'),
        ('Categories','list','/categories/','categories'),
        ('Tags','tag','/tags/','tags'),
    ]
    social = [
        ('Website','monitor','/writeups/'),
        ('GitHub','github','https://github.com/abdullah-5j'),
        ('X','x','https://x.com/abdullah5j009'),
        ('Medium','medium','https://medium.com/@abdullah5j009'),
        ('TryHackMe','target','https://tryhackme.com/p/Verox.'),
        ('Hack The Box','cube','https://app.hackthebox.com/users/2654143'),
        ('Discord','discord','https://discord.com/users/@me'),
    ]
    ss = []
    for name,icon,href in social:
        if name == 'Discord':
            ss.append(f'<button type="button" class="social-link" id="discord-copy" title="Copy Discord username: notabdu11ah" aria-label="Copy Discord username: notabdu11ah">{svg(icon)}</button>')
        else:
            extra=' target="_blank" rel="noopener noreferrer"' if href.startswith('https:') else ''
            ss.append(f'<a class="social-link" href="{h(href)}" title="{h(name)}" aria-label="{h(name)}"{extra}>{svg(icon)}</a>')
    ss.append(f'<span id="theme-control-container"><button id="theme-toggle" class="theme-control" aria-label="Choose appearance" aria-expanded="false" title="Appearance">{svg("moon")}</button><span class="theme-menu" id="theme-menu" role="menu"><button type="button" data-theme-choice="light">☀ &nbsp; Light</button><button type="button" data-theme-choice="dark">☾ &nbsp; Dark</button><button type="button" data-theme-choice="system">▣ &nbsp; System</button></span></span>')
    nav=''.join(nav_item(*x[:3],active=(x[3]==active)) for x in links)
    return f'''<aside class="sidebar" id="sidebar">
    <div class="identity"><a href="/writeups/" aria-label="verox Writeups"><img class="portrait" src="/assets/avatar-king.jpg?v={ASSET_VERSION}" alt="verox crowned king avatar"/></a><a class="brand" href="/writeups/">verox</a><p class="subtitle">Writeups &amp; Thoughts</p></div>
    <nav class="side-nav" aria-label="Primary">{nav}</nav>
    <div class="social-wrap"><div class="social-icons">{''.join(ss)}</div></div><div class="copyright">© 2026 verox</div>
    </aside>'''


def short_list(posts):
    if not posts: return ''
    return ''.join(f'<a class="recent-link" href="{h(p["url"])}">{h(p["title"])}</a>' for p in posts[:5])


def rail(posts):
    tags=''.join(f'<a class="mini-tag" href="/tags/?tag={quote(tag)}">{h(tag)}</a>' for tag in TOPICS[:10])
    return f'''<aside class="rail" aria-label="Related content"><div class="rail-section"><h2>Recently Updated</h2>{short_list(posts)}</div>
    <div class="rail-section"><h2>Topics</h2><div class="mini-tags">{tags}</div></div></aside>'''


def wrapper(title, active, current, body, posts, description='Cybersecurity writeups, research, and thoughts by verox.'):
    seo_url = ('/writeups/' if current=='Writeups' else '/'+current.lower().replace(' ','-')+'/')
    return f'''<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
    <meta name="description" content="{h(description)}"/><meta name="theme-color" content="#0c1522"/><meta property="og:site_name" content="verox"/>
    <meta property="og:title" content="{h(title)} | verox"/><meta property="og:description" content="{h(description)}"/>
    <title>{h(title)} | verox</title><link rel="icon" href="/assets/avatar-king.jpg?v={ASSET_VERSION}"/><link rel="stylesheet" href="/assets/style.css?v={ASSET_VERSION}"/>
    <script>try{{const t=localStorage.getItem('verox-theme')||'dark';document.documentElement.dataset.theme=t==='system'?(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'):t}}catch(e){{}}</script></head>
    <body>{sidebar(active)}<div class="shell"><header class="topbar"><div class="crumbs"><button class="mobile-trigger" id="mobile-trigger" aria-label="Toggle menu">{svg('menu')}</button><a href="/writeups/">verox</a><span class="crumb-sep">›</span><span>{h(current)}</span></div><button type="button" class="search-pill" id="open-search" aria-label="Search articles">{svg('search')}Search...</button></header>
    <div class="layout"><main class="main-content" id="main">{body}</main>{rail(posts)}</div>
    <footer class="footer"><span>© 2026 <a href="/writeups/">verox</a>. Some rights reserved.</span><span>Design inspired by <a href="https://github.com/cotes2020/jekyll-theme-chirpy" target="_blank" rel="noopener noreferrer">Chirpy</a>.</span></footer></div>
    <div class="search-backdrop" id="search-backdrop" role="dialog" aria-modal="true" aria-label="Search writeups"><div class="search-dialog"><div class="search-input-row">{svg('search')}<input type="search" autocomplete="off" id="search-input" aria-label="Search posts" placeholder="Search writeups and thoughts..."/><button id="close-search" class="close-search" type="button" aria-label="Close search">Esc</button></div><div class="search-results" id="search-results"></div></div></div>
    <script src="/assets/app.js?v={ASSET_VERSION}" defer></script></body></html>'''


def heading(title, subtitle='', icon=None):
    return f'<div class="heading-block"><h1 class="page-title">{svg(icon,38) if icon else ""}{h(title)}</h1>{f"<p class=\"intro\">{h(subtitle)}</p>" if subtitle else ""}</div>'


def link_panel(label, url, count=None):
    count_html = f'<span class="category-count">{count} post{"s" if count != 1 else ""}</span>' if count is not None else ''
    return f'<div class="category-panel"><a class="category-link" href="{h(url)}">{svg("folder")}<span>{h(label)}{count_html}</span>{svg("chevron")}</a></div>'


def post_card(p):
    dt=f'<span>{svg("calendar",15)} {h(p["date_short"])}</span>' if p['date_short'] else ''
    meta=f'<div class="post-card-meta">{dt}<span>{svg("folder",15)} {h(SECTIONS[p["section"]])}</span></div>'
    image=f'<img class="post-thumb" src="{h(p["image"])}" alt="" loading="lazy"/>' if p.get('image') else ''
    return f'<article class="post-card{"" if image else " no-thumb"}"><div class="post-card-body"><h3 class="post-card-title"><a href="{h(p["url"])}">{h(p["title"])}</a></h3><p class="post-card-desc">{h(p["summary"])}</p>{meta}</div>{image}</article>'


def read_posts():
    out=[]
    for file in sorted(POST_DIR.rglob('*.md')):
        source=file.read_text(encoding='utf-8-sig')
        if not source.startswith('---\n'):
            raise ValueError(f'{file.relative_to(ROOT)} needs YAML front matter with title and section')
        try: _, yaml_text, body=source.split('---',2)
        except ValueError: raise ValueError(f'Bad front matter in {file}')
        try:
            import yaml
        except ImportError as ex:
            raise SystemExit('Missing dependency. Run: pip install -r requirements.txt') from ex
        data=yaml.safe_load(yaml_text) or {}
        title=str(data.get('title') or '').strip()
        section=str(data.get('section') or '').strip().lower().replace(' ','').replace('-','')
        if not title or section not in SECTIONS:
            raise ValueError(f'{file}: title and section ({", ".join(SECTIONS)}) are required')
        value=data.get('date')
        published=value.isoformat() if isinstance(value,(date,datetime)) else str(value).strip() if value else ''
        if published:
            try:
                parsed=datetime.fromisoformat(published.replace('Z','+00:00'))
                dt=parsed.replace(tzinfo=None)
            except ValueError:
                try: dt=datetime.combine(date.fromisoformat(published),time.min)
                except ValueError as ex: raise ValueError(f'{file}: date must be an ISO date or timestamp') from ex
        else: dt=None
        rel=file.relative_to(POST_DIR)
        slug = '-'.join(re.findall(r'[a-z0-9]+',rel.stem.lower())) or 'post'
        section_dir='thoughts' if section=='thoughts' else f'writeups/{section}'
        url=f'/{section_dir}/{slug}/'
        short_date=(dt.strftime('%b ') + str(dt.day) + dt.strftime(', %Y')) if dt else ''
        try: display_order=int(data.get('order',100000))
        except (TypeError,ValueError) as ex: raise ValueError(f'{file}: order must be an integer') from ex
        out.append({'title':title,'summary':str(data.get('summary') or '').strip(),'section':section,
                    'date':published,'date_short':short_date,
                    'dt':dt,'url':url,'tags':[str(t).strip().lower() for t in (data.get('tags') or [])],
                    'image':str(data.get('image') or '').strip(), 'body':body, 'source':str(rel),
                    'order':display_order})
    urls=[p['url'] for p in out]
    if len(urls)!=len(set(urls)):raise ValueError('Duplicate post slugs: rename one of the conflicting Markdown files')
    return sorted(out,key=lambda p:(p['order'],-p['dt'].toordinal() if p['dt'] else 0,p['title'].lower()))


def article_html(p):
    try: import mistune
    except ImportError as ex: raise SystemExit('Missing dependency. Run: pip install -r requirements.txt') from ex
    md=mistune.create_markdown(escape=True,plugins=['table','strikethrough','url'])
    body=md(p['body'])
    # headings automatically become anchor links for a future table of contents
    body=re.sub(r'<h([2-3])>(.*?)</h\1>',lambda m:f'<h{m.group(1)} id="{h("-".join(re.findall(r"[a-z0-9]+",re.sub("<[^>]+>","",m.group(2)).lower())))}">{m.group(2)}</h{m.group(1)}>',body)
    meta=(p['date_short']+' · ' if p['date_short'] else '')+SECTIONS[p['section']]
    return f'<article class="article"><div class="heading-block"><h1>{h(p["title"])}</h1><div class="article-meta">{h(meta)}</div></div><div class="article-body">{body}</div></article>'


def archive_html(posts):
    dated=[p for p in posts if p['dt']]
    groups=defaultdict(list)
    for p in dated: groups[p['dt'].year].append(p)
    output=[]
    for yr in sorted(groups,reverse=True):
        bits=[]
        for p in groups[yr]:
            mm=p['dt'].strftime('%d %b')
            bits.append(f'<div class="timeline-item"><span class="timeline-date">{h(mm)}</span><a href="{h(p["url"])}">{h(p["title"])}</a></div>')
        output.append(f'<section class="timeline"><h2 class="timeline-year">{yr}</h2><div class="timeline-rail">{"".join(bits)}</div></section>')
    return ''.join(output)


def write_file(rel,txt):
    path=ROOT/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(txt,encoding='utf8')


def build():
    posts=read_posts()
    write_file('site.json',json.dumps([{k:p[k] for k in ['title','summary','section','date','url','tags']} for p in posts],indent=2,ensure_ascii=False)+'\n')
    writeups=heading('Writeups','of Hack The Box, Research, and TryHackMe','feather')
    for section in ORDER:
        matches=[p for p in posts if p['section']==section]
        writeups+=link_panel(SECTIONS[section],page_path(section),len(matches))
    write_file('index.html',wrapper('Writeups','writeups','Writeups',writeups,posts))
    write_file('writeups/index.html',wrapper('Writeups','writeups','Writeups',writeups,posts))
    for section in ORDER:
        heading_page=heading(SECTIONS[section], 'Writeups' if section!='research' else 'Security research and technical notes')
        section_posts=[p for p in posts if p['section']==section]
        write_file(f'writeups/{section}/index.html',wrapper(SECTIONS[section],'writeups',SECTIONS[section],heading_page+''.join(post_card(p) for p in section_posts),posts))
    thought_posts=[p for p in posts if p['section']=='thoughts']
    write_file('thoughts/index.html',wrapper('Thoughts','thoughts','Thoughts',heading('Thoughts')+''.join(post_card(p) for p in thought_posts),posts))
    write_file('archives/index.html',wrapper('Archives','archives','Archives',heading('Archives')+archive_html(posts),posts))
    categories=heading('Categories')+link_panel('Writeups','/writeups/',len(posts)-len(thought_posts))+link_panel('Thoughts','/thoughts/',len(thought_posts))
    write_file('categories/index.html',wrapper('Categories','categories','Categories',categories,posts))
    tags=Counter(t for p in posts for t in p['tags'])
    vocabulary=TOPICS+[t for t in sorted(tags) if t not in TOPICS]
    pills=''.join(f'<a class="tag-pill" href="/tags/?tag={quote(t)}">{h(t)}{f"<span class=\"tag-count\">{tags[t]}</span>" if tags[t] else ""}</a>' for t in vocabulary)
    tags_body=heading('Tags')+'<div class="tags-list">'+pills+'</div><div id="tag-results"></div>'
    tag_script='''<script>(async()=>{const t=new URLSearchParams(location.search).get('tag');if(!t)return;const target=document.getElementById('tag-results');try{const r=await fetch('/site.json');const posts=await r.json();const matches=posts.filter(p=>p.tags.includes(t));let box='<h2 class="section-title">'+t.replace(/[<>&]/g,'')+'</h2>';box+=matches.map(p=>'<article class="post-card no-thumb"><div class="post-card-body"><h3 class="post-card-title"><a href="'+p.url+'">'+p.title.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</a></h3></div></article>').join('');target.innerHTML=box;}catch{}})();</script>'''
    write_file('tags/index.html',wrapper('Tags','tags','Tags',tags_body+tag_script,posts))
    for p in posts:
        rel=p['url'].lstrip('/')+'index.html'
        write_file(rel,wrapper(p['title'],'thoughts' if p['section']=='thoughts' else 'writeups',p['title'],article_html(p),posts,p['summary'] or 'A cybersecurity writeup by verox.'))
    print('Built verox:',len(posts),'posts. Categories:',{s:sum(p['section']==s for p in posts) for s in SECTIONS})

if __name__=='__main__':
    build()
