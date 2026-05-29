"""
Génère le diagramme de Gantt Excel — MSPR TPRE921 COFRAP
Dates réelles : J1=20/04  J2=21/04  J3=22/04  J4=23/04/2026
python3 scripts/generate_gantt.py
"""

import os
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../docs/planning/Gantt_MSPR_COFRAP.xlsx")

COLORS = {
    "youssef":   ("1F4E79", "DEEBF7"),
    "soulaiman": ("375623", "E2EFDA"),
    "hamza":     ("833C00", "FCE4D6"),
    "p4":        ("3D1359", "EAD1DC"),
    "all":       ("404040", "EDEDED"),
    "milestone": ("C00000", "FFE7E7"),
    "hdr_main":  "1F3864",
    "hdr_day":   "2E75B6",
    "hdr_hour":  "BDD7EE",
    "gap":       "F2F2F2",
    "crit_brd":  "C00000",
    "white":     "FFFFFF",
    "alt_row":   "F5F9FF",
    "section":   "D6E4F0",
}

def f(h): return PatternFill("solid", fgColor=h)
def ft(bold=False, color="000000", sz=9, italic=False):
    return Font(bold=bold, color=color, size=sz, italic=italic, name="Calibri")
def al(h="center", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)
def bd(color="B8CCE4", thick=False):
    c = "C00000" if thick else color
    s = "medium" if thick else "thin"
    S = lambda: Side(border_style=s, color=c)
    return Border(left=S(), right=S(), top=S(), bottom=S())
def outer(color="1F3864"):
    S = lambda: Side(border_style="medium", color=color)
    return Border(left=S(), right=S(), top=S(), bottom=S())

TASKS = [
    dict(id="MACA-73", section="  J1 — Lundi 20/04/2026  ·  Cadrage & Organisation",
         title="Initialisation dépôt Git & structure projet",
         who="youssef",  day=0, sh=9,  dh=1, crit=False),
    dict(id="MACA-74", section=None,
         title="Configuration Jira (Epics, Sprints, Tickets MACA)",
         who="youssef",  day=0, sh=10, dh=1, crit=False),
    dict(id="MACA-75", section=None,
         title="Rédaction Gantt & planning projet",
         who="youssef",  day=0, sh=11, dh=2, crit=False),
    dict(id="MACA-76", section=None,
         title="Architecture technique COFRAP (schéma Frontend↔OpenFaaS↔DB)",
         who="all",      day=0, sh=13, dh=3, crit=True),

    dict(id="MACA-77", section="  J2 — Mardi 21/04/2026  ·  Infrastructure & Développement",
         title="Setup environnement dev local (.env, dépendances Python)",
         who="all",      day=1, sh=9,  dh=2, crit=True),
    dict(id="MACA-78", section=None,
         title="Schéma PostgreSQL — table users (password_hash, totp_secret)",
         who="soulaiman",day=1, sh=9,  dh=2, crit=True),
    dict(id="MACA-79", section=None,
         title="Installation K3S + kubectl (control-plane + worker node)",
         who="hamza",    day=1, sh=11, dh=3, crit=True),
    dict(id="MACA-80", section=None,
         title="Déploiement OpenFaaS Community via Helm (faas-netes)",
         who="hamza",    day=1, sh=14, dh=2, crit=True),
    dict(id="MACA-81", section=None,
         title="Déploiement PostgreSQL Helm + secrets OpenFaaS (db-password, fernet-key)",
         who="soulaiman",day=1, sh=11, dh=2, crit=True),
    dict(id="MACA-82", section=None,
         title="Développement fonction generate-password (24 chars + bcrypt + QR Code)",
         who="soulaiman",day=1, sh=13, dh=4, crit=True),

    dict(id="MACA-83", section="  J3 — Mercredi 22/04/2026  ·  Intégration & Frontend",
         title="Développement fonction generate-2fa (TOTP + QR Code base64)",
         who="soulaiman",day=2, sh=9,  dh=3, crit=True),
    dict(id="MACA-84", section=None,
         title="Développement fonction authenticate (password + TOTP + expiry 6 mois)",
         who="hamza",    day=2, sh=12, dh=3, crit=True),
    dict(id="MACA-85", section=None,
         title="Frontend React — Pages Create Account + génération QR Codes",
         who="p4",       day=2, sh=9,  dh=4, crit=False),
    dict(id="MACA-86", section=None,
         title="Frontend React — Pages Login + Renouvellement credentials",
         who="p4",       day=2, sh=13, dh=3, crit=False),
    dict(id="MACA-87", section=None,
         title="Build & push images Docker Hub (3 fonctions OpenFaaS)",
         who="hamza",    day=2, sh=9,  dh=2, crit=True),
    dict(id="MACA-88", section=None,
         title="Intégration Frontend ↔ OpenFaaS Gateway + tests Postman",
         who="all",      day=2, sh=15, dh=2, crit=True),

    dict(id="MACA-89", section="  J4 — Jeudi 23/04/2026  ·  Tests & Soutenance",
         title="Tests E2E complets — 4 scénarios Postman (succès/expiré/échec/renouvellement)",
         who="all",      day=3, sh=8,  dh=2, crit=True),
    dict(id="MACA-90", section=None,
         title="Rédaction dossier technique final (architecture, screenshots, annexes code)",
         who="p4",       day=3, sh=8,  dh=3, crit=False),
    dict(id="MACA-91", section=None,
         title="Déploiement Frontend sur K3S (Ingress Traefik + CORS)",
         who="hamza",    day=3, sh=8,  dh=2, crit=True),
    dict(id="MACA-92", section=None,
         title="Préparation support soutenance — slides + démo live (backup screenshots)",
         who="youssef",  day=3, sh=10, dh=2, crit=True),
    dict(id="MACA-93", section=None,
         title="Répétition générale soutenance (20 min chronométrées) + relecture dossier",
         who="all",      day=3, sh=12, dh=2, crit=True),
    dict(id="🎯 M5",   section=None,
         title="SOUTENANCE MSPR  —  Jeudi 23/04/2026  à  14h00",
         who="milestone", day=3, sh=14, dh=0, crit=True),
]

DAY_CFG = [
    dict(label="J1  ·  Lundi 20/04/2026",      bh=9, nh=9),
    dict(label="J2  ·  Mardi 21/04/2026",      bh=9, nh=9),
    dict(label="J3  ·  Mercredi 22/04/2026",   bh=9, nh=9),
    dict(label="J4  ·  Jeudi 23/04/2026",      bh=8, nh=7),
]
GAP = 1
INFO = 5

def day_off(d):
    return sum(DAY_CFG[i]["nh"] + GAP for i in range(d))

def bar_slots(t):
    d = t["day"]; cfg = DAY_CFG[d]; base = day_off(d)
    s = t["sh"] - cfg["bh"]
    if t["dh"] == 0: return [base + s]
    return [base + s + i for i in range(t["dh"]) if s + i < cfg["nh"]]

TOTAL_TL = sum(c["nh"] for c in DAY_CFG) + GAP * (len(DAY_CFG) - 1)
TOTAL_C  = INFO + TOTAL_TL

def build():
    wb = Workbook(); ws = wb.active; ws.title = "Gantt MSPR COFRAP"

    # largeurs
    widths = [9, 46, 12, 6, 5]
    slot = 0
    for d, cfg in enumerate(DAY_CFG):
        for _ in range(cfg["nh"]): widths.append(3.2); slot += 1
        if d < len(DAY_CFG)-1: widths.append(1.5); slot += 1
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Row 1 titre ──
    ws.row_dimensions[1].height = 28
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=TOTAL_C)
    c = ws.cell(1, 1, "MSPR TPRE921 — COFRAP Serverless Auth System  ·  Diagramme de Gantt  ·  20/04/2026 → 23/04/2026  ·  Soutenance J4 14h00")
    c.fill=f(COLORS["hdr_main"]); c.font=ft(True,"FFFFFF",12); c.alignment=al(); c.border=outer()

    # ── Row 2 sous-titre ──
    ws.row_dimensions[2].height = 14
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=TOTAL_C)
    c = ws.cell(2, 1, "Python · OpenFaaS Community · K3S · PostgreSQL · React.js · Helm · Docker Hub   |   Équipe : Youssef · Soulaiman · Hamza · [PRÉNOM4]   |   🔴 = Chemin critique")
    c.fill=f("2E75B6"); c.font=ft(False,"FFFFFF",8,True); c.alignment=al()

    # ── Row 3 : en-têtes jours ──
    ws.row_dimensions[3].height = 18
    for ci, lbl in enumerate(["ID","Tâche","Responsable","Dur.","★"],1):
        ws.merge_cells(start_row=3, start_column=ci, end_row=4, end_column=ci)
        c=ws.cell(3,ci,lbl); c.fill=f(COLORS["hdr_main"]); c.font=ft(True,"FFFFFF",9)
        c.alignment=al(wrap=True); c.border=bd("FFFFFF")

    for d, cfg in enumerate(DAY_CFG):
        off=day_off(d); cs=INFO+1+off; ce=cs+cfg["nh"]-1
        ws.merge_cells(start_row=3, start_column=cs, end_row=3, end_column=ce)
        c=ws.cell(3,cs,cfg["label"]); c.fill=f(COLORS["hdr_day"])
        c.font=ft(True,"FFFFFF",10); c.alignment=al(); c.border=bd("FFFFFF")
        if d < len(DAY_CFG)-1:
            gc=INFO+1+off+cfg["nh"]
            ws.merge_cells(start_row=3, start_column=gc, end_row=4, end_column=gc)
            ws.cell(3,gc).fill=f(COLORS["gap"])

    # ── Row 4 : heures ──
    ws.row_dimensions[4].height = 13
    for d, cfg in enumerate(DAY_CFG):
        off=day_off(d)
        for hi in range(cfg["nh"]):
            ca=INFO+1+off+hi
            c=ws.cell(4,ca,f"{cfg['bh']+hi}h")
            c.fill=f(COLORS["hdr_hour"]); c.font=ft(sz=7,color="1F3864")
            c.alignment=al(); c.border=bd(COLORS["hdr_day"])

    # ── Tâches ──
    row=5; last_sec=None
    for ti, t in enumerate(TASKS):
        if t.get("section") and t["section"] != last_sec:
            last_sec=t["section"]
            ws.row_dimensions[row].height=14
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=TOTAL_C)
            c=ws.cell(row,1,t["section"])
            c.fill=f(COLORS["section"]); c.font=ft(True,COLORS["hdr_main"],10)
            c.alignment=al("left"); c.border=bd(COLORS["hdr_day"]); row+=1

        ws.row_dimensions[row].height=15
        alt=COLORS["alt_row"] if ti%2==0 else COLORS["white"]
        ms=t["who"]=="milestone"
        bc,lc=((COLORS["milestone"]) if ms else COLORS[t["who"]])
        crit=t["crit"]
        active=set(bar_slots(t))

        who_lbl={"youssef":"Youssef","soulaiman":"Soulaiman","hamza":"Hamza",
                 "p4":"[PRÉNOM4]","all":"Équipe","milestone":"ÉQUIPE"}[t["who"]]

        # ID
        c=ws.cell(row,1,t["id"])
        c.fill=f(bc if (ms or crit) else COLORS["hdr_hour"])
        c.font=ft(True,"FFFFFF" if (ms or crit) else COLORS["hdr_main"],8)
        c.alignment=al(); c.border=bd(COLORS["hdr_day"])
        # titre
        c=ws.cell(row,2,t["title"])
        c.fill=f(lc if ms else alt)
        c.font=ft(ms or crit,color=bc if ms else "000000",sz=9)
        c.alignment=al("left"); c.border=bd(thick=crit and not ms)
        # responsable
        c=ws.cell(row,3,who_lbl)
        c.fill=f(bc); c.font=ft(True,"FFFFFF",8); c.alignment=al(); c.border=bd(COLORS["hdr_day"])
        # durée
        c=ws.cell(row,4,"◆" if ms else f"{t['dh']}h")
        c.fill=f(alt); c.font=ft(ms,bc if ms else "404040",9); c.alignment=al(); c.border=bd(COLORS["hdr_day"])
        # critique
        c=ws.cell(row,5,"🔴" if crit and not ms else "")
        c.fill=f(alt); c.font=ft(sz=9); c.alignment=al(); c.border=bd(COLORS["hdr_day"])

        # timeline
        for d,cfg in enumerate(DAY_CFG):
            off=day_off(d)
            for hi in range(cfg["nh"]):
                sl=off+hi; ca=INFO+1+sl
                c=ws.cell(row,ca)
                if sl in active:
                    if ms:
                        c.value="◆"; c.fill=f(lc)
                        c.font=ft(True,bc,13); c.alignment=al()
                        c.border=outer(bc)
                    else:
                        c.fill=f(bc)
                        if crit:
                            c.border=Border(
                                left=Side("medium",color=COLORS["crit_brd"]),
                                right=Side("medium",color=COLORS["crit_brd"]),
                                top=Side("thin",color=COLORS["crit_brd"]),
                                bottom=Side("thin",color=COLORS["crit_brd"]))
                        else:
                            c.border=bd(COLORS["hdr_day"])
                else:
                    c.fill=f(alt); c.border=bd("D9E1F2")
            if d<len(DAY_CFG)-1:
                ws.cell(row,INFO+1+off+cfg["nh"]).fill=f(COLORS["gap"])
        row+=1

    # ── Légende ──
    row+=1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=TOTAL_C)
    c=ws.cell(row,1,"  LÉGENDE  —  Responsables & Conventions")
    c.fill=f(COLORS["hdr_main"]); c.font=ft(True,"FFFFFF",10); c.alignment=al("left"); row+=1

    for lbl,who,desc in [
        ("Youssef",    "youssef",   "Chef de Projet · Architecte Solution · DevOps"),
        ("Soulaiman",  "soulaiman", "Développeur Backend Lead  (Python · OpenFaaS · PostgreSQL)"),
        ("Hamza",      "hamza",     "Développeur Backend Auth + DevOps K3S · Docker"),
        ("[PRÉNOM4]",  "p4",        "Développeur Frontend React.js + Rédacteur dossier final"),
        ("Équipe",     "all",       "Tâche collective — toute l'équipe mobilisée"),
        ("🔴 Crit.",  None,        "Chemin critique : retard = impact soutenance"),
        ("◆ Jalon",   None,        "Milestone — événement clé (ex: Soutenance 14h00)"),
    ]:
        ws.row_dimensions[row].height=14
        bc2=COLORS[who][0] if who else COLORS["hdr_day"]
        ws.merge_cells(start_row=row,start_column=1,end_row=row,end_column=2)
        c=ws.cell(row,1,f"  {lbl}"); c.fill=f(bc2); c.font=ft(True,"FFFFFF",9)
        c.alignment=al("left"); c.border=bd(COLORS["hdr_day"])
        ws.merge_cells(start_row=row,start_column=3,end_row=row,end_column=12)
        c=ws.cell(row,3,desc); c.fill=f(COLORS["alt_row"]); c.font=ft(sz=9)
        c.alignment=al("left"); c.border=bd(COLORS["hdr_day"]); row+=1

    ws.freeze_panes=f"{get_column_letter(INFO+1)}5"
    ws.sheet_view.zoomScale=100
    ws.page_setup.orientation="landscape"; ws.page_setup.fitToPage=True; ws.page_setup.fitToWidth=1

    os.makedirs(os.path.dirname(OUT_PATH),exist_ok=True)
    wb.save(OUT_PATH)
    print(f"✅  {OUT_PATH}")

if __name__=="__main__":
    build()
