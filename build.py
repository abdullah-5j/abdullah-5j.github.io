#!/usr/bin/env python3
"""Build the verox static blog. Usage: python build.py.
Posts are optional: an empty posts/ directory produces a clean, empty website.
After importing Markdown posts, run `pip install -r requirements.txt` once.
"""
from __future__ import annotations

import html
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POST_DIR = ROOT / 'posts'
SITE = 'https://abdullah-5j.github.io'
ASSET_VERSION = 'verox-20261024-full-features'
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

AUTHOR = 'verox'
AUTHOR_URL = f'{SITE}/writeups/'


def h(value):
    return html.escape(str(value), quote=True)


def slugify(value):
    return '-'.join(re.findall(r'[a-z0-9]+', str(value).lower())) or 'item'


def tag_url(tag):
    return f'/tags/{slugify(tag)}/'


def plain_text(markdown):
    text=re.sub(r'!\[([^]]*)\]\([^)]*\)', r'\1', markdown)
    text=re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', text)
    text=re.sub(r'[`*_>#|~-]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def git_updated(rel, fallback):
    try:
        result=subprocess.run(['git','log','-1','--format=%cs','--',str(rel)],cwd=ROOT,
                              capture_output=True,text=True,check=False)
        value=result.stdout.strip()
        return datetime.combine(date.fromisoformat(value),time.min) if value else fallback
    except (OSError,ValueError):
        return fallback


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
        'rss': '<path d="M4 11a9 9 0 0 1 9 9M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1" fill="currentColor" stroke="none"/>',
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
        ('RSS','rss','/feed.xml'),
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


def recently_updated(posts):
    floor=datetime.min
    return sorted(posts,key=lambda p:p.get('updated_dt') or p.get('dt') or floor,reverse=True)


def trending_tags(posts, limit=10):
    counts=Counter(tag for p in posts for tag in p['tags'])
    return sorted(counts,key=lambda tag:(-counts[tag],tag))[:limit]


def rail(posts, toc_html=''):
    tags=''.join(f'<a class="mini-tag" href="{tag_url(tag)}">{h(tag)}</a>' for tag in trending_tags(posts))
    toc=f'<div class="rail-section toc-section"><h2>Contents</h2>{toc_html}</div>' if toc_html else ''
    return f'''<aside class="rail" aria-label="Related content"><div class="rail-section"><h2>Recently Updated</h2>{short_list(recently_updated(posts))}</div>
    <div class="rail-section"><h2>Trending Tags</h2><div class="mini-tags">{tags}</div></div>{toc}</aside>'''


def wrapper(title, active, current, body, posts, description='Cybersecurity writeups, research, and thoughts by verox.',
            canonical_path=None, image='', page_type='website', published='', updated='', toc_html=''):
    canonical_path=canonical_path or ('/writeups/' if current=='Writeups' else '/'+slugify(current)+'/')
    canonical=SITE+canonical_path
    share_image=SITE+(image if image.startswith('/') else '/assets/avatar-king.jpg')
    schema={'@context':'https://schema.org','@type':'BlogPosting' if page_type=='article' else 'WebPage',
            'name':title,'headline':title,'description':description,'url':canonical,
            'author':{'@type':'Person','name':AUTHOR,'url':AUTHOR_URL},'image':share_image}
    if page_type=='article':
        if published: schema['datePublished']=published
        if updated: schema['dateModified']=updated
    structured=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    og_type='article' if page_type=='article' else 'website'
    article_dates=(f'<meta property="article:published_time" content="{h(published)}"/><meta property="article:modified_time" content="{h(updated or published)}"/>' if page_type=='article' and published else '')
    return f'''<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
    <meta name="description" content="{h(description)}"/><meta name="theme-color" content="#0c1522"/><meta name="author" content="{AUTHOR}"/>
    <link rel="canonical" href="{h(canonical)}"/><link rel="alternate" type="application/rss+xml" title="verox feed" href="/feed.xml"/>
    <meta property="og:site_name" content="verox"/><meta property="og:type" content="{og_type}"/><meta property="og:url" content="{h(canonical)}"/>{article_dates}
    <meta property="og:title" content="{h(title)} | verox"/><meta property="og:description" content="{h(description)}"/><meta property="og:image" content="{h(share_image)}"/>
    <meta name="twitter:card" content="summary_large_image"/><meta name="twitter:title" content="{h(title)} | verox"/><meta name="twitter:description" content="{h(description)}"/><meta name="twitter:image" content="{h(share_image)}"/>
    <script type="application/ld+json">{structured}</script><title>{h(title)} | verox</title>
    <link rel="icon" type="image/svg+xml" href="/assets/site-icon.svg?v={ASSET_VERSION}"/><link rel="alternate icon" href="/assets/avatar-king.jpg?v={ASSET_VERSION}"/>
    <link rel="apple-touch-icon" href="/assets/avatar-king.jpg?v={ASSET_VERSION}"/><link rel="manifest" href="/site.webmanifest"/>
    <link rel="stylesheet" href="/assets/style.css?v={ASSET_VERSION}"/>
    <script>try{{const t=localStorage.getItem('verox-theme')||'dark';document.documentElement.dataset.theme=t==='system'?(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'):t}}catch(e){{}}</script></head>
    <body>{sidebar(active)}<div class="shell"><header class="topbar"><div class="crumbs"><button class="mobile-trigger" id="mobile-trigger" aria-label="Toggle menu">{svg('menu')}</button><a href="/writeups/">verox</a><span class="crumb-sep">›</span><span>{h(current)}</span></div><button type="button" class="search-pill" id="open-search" aria-label="Search articles">{svg('search')}Search...</button></header>
    <div class="layout"><main class="main-content" id="main">{body}</main>{rail(posts,toc_html)}</div>
    <footer class="footer"><span>© 2026 <a href="/writeups/">verox</a>. Some rights reserved.</span><span>Design inspired by <a href="https://github.com/cotes2020/jekyll-theme-chirpy" target="_blank" rel="noopener noreferrer">Chirpy</a>.</span></footer></div>
    <button id="back-to-top" class="back-to-top" type="button" aria-label="Back to top">↑</button>
    <dialog id="image-lightbox" class="image-lightbox"><button type="button" class="lightbox-close" aria-label="Close image">×</button><img alt=""/><p></p></dialog>
    <div class="update-toast" id="update-toast" role="status" aria-live="polite"><span>New content available</span><button type="button" id="apply-update">Update</button><button type="button" id="dismiss-update" aria-label="Dismiss update">×</button></div>
    <div class="search-backdrop" id="search-backdrop" role="dialog" aria-modal="true" aria-label="Search writeups"><div class="search-dialog"><div class="search-input-row">{svg('search')}<input type="search" autocomplete="off" id="search-input" aria-label="Search posts" placeholder="Search writeups and thoughts..."/><button id="close-search" class="close-search" type="button" aria-label="Close search">Esc</button></div><div class="search-results" id="search-results"></div></div></div>
    <script src="/assets/app.js?v={ASSET_VERSION}" defer></script></body></html>'''


def heading(title, subtitle='', icon=None):
    return f'<div class="heading-block"><h1 class="page-title">{svg(icon,38) if icon else ""}{h(title)}</h1>{f"<p class=\"intro\">{h(subtitle)}</p>" if subtitle else ""}</div>'


def link_panel(label, url, count=None):
    count_html = f'<span class="category-count">{count} post{"s" if count != 1 else ""}</span>' if count is not None else ''
    return f'<div class="category-panel"><a class="category-link" href="{h(url)}">{svg("folder")}<span>{h(label)}{count_html}</span>{svg("chevron")}</a></div>'


def post_card(p):
    dt=f'<span>{svg("calendar",15)} {h(p["date_short"])}</span>' if p['date_short'] else ''
    event=f'<span class="post-event">{h(p["event"])}</span>' if p.get('event') else ''
    meta=f'<div class="post-card-meta">{dt}<span>{svg("folder",15)} {h(SECTIONS[p["section"]])}</span>{event}</div>'
    fit=' contain' if p.get('image_fit') == 'contain' else ''
    background=' black' if p.get('image_background') == 'black' else ''
    image=f'<img class="post-thumb{fit}{background}" src="{h(p["image"])}" alt="{h(p["title"])} artwork" loading="lazy"/>' if p.get('image') else ''
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
        source_rel=file.relative_to(ROOT)
        slug = '-'.join(re.findall(r'[a-z0-9]+',rel.stem.lower())) or 'post'
        section_dir='thoughts' if section=='thoughts' else f'writeups/{section}'
        url=f'/{section_dir}/{slug}/'
        short_date=(dt.strftime('%b ') + str(dt.day) + dt.strftime(', %Y')) if dt else ''
        updated_dt=git_updated(source_rel,dt)
        updated=updated_dt.date().isoformat() if updated_dt else published
        updated_short=(updated_dt.strftime('%b ') + str(updated_dt.day) + updated_dt.strftime(', %Y')) if updated_dt else short_date
        searchable=plain_text(body)
        read_time=max(1,math.ceil(len(re.findall(r'\b[\w-]+\b',searchable))/220))
        try: display_order=int(data.get('order',100000))
        except (TypeError,ValueError) as ex: raise ValueError(f'{file}: order must be an integer') from ex
        image_fit=str(data.get('image_fit') or 'cover').strip().lower()
        if image_fit not in ('cover','contain'):
            raise ValueError(f'{file}: image_fit must be cover or contain')
        image_background=str(data.get('image_background') or '').strip().lower()
        if image_background not in ('','black'):
            raise ValueError(f'{file}: image_background must be black when provided')
        out.append({'title':title,'summary':str(data.get('summary') or '').strip(),'section':section,
                    'date':published,'date_short':short_date,'updated':updated,'updated_short':updated_short,
                    'updated_dt':updated_dt,'read_time':read_time,'search_text':searchable,
                    'dt':dt,'url':url,'tags':[str(t).strip().lower() for t in (data.get('tags') or [])],
                    'image':str(data.get('image') or '').strip(), 'image_fit':image_fit,
                    'image_background':image_background,
                    'event':str(data.get('event') or '').strip(), 'body':body, 'source':str(rel),
                    'order':display_order})
    urls=[p['url'] for p in out]
    if len(urls)!=len(set(urls)):raise ValueError('Duplicate post slugs: rename one of the conflicting Markdown files')
    return sorted(out,key=lambda p:(p['order'],-p['dt'].toordinal() if p['dt'] else 0,p['title'].lower()))


def article_html(p, posts):
    try: import mistune
    except ImportError as ex: raise SystemExit('Missing dependency. Run: pip install -r requirements.txt') from ex
    md=mistune.create_markdown(escape=True,plugins=['table','strikethrough','url'])
    body=md(p['body'])
    headings=[]
    seen=Counter()
    def heading_repl(match):
        level=int(match.group(1)); content=match.group(2)
        label=re.sub('<[^>]+>','',content)
        base=slugify(label); seen[base]+=1
        anchor=base if seen[base]==1 else f'{base}-{seen[base]}'
        headings.append((level,anchor,label))
        return f'<h{level} id="{h(anchor)}"><a class="heading-anchor" href="#{h(anchor)}" aria-label="Link to {h(label)}">#</a>{content}</h{level}>'
    body=re.sub(r'<h([2-3])>(.*?)</h\1>',heading_repl,body,flags=re.S)
    def code_repl(match):
        attrs=match.group(1); code=match.group(2)
        lines=code.split('\n')
        if lines and lines[-1]=='': lines=lines[:-1]
        numbered=''.join(f'<span class="code-line" data-line="{i}">{line or " "}</span>' for i,line in enumerate(lines,1))
        return f'<div class="code-block"><button type="button" class="code-copy" aria-label="Copy code">Copy</button><pre><code{attrs}>{numbered}</code></pre></div>'
    body=re.sub(r'<pre><code([^>]*)>(.*?)</code></pre>',code_repl,body,flags=re.S)
    toc_html='<ol class="toc-list">'+''.join(f'<li class="toc-level-{level}"><a href="#{h(anchor)}">{h(label)}</a></li>' for level,anchor,label in headings)+'</ol>' if headings else ''
    category=SECTIONS[p['section']]
    meta=[h(f'Posted {p["date_short"]}' if p['date_short'] else 'Published'),f'By <a href="/writeups/">{AUTHOR}</a>',h(f'{p["read_time"]} min read')]
    if p.get('event'): meta.append(h(p['event']))
    tags=''.join(f'<a class="post-tag" href="{tag_url(tag)}">{h(tag)}</a>' for tag in p['tags'])
    candidates=[]
    current_tags=set(p['tags'])
    for candidate in posts:
        if candidate['url']==p['url']: continue
        score=len(current_tags.intersection(candidate['tags']))*3+(2 if candidate['section']==p['section'] else 0)
        candidates.append((score,candidate.get('updated_dt') or candidate.get('dt') or datetime.min,candidate))
    candidates.sort(key=lambda item:(item[0],item[1]),reverse=True)
    related=[item[2] for item in candidates[:3]]
    related_html=''.join(f'<a class="related-card" href="{h(item["url"])}"><time>{h(item["date_short"])}</time><strong>{h(item["title"])}</strong><span>{h(item["summary"])}</span></a>' for item in related)
    related_section=f'<section class="related-posts"><h2>Further Reading</h2><div class="related-grid">{related_html}</div></section>' if related_html else ''
    idx=next(i for i,item in enumerate(posts) if item['url']==p['url'])
    newer=posts[idx-1] if idx>0 else None
    older=posts[idx+1] if idx+1<len(posts) else None
    nav_bits=[]
    if older: nav_bits.append(f'<a class="post-nav-link older" href="{h(older["url"])}"><small>Older</small><span>{h(older["title"])}</span></a>')
    if newer: nav_bits.append(f'<a class="post-nav-link newer" href="{h(newer["url"])}"><small>Newer</small><span>{h(newer["title"])}</span></a>')
    post_nav=f'<nav class="post-navigation" aria-label="Post navigation">{"".join(nav_bits)}</nav>' if nav_bits else ''
    article=f'''<article class="article"><div class="heading-block"><h1>{h(p["title"])}</h1><div class="article-meta">{'<span>·</span>'.join(meta)}</div></div>
    <div class="article-body">{body}</div><footer class="post-tail"><div class="post-taxonomy"><a class="post-category" href="{page_path(p['section'])}">{h(category)}</a><div class="post-tags">{tags}</div></div></footer></article>{related_section}{post_nav}'''
    return article,toc_html


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


def feed_xml(posts):
    dated=[p for p in posts if p.get('dt')]
    newest=max((p.get('updated_dt') or p['dt'] for p in dated),default=datetime.now())
    build_date=format_datetime(newest.replace(tzinfo=timezone.utc),usegmt=True)
    items=[]
    for p in recently_updated(dated)[:20]:
        pub=format_datetime(p['dt'].replace(tzinfo=timezone.utc),usegmt=True)
        items.append(f'''<item><title>{h(p['title'])}</title><link>{SITE}{p['url']}</link><guid isPermaLink="true">{SITE}{p['url']}</guid><pubDate>{pub}</pubDate><description>{h(p['summary'])}</description></item>''')
    return f'''<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>verox</title><link>{SITE}/writeups/</link><description>Cybersecurity writeups, research, and thoughts by verox.</description><language>en</language><lastBuildDate>{build_date}</lastBuildDate><atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>{''.join(items)}</channel></rss>\n'''


def sitemap_xml(posts, tags):
    paths=['/','/writeups/','/thoughts/','/archives/','/categories/','/tags/']
    paths += [f'/writeups/{section}/' for section in ORDER]
    paths += [p['url'] for p in posts]
    paths += [tag_url(tag) for tag in tags]
    latest=max((p.get('updated') or p.get('date') or '' for p in posts),default='')
    urls=''.join(f'<url><loc>{SITE}{path}</loc>{f"<lastmod>{latest}</lastmod>" if latest else ""}</url>' for path in dict.fromkeys(paths))
    return f'''<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n'''


def service_worker_source():
    return '''const CACHE='__VERSION__';
const CORE=['/','/writeups/','/archives/','/categories/','/tags/','/site.json','/assets/style.css?v=__VERSION__','/assets/app.js?v=__VERSION__','/assets/site-icon.svg?v=__VERSION__'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE))));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('message',event=>{if(event.data==='SKIP_WAITING')self.skipWaiting()});
self.addEventListener('fetch',event=>{if(event.request.method!=='GET')return;const request=event.request;if(request.mode==='navigate'){event.respondWith(fetch(request).then(response=>{const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(request,copy));return response}).catch(()=>caches.match(request).then(hit=>hit||caches.match('/writeups/'))));return}event.respondWith(caches.match(request).then(hit=>hit||fetch(request).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(request,copy))}return response})))});
'''.replace('__VERSION__',ASSET_VERSION)


def build():
    posts=read_posts()
    search_rows=[{k:p[k] for k in ['title','summary','section','date','updated','url','tags','search_text']} for p in posts]
    write_file('site.json',json.dumps(search_rows,indent=2,ensure_ascii=False)+'\n')
    writeups=heading('Writeups','of Hack The Box, Research, and TryHackMe','feather')
    for section in ORDER:
        matches=[p for p in posts if p['section']==section]
        writeups+=link_panel(SECTIONS[section],page_path(section),len(matches))
    write_file('index.html',wrapper('Writeups','writeups','Writeups',writeups,posts,canonical_path='/writeups/'))
    write_file('writeups/index.html',wrapper('Writeups','writeups','Writeups',writeups,posts,canonical_path='/writeups/'))
    for section in ORDER:
        heading_page=heading(SECTIONS[section], 'Writeups' if section!='research' else 'Security research and technical notes')
        section_posts=[p for p in posts if p['section']==section]
        write_file(f'writeups/{section}/index.html',wrapper(SECTIONS[section],'writeups',SECTIONS[section],heading_page+''.join(post_card(p) for p in section_posts),posts,canonical_path=page_path(section)))
    thought_posts=[p for p in posts if p['section']=='thoughts']
    write_file('thoughts/index.html',wrapper('Thoughts','thoughts','Thoughts',heading('Thoughts')+''.join(post_card(p) for p in thought_posts),posts,canonical_path='/thoughts/'))
    write_file('archives/index.html',wrapper('Archives','archives','Archives',heading('Archives')+archive_html(posts),posts,canonical_path='/archives/'))
    categories=heading('Categories')+link_panel('Writeups','/writeups/',len(posts)-len(thought_posts))+link_panel('Thoughts','/thoughts/',len(thought_posts))
    write_file('categories/index.html',wrapper('Categories','categories','Categories',categories,posts,canonical_path='/categories/'))
    tags=Counter(t for p in posts for t in p['tags'])
    vocabulary=sorted(tags,key=lambda tag:(tag.lower()))
    pills=''.join(f'<a class="tag-pill" href="{tag_url(t)}">{h(t)}<span class="tag-count">{tags[t]}</span></a>' for t in vocabulary)
    tags_body=heading('Tags')+'<div class="tags-list">'+pills+'</div>'
    write_file('tags/index.html',wrapper('Tags','tags','Tags',tags_body,posts,canonical_path='/tags/'))
    for tag in vocabulary:
        matches=[p for p in posts if tag in p['tags']]
        body=heading(tag,f'{len(matches)} post{"s" if len(matches)!=1 else ""}')+''.join(post_card(p) for p in matches)
        write_file(f'tags/{slugify(tag)}/index.html',wrapper(tag,'tags',tag,body,posts,canonical_path=tag_url(tag)))
    for p in posts:
        rel=p['url'].lstrip('/')+'index.html'
        article,toc_html=article_html(p,posts)
        write_file(rel,wrapper(p['title'],'thoughts' if p['section']=='thoughts' else 'writeups',p['title'],article,posts,p['summary'] or 'A cybersecurity writeup by verox.',
                               canonical_path=p['url'],image=p['image'],page_type='article',published=p['date'],updated=p['updated'],toc_html=toc_html))
    write_file('feed.xml',feed_xml(posts))
    write_file('sitemap.xml',sitemap_xml(posts,vocabulary))
    write_file('robots.txt',f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    manifest={'name':'verox — Writeups & Thoughts','short_name':'verox','start_url':'/writeups/','scope':'/','display':'standalone',
              'background_color':'#0e1520','theme_color':'#0c1522','description':'Cybersecurity writeups, research, and thoughts by verox.',
              'icons':[{'src':'/assets/site-icon.svg','sizes':'any','type':'image/svg+xml','purpose':'any maskable'}]}
    write_file('site.webmanifest',json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    write_file('sw.js',service_worker_source())
    icon='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="112" fill="#0b121f"/><path d="M122 130h74l60 166 60-166h74L289 382h-67z" fill="#b3a1f0"/><circle cx="256" cy="256" r="220" fill="none" stroke="#2a3646" stroke-width="18"/></svg>'''
    write_file('assets/site-icon.svg',icon)
    not_found=heading('404','That page could not be found.')+'<p class="not-found-copy">The address may have changed or the page may no longer exist.</p><a class="primary-action" href="/writeups/">Return to writeups</a>'
    write_file('404.html',wrapper('404','', 'Page not found',not_found,posts,'The requested page could not be found.',canonical_path='/404.html'))
    print('Built verox:',len(posts),'posts. Categories:',{s:sum(p['section']==s for p in posts) for s in SECTIONS})

if __name__=='__main__':
    build()
