import json,re,collections
d=json.load(open('data/lvo_2026_lists_raw.json'))
norm=lambda s:s.replace('\xa0',' ').replace('’',"'").replace('‘',"'").strip()
FACTIONS=['Space Marines','Orks','Adeptus Custodes','Necrons','Tyranids',"T'au Empire",'Imperial Knights','World Eaters','Chaos Space Marines','Chaos Daemons','Adeptus Mechanicus','Death Guard',"Emperor's Children",'Leagues of Votann','Adepta Sororitas','Grey Knights','Astra Militarum','Aeldari','Thousand Sons','Chaos Knights','Genestealer Cults','Drukhari','Imperial Agents']
CHAPTERS=['Dark Angels','Blood Angels','Space Wolves','Ultramarines','Black Templars','Salamanders','Iron Hands','Imperial Fists','Raven Guard','White Scars','Deathwatch']
FD={'take and hold':'Take and Hold','priority assets':'Priority Assets','purge the foe':'Purge the Foe','reconnaissance':'Reconnaissance','disruption':'Disruption'}
PROTECT={'Legends of Saga and Song':'Legends of Saga@Song','Ordo Xenos, Alien Hunters':'Ordo Xenos@@Alien Hunters'}
# detachment vocab
dv=set()
for r in d:
    for l in r['text'].split('\n'):
        m=re.match(r'^(.*) \(\d Detachment Points\)$',norm(l))
        if m:
            s=m.group(1)
            for k,v in PROTECT.items(): s=s.replace(k,v)
            for p in re.split(r',\s*and\s+|,\s*|\s+and\s+',s):
                p=p.replace('@@',', ').replace('@',' and ').strip()
                if p: dv.add(p)
dv.add('Cohort Acquisitus'); dv.add('Warhost')
for extra in ['Soul Grinder','Plaguebringers']: pass; dv.add("Da Big Hunt")
dvl={x.lower():x for x in dv}
dvl['lions of the emperor']='Lions of the Emperor'
# unit vocab from standard format
uv=collections.Counter()
for r in d:
    L=[norm(l) for l in r['text'].split('\n')]
    if not any(re.match(r'^Strike Force \(2,?000 [Pp]oints\)$',l) for l in L): continue
    started=False
    for l in L:
        if re.match(r'^Strike Force \(',l): started=True; continue
        if not started: continue
        m=re.match(r'^([^•\d(][^(]*?) \((\d[\d,]*) [Pp]oints\)$',l)
        if m: uv[m.group(1)]+=1
for r in d:
    for l in r['text'].split('\n'):
        l=norm(l)
        m=re.match(r"^(?:[A-Za-z]{4}\d*:\s*)?(?:\d+x\s+)?([A-Z][A-Za-z' \-]+?)\s*(?:\[WARLORD\]\s*)?[\(\[]\d+ (?:pts|points)[\)\]]:?",l,re.I)
        if m and len(m.group(1))>3 and not re.search(r'epic hero|character|battleline|infantry|attached|dedicated|other|vehicle|monster|beast|mounted|fortification|swarm|army roster|strike force',m.group(1),re.I): uv[m.group(1).strip()]+=0.5
uv={k:v for k,v in uv.items() if v>=1 or k in uv and v>=0.5}
uv['Soul Grinder']=1
UV=sorted(uv,key=len,reverse=True)
unit_re=re.compile(r'^(?:[A-Za-z]{4}\d*:\s*)?(?:\d+\s*-\s*)?(?:\d+x\s+|x\d+\s+)?(?P<name>'+'|'.join(re.escape(u) for u in UV)+r')(?=$|[\s\[\(:\-,])',re.I)
pts_re=re.compile(r'[\(\[]\s*\+?(\d[\d,]*)\s*(?:points|pts|Points)|-\s*(\d+)\s*pts|^(\d+)\s*-')
UVL={u.lower():u for u in UV}
res=[]
for r in d:
    t=r['text']; i=t.find('LVO 2026 - Warhammer'); L=[norm(l) for l in t[i:].split('\n')]
    end=next((k for k,l in enumerate(L) if l.startswith('Uploaded with Best Coast') or l=='Connect with us' or (l.startswith('Exported with App Version') and k>8)),len(L))
    L=L[:end]
    tl=([l for l in L[2:] if l] or [''])[0]
    idx=[k for k,l in enumerate(L) if l==tl]
    if len(idx)>1 and re.search(r'[A-Za-z]{3}',tl) and not tl.startswith('+'): L=L[:idx[1]]
    player=L[1]
    nb=[l for l in L[2:] if l]
    head=nb[:45]; headtxt='\n'.join(head)
    title=nb[0]
    # total pts
    m=re.search(r'(\d[\d,]{2,5})\s*(?:points|pts|Points)',title) or re.search(r'TOTAL ARMY POINTS:\s*(\d+)',headtxt) or re.search(r'\[(\d+) pts',headtxt) or re.search(r'(\d{4})\s*/\s*2000',headtxt)
    total=int(m.group(1).replace(',','')) if m else None
    # faction
    fac=None
    for l in head:
        for f in FACTIONS:
            if l.lower()==f.lower(): fac=f;break
        if fac:break
    chap=None
    low=headtxt.lower()
    for c in CHAPTERS:
        if c.lower() in low: chap=c;break
    if not fac:
        cands=[(low.find(f.lower()),f) for f in FACTIONS+['Adeptus Astartes'] if f.lower() in low]
        if cands: fac=min(cands)[1]
    if fac=='Adeptus Astartes' or (chap and not fac): fac='Space Marines'
    if fac and fac!='Space Marines' and chap in ('Deathwatch','Black Templars'): pass
    if chap=='Deathwatch' and fac!='Space Marines' and 'deathwatch' in low and fac in (None,): fac='Space Marines'
    # detachments (search header)
    dets=[]
    scan=re.sub(r'\s+',' ',low.replace('\n',' | '))
    for k in sorted(dvl,key=len,reverse=True):
        pos=scan.find(k)
        if pos>=0 and not any(k in x.lower() for _,x in dets):
            dets.append((pos,dvl[k]))
    dets=[x for _,x in sorted(dets)]
    fd=None
    for k,v in FD.items():
        if k in low: fd=v;break
    if not fd and re.search(r'^recon$',low,re.M): fd='Reconnaissance'
    # units
    units=[];enh=[]
    for l in L:
        s=l.lstrip('#').strip()
        if not s or s==title: continue
        me=re.match(r'^(?:•\s*)?Enhancements?:\s*(.+?)(?:\s*[\(\[]\+?\d+.*)?$',s,re.I)
        if me: enh.append(me.group(1).strip()); continue
        me=re.search(r'\bENHANCEMENT:\s*(.+)',s)
        if s.startswith('•') : continue
        parts=[s]
        if ' + ' in s:
            if ':' not in s.split(' + ')[0] and not re.search(r'^\w{4}\d+:',s): continue
            parts=s.split(' + ')
        for pi,p in enumerate(parts):
            m=unit_re.match(p.strip())
            if not m: continue
            pm=pts_re.search(p) or pts_re.search(s)
            if not pm: continue
            name=UVL[m.group('name').lower()]
            if name.lower()==(fac or '').lower(): continue
            ptv=int(next(g for g in pm.groups() if g).replace(',',''))
            if pi>0: ptv=0
            mult=re.match(r'^(\d+)x\s+'+re.escape(name)+r'\s*:',p.strip(),re.I)
            n=1
            # "2x Defiler: ... (710 pts)" in one-line format means 2 units
            if mult and ' - ' not in p and '(' in p and 'x Flawless' not in p and int(mult.group(1))<=3 and ptv>=150*int(mult.group(1))*0: n=int(mult.group(1)) if r['id']=='74wejT5TpVZE' else 1
            if ptv>=1500: continue
            for _ in range(n): units.append((name,ptv//n))
    res.append(dict(id=r['id'],url=r['url'],player=player,title=title,total=total,faction=fac,chapter=chap if fac=='Space Marines' else None,detachments=dets,disposition=fd,units=units,enh=enh))
# infer faction from units
u2f=collections.defaultdict(collections.Counter)
for x in res:
    if x['faction']:
        for n,_ in x['units']: u2f[n][x['faction']]+=1
for x in res:
    if not x['faction']:
        c=collections.Counter()
        for n,_ in x['units']:
            if u2f[n]: c[u2f[n].most_common(1)[0][0]]+=1
        if c: x['faction']=c.most_common(1)[0][0]; x['faction_inferred']=True
json.dump(res,open('data/lvo_2026_lists_parsed.json','w'),ensure_ascii=False)
c=collections.Counter
print('nofac',[ (x['player'],x['id']) for x in res if not x['faction']])
print('nodet',[ (x['player'],x['id']) for x in res if not x['detachments']])
print('nofd',len([x for x in res if not x['disposition']]))
bad=[(x['player'],x['id'],sum(p for _,p in x['units']),len(x['units'])) for x in res if not 1800<=sum(p for _,p in x['units'])<=2010]
print('ptsoff',len(bad)); [print(b) for b in bad]
print(c(x['faction'] for x in res))
