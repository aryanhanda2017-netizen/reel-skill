"""Declarative YouTube edit engine. All authored times are source times.
Use init(), full(), side(), tag(), pip(), sidel(), then plan() or build().
"""
import html, json, os, re, subprocess, sys, math
from pathlib import Path
from fractions import Fraction
from projectlib import write_text, validate_cuts, validate_words, load_json

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = html.escape
ANIMS, HOSTS, CARDS, MISSING = [], [], [], []
W, _TOK, CUTS, TRACK = [], [], [], []
P = {}  # root, fps, src_dur, dur, id, title, footage
_SCREENS = {}
_uid = [0]
_norm = lambda s: re.sub(r"[^\w+]|_", "", s.casefold())


# ---------------------------------------------------------------- setup + time
def _load(path):
    return load_json(path) if os.path.exists(path) else None


def _probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 3)


def _in_cut(t):
    return any(a <= t < b for a, b in CUTS)


def init(root, src_dur=None, cuts=None, fps=None, title=None, comp_id=None):
    root = os.path.abspath(root)
    cfg = _load(os.path.join(root, "project.json")) or {}
    cj = _load(os.path.join(root, "cuts.json")) or {}
    P.clear()
    P["root"] = root
    P["fps"] = fps or cfg.get("fps", 25)
    P["src_dur"] = src_dur or cfg.get("src_dur") or _probe_dur(os.path.join(root, "public", "footage.mp4"))
    P["id"] = re.sub(r"[^a-zA-Z0-9_-]", "-", comp_id or cfg.get("id") or os.path.basename(root))
    P["title"] = title or cfg.get("title") or P["id"]
    P["width"] = int(cfg.get("width", 1440))
    P["height"] = int(cfg.get("height", 1080))
    P["fps_rate"] = str(P["fps"])
    P["fps"] = float(Fraction(P["fps_rate"]))
    P["theme"] = cfg.get("theme", {})
    P["caption_settings"] = cfg.get("captions", {})
    CUTS[:] = validate_cuts(cuts if cuts is not None else cj.get("cuts", []), P["src_dur"])
    P["dur"] = round(P["src_dur"] - sum(b - a for a, b in CUTS), 6)
    P["footage"] = cj.get("footage", "footage-cut.mp4") if CUTS else "footage.mp4"
    transcript_file = cfg.get("transcript_file", "transcript.json")
    if os.path.isabs(transcript_file) or ".." in transcript_file.replace("\\", "/").split("/"):
        raise ValueError("transcript_file must be project-relative")
    words = validate_words(load_json(os.path.join(root, transcript_file)), P["src_dur"])
    W[:] = [w for w in words if not _in_cut(w["start"])]
    _layout()
    _TOK[:] = [_norm(w["text"]) for w in W]
    for lst in (ANIMS, HOSTS, CARDS, MISSING, TRACK):
        lst.clear()
    _SCREENS.clear()
    _uid[0] = 0


def sh(t):
    """Source time -> cut time. A time inside a cut lands on the edit point."""
    off = 0.0
    for a, b in CUTS:
        if t < a:
            break
        if t < b:
            return round(a - off, 3)
        off += b - a
    return round(t - round(off, 6), 3) if off else t


def unsh(c):
    """Finished-video time -> source time."""
    off = 0.0
    for a, b in CUTS:
        if c + off < a:
            break
        off += b - a
    return round(c + off, 3)


def at(phrase, after=0.0):
    """Source start time of the first occurrence of phrase at or after `after`."""
    p = [_norm(x) for x in phrase.split()]
    if not p or not any(p):raise ValueError("Phrase anchor cannot be empty")
    for i in range(len(W) - len(p) + 1):
        if W[i]["start"] >= after and _TOK[i:i + len(p)] == p:
            return W[i]["start"]
    raise SystemExit("phrase not found: " + phrase)


def words_between(t0, t1):
    return [w for w in W if t0 <= w["start"] < t1]


def uid(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def A(sel, kind, t, **o):
    """Queue one animation (t in source time). Kinds live in the template's runtime:
    in, fade, left, pop, out, strike, fill, hi, scroll(dy), type."""
    if "times" in o:
        o["times"] = [sh(x) for x in o["times"]]
    if "until" in o:
        o["until"] = sh(o["until"])
    ANIMS.append([sel, kind, round(sh(t), 3), o])


def anim_el(tag, cls, inner, kind, t, idp="e", **o):
    i = uid(idp)
    A("#" + i, kind, t, **o)
    return f'<{tag} id="{i}" class="{cls} a">{inner}</{tag}>'


def _text(s, n=110):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"


def typed(text, t, cls, step=None, hold_until=None):
    """Typewriter headline: chars appear one by one, accent cursor blinks."""
    i = uid("ty")
    n = len(text.replace("\n", ""))
    step = step or min(0.065, 1.0 / max(n, 1))
    parts = []
    for ch in text:
        if ch == "\n":
            parts.append("<br>")
        else:
            parts.append(f'<span class="ch">{"&nbsp;" if ch == " " else e(ch)}</span>')
    A("#" + i, "type", t, step=step, until=hold_until or (t + n * step + 2.5))
    return f'<div id="{i}" class="{cls}">{"".join(parts)}<span class="cur"></span></div>'


def card(kind, t0, t1, body, zone=None, label=None):
    """kind: FULL (section card), SIDE (card right, footage left), SIDEL (card left, footage right),
    TAG (callout over the full footage), COL (notes column beside a PIP screen)."""
    CARDS.append(dict(kind=kind, t0=sh(t0), t1=sh(t1), label=label or _text(body)))
    cid = uid("c")
    A(f"#{cid} > .root", "in" if kind != "FULL" else "fade", t0, y=24 if kind != "FULL" else 0)
    A(f"#{cid} > .root", "out", t1 - 0.32)
    z = zone or kind
    HOSTS.append(dict(id=cid, zone=z, t0=sh(t0), t1=sh(t1), body=body, timed=True))
    return cid


# ---------------------------------------------------------------- screen panel (B-roll, mocks, recap)
def screen(t0, t1, inner=None, broll=None, label=None, media_start=0.0, h=None):
    """The big screen panel used in PIP state. broll = a file in public/broll/ (missing -> placeholder +
    shot list in plan.md). h = panel height for recordings that aren't 16:9 (broll.py prints it)."""
    sid = uid("s")
    A(f"#{sid} > .root", "in", t0, y=6)
    A(f"#{sid} > .root", "out", t1 - 0.32)
    timed = True
    if broll is not None:
        path = os.path.join(P["root"], "public", "broll", broll)
        if os.path.exists(path):
            vid = uid("v")
            inner = (f'<video id="{vid}" class="clip broll" src="broll/{e(broll)}" muted playsinline '
                     f'data-start="{sh(t0):.3f}" data-duration="{sh(t1) - sh(t0):.3f}" data-media-start="{media_start:.3f}" '
                     f'data-has-audio="false" data-track-index="2"></video>')
            timed = False  # the video carries the timing; its host must not
            _SCREENS[sid] = f"Recording: {broll}"
        else:
            inner = (f'<div class="ph"><div class="ph-k">B-ROLL · SCREEN RECORDING</div>'
                     f'<div class="ph-t">{e(label or broll)}</div><div class="ph-s">recording goes here</div></div>')
            MISSING.append(dict(t0=sh(t0), t1=sh(t1), file=broll, label=label or broll, h=h))
            _SCREENS[sid] = f"MISSING recording: {label or broll}"
    else:
        _SCREENS[sid] = "Designed screen: " + (label or _text(inner or "", 70))
    box = None
    HOSTS.append(dict(id=sid, zone="SCREEN", t0=sh(t0), t1=sh(t1), body=inner, timed=timed, box=box))
    return sid


def column(t0, t1, items):
    """Right-hand annotation column beside the screen panel (PIP state)."""
    return card("COL", t0, t1, "".join(items), zone="COL")


def pip(t0, t1, screen_kw, col_items):
    """Screen big top-left, speaker small bottom-right, notes column on the right."""
    sid = screen(t0, t1, **screen_kw)
    column(t0, t1, col_items)
    CARDS.append(dict(kind="PIP", t0=sh(t0), t1=sh(t1), label=_SCREENS[sid] + " | " + CARDS[-1]["label"]))


def note(t, kicker=None, text=None, cls="", italic=None):
    inner = ""
    if kicker:
        inner += f'<div class="k">{kicker}</div>'
    if text:
        inner += f'<div class="nt">{text}</div>'
    if italic:
        inner += f'<div class="it">{italic}</div>'
    return anim_el("div", "note glass " + cls, inner, "in", t)


def chip(t, text, cls="", kind="pop"):
    return anim_el("span", "chip " + cls, text, kind, t)


def chips(items, cls=""):
    """items: [(t, text), ...]; cls: "" (accent), "ghost", "warn" (accent outline)."""
    return '<div class="chips">' + "".join(chip(t, x, cls) for t, x in items) + "</div>"


def chipnote(t, kicker, items, cls=""):
    inner = (f'<div class="k">{kicker}</div>' if kicker else "") + chips(items, cls)
    return anim_el("div", "note glass", inner, "in", t)


def num(n):
    return f'<span class="num">{n}</span>'


# ---------------------------------------------------------------- FULL section cards
def set_track(items):
    """Stage track shown under FULL cards: [(NAME, "DAY 1–15"), ...]."""
    TRACK[:] = items


def _head_cls(head):
    if "\n" in head:
        return "fh fh2"
    n = len(head)
    return "fh" if n <= 9 else "fh fh3" if n <= 14 else "fh fh2"


def full(t0, t1, kicker, head, sub, stage=None, head_cls=None):
    """Full-screen section card: kicker (put the number in <span class="tc">), typed headline, italic subline,
    optional stage track. Headline: one line <= 9 chars full size, <= 14 auto-shrinks, else split with \\n."""
    head_cls = head_cls or _head_cls(head)
    kid = uid("fk")
    k = f'<div class="fk a" id="{kid}">{kicker}</div>'
    A("#" + kid, "in", t0, y=6)
    body = '<div class="fglow"></div><div class="fgrid"></div><div class="fwrap">' + k
    body += typed(head, t0 + 0.04, head_cls)
    sub_html = anim_el("div", "fs", sub, "in", min(t1-.4, t0 + 1.2))
    body += sub_html + "</div>"
    if stage:
        segs = ""
        for i, (nm, days) in enumerate(TRACK, 1):
            cur = " cur-seg" if i == stage else ""
            done = " done" if i < stage else ""
            segs += f'<div class="seg{cur}{done}"><div class="bar"><i></i></div><div class="sl"><b>{i:02d}</b> {nm}</div><div class="sd">{days}</div></div>'
        tid = uid("tr")
        A(f"#{tid} .cur-seg .bar i", "fill", t0 + 0.5, d=1.6)
        cols = "" if len(TRACK) == 4 else f' style="grid-template-columns: repeat({len(TRACK)}, 1fr)"'
        body += f'<div class="track" id="{tid}"{cols}>{segs}</div>'
    card("FULL", t0, t1, body, label=_text(kicker) + " · " + head.replace("\n", " "))


# ---------------------------------------------------------------- SIDE / SIDEL / TAG cards
def side(t0, t1, kicker, title, rows, foot=None, title_t=None):
    """Glass card on the right, the footage slides left. rows: row()/chips()/anim_el() html."""
    body = '<div class="side glass"><div class="sheen"></div>'
    body += anim_el("div", "k", kicker, "in", t0, y=6)
    if title:
        body += anim_el("div", "st", title, "in", title_t if title_t is not None else t0)
    body += "".join(rows)
    if foot:
        body += foot
    body += "</div>"
    card("SIDE", t0, t1, body)


def row(t, idx, text, sub=None, cls=""):
    inner = (f'<span class="ix">{idx}</span>' if idx else "") + f'<span class="rt">{text}'
    if sub:
        inner += f'<span class="rs">{sub}</span>'
    inner += "</span>"
    return anim_el("div", "row " + cls, inner, "left", t)


def foot(t, text):
    return anim_el("div", "foot", text, "in", t)


def tag(t0, t1, kicker, lines):
    """Small callout top-left over the full talking head. lines: [(t, html), ...]."""
    body = '<div class="tag glass">' + anim_el("div", "k", kicker, "in", t0, y=6)
    for t, txt in lines:
        body += anim_el("div", "tt", txt, "in", t, y=10)
    card("TAG", t0, t1, body + "</div>")


def tool_card(t, logo_html, name, sub):
    """Logo card for sidel(). logo_html: '<img src="logos/x.svg" alt="">' (or class="tfull" for a full-bleed icon)."""
    return anim_el("div", "tool glass", f'<div class="tlogo">{logo_html}</div><div class="tname">{name}<span>{sub}</span></div>', "left", t)


def sidel(t0, t1, kicker, rows):
    """List of glass cards on the LEFT, the footage slides right."""
    body = '<div class="sidel">' + anim_el("div", "k", kicker, "in", t0, y=6) + "".join(rows) + "</div>"
    card("SIDEL", t0, t1, body)


def doc_mock(t, title, rows, footer=""):
    """A generic document preview. Supply only real, approved content."""
    pr = "".join(f'<div class="pr"><b>{a}</b><span>{b}</span></div>' for a,b in rows)
    return anim_el("div", "pdf", f'<div class="ph1">{title}</div>{pr}<div class="pfoot">{footer}</div>', "pop", t)


# ---------------------------------------------------------------- build
ZONES = {}

def _layout():
    w,h = P["width"], P["height"]
    scale = h / 1080
    margin = round(36*scale)
    wide = w/h > 1.55
    screen_w = w-round(420*scale) if wide else w
    screen_h = min(round(screen_w*9/16), round(h*.75))
    pip_w = round(w*(.16 if wide else .20))
    pip_h = round(pip_w*h/w)
    pip_x = w-pip_w-margin
    pip_y = h-pip_h-margin
    P["layout"] = {"pip_x":pip_x,"pip_y":pip_y,"pip_scale":pip_w/w,
                   "screen_height":screen_h,"scale":scale}
    ZONES.update({
        "FULL":(0,0,w,h), "SIDE":(w-round(w*.36)-margin,round(h*.41),round(w*.36),round(h*.46)),
        "SIDEL":(margin,round(h*.41),round(w*.36),round(h*.46)),
        "TAG":(margin,margin,round(w*.42),round(h*.20)),
        "SCREEN":(0,0,screen_w,screen_h),
        "COL":(screen_w+margin,margin,w-screen_w-2*margin,round(h*.58)) if wide else
              (margin,screen_h+round(22*scale),pip_x-2*margin,round(h*.14))
    })

KIND_NAMES = {"FULL": "Section card (full screen)", "SIDE": "Card right, you left", "SIDEL": "Cards left, you right",
              "TAG": "Callout over you", "PIP": "Screen big, you small"}


def _states():
    runs=[]
    for c in sorted((c for c in CARDS if c["kind"]=="PIP"), key=lambda c:c["t0"]):
        if runs and c["t0"]-runs[-1][1] < .7:runs[-1][1]=max(runs[-1][1],c["t1"])
        else:runs.append([c["t0"],c["t1"]])
    return runs


def _pages():
    result=[];group=[];chars=0
    cfg=P["caption_settings"]
    for i,w in enumerate(W):
        pause=i and sh(w["start"])-sh(W[i-1]["end"])>cfg.get("pause",.38)
        if group and (pause or len(group)>=cfg.get("max_words",5) or chars+len(w["text"])+1>cfg.get("max_chars",32)):
            result.append([group]);group=[];chars=0
        group.append(i);chars+=len(w["text"])+1
        if re.search(r"[.!?]$",w["text"]) or (re.search(r"[,;]$",w["text"]) and len(group)>=3):
            result.append([group]);group=[];chars=0
    if group:result.append([group])
    return result


def _captions():
    pages=_pages();markup=[];meta=[]
    lead=float(P["caption_settings"].get("page_lead",.08))
    for n,lines in enumerate(pages):
        first,last=lines[0][0],lines[-1][-1]
        a=max(0,sh(W[first]["start"])-lead)
        if n+1<len(pages):
            next_start=max(0,sh(W[pages[n+1][0][0]]["start"])-lead)
            b=next_start if next_start-sh(W[last]["end"])<.38 else min(next_start,sh(W[last]["end"])+.12)
        else:b=min(P["dur"],sh(W[last]["end"])+.18)
        if b<=a:raise ValueError("Caption page has non-positive duration; inspect word times")
        inner=" ".join(f'<span class="w" id="w{i}">{e(W[i]["text"])}</span>' for i in lines[0])
        markup.append(f'<div id="pg{n}" class="caption-page clip" data-start="{a:.6f}" data-duration="{b-a:.6f}" data-track-index="5"><div class="caption-text">{inner}</div></div>')
        meta.append([a,b,first,last])
    return markup,meta,[[sh(w["start"]),sh(w["end"])] for w in W]


def mmss(t):
    t = max(0.0, t)
    return f"{int(t // 60)}:{int(t % 60):02d}"


def _plan(states):
    """plan.md: the gate-1 table for review, all in finished-video (cut) time."""
    L = [f"# Edit plan: {P['title']}", "",
         "Times are in the finished video (after cuts), as the viewer will see them.",
         f"Length: {mmss(P['dur'])} ({P['dur']:.2f} s). Source footage: {mmss(P['src_dur'])}. Cuts: {len(CUTS)}.", "",
         "| # | In | Out | What you see | On screen |", "|---|---|---|---|---|"]
    shown = [c for c in sorted(CARDS, key=lambda c: c["t0"]) if c["kind"] != "COL"]
    for n, c in enumerate(shown, 1):
        L.append(f"| {n} | {mmss(c['t0'])} | {mmss(c['t1'])} | {KIND_NAMES.get(c['kind'], c['kind'])} | {c['label'].replace('|', '/')} |")
    counts = {}
    for c in shown:
        counts[c["kind"]] = counts.get(c["kind"], 0) + 1
    L += ["", "Graphics: " + ", ".join(f"{KIND_NAMES[k]} x{v}" for k, v in counts.items()) +
          f" = {len(shown)} ({len(shown) / max(P['dur'] / 60, 0.1):.1f} a minute)."]
    if MISSING:
        L += ["", "## Shot list: B-roll still missing", "",
              "| When | Length | Shot | File |", "|---|---|---|---|"]
        for m in MISSING:
            L.append(f"| {mmss(m['t0'])} | {m['t1'] - m['t0']:.0f} s | {m['label']} | public/broll/{m['file']}" +
                     (f" (panel h={m['h']})" if m["h"] else "") + " |")
    if CUTS:
        L += ["", "## Cuts", "", "| Source | Removed | Lands at |", "|---|---|---|"]
        for a, b in CUTS:
            L.append(f"| {mmss(a)} to {mmss(b)} ({a:.2f} to {b:.2f}) | {b - a:.2f} s | {mmss(sh(a))} |")
    fulls = [c for c in shown if c["kind"] == "FULL"]
    if len(fulls) >= 3 and fulls[0]["t0"] >= 10 and all(b["t0"]-a["t0"] >= 10 for a,b in zip(fulls,fulls[1:])) and P["dur"]-fulls[-1]["t0"] >= 10:
        L += ["", "## Chapters (from the section cards; YouTube needs 0:00 first, 3+ chapters, each 10 s+)", ""]
        if fulls[0]["t0"] >= 10:
            L.append("0:00 Intro")
        for c in fulls:
            L.append(f"{mmss(c['t0'])} {c['label']}")
    return "\n".join(L) + "\n"


def _theme_css():
    colors={"background":"#121722","surface":"#1C2432","text":"#F4F6FA","muted":"#B5C0D2","accent":"#98BEFF","highlight_text":"#111827","border":"#64748B"}
    colors.update(P["theme"])
    for key,value in colors.items():
        if key not in {"background","surface","text","muted","accent","highlight_text","border"} or not re.fullmatch(r"#[0-9a-fA-F]{6}",str(value)):
            raise ValueError("Theme accepts known keys and six-digit hex colors only")
    return ":root{"+";".join("--"+k.replace("_","-")+":"+v for k,v in colors.items())+";}"


def plan():
    states=_states()
    storyboard=dict(dur=P["dur"],cuts=CUTS,states=states,cards=sorted(CARDS,key=lambda c:c["t0"]),missing=MISSING)
    write_text(os.path.join(P["root"],"storyboard.json"),json.dumps(storyboard,indent=2)+"\n")
    write_text(os.path.join(P["root"],"plan.md"),_plan(states))
    return storyboard


def _native_notes():
    for host in HOSTS:
        if host["zone"]!="COL" or 'data-track-index="4"' in host["body"]:continue
        ids=re.findall(r'<div id="([^"]+)" class="note',host["body"])
        cues=[]
        for nid in ids:
            cue=next((a[2] for a in ANIMS if a[0]=="#"+nid and a[1] in ("in","left","pop")),host["t0"])
            cues.append((nid,max(host["t0"],cue)))
        for i,(nid,cue) in enumerate(cues):
            end=cues[i+1][1] if i+1<len(cues) else host["t1"]
            if end<=cue:raise ValueError("Notes need distinct, ascending cues inside the screen window")
            pattern=r'<div id="'+re.escape(nid)+r'" class="([^"]+)"'
            def convert(m):
                cls=" ".join(c for c in m[1].split() if c!="a")+" clip"
                return f'<div id="{nid}" class="{cls}" data-start="{cue:.6f}" data-duration="{end-cue:.6f}" data-track-index="4"'
            host["body"]=re.sub(pattern,convert,host["body"])
        native={"#"+nid for nid in ids}
        ANIMS[:]=[a for a in ANIMS if a[0] not in native]


def build(out=None, template=None):
    _native_notes()
    root = P["root"]
    states = _states()
    cap_html, cap_meta, WT = _captions()
    host_html = []
    for h in sorted(HOSTS, key=lambda h: h["t0"]):
        x, y, w_, h_ = h.get("box") or ZONES[h["zone"]]
        timing = (f' data-start="{h["t0"]:.3f}" data-duration="{h["t1"] - h["t0"]:.3f}" data-track-index="3"'
                  if h["timed"] else "")
        cls = "card-host clip" if h["timed"] else "card-host"
        host_html.append(f'<div id="{h["id"]}" class="{cls} z-{h["zone"].lower()}"{timing} '
                         f'style="left:{x}px;top:{y}px;width:{w_}px;height:{h_}px;"><div class="root a">{h["body"]}</div></div>')
    local_tpl = os.path.join(root, "src", "template.html")
    tpl_path = template or (local_tpl if os.path.exists(local_tpl) else os.path.join(SKILL_DIR, "assets", "template.html"))
    tpl = Path(tpl_path).read_text(encoding="utf-8")
    html_out = (tpl.replace("/*DUR*/", f"{P['dur']}")
                   .replace("/*FPS*/", str(P["fps"]))
                   .replace("/*ID*/", e(P["id"]))
                   .replace("/*WIDTH*/", str(P["width"]))
                   .replace("/*CAPWIDTH*/", str(round(min(P["width"]*.52,1000*P["height"]/1080))))
                   .replace("/*HEIGHT*/", str(P["height"]))
                   .replace("/*THEME*/", _theme_css())
                   .replace("/*LAYOUT*/", json.dumps(P["layout"]))
                   .replace("/*WORD_LEAD*/", str(P["caption_settings"].get("word_lead",.04)))
                   .replace("/*TITLE*/", e(P["title"]))
                   .replace("/*FOOTAGE*/", P["footage"])
                   .replace("<!--HOSTS-->", "\n".join(host_html))
                   .replace("<!--CAPTIONS-->", "\n".join(cap_html))
                   .replace("/*ANIMS*/", json.dumps(ANIMS))
                   .replace("/*STATES*/", json.dumps(states))
                   .replace("/*PAGES*/", json.dumps(cap_meta))
                   .replace("/*WORDS*/", json.dumps(WT)))
    write_text(out or os.path.join(root,"public","index.html"),html_out)
    plan()
    print(f"hosts={len(HOSTS)} anims={len(ANIMS)} caption_pages={len(cap_meta)} states={len(states)} "
          f"missing_broll={len(MISSING)} dur={P['dur']} template={'project src/' if tpl_path == local_tpl else 'skill assets/' if not template else template}")


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[2] not in ("--cut", "--src"):
        raise SystemExit(__doc__)
    root = os.path.abspath(sys.argv[1])
    cj = _load(os.path.join(root, "cuts.json")) or {}
    CUTS[:] = sorted([float(a), float(b)] for a, b in cj.get("cuts", []))
    t = float(sys.argv[3].split(":")[0]) * 60 + float(sys.argv[3].split(":")[1]) if ":" in sys.argv[3] else float(sys.argv[3])
    if sys.argv[2] == "--cut":
        s = unsh(t)
        print(f"cut {mmss(t)} ({t:.2f}) -> source {mmss(s)} ({s:.2f})")
    else:
        c = sh(t)
        print(f"source {mmss(t)} ({t:.2f}) -> cut {mmss(c)} ({c:.2f})" + ("  [inside a cut]" if _in_cut(t) else ""))
