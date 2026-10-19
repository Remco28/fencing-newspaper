import json,re,html,sys
R='/workspace/fencing-newspaper/'
D={i['id']:i for i in json.load(open(R+'staging/weeks/2026-10-19/items.json'))['items']}
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
OV=json.load(open(R+'issues/2026-10-19/build/overrides.json')) if len(sys.argv)>1 else {}
def body(k): return OV.get(k) or D[S[k]['item']]['body']
TPL_CSS=open(R+'prototype/template-a-v2.css').read()
FLANK=json.load(open(R+'flank-quotes.json'))
css=open(R+'issues/2026-10-13/issue.html').read().split('<style>')[1].split('</style>')[0]
css+="""  /* ---- Issue 2026-10-19 composition additions (no furniture changes) ---- */
  .credit { font-family: "Arial", "Liberation Sans", sans-serif; font-size: 7pt; color: #333; margin-top: 2pt; text-align: left; line-height: 1.25; overflow-wrap: anywhere; text-align: left !important; hyphens: none; }
  .c > .rail-block + .slot-b, .c > .slot-b + .box { margin-top: 6pt; }
  .eds-note { font-style: italic; }
  p, td { text-wrap: pretty; }
  h1.head, h2.head { text-wrap: balance; }
"""+TPL_CSS
cc=body('secondary-a')
def table(head,rows,cols,numcol=0):
    h="<tr>"+"".join(f'<th{" class=\"r\"" if i==numcol else ""}>{ty(x)}</th>' for i,x in enumerate(head))+"</tr>"
    rr="".join("<tr>"+"".join(f'<td{" class=\"num\"" if i==numcol else ""}>{x}</td>' for i,x in enumerate(r))+"</tr>" for r in rows)
    cg="<colgroup>"+"".join(f'<col style="width:{c}">' if c else "<col>" for c in cols)+"</colgroup>"
    return f'<table class="board">{cg}{h}{rr}</table>'
def am(t): return t.replace(' a.m.',' AM').replace(' p.m.',' PM')
mor=S['signup']['panels']['panels']
def morrows(p): return [[am(r[0]),r[1],r[2].replace('Ash Shah-Mirani','<span style="white-space:nowrap">Ash Shah-Mirani</span>')] for r in p['rows']]
ult=[["Sat 10/31","Junior Women","Olivia Hayes, Anayaa Sheth, Adela Sullivan"],["Sat 10/31","Cadet Men","Maksim Milinkovic, Caden Wu"],["Sun 11/1","Junior Men","Pablo Aguirre, Dieko Johnson, Maksim Milinkovic, Nico Ng"],["Sun 11/1","Cadet Women","Olivia Hayes, Lillian Liu, Adela Sullivan, Penny Young"]]
med=[["Sun 10/25","#4","Nora Li (Y10 Mixed)"],["Sun 11/8","#5","Samuel SarroWaite (Y12 Men), Christina Jiang (Y12 Women), Nora Li (Y10 Mixed), Owen Li (Y14 Men)"]]
dl=[["Thu 10/22","Morris Cup: last day to enter (late fees)"],["Thu 10/29","Ultimate Cup: last day to enter (late fees)"],["Sun 11/1","Cobra Challenge (Secaucus, Nov.&nbsp;27–29): regular entry closes; late entry to Nov.&nbsp;7"],["Wed 11/11","Junior Olympics: regular-fee deadline"],["Fri 1/8","N.J. high school: independent fencers’ entries close"]]

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
ph=D['history-photo-06-dutch-team-epee-1965']
credit=OV.get('credit') or ph['credit']
camp=body('camp'); cls=D[S['classes']['item']]['body']
P1R=OV.get('p1_right',['eds','btb','parents']); P2C=OV.get('p2_cols',[['deadlines','camp','classes','njhs'],['photo'],['overheard']])
blocks={
 'eds':f'<div class="slot-b"><h2 class="head">World No.&nbsp;1’s Message to His Future Self</h2>{paras(body("secondary-b"))}</div>',
 'btb':f'<div class="rail-block"><div class="rail-title">By the Book</div><h2 class="head">You Can’t Appeal What the Referee Saw</h2>{paras(body("by-the-book"))}</div>',
 'parents':f'<div class="rail-block"><div class="rail-title">For the Parents</div><h2 class="head">Qualifying Isn’t Registering</h2>{paras(body("for-parents"))}</div>',
 'deadlines':f'<div class="box"><div class="boxtitle">Deadlines</div>{table(["Date","What closes"],dl,["0.62in",None])}<p class="boxnote">Tournament deadlines are 11:59 p.m. Pacific (2:59 a.m. Eastern the next day), from the USA Fencing pages.</p></div>',
 'camp':f'<div class="slot-b"><h2 class="head">Winter Camp: Sign Up Now</h2>{paras(camp)}</div>',
 'classes':f'<div class="slot-b"><h2 class="head">Class Notes</h2>{paras(cls)}</div>',
 'njhs':f'<div class="slot-b"><h2 class="head">N.J. High School Fencing: <span style="white-space:nowrap">2026–27</span> Dates Are Set</h2>{paras(body("nj-hs"))}</div>',
 'photo':f'<div class="rail-block"><div class="rail-title">Photo from History</div><h2 class="head">{ty(OV.get("photo_head","1965: Club Epee, With Everyone Close Enough to Watch"))}</h2><div class="photo"><img src="media/06-dutch-team-epee-1965-crop.jpg" alt="{html.escape(ph["alt_text"])}"><p class="caption">{ty(OV.get("photo_caption",ph["caption"]))}</p></div>{paras(OV.get("photo_blurb",ph["body"]))}<p class="credit">{html.escape(credit)}</p></div>',
 'overheard':f'<div class="slot-b"><h2 class="head">Overheard on Reddit: After the Split</h2>{paras(body("overheard"))}<p class="factcheck">{ty(D[S["overheard"]["item"]]["fact_check_line"].replace("*Fact check:*","**Fact check:**"))}</p></div>',
}
lead=body('lead'); dek=OV.get('dek','')
foot='''  <div class="footer">
    <span>En Garde Gazette · Issue No. 3</span>
    <span class="foot-archive">Past issues · newsletter.teamremco.org</span>
    <span>For fun only — facts aren’t guaranteed accurate.</span>
  </div>'''
h=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>En Garde Gazette — Vol. I No. 3 — October 19, 2026</title>
<meta name="author" content="Nico's Dad">
<style>{css}</style>
</head>
<body>

<!-- ==================== PAGE 1 (FRONT) ==================== -->
<div class="page">
  <div class="masthead">
    <div class="flank left">{FLANK["left_flank_fixed"]}</div>
    <img src="../../masthead001.png" alt="The En Garde Gazette — The Elite Fencers Club Weekly">
    <div class="flank right">It is better to deserve a rating than to have one.</div>
  </div>
  <div class="dateline">
    <div class="edition">Monday Edition</div>
    <div class="meta">Vol. I — No. 3 &nbsp;·&nbsp; Chatham, N.J. &nbsp;·&nbsp; October 19, 2026</div>
  </div>

  <div class="cols3 ruled">
    <div class="c span2">
      <h1 class="head">{ty(OV.get("lead_head","Vet Worlds, Part Two: Two World Titles for U.S. Women"))}</h1>
      {f'<p class="dek">{ty(dek)}</p>' if dek else ''}
      {paras(lead)}

      <div class="slot-a" style="margin-top:6pt;">
        <h2 class="head">Controversial Calls: The Touch Only the Referee Thought She Saw</h2>
        {paras(cc).replace("<p><i>Editor","<p class=\"eds-note\"><i>Editor")}
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
    <div class="meta">Club Calendar &amp; Notes &nbsp;·&nbsp; Vol. I — No. 3</div>
  </div>

  <div class="box w3">
    <div class="boxtitle">Nearby Tournaments — Elite FC Entries</div>
    <div class="board-split">
      <div>
        {tourney("Morris Cup RYC/RJCC","Suffern, N.Y.","Oct.&nbsp;24–25",["Time","Event","Elite FC"],["0.62in","0.8in",None],[("Saturday, Oct.&nbsp;24",morrows(mor[0])),("Sunday, Oct.&nbsp;25",morrows(mor[1]))])}
      </div>
      <div>
        {tourney("Ultimate Cup RJCC","Hillsborough, N.J.","Oct.&nbsp;31–Nov.&nbsp;1",["Event","Elite FC"],["0.85in",None],[("Saturday, Oct.&nbsp;31",[r[1:] for r in ult if r[0].startswith("Sat")]),("Sunday, Nov.&nbsp;1",[r[1:] for r in ult if r[0].startswith("Sun")])])}
        {tourney("Medeo Youth Challenges","Bound Brook, N.J.","Oct.&nbsp;25 &amp; Nov.&nbsp;8",["Event","Elite FC"],["0.85in",None],[("No.&nbsp;4 · Sunday, Oct.&nbsp;25",[["Y10 Mixed","Nora Li"]]),("No.&nbsp;5 · Sunday, Nov.&nbsp;8",[["Y12 Men","Samuel SarroWaite"],["Y12 Women","Christina Jiang"],["Y10 Mixed","Nora Li"],["Y14 Men","Owen Li"]])])}
      </div>
    </div>
    <p class="boxnote">Morris Cup is at Rockland Community College’s Eugene Levy Field House: 20 Elite FC fencers, 30 entries. Ultimate Cup is at Iron Peak Sports &amp; Events in Hillsborough: 10 Elite FC fencers, 13 entries.</p>
  </div>

  <div class="cols3 ruled">
    {"".join('<div class="c">'+"".join(blocks[k] for k in col)+'</div>' for col in P2C)}
  </div>
{foot}
</div>

</body>
</html>
'''
open(R+'issues/2026-10-19/issue.html','w').write(h)
print('ok')
