import json,re,html,sys
R='/workspace/fencing-newspaper/'
D={i['id']:i for i in json.load(open(R+'staging/weeks/next/items.json'))['items']}
L=json.load(open(R+'budget-demo/practice-lineup.json')); S={s['key']:s for s in L['slots']}
def ty(t):
    t=html.escape(t,quote=False)
    t=re.sub(r'(^|[\s(\[—–-])"',r'\1“',t); t=t.replace('"','”')
    t=re.sub(r"(\w)'(\w)",r"\1’\2",t); t=re.sub(r"(^|[\s(“])'",r"\1‘",t); t=t.replace("'","’")
    t=re.sub(r'\*\*(.+?)\*\*',r'<b class="run">\1</b>',t); t=re.sub(r'\*(.+?)\*',r'<i>\1</i>',t)
    t=re.sub(r'(Oct|Nov|Dec|Jan|Feb)\. (\d)',r'\1.&nbsp;\2',t)
    t = re.sub(r'(\d) (a\.m\.|p\.m\.)', '\\1&nbsp;\\2', t)
    return t
def paras(t): return "\n".join(f"<p>{ty(p.strip())}</p>" for p in t.strip().split("\n\n") if p.strip())
OV=json.load(open(R+'issues/2026-10-26/build/overrides.json')) if len(sys.argv)>1 else {}
def body(k): return OV.get(k) or D[S[k]['item']]['body']
TPL_CSS=open(R+'prototype/template-a-v2.css').read()
FLANK=json.load(open(R+'flank-quotes.json'))
css=open(R+'issues/2026-10-13/issue.html').read().split('<style>')[1].split('</style>')[0]
css+="""  /* ---- Issue 2026-10-26 composition additions (no furniture changes) ---- */
  .credit { font-family: "Arial", "Liberation Sans", sans-serif; font-size: 7pt; color: #333; margin-top: 2pt; text-align: left; line-height: 1.25; overflow-wrap: anywhere; text-align: left !important; hyphens: none; }
  .c > .rail-block + .slot-b, .c > .slot-b + .box { margin-top: 6pt; }
  .eds-note { font-style: italic; }
  p, td { text-wrap: pretty; }
  .pullquote { font-style: italic; font-size: 11.5pt; line-height: 1.22; text-align: center !important; margin: 5pt 6pt 6pt; hyphens: none; }
  h1.head, h2.head { text-wrap: balance; }
"""+TPL_CSS
def table(head,rows,cols,numcol=0):
    h="<tr>"+"".join(f'<th{" class=\"r\"" if i==numcol else ""}>{ty(x)}</th>' for i,x in enumerate(head))+"</tr>"
    rr="".join("<tr>"+"".join(f'<td{" class=\"num\"" if i==numcol else ""}>{x}</td>' for i,x in enumerate(r))+"</tr>" for r in rows)
    cg="<colgroup>"+"".join(f'<col style="width:{c}">' if c else "<col>" for c in cols)+"</colgroup>"
    return f'<table class="board">{cg}{h}{rr}</table>'
def tourney(name,where,dates,head,cols,days):
    """One coherent block per tournament: name · town · dates once; days as sub-rows (STYLE-GUIDE §9b)."""
    n=len(head)
    h="<tr>"+"".join(f'<th{" class=\"r\"" if (i==0 and head[0]=="Time") else ""}>{x}</th>' for i,x in enumerate(head))+"</tr>"
    rr=""
    for label,rows in days:
        rr+=f'<tr class="day"><td colspan="{n}">{label}</td></tr>'
        rr+="".join("<tr>"+"".join(f'<td{" class=\"num\"" if (i==0 and head[0]=="Time") else ""}>{x}</td>' for i,x in enumerate(r))+"</tr>" for r in rows)
    cg="<colgroup>"+"".join(f'<col style="width:{c}">' if c else "<col>" for c in cols)+"</colgroup>"
    return f'<div class="tourney"><div class="tourney-head">{name} <span>· {where} · {dates}</span></div><table class="board">{cg}{h}{rr}</table></div>'
NB='&nbsp;'
def nw(n): return f'<span style="white-space:nowrap">{n}</span>'
ult=[("Saturday, Oct.&nbsp;31",[["8:00 AM","Junior Women","Olivia Hayes, Lillian Liu, Anayaa Sheth, Adela Sullivan"],["1:00 PM","Cadet Men","Maksim Milinkovic, Caden Wu"]]),
     ("Sunday, Nov.&nbsp;1",[["8:00 AM","Junior Men","Pablo Aguirre, Dieko Johnson, Maksim Milinkovic, Nico Ng"],["1:00 PM","Cadet Women","Olivia Hayes, Lillian Liu, Adela Sullivan, Penny Young"]])]
cob=[("Friday, Nov.&nbsp;27",[["Y14 Men","Connor Anderson, Noah Gore, Kian Jaising, Remy Ng, "+nw("Ash Shah-Mirani")],["Cadet Women","Amina Gore, Olivia Hayes, Stella Kuo, Lillian Liu, Mila Siu, Penny Young"],["Y10 Men","Bryce Cheng, Joshua Jeong"]]),
     ("Saturday, Nov.&nbsp;28",[["Y12 Women","Christina Jiang, Stella Kuo, Mila Siu, Penny Young"],["Y12 Men","Kian Jaising, Joshua Jeong, Remy Ng"]]),
     ("Sunday, Nov.&nbsp;29",[["Y14 Women","Stella Kuo, Mila Siu, Penny Young"],["Cadet Men","Connor Anderson, Nico Ng, Caden Wu"]])]
med=[("Sunday, Nov.&nbsp;8",[["9:30 AM","Y12 Men","Samuel SarroWaite"],["9:30 AM","Y12 Women","Christina Jiang"],["11:30 AM","Y10 Mixed","Nora Li"],["11:30 AM","Y14 Men","Owen Li"]])]
nyfa=[("Sunday, Nov.&nbsp;8",[["9:00 AM","Y10 Mixed","Bryce Cheng"]])]
dl=[["Thu 10/29","Ultimate Cup: last day to enter (late fees)"],["Sun 11/1","Cobra Challenge: regular entry closes (late to Nov.&nbsp;7)"],["Sat 11/7","Medeo #5: preregistration closes"],["Wed 11/11","Junior Olympics: regular-fee deadline"],["Fri 1/8","N.J. high school: independent fencers’ entries close"]]
tv=D[S['tv']['item']]['rows']
cobra_txt=OV.get('cobra') or "Regular entry for the Cobra Challenge closes Sunday, Nov. 1. Late entry, at higher fees, runs through Nov. 7, when online entry closes. Every event has a cap; full events take a waitlist, which is free to join, but USA Fencing says you need a payment method on file to be officially on it.\n\nCheck-in times will be posted by Nov. 1. The Meadowlands Expo Center opens at 6:30 a.m., parking in the adjacent garages is free, and there's no Wi-Fi inside; results post only on FencingTimeLive. Medals go to the top 8.\n\nRegular fees are a $35 registration fee plus $90 per event; late entries pay $70 plus $180 per event."
ref=body('secondary-b'); lead=OV.get('lead') or body('lead')+OV.get('lead_add',''); cas=body('secondary-a')
PHOTO=OV.get('photo',True)
PQ=OV.get('pullquote',"Examiners look for consistency: the same call at 14-14 as at 1-1.")
def pq(h):
    if not PQ: return h
    parts=h.split('</p>\n'); k=OV.get('pq_after',2)
    return '</p>\n'.join(parts[:k])+'</p>\n'+f'<p class="pullquote">{ty(PQ)}</p>\n'+'</p>\n'.join(parts[k:])
P1R=OV.get('p1_right',['ref','results']); P2C=OV.get('p2_cols',[['deadlines','camp'],['cobra','podium'],['tv','btb']])
blocks={
 'ref':f'<div class="slot-b"><h2 class="head">{ty(D[S["secondary-b"]["item"]]["headline"])}</h2>{pq(paras(ref))}</div>',
 'results':f'<div class="box"><div class="boxtitle">Club Results</div>{table(["Fencer","Event","Place"],[["Maksim Milinkovic","Cadet Men, FIE Cadet World Cup (San José, Costa Rica, Oct.&nbsp;22)","6th"]],["0.78in",None,"0.4in"],numcol=None)}<p class="boxnote">Morris Cup finishes are in the lead story.</p></div>',
 'btb':f'<div class="rail-block"><div class="rail-title">By the Book</div><h2 class="head">One Quiet Minute</h2>{paras(body("by-the-book"))}</div>',
 'deadlines':f'<div class="box"><div class="boxtitle">Deadlines</div>{table(["Date","What closes"],dl,["0.62in",None])}<p class="boxnote">USA Fencing deadlines are 11:59 p.m. Pacific (2:59 a.m. Eastern the next day).</p></div>',
 'cobra':f'<div class="slot-b"><h2 class="head">Cobra Challenge: Still Time to Enter</h2>{paras(cobra_txt)}</div>',
 'camp':f'<div class="slot-b"><h2 class="head">Winter Camp: Sign Up Now</h2>{paras(body("camp"))}</div>',
 'podium':f'<div class="photo" style="margin-top:6pt;"><img src="media/morris-cup-y8-podium-crop.jpg" alt="Y8 Women medalists on the Morris Cup podium"><p class="caption">{ty(OV.get("podium_caption","The Y8 Women medalists at the Morris Cup. Elite FC’s Madeline Siu won the event."))}</p><p class="credit">Photo: Elite FC newsletter (cropped).</p></div>',
 'tv':f'<div class="box"><div class="boxtitle">Epee on Screen</div>{table(["Dates","Event","Watch"],tv,["0.64in",None,"0.56in"])}<p class="boxnote">From the FIE calendar; no start times or prices listed.</p></div>',
}
photo=f'<div class="photo" style="margin:3pt 0 4pt;"><img src="media/morris-cup-group.jpg" alt="Elite FC fencers and a coach in a group photo at the Morris Cup"><p class="caption">{ty(OV.get("caption","Elite FC fencers at the Morris Cup in Suffern, N.Y."))}</p><p class="credit">Photo: Elite FC newsletter.</p></div>' if PHOTO else ''
foot='''  <div class="footer">
    <span>En Garde Gazette · Issue No. 4</span>
    <span class="foot-archive">Past issues · newsletter.teamremco.org</span>
    <span>For fun only — facts aren’t guaranteed accurate.</span>
  </div>'''
h=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>En Garde Gazette — Vol. I No. 4 — October 26, 2026</title>
<meta name="author" content="Nico's Dad">
<style>{css}</style>
</head>
<body>

<!-- ==================== PAGE 1 (FRONT) ==================== -->
<div class="page">
  <div class="masthead">
    <div class="flank left">{FLANK["left_flank_fixed"]}</div>
    <img src="../../masthead001.png" alt="The En Garde Gazette — The Elite Fencers Club Weekly">
    <div class="flank right">{FLANK["right_flank_default"]}</div>
  </div>
  <div class="dateline">
    <div class="edition">Monday Edition</div>
    <div class="meta">Vol. I — No. 4 &nbsp;·&nbsp; Chatham, N.J. &nbsp;·&nbsp; October 26, 2026</div>
  </div>

  <div class="cols3 ruled">
    <div class="c span2">
      <h1 class="head">{ty(OV.get("lead_head",D[S["lead"]["item"]]["headline"]))}</h1>
      {photo}
      {paras(lead)}

      <div class="slot-a" style="margin-top:6pt;">
        <h2 class="head">{ty(D[S["secondary-a"]["item"]]["headline"])}</h2>
        {paras(cas)}
      </div>
    </div>
    <div class="c">
      {"".join(blocks[k] for k in P1R)}
    </div>
  </div>
{foot}
</div>

<!-- ==================== PAGE 2 (BACK) ==================== -->
<div class="page">
  <div class="dateline" style="margin-top:0;">
    <div class="edition">Page Two</div>
    <div class="meta">Club Calendar &amp; Notes &nbsp;·&nbsp; Vol. I — No. 4</div>
  </div>

  <div class="box w3">
    <div class="boxtitle">Nearby Tournaments — Elite FC Entries</div>
    <div class="board-split">
      <div>
        {tourney("Cobra Challenge SYC/RCC","Secaucus, N.J.","Nov.&nbsp;27–29",["Event","Elite FC"],["0.85in",None],cob)}
        {tourney("NYFA Youth Cup #1","Brooklyn, N.Y.","Nov.&nbsp;8",["Time","Event","Elite FC"],["0.62in","0.85in",None],nyfa)}
      </div>
      <div>
        {tourney("Ultimate Cup RJCC","Hillsborough, N.J.","Oct.&nbsp;31–Nov.&nbsp;1",["Time","Event","Elite FC"],["0.62in","0.85in",None],ult)}
        {tourney("Medeo Youth Challenge #5","Bound Brook, N.J.","Nov.&nbsp;8",["Time","Event","Elite FC"],["0.62in","0.85in",None],med)}
      </div>
    </div>
    <p class="boxnote">{ty(OV.get("boardnote","Cobra Challenge is at the Meadowlands Expo Center in Secaucus: 16 Elite FC fencers, 26 entries; check-in times post by Nov. 1. Ultimate Cup is at Iron Peak Sports & Events in Hillsborough: 10 Elite FC fencers, 14 entries."))}</p>
  </div>

  <div class="cols3 ruled">
    {"".join('<div class="c">'+"".join(blocks[k] for k in col)+'</div>' for col in P2C)}
  </div>
{foot}
</div>

</body>
</html>
'''
open(R+'issues/2026-10-26/issue.html','w').write(h)
print('ok')
