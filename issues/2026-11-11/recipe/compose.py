#!/usr/bin/env python3
"""Compose En Garde Gazette No. 6 (Wednesday, Nov. 11, 2026) from the approved budget."""
import json,re,html,sys
from pathlib import Path
R='/workspace/fencing-newspaper/'
WEEK='staging/weeks/2026-11-11'
ISSUE='issues/2026-11-11'
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
OV=json.load(open(R+'issues/2026-11-03/recipe/overrides.json')) if len(sys.argv)>1 else {}
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

OV_PATH=Path(R+ISSUE+'/recipe/overrides.json')
OV=json.loads(OV_PATH.read_text()) if OV_PATH.is_file() and len(sys.argv)>1 else {}
def body(k):
    if k in OV: return OV[k]
    return D[S[k]['item']]['body']
TPL_CSS=open(R+'prototype/template-a-v2.css').read()
FLANK=json.load(open(R+'flank-quotes.json'))
css=open(R+'issues/2026-10-13/issue.html').read().split('<style>')[1].split('</style>')[0]
css+="""  /* ---- Issue 2026-11-11 composition additions (no furniture changes) ---- */
  .credit { font-family: "Arial", "Liberation Sans", sans-serif; font-size: 7pt; color: #333; margin-top: 2pt; text-align: left; line-height: 1.25; overflow-wrap: anywhere; text-align: left !important; hyphens: none; }
  .c > .rail-block + .slot-b, .c > .slot-b + .box, .c > .box + .rail-block, .c > .rail-block + .rail-block, .c > .box + .slot-b, .c > .box + .box { margin-top: 6pt; }
  p, td { text-wrap: pretty; }
  h1.head, h2.head { text-wrap: balance; }
  .comicfig { margin: 0; }
  .comicfig img { display: block; width: 100%; height: auto; }
  .under-comic { display: flex; gap: 8pt; margin-top: 6pt; align-items: stretch; }
  .under-comic > .box { flex: 1; min-width: 0; margin-bottom: 0; }
  .parents-wide { margin-top: 5pt; }
  .parents-wide .rail-title { margin-bottom: 0; }
  .parents-wide .parent-cols { display: flex; gap: 12pt; margin-top: 2pt; align-items: stretch; }
  .parents-wide .parent-cols .col { flex: 1; min-width: 0; }
  .parents-wide .parent-cols .col p { margin: 0 0 5pt 0; }
  .parents-wide .parent-cols .col p:last-child { margin-bottom: 0; }
  .comic-wide { margin-top: 5pt; }
  .comic-wide, .comic-wide .comicfig { margin-left: 0; margin-right: 0; }
  .comic-wide img, .comic-wide .comicfig img { display: block; width: auto; height: auto; max-width: 100%; max-height: 3.68in; margin: 0 auto; }
  .page-2-tighten .box.w3 { margin-bottom: 2pt; padding: 3pt 5pt; }
  .page-2-tighten .tourney + .tourney { margin-top: 5pt; }
  /* Proof v3: Frank mockup — left article, right fees + cartoon */
  .page2-lower { display: flex; gap: 10pt; align-items: stretch; margin-top: 4pt; }
  .p2-left { flex: 0 0 35%; min-width: 0; }
  .p2-left .rail-title { margin-bottom: 0; }
  .p2-left h2.head { margin-bottom: 3pt; }
  .p2-left p { margin: 0 0 4pt 0; }
  .p2-left p:last-child { margin-bottom: 0; }
  .p2-right { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: flex-start; gap: 4pt; }
  .p2-right .fees-block .rail-title { margin-bottom: 0; }
  .p2-right .fees-block h2.head { margin-bottom: 3pt; }
  .p2-right .fees-block p { margin: 0 0 4pt 0; }
  .p2-right .fees-block p:last-child { margin-bottom: 0; }
  .p2-right .comic-wide { margin-top: auto; }
  .p2-right .comic-wide img,
  .p2-right .comic-wide .comicfig img { display: block; width: 100%; height: auto; max-width: 100%; max-height: none; margin: 0; }
"""+TPL_CSS+OV.get('css_add','')

# Boards: Pizza + Cobra unchanged since No. 5 / Nov. 9–10 checks. Times in the board's AM/PM house form.
cob=[("Friday, Nov.&nbsp;27",[["Y14 Men","Connor Anderson, Noah Gore, Kian Jaising, Remy Ng, "+nw("Ash Shah-Mirani")],["Cadet Women","Amina Gore, Olivia Hayes, Stella Kuo, Lillian Liu, Mila Siu, Penny Young"],["Y10 Men","Bryce Cheng, Joshua Jeong"]]),
     ("Saturday, Nov.&nbsp;28",[["Y12 Women","Christina Jiang, Stella Kuo, Mila Siu, Penny Young"],["Y12 Men","Kian Jaising, Joshua Jeong, Remy Ng"]]),
     ("Sunday, Nov.&nbsp;29",[["Y14 Women","Stella Kuo, Mila Siu, Penny Young"],["Cadet Men","Connor Anderson, Nico Ng, Caden Wu"]])]
piz=[("Saturday, Nov.&nbsp;14",[["8:00 AM","Y14 Women","Penny Young"],["1:00 PM","Junior Women","Amina Gore"]]),
     ("Sunday, Nov.&nbsp;15",[["8:00 AM","Cadet Women","Amina Gore, Penny Young"],["12:00 PM","Y12 Women","Penny Young"]])]
kie=[("Saturday, Nov.&nbsp;14",[["Y14 Women","Stella Kuo, Mila Siu"]]),
     ("Sunday, Nov.&nbsp;15",[["Y12 Women","Stella Kuo, Mila Siu"]])]
nac=[("Friday, Nov.&nbsp;20",[["Junior Women","Anayaa Sheth"]]),
     ("Saturday, Nov.&nbsp;21",[["Cadet Men","Nico Ng"]]),
     ("Sunday, Nov.&nbsp;22",[["Junior Men",nw("Athreya Aravind")+", Nico Ng"]])]
# Club Results: drop weapon labels in club context (STYLE-GUIDE 0c).
res_rows=[
    ["Maksim Milinkovic","Senior Open, Mixed (Nov.&nbsp;8)","7th of 31"],
    ["Nico Ng","Senior Open, Mixed (Nov.&nbsp;8)","8th of 31"],
    ["Madeline Siu","NYFA #1, Y8 Mixed (Nov.&nbsp;8)","3rd of 4"],
    ["Maximus Siu","NYFA #1, Y10 Mixed (Nov.&nbsp;8)","8th of 17"],
    ["Remy Ng","NYFA #1, Y12 Men (Nov.&nbsp;8)","8th of 13"],
    ["Christina Jiang","NYFA #1, Y12 Women (Nov.&nbsp;8)","5th of 9"],
    ["Mila Siu","NYFA #1, Y14 Women (Nov.&nbsp;8)","5th of 10"],
    ["Stella Kuo","NYFA #1, Y14 Women (Nov.&nbsp;8)","6th of 10"],
]
res=[[c if i==1 else ty(c) for i,c in enumerate(r)] for r in res_rows]
dl_rows=OV.get('deadlines_rows') or S['deadlines']['table']['rows']
dl=[[ty(c) for c in r] for r in dl_rows]
TVR=OV.get('tv_rows') or [[r[0], r[1]+(' \u2014 FencingTV' if len(r)>2 and r[2]=='FencingTV' else '')] for r in S['tv']['table']['rows']]
tv=[[ty(c) for c in r] for r in TVR]
tv_note=OV.get('tv_note',"Dakar streams from the FIE; Berne, Wuxi and Vancouver are on FencingTV. No start times listed. No stream listed for Novi Sad.")
lead_dek=OV.get('lead_dek',"Seven Elite FC fencers, most in their first tournament, stepped on the strip at Medeo Youth Challenge #5.")
lead_head=OV.get('lead_head',D[S['lead']['item']]['headline'])
parents_head=OV.get('parents_head',"What a Rating Letter Means")
shoes_head=OV.get('shoes_head',"Do You Need Fencing Shoes?")
photo_caption=OV.get('photo_caption',"Maximus Siu, 8th of 17 in Y10, is among the finalists pictured at NYFA Youth Cup #1.")
photo_alt=OV.get('photo_alt',"A group of young fencers with medals, and two adults, standing in front of New York Fencing Academy banners after NYFA Youth Cup #1.")
results_note=OV.get('results_note', D[S['club-results']['item']].get('boxnote') or "")
cal_note=OV.get('calendar_note', body('signup-local'))
if not OV.get('calendar_note') and cal_note.lower().startswith('also on the calendar'):
    cal_note='This weekend, three local events have no Elite FC entries yet. ' + cal_note.split('yet. ',1)[-1] if 'yet. ' in cal_note else cal_note
boardnote=OV.get('boardnote',"Pizza is at the Floyd Little Athletic Center. Cobra is at the Meadowlands Expo Center. Entry lists last confirmed Nov. 9–10; Cobra lists no start times.")

# Proof v2: three balanced columns, sourced from the 2026-27 Athlete Handbook.
PARENTS_COLS=OV.get('parents_cols') or [
"A rating is a letter. USA Fencing classifies fencers A (the highest), then B, C, D, E, and U \u2014 unclassified, where everyone starts. The letter is followed by a year: A26 means an A earned or re-earned in 2026. A rating is official only on USA Fencing\u2019s membership list. It lasts four seasons; if it isn\u2019t renewed, it drops one letter at the start of the next season, on Aug. 1 \u2014 a B earned in 2020 (B20) became a C24 on Aug. 1, 2024.",
"Ratings are earned, one weapon at a time, at sanctioned competitions from local events to national ones. A competition\u2019s classification \u2014 Group E1, D1, C1 and so on \u2014 depends on the size of the field and the ratings already in it, and that determines what can be awarded. Group E1, the smallest that awards a rating, needs at least six fencers, none of whom have to be rated already. First place earns an E. Larger groups can award higher letters, and E\u2019s further down the results. The official chart is in the Athlete Handbook (2026–27).",
"Ratings also seed the field, ordering fencers from strongest to weakest at the start of a competition. At local youth events, seeding is by rating and the year it was last earned. At many regional and national events, national points come first, then rating and year. In many categories, fencers with the same letter and year are placed in random order. Only official membership-list ratings should be used when seeding. The letter is a seeding tool, not a verdict. Every A in the club started as a U."
]

FEES_HEAD=OV.get('fees_head',"What “Triple Fees” Means")
FEES_BODY=OV.get('fees_body') or D.get('desk-for-the-parents-triple-fees-2026-11-10',{}).get('body') or ""


blocks={
 'results':f'<div class="box"><div class="boxtitle">Club Results</div>{table(["Fencer","Event","Finish"],res,["0.72in",None,"0.62in"],numcol=None)}<p class="boxnote">{ty(results_note)}</p></div>',
 'photo':f'<div class="rail-block" style="margin-top:6pt;"><div class="photo"><img src="media/nyfa-youth-cup1-podium-4-2026-11-08.jpg" alt="{html.escape(photo_alt)}"><p class="caption">{ty(photo_caption)}</p></div></div>',
 'shoes':f'<div class="rail-block" style="margin-top:7pt;"><div class="rail-title">Overheard on Reddit</div><h2 class="head">{ty(shoes_head)}</h2>{paras(body("overheard-reddit"))}</div>',
 'parents':f'<div class="rail-block"><div class="rail-title">For the Parents</div><h2 class="head">{ty(parents_head)}</h2>{paras(body("overheard"))}</div>',
 'deadlines':f'<div class="box"><div class="boxtitle">Deadlines</div>{table(["Date","What closes"],dl,["0.62in",None])}<p class="boxnote">{ty("USA Fencing deadlines are 11:59 p.m. Pacific (2:59 a.m. Eastern the next day). The Junior Olympics regular-fee deadline is today.")}</p></div>',
 'tv':f'<div class="box"><div class="boxtitle">Epee on Screen</div>{table(["Dates","Event"],tv,["0.64in",None])}<p class="boxnote">{ty(tv_note)}</p></div>',
 'cartoon':f'<div class="comicfig"><img src="media/tournament-day-cartoon.jpg" alt="{html.escape(OV.get("cartoon_alt","A black-and-white comic titled Tournaments, showing a parent and young fencer’s tournament day in a clockwise loop."))}"></div>',
}
foot = (
  '  <div class="footer">\n'
  '    <span>En Garde Gazette · Issue No. 6</span>\n'
  '    <span class="foot-archive">Past issues · newsletter.teamremco.org</span>\n'
  '    <span>For fun only — facts aren’t guaranteed accurate.</span>\n'
  '  </div>'
)


h = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>En Garde Gazette — Vol. I No. 6 — November 11, 2026</title>
<meta name="author" content="Nico's Dad">
<style>""" + css + """</style>
</head>
<body>

<!-- ==================== PAGE 1 (FRONT) ==================== -->
<div class="page">
  <div class="masthead">
    <div class="flank left">""" + FLANK["left_flank_fixed"] + """</div>
    <img src="../../masthead001.png" alt="The En Garde Gazette — The Elite Fencers Club Weekly">
    <div class="flank right">""" + FLANK["right_flank_default"] + """</div>
  </div>
  <div class="dateline">
    <div class="edition">Wednesday Edition</div>
    <div class="meta">Vol. I — No. 6 &nbsp;·&nbsp; Chatham, N.J. &nbsp;·&nbsp; November 11, 2026</div>
  </div>

  <div class="cols3 ruled">
    <div class="c span2">
      <h1 class="head">""" + ty(lead_head) + """</h1>
      <p class="dek">""" + ty(lead_dek) + """</p>
      """ + paras(body("lead")) + """
      """ + blocks["shoes"] + """
      <div style="margin-top:6pt;">
      """ + blocks["deadlines"] + """
      </div>
      <div style="margin-top:6pt;">
      """ + blocks["tv"] + """
      </div>
    </div>
    <div class="c">
      """ + blocks["results"] + """
      """ + blocks["photo"] + """
    </div>
  </div>

  <div class="box w3" style="margin-top:8pt;">
    <div class="boxtitle">On the Road — Elite FC Entries</div>
    <div class="board-split">
      <div>
        """ + tourney("Kiefer Meinhardt Cup","Glen Allen, Va.","Nov.&nbsp;14–15",["Event","Elite FC"],["0.85in",None],kie) + """
      </div>
      <div>
        """ + tourney("November NAC","Columbus, Ohio","Nov.&nbsp;20–23",["Event","Elite FC"],["0.85in",None],nac) + """
      </div>
    </div>
  </div>
""" + foot + """
</div>

<!-- ==================== PAGE 2 (BACK) ==================== -->
<div class="page page-2-tighten">
  <div class="dateline" style="margin-top:0;">
    <div class="edition">Page Two</div>
    <div class="meta">Club Calendar &amp; Notes &nbsp;·&nbsp; Vol. I — No. 6</div>
  </div>

  <div class="box w3">
    <div class="boxtitle">Nearby Tournaments — Elite FC Entries</div>
    <div class="board-split">
      <div>
        """ + tourney("Pizza RYC/RJCC","New Haven, Conn.","Nov.&nbsp;14–15",["Time","Event","Elite FC"],["0.62in","0.85in",None],piz) + """
      </div>
      <div>
        """ + tourney("Cobra Challenge SYC/RCC","Secaucus, N.J.","Nov.&nbsp;27–29",["Event","Elite FC"],["0.85in",None],cob) + """
      </div>
    </div>
    <p class="boxnote">""" + ty(boardnote) + """</p>
    <p class="boxnote"><b>Also on the calendar.</b> """ + ty(cal_note) + """</p>
  </div>

  <div class="page2-lower">
    <div class="p2-left">
      <div class="rail-block">
        <div class="rail-title">For the Parents</div>
        <h2 class="head">""" + ty(parents_head) + """</h2>
        """ + "".join(paras(c) for c in PARENTS_COLS) + """
      </div>
    </div>
    <div class="p2-right">
      <div class="rail-block fees-block">
        <div class="rail-title">For the Parents</div>
        <h2 class="head">""" + ty(FEES_HEAD) + """</h2>
        """ + paras(FEES_BODY) + """
      </div>
      <div class="comic-wide">
        """ + blocks["cartoon"] + """
      </div>
    </div>
  </div>
""" + foot + """
</div>

</body>
</html>
"""
open(R+ISSUE+'/issue.html','w').write(h)
print('ok')
