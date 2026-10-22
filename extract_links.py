import re
from datetime import datetime
from collections import defaultdict, OrderedDict
from urllib.parse import urlparse

with open('extracted/_chat.txt', 'r', encoding='utf-8') as f:
    content = f.read()

msg_pattern = re.compile(r'\[(\d{2}/\d{2}/\d{2}), (\d{1,2}:\d{2}:\d{2}\s*[AP]M)\]')
positions = [(m.start(), m.group(1)) for m in msg_pattern.finditer(content)]

messages = []
for i, (pos, date_str) in enumerate(positions):
    end = positions[i+1][0] if i+1 < len(positions) else len(content)
    msg_text = content[pos:end]
    try:
        dt = datetime.strptime(date_str, '%d/%m/%y')
    except:
        continue
    messages.append((dt, msg_text))

cutoff = datetime(2025, 10, 22)
recent = [(dt, msg) for dt, msg in messages if dt >= cutoff]

url_pattern = re.compile(r'https?://[^\s\]<>"]+')
all_entries = []
for dt, msg in recent:
    urls = url_pattern.findall(msg)
    for url in urls:
        clean_url = url.rstrip('.,;:!?)>"').rstrip('`')
        ctx_match = re.search(r'\] [^:]+: (.+)', msg, re.DOTALL)
        ctx = ''
        if ctx_match:
            ctx = ctx_match.group(1).strip()
            ctx = re.sub(r'https?://[^\s]+', '', ctx)
            ctx = re.sub(r'<attached:[^>]+>', '', ctx)
            ctx = re.sub(r'\u200e', '', ctx)
            ctx = ctx.strip()[:200].replace('\n', ' ').strip()
        all_entries.append((dt.strftime('%Y-%m-%d'), clean_url, ctx))

skip_patterns = ['localhost', 'supabase.co', 'runpod.ai', 'modal.run',
                'nebius.com', 'tokenfactory.nebius', 'hana.ondemand.com', 'cfapps.',
                'gpay.app.goo.gl', 'icici.co', 'greythr.com', 'vakilsearch.com',
                'littlebirdygifts.com', 'airbnb.co', 'maps.app.goo.gl', 'google.com/maps',
                'myaccount.google.com', 'forms.gle', 'main-api:', 'your-host']

seen = set()
cat_map = defaultdict(list)

for date, url, ctx in all_entries:
    if url in seen:
        continue
    seen.add(url)

    skip = False
    for s in skip_patterns:
        if s in url:
            skip = True
            break
    if skip:
        continue

    domain = urlparse(url).netloc.lower()

    if 'x.com' in domain or 'twitter.com' in domain:
        cat = 'X (Twitter) Posts'
    elif 'youtube.com' in domain or 'youtu.be' in domain:
        cat = 'YouTube Videos'
    elif 'linkedin.com' in domain or 'lnkd.in' in domain:
        cat = 'LinkedIn Posts'
    elif 'github.com' in domain:
        cat = 'GitHub Repositories'
    elif 'arxiv.org' in domain or 'researchgate.net' in domain:
        cat = 'Research Papers'
    elif 'kaggle.com' in domain:
        cat = 'ML / Data Science Resources'
    elif 'coursera.org' in domain:
        cat = 'Online Courses'
    elif 'geeksforgeeks.org' in domain:
        cat = 'Technical Articles'
    elif 'colab.research.google.com' in domain:
        cat = 'Google Colab Notebooks'
    elif 'figma.com' in domain:
        cat = 'Design Tools'
    elif 'claude.ai' in domain or 'anthropic.com' in domain or 'openai.com' in domain:
        cat = 'AI Platforms & APIs'
    elif 'groq.com' in domain or 'googleapis.com' in domain:
        cat = 'AI Platforms & APIs'
    elif 'credly.com' in domain:
        cat = 'Certifications & Badges'
    elif 'community.sap.com' in domain:
        cat = 'SAP & Enterprise Tech'
    elif 'drive.google.com' in domain or 'share.google' in domain or 'photos.app.goo.gl' in domain:
        cat = 'Google Drive / Shared Files'
    elif 'instagram.com' in domain:
        cat = 'Social Media'
    elif 'healthline.com' in domain:
        cat = 'Health & Wellness'
    elif 'neo4j.io' in domain:
        cat = 'Databases & Tools'
    elif 'aicrowd.com' in domain:
        cat = 'AI Competitions'
    elif 'startup.jobs' in domain:
        cat = 'Career Resources'
    elif 'languagemodelbuilder.com' in domain or 'signals.forwardfuture.com' in domain:
        cat = 'AI Tools'
    elif 'dheeplearning.co.in' in domain:
        cat = 'Personal Projects'
    elif 'itresonance.com' in domain or 'ditrtransform' in domain:
        cat = 'Work Projects'
    elif 'filmflow' in url or 'railway.app' in domain:
        cat = 'Personal Projects'
    elif 'imdb.com' in domain:
        cat = 'Entertainment'
    elif 'sharepoint.com' in domain or 'zoom.us' in domain:
        cat = 'Work / Meetings'
    elif 'supabase.com' in domain:
        cat = 'Technical Articles'
    else:
        cat = 'Other'

    cat_map[cat].append((date, url, ctx))

priority = [
    'X (Twitter) Posts', 'LinkedIn Posts', 'YouTube Videos',
    'GitHub Repositories', 'Research Papers', 'Technical Articles',
    'Online Courses', 'ML / Data Science Resources', 'Google Colab Notebooks',
    'AI Platforms & APIs', 'AI Tools', 'AI Competitions',
    'SAP & Enterprise Tech', 'Certifications & Badges',
    'Career Resources', 'Databases & Tools', 'Design Tools',
    'Personal Projects', 'Work Projects', 'Work / Meetings',
    'Google Drive / Shared Files', 'Social Media', 'Entertainment',
    'Health & Wellness', 'Other'
]

md = []
md.append('# WhatsApp Saved Links - Curated Collection')
md.append('')
md.append('> Extracted from WhatsApp "Message Yourself" chat | **Period: Oct 2025 - Oct 2026** | **%d unique links**' % sum(len(v) for v in cat_map.values()))
md.append('')
md.append('## Table of Contents')
md.append('')
for cat in priority:
    if cat in cat_map:
        anchor = cat.lower().replace(' ', '-').replace('/', '').replace('&', '').replace('(', '').replace(')', '')
        md.append('- [%s (%d)](#%s)' % (cat, len(cat_map[cat]), anchor))
md.append('')
md.append('---')
md.append('')

for cat in priority:
    if cat not in cat_map:
        continue
    items = cat_map[cat]
    md.append('## %s' % cat)
    md.append('')
    md.append('| Date | Link | Context |')
    md.append('|------|------|---------|')
    for date, url, ctx in items:
        ctx_clean = ctx.replace('|', '/').replace('\n', ' ')[:100]
        display = url if len(url) <= 80 else url[:77] + '...'
        md.append('| %s | [%s](%s) | %s |' % (date, display, url, ctx_clean))
    md.append('')

md.append('---')
md.append('')
md.append('*Auto-extracted and categorized from WhatsApp chat export*')

output = '\n'.join(md)
with open('WHATSAPP_LINKS.md', 'w', encoding='utf-8') as f:
    f.write(output)

print('Written %d lines to WHATSAPP_LINKS.md' % len(md))
print('Categories: %d' % len(cat_map))
for cat in priority:
    if cat in cat_map:
        print('  %s: %d' % (cat, len(cat_map[cat])))
