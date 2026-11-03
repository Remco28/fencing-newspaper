import json,re,html,sys
R='/workspace/fencing-newspaper/'
WEEK='staging/weeks/2026-11-03'   # No. 5's staging week (history after the No. 5 roll-forward 2026-11-03)
D={i['id']:i for i in json.load(open(R+WEEK+'/items.json'))['items']}
L=json.load(open(R+'budget-demo/practice-lineup.json')); S={s['key']:s for s in L['slots']}
def ty(t):
    t=html.escape(t,quote=False)
    t=re.sub(r'(^|[\s(\[—–-])"',r'\1“',t); t=t.replace('"','”')
    t=re.sub(r"(\w)'(\w)",r"\1’\2",t); t=re.sub(r"(^|[\s(“])'",r"\1‘",t); t=t.replace("'","’")
    t=re.sub(r'\*\*(.+?)\*\*',r'<b class="run">\1</b>',t); t=re.sub(r'\*(.+?)\*',r'<i>\1</i>',t)
    t=re.sub(r'(Oct|Nov|Dec|Jan|Feb)\. (\d)',r'\1.&nbsp;\2',t)
    t=re.sub(r'(\d) (a\.m\.|p\.m\.)','\\1&nbsp;\\2',t)
    t=re.sub(r'(\d) (milliseconds)','\\1&nbsp;\\2',t)
    return t
def paras(t): return "\n".join(f"<p>{ty(p.strip())}</p>" for p in t.strip().split("\n\n") if p.strip())
OV=json.load(open(R+'issues/2026-11-03/build/overrides.json')) if len(sys.argv)>1 else {}
def body(k): return OV.get(k) or D[S[k]['item']]['body']
TPL_CSS=open(R+'prototype/template-a-v2.css').read()
FLANK=json.load(open(R+'flank-quotes.json'))
css=open(R+'issues/2026-10-13/issue.html').read().split('<style>')[1].split('</style>')[0]
css+="""  /* ---- Issue 2026-11-03 composition additions (no furniture changes) ---- */
  .credit { font-family: "Arial", "Liberation Sans", sans-serif; font-size: 7pt; color: #333; margin-top: 2pt; text-align: left; line-height: 1.25; overflow-wrap: anywhere; text-align: left !important; hyphens: none; }
  .c > .rail-block + .slot-b, .c > .slot-b + .box, .c > .box + .rail-block, .c > .rail-block + .rail-block, .c > .box + .slot-b { margin-top: 6pt; }
  p, td { text-wrap: pretty; }
  h1.head, h2.head { text-wrap: balance; }
  .pfloat { float: left; width: 2.15in; margin: 2pt 9pt 3pt 0; }
  .photowide::after { content: ""; display: block; clear: both; }
"""+TPL_CSS+OV.get('css_add','')
def table(head,rows,cols,numcol=0):
    h="<tr>"+"".join(f'<th{" class=\"r\"" if i==numcol else ""}>{ty(x)}</th>' for i,x in enumerate(head))+"</tr>"
    rr="".join("<tr>"+"".join(f'<td{" class=\"num\"" if i==numcol else ""}>{x}</td>' for i,x in enumerate(r))+"</tr>" for r in rows)
    cg="<colgroup>"+"".join(f'<col style="width:{c}">' if c else "<col>" for c in cols)+"</colgroup>"
    return f'<table class="board">{cg}{h}{rr}</table>'
def tourney(name,where,dates,head,cols,days):
    """One coherent block per tournament: name · town · dates once; days as sub-rows (STYLE-GUIDE §10a)."""
    n=len(head)
    h="<tr>"+"".join(f'<th{" class=\"r\"" if (i==0 and head[0]=="Time") else ""}>{x}</th>' for i,x in enumerate(head))+"</tr>"
    rr=""
    for label,rows in days:
        if label: rr+=f'<tr class="day"><td colspan="{n}">{label}</td></tr>'
        rr+="".join("<tr>"+"".join(f'<td{" class=\"num\"" if (i==0 and head[0]=="Time") else ""}>{x}</td>' for i,x in enumerate(r))+"</tr>" for r in rows)
    cg="<colgroup>"+"".join(f'<col style="width:{c}">' if c else "<col>" for c in cols)+"</colgroup>"
    return f'<div class="tourney"><div class="tourney-head">{name} <span>· {where} · {dates}</span></div><table class="board">{cg}{h}{rr}</table></div>'
def nw(n): return f'<span style="white-space:nowrap">{n}</span>'
# Boards: from the budget lineup (Frank-vetted), times in the board's AM/PM house form.
cob=[("Friday, Nov.&nbsp;27",[["Y14 Men","Connor Anderson, Noah Gore, Kian Jaising, Remy Ng, "+nw("Ash Shah-Mirani")],["Cadet Women","Amina Gore, Olivia Hayes, Stella Kuo, Lillian Liu, Mila Siu, Penny Young"],["Y10 Men","Bryce Cheng, Joshua Jeong"]]),
     ("Saturday, Nov.&nbsp;28",[["Y12 Women","Christina Jiang, Stella Kuo, Mila Siu, Penny Young"],["Y12 Men","Kian Jaising, Joshua Jeong, Remy Ng"]]),
     ("Sunday, Nov.&nbsp;29",[["Y14 Women","Stella Kuo, Mila Siu, Penny Young"],["Cadet Men","Connor Anderson, Nico Ng, Caden Wu"]])]
nyfa=[("",[["9:00 AM","Y10 Mixed","Bryce Cheng, Maximus Siu"],["9:00 AM","Y8 Mixed","Madeline Siu"],["12:30 PM","Y12 Men","Remy Ng"],["12:30 PM","Y12 Women","Christina Jiang"],["4:00 PM","Y14 Women","Mila Siu"]])]
med=[("",[["9:30 AM","Y12 Men","Samuel SarroWaite"],["9:30 AM","Y12 Women","Christina Jiang"],["11:30 AM","Y10 Mixed","Ian Huang, Nora Li, Elle\u00a0Peterfreund, Claire Widjaja"],["11:30 AM","Y14 Men","Owen Li"],["11:30 AM","Y14 Women","Mira Shukla"]])]
piz=[("Saturday, Nov.&nbsp;14",[["8:00 AM","Y14 Women","Penny Young"],["1:00 PM","Junior Women","Amina Gore"]]),
     ("Sunday, Nov.&nbsp;15",[["8:00 AM","Cadet Women","Amina Gore, Penny Young"],["12:00 PM","Y12 Women","Penny Young"]])]
dl=[["Sat 11/7","Cobra Challenge: late entry closes"],["Sat 11/7","Medeo #5: preregistration closes"],["Wed 11/11","Junior Olympics: regular-fee deadline"],["Fri 1/8","N.J. high school: independent fencers’ entries close"]]
# Epee on Screen: two columns (dates, event); the stream note moves to the boxnote to stop "No stream listed" wrapping.
TVR=OV.get('tv_rows') or [[r[0],r[1]+(' — FencingTV' if r[2]=='FencingTV' else '')] for r in D[S['tv']['item']]['rows']]
tv=[[ty(c) for c in r] for r in TVR]
res=[[ty(c) for c in r] for r in S['club-results']['table']['rows']]
rat=[["Maksim Milinkovic","A26 <span style=\"white-space:nowrap\">(from B26)</span>","Ultimate Cup RJCC, Oct.&nbsp;31"]]
ph=D[S['photo-history']['item']]
P1R=OV.get('p1_right',['results','ratings','newclass','btb']); P2C=OV.get('p2_cols',[['deadlines','tv','camp'],['overheard'],['photo']])
# Overheard: run in full from the research draft (Frank, chat Nov. 2, 8:56 PM).
oh=open(R+'staging/research/overheard-fie-wfl-draft.md').read().split('---')[1]
oh_lines=[l for l in oh.strip().split('\n\n') if not l.startswith('**OVERHEARD') and not l.startswith('**Can the FIE')]
oh_fc=[l for l in oh_lines if l.startswith('*Fact check:*')][0]
oh_paras=[l for l in oh_lines if not l.startswith('*Fact check:*')]
OHS=OV.get('overheard_split',len(oh_paras))
oh_body="\n\n".join(oh_paras[:OHS]); oh_body2="\n\n".join(oh_paras[OHS:])
blocks={
 'results':f'<div class="box"><div class="boxtitle">Club Results</div>{table(["Fencer","Event","Finish"],res,["0.72in",None,"0.62in"],numcol=None)}</div>',
 'ratings':f'<div class="box"><div class="boxtitle">Ratings Earned</div>{table(["Fencer","Rating","Where"],rat,["0.72in","0.62in",None],numcol=None)}</div>',
 'newclass':f'<div class="slot-b"><h2 class="head">{ty(OV.get("newclass_head","New Friday Class"))}</h2>{paras(body("newclass"))}</div>',
 'btb':f'<div class="rail-block"><div class="rail-title">By the Book</div><h2 class="head">{ty(OV.get("btb_head",""))}</h2>{paras(body("btb"))}</div>',
 'deadlines':f'<div class="box"><div class="boxtitle">Deadlines</div>{table(["Date","What closes"],dl,["0.62in",None])}<p class="boxnote">USA Fencing deadlines are 11:59 p.m. Pacific (2:59 a.m. Eastern the next day).</p></div>',
 'camp':f'<div class="slot-b"><h2 class="head">Winter Camp: Sign Up Now</h2>{paras(body("camp"))}</div>',
 'tv':f'<div class="box"><div class="boxtitle">Epee on Screen</div>{table(["Dates","Event"],tv,["0.64in",None])}<p class="boxnote">{ty(OV.get("tv_note","From the FIE calendar; no start times or prices listed."))}</p></div>',
 'overheard':f'<div class="rail-block"><div class="rail-title">Overheard on Reddit</div><h2 class="head">{ty(OV.get("overheard_head",""))}</h2>{paras(oh_body)}'+('</div>' if oh_body2 else f'<p class="factcheck">{ty(oh_fc.replace("*Fact check:*","**Fact check:**"))}</p></div>'),
 'overheard2':f'<div class="rail-block">{paras(oh_body2)}<p class="factcheck">{ty(oh_fc.replace("*Fact check:*","**Fact check:**"))}</p></div>',
 'photowide':f'<div class="rail-block photowide" style="margin-top:7pt;"><div class="rail-title">Photo from History</div><h2 class="head">{ty(OV.get("photo_head",ph["headline"]))}</h2><div class="photo pfloat"><img src="media/09-laura-flessel-crop.jpg" alt="{html.escape(ph["alt_text"])}"><p class="caption">{ty(OV.get("photo_caption",ph["caption"]))}</p></div>{paras(OV.get("photo_blurb",ph["body"]))}<p class="credit">{html.escape(OV.get("credit",ph["credit"]))}</p></div>',
 'photo':f'<div class="rail-block"><div class="rail-title">Photo from History</div><h2 class="head">{ty(OV.get("photo_head",ph["headline"]))}</h2><div class="photo"><img src="media/09-laura-flessel-crop.jpg" alt="{html.escape(ph["alt_text"])}"><p class="caption">{ty(OV.get("photo_caption",ph["caption"]))}</p></div>{paras(OV.get("photo_blurb",ph["body"]))}<p class="credit">{html.escape(OV.get("credit",ph["credit"]))}</p></div>',
}
foot='''  <div class="footer">
    <span>En Garde Gazette · Issue No. 5</span>
    <span class="foot-archive">Past issues · newsletter.teamremco.org</span>
    <span>For fun only — facts aren’t guaranteed accurate.</span>
  </div>'''
h=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>En Garde Gazette — Vol. I No. 5 — November 3, 2026</title>
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
    <div class="edition">Tuesday Edition</div>
    <div class="meta">Vol. I — No. 5 &nbsp;·&nbsp; Chatham, N.J. &nbsp;·&nbsp; November 3, 2026</div>
  </div>

  <div class="cols3 ruled">
    <div class="c span2">
      <h1 class="head">{ty(OV.get("lead_head",D[S["lead"]["item"]]["headline"]))}</h1>
      {paras(body("lead"))}

      <div class="slot-a" style="margin-top:6pt;">
        <h2 class="head">{ty(OV.get("dakar_head",D[S["secondary-a"]["item"]]["headline"]))}</h2>
        {paras(body("dakar"))}
      </div>
      {"".join(blocks[k] for k in OV.get('p1_span2_after',[]))}
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
    <div class="meta">Club Calendar &amp; Notes &nbsp;·&nbsp; Vol. I — No. 5</div>
  </div>

  <div class="box w3">
    <div class="boxtitle">Nearby Tournaments — Elite FC Entries</div>
    <div class="board-split">
      <div>
        {tourney("NYFA Youth Cup #1","Brooklyn, N.Y.","Sunday, Nov.&nbsp;8",["Time","Event","Elite FC"],["0.62in","0.85in",None],nyfa)}
        {tourney("Pizza RYC/RJCC","New Haven, Conn.","Nov.&nbsp;14–15",["Time","Event","Elite FC"],["0.62in","0.85in",None],piz)}
      </div>
      <div>
        {tourney("Medeo Youth Challenge #5","Bound Brook, N.J.","Sunday, Nov.&nbsp;8",["Time","Event","Elite FC"],["0.62in","0.85in",None],med)}
        {tourney("Cobra Challenge SYC/RCC","Secaucus, N.J.","Nov.&nbsp;27–29",["Event","Elite FC"],["0.85in",None],cob)}
      </div>
    </div>
    <p class="boxnote">{ty(OV.get("boardnote",""))}</p>
  </div>

  <div class="cols3 ruled">
    {"".join('<div class="c">'+"".join(blocks[k] for k in col)+'</div>' for col in P2C)}
  </div>
{foot}
</div>

</body>
</html>
'''
open(R+'issues/2026-11-03/issue.html','w').write(h)
print('ok')
