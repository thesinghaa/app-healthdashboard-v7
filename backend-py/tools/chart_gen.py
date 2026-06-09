"""
chart_gen.py — generate report charts as base64 PNGs.

Primary renderer: Plotly (via kaleido)
Fallback:         Matplotlib (if kaleido not installed or render fails)
"""

import base64, io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Plotly availability check ─────────────────────────────────────────────────
try:
    import plotly.graph_objects as go
    import plotly.io as pio
    pio.kaleido.scope.default_width  = 700
    pio.kaleido.scope.default_height = 420
    _PLOTLY_OK = True
except Exception:
    _PLOTLY_OK = False

PALETTE = {
    "gap":      "#D93258",
    "close":    "#C8780A",
    "achieved": "#149650",
    "bg":       "#0a1628",
    "card":     "#0f1f38",
    "text":     "#ffffff",
    "subtext":  "#b8ccd8",
    "org":      "#FF5500",
    "grid":     "#1e3050",
}

# ── Shared helpers ────────────────────────────────────────────────────────────

def _mpl_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def _plotly_to_base64(fig) -> str:
    img_bytes = pio.to_image(fig, format="png", scale=2)
    return base64.b64encode(img_bytes).decode()


def _plotly_layout(title: str, height: int = 420) -> dict:
    """Shared dark-theme Plotly layout dict."""
    return dict(
        title=dict(text=title, font=dict(color=PALETTE["text"], size=13), x=0.05),
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["card"],
        font=dict(color=PALETTE["text"], family="Inter, Arial, sans-serif"),
        height=height,
        margin=dict(l=180, r=60, t=50, b=50),
        showlegend=True,
    )


# ── Chart 1 — Programme Status Donut ─────────────────────────────────────────

def _plotly_donut(div_data: dict) -> str:
    programmes = div_data.get("programmes", {})
    counts = {"red": 0, "yellow": 0, "green": 0}
    for p in programmes.values():
        s = p.get("status", "yellow")
        counts[s] = counts.get(s, 0) + 1

    labels = ["Critical", "Caution", "On Track"]
    values = [counts["red"], counts["yellow"], counts["green"]]
    colors = [PALETTE["gap"], PALETTE["close"], PALETTE["achieved"]]

    # Filter zero slices
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not filtered:
        return ""
    labels, values, colors = zip(*filtered)

    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=list(colors), line=dict(color=PALETTE["bg"], width=2)),
        textinfo="label+value",
        textfont=dict(size=11, color=PALETTE["text"]),
        hovertemplate="%{label}: %{value} programmes<extra></extra>",
        direction="clockwise",
        sort=False,
    ))
    fig.update_layout(
        **_plotly_layout(f"{div_data.get('label', 'Division')} Programme Status", height=380),
        margin=dict(l=20, r=20, t=50, b=20),
        annotations=[dict(
            text=f"<b>{total}</b><br><span style='font-size:10px'>Programmes</span>",
            x=0.5, y=0.5, font=dict(size=16, color=PALETTE["text"]),
            showarrow=False,
        )],
        legend=dict(
            orientation="h", x=0.5, xanchor="center", y=-0.08,
            font=dict(size=10, color=PALETTE["text"]),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return _plotly_to_base64(fig)


def _mpl_donut(div_data: dict) -> str:
    programmes = div_data.get("programmes", {})
    counts = {"red": 0, "yellow": 0, "green": 0}
    for p in programmes.values():
        s = p.get("status", "yellow")
        counts[s] = counts.get(s, 0) + 1

    labels = ["Critical", "Caution", "On Track"]
    values = [counts["red"], counts["yellow"], counts["green"]]
    colors = [PALETTE["gap"], PALETTE["close"], PALETTE["achieved"]]

    fig, ax = plt.subplots(figsize=(4, 4), facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])
    ax.pie(
        [max(v, 0.01) for v in values],
        colors=colors, startangle=90,
        wedgeprops=dict(width=0.52, edgecolor=PALETTE["bg"], linewidth=2),
        counterclock=False,
    )
    total = sum(values)
    ax.text(0, 0.08, str(total), ha="center", va="center",
            fontsize=26, fontweight="bold", color=PALETTE["text"])
    ax.text(0, -0.22, "Programmes", ha="center", va="center",
            fontsize=9, color=PALETTE["subtext"])
    legend = [mpatches.Patch(color=c, label=f"{l} ({v})")
              for l, v, c in zip(labels, values, colors) if v > 0]
    ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(0.5, -0.18),
              ncol=3, frameon=False, labelcolor=PALETTE["text"], fontsize=8)
    ax.set_title(f"{div_data.get('label', 'Division')} Programme Status",
                 color=PALETTE["text"], fontsize=11, pad=12)
    return _mpl_to_base64(fig)


def programme_status_donut(div_data: dict) -> str:
    if _PLOTLY_OK:
        try:
            return _plotly_donut(div_data)
        except Exception:
            pass
    return _mpl_donut(div_data)


# ── Chart 2 — Top Critical KD Gaps ───────────────────────────────────────────

def _build_kd_rows(div_data: dict, n: int = 8) -> list:
    rows = []
    for prog in div_data.get("programmes", {}).values():
        for kd in prog.get("kds", []):
            t, a = kd.get("target"), kd.get("achievement")
            if not t or a is None or t == 0:
                continue
            ratio = a / t
            deficit = (ratio - 1.0) if kd.get("lowerIsBetter") else (1.0 - ratio)
            if deficit > 0.01:
                rows.append({
                    "label":   kd["indicator"][:42],
                    "deficit": deficit,
                    "achieved": a,
                    "target":   t,
                    "unit":     kd.get("unit", ""),
                })
    rows.sort(key=lambda x: x["deficit"], reverse=True)
    return rows[:n]


def _plotly_critical_kds(div_data: dict, n: int = 8) -> str:
    rows = _build_kd_rows(div_data, n)
    if not rows:
        return ""

    labels   = [r["label"] for r in rows][::-1]   # bottom-to-top for barh
    deficits = [r["deficit"] * 100 for r in rows][::-1]
    annots   = [f"{r['achieved']}{r['unit']} / {r['target']}{r['unit']}"
                for r in rows][::-1]
    bar_colors = [PALETTE["gap"] if d > 25 else PALETTE["close"] for d in deficits]

    fig = go.Figure(go.Bar(
        x=deficits,
        y=labels,
        orientation="h",
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=annots,
        textposition="outside",
        textfont=dict(size=9, color=PALETTE["subtext"]),
        hovertemplate="%{y}<br>Gap: %{x:.1f}%<extra></extra>",
        cliponaxis=False,
    ))
    height = max(360, len(rows) * 44 + 80)
    layout = _plotly_layout("Top Critical KD Gaps", height=height)
    layout.update(
        xaxis=dict(
            title="Gap from Target (%)",
            title_font=dict(color=PALETTE["subtext"], size=10),
            tickfont=dict(color=PALETTE["subtext"], size=9),
            gridcolor=PALETTE["grid"], zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color=PALETTE["text"], size=9),
            gridcolor=PALETTE["grid"],
        ),
        showlegend=False,
        bargap=0.35,
    )
    fig.update_layout(**layout)
    return _plotly_to_base64(fig)


def _mpl_critical_kds(div_data: dict, n: int = 8) -> str:
    rows = _build_kd_rows(div_data, n)
    if not rows:
        return ""

    labels   = [r["label"] for r in rows]
    deficits = [r["deficit"] * 100 for r in rows]
    colors   = [PALETTE["gap"] if d > 25 else PALETTE["close"] for d in deficits]

    fig, ax = plt.subplots(figsize=(7, max(3, len(rows) * 0.55 + 1)),
                           facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])
    bars = ax.barh(labels, deficits, color=colors, height=0.55,
                   edgecolor=PALETTE["bg"], linewidth=0.5)
    for bar, row in zip(bars, rows):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{row['achieved']}{row['unit']} / {row['target']}{row['unit']}",
                va="center", ha="left", fontsize=7, color=PALETTE["subtext"])
    ax.set_xlabel("Gap from Target (%)", color=PALETTE["subtext"], fontsize=9)
    ax.set_title("Top Critical KD Gaps", color=PALETTE["text"], fontsize=11, pad=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", colors=PALETTE["text"], labelsize=8)
    ax.tick_params(axis="x", colors=PALETTE["subtext"])
    plt.tight_layout()
    return _mpl_to_base64(fig)


def top_critical_kds_chart(div_data: dict, n: int = 8) -> str:
    if _PLOTLY_OK:
        try:
            return _plotly_critical_kds(div_data, n)
        except Exception:
            pass
    return _mpl_critical_kds(div_data, n)


# ── Chart 3 — Programme Scorecard ─────────────────────────────────────────────

def _build_scorecard_rows(div_data: dict) -> tuple:
    progs = list(div_data.get("programmes", {}).values())
    names, pcts = [], []
    for p in progs:
        kds = p.get("kds", [])
        scored = [k for k in kds if k.get("target") and k.get("achievement") is not None]
        if not scored:
            names.append(p["name"][:24])
            pcts.append(0)
            continue
        ach = sum(1 for k in scored if (
            (k["achievement"] / k["target"] >= 1.0 and not k.get("lowerIsBetter")) or
            (k["achievement"] / k["target"] <= 1.0 and k.get("lowerIsBetter"))
        ))
        names.append(p["name"][:24])
        pcts.append(round(ach / len(scored) * 100))
    return names, pcts


def _plotly_scorecard(div_data: dict) -> str:
    names, pcts = _build_scorecard_rows(div_data)
    if not names:
        return ""

    bar_colors = [
        PALETTE["achieved"] if p >= 60 else (PALETTE["close"] if p >= 35 else PALETTE["gap"])
        for p in pcts
    ]
    names_r = names[::-1]
    pcts_r  = pcts[::-1]
    colors_r = bar_colors[::-1]

    fig = go.Figure(go.Bar(
        x=pcts_r,
        y=names_r,
        orientation="h",
        marker=dict(color=colors_r, line=dict(width=0)),
        text=[f"{p}%" for p in pcts_r],
        textposition="outside",
        textfont=dict(size=10, color=PALETTE["text"]),
        hovertemplate="%{y}<br>KDs Achieved: %{x}%<extra></extra>",
        cliponaxis=False,
    ))

    height = max(360, len(names) * 44 + 80)
    layout = _plotly_layout("Programme KD Achievement Rate", height=height)
    layout.update(
        xaxis=dict(
            title="% KDs Achieved", range=[0, 115],
            title_font=dict(color=PALETTE["subtext"], size=10),
            tickfont=dict(color=PALETTE["subtext"], size=9),
            gridcolor=PALETTE["grid"], zeroline=False,
        ),
        yaxis=dict(tickfont=dict(color=PALETTE["text"], size=9), gridcolor=PALETTE["grid"]),
        showlegend=False,
        bargap=0.35,
        shapes=[dict(
            type="line", x0=75, x1=75, y0=-0.5, y1=len(names) - 0.5,
            line=dict(color=PALETTE["close"], width=1, dash="dash"),
        )],
        annotations=[dict(
            x=76, y=len(names) - 0.8, text="75%", showarrow=False,
            font=dict(color=PALETTE["close"], size=9),
        )],
    )
    fig.update_layout(**layout)
    return _plotly_to_base64(fig)


def _mpl_scorecard(div_data: dict) -> str:
    names, pcts = _build_scorecard_rows(div_data)
    if not names:
        return ""

    colors = [
        PALETTE["achieved"] if p >= 60 else (PALETTE["close"] if p >= 35 else PALETTE["gap"])
        for p in pcts
    ]
    fig, ax = plt.subplots(figsize=(7, max(3, len(names) * 0.6 + 1)),
                           facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])
    bars = ax.barh(names, pcts, color=colors, height=0.55,
                   edgecolor=PALETTE["bg"], linewidth=0.5)
    for bar, pct in zip(bars, pcts):
        ax.text(min(bar.get_width() + 1, 98), bar.get_y() + bar.get_height() / 2,
                f"{pct}%", va="center", ha="left", fontsize=8,
                color=PALETTE["text"], fontweight="bold")
    ax.set_xlim(0, 110)
    ax.set_xlabel("% KDs Achieved", color=PALETTE["subtext"], fontsize=9)
    ax.set_title("Programme KD Achievement Rate", color=PALETTE["text"], fontsize=11, pad=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="y", colors=PALETTE["text"], labelsize=8)
    ax.tick_params(axis="x", colors=PALETTE["subtext"])
    ax.axvline(75, color=PALETTE["close"], linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(75.5, len(names) - 0.3, "75% threshold", color=PALETTE["close"], fontsize=7)
    plt.tight_layout()
    return _mpl_to_base64(fig)


def programme_scorecard_chart(div_data: dict) -> str:
    if _PLOTLY_OK:
        try:
            return _plotly_scorecard(div_data)
        except Exception:
            pass
    return _mpl_scorecard(div_data)


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_all_charts(div_data: dict) -> dict:
    return {
        "status_donut": programme_status_donut(div_data),
        "critical_kds": top_critical_kds_chart(div_data),
        "scorecard":    programme_scorecard_chart(div_data),
    }
