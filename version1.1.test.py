"""
Tiger Analytics | Sense & Respond OS
Multimodal Agentic Operating System — Bleeding Signals Engine
Powered by Groq (llama-3.3-70b-versatile) + SMART Signal Framework
"""

import streamlit as st
import json
import os
import time
import re
import csv
import io
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ─────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tiger Analytics | Sense & Respond OS",
    page_icon="🐯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────
# LOGO — pinned top-left
# ─────────────────────────────────────────────────────
if Path("tiger_logo.png").exists():
    st.logo("tiger_logo.png")

# ─────────────────────────────────────────────────────
# CUSTOM CSS — Tiger Analytics brand
# ─────────────────────────────────────────────────────
# ── Theme tokens injected dynamically after theme toggle
def apply_theme(dark: bool) -> None:
    """Inject CSS precisely matching the Lovable TigerTrend OS design system."""
    if dark:
        BG          = "#1A1A1A"
        BG_MID      = "#202020"
        BG_CARD     = "#161616"
        BG_ELEV     = "#252525"
        FG          = "#F5F5F5"
        FG2         = "#BCBCBC"
        BORDER      = "#333333"
        ORANGE      = "#E8941A"
        ORANGE_GLOW = "rgba(232,148,26,0.22)"
        ORANGE_DIM  = "rgba(232,148,26,0.12)"
        RED         = "#D45C5C"
        GREEN       = "#4DC98A"
        SHADOW      = "0 1px 0 rgba(255,255,255,0.04) inset, 0 8px 30px rgba(0,0,0,0.45)"
        INPUT_BG    = "#202020"
        SIDEBAR_BG  = "#202020"
        SCROLL_TR   = "#161616"
        SCROLL_TH   = "#333333"
        AMBIENT     = "radial-gradient(1200px 600px at 80% -10%, rgba(232,148,26,0.07) 0%, transparent 60%), radial-gradient(900px 500px at -10% 110%, rgba(122,180,224,0.05) 0%, transparent 60%)"
        HEADER_BG   = "#161616"
        HEADER_BORD = "#333333"
        INVERT      = "1"
    else:
        BG          = "#FAFAF8"
        BG_MID      = "#F2EFE9"
        BG_CARD     = "#FFFFFF"
        BG_ELEV     = "#EDEAE4"
        FG          = "#1A1009"
        FG2         = "#6B5A45"
        BORDER      = "#E0D8CC"
        ORANGE      = "#C47208"
        ORANGE_GLOW = "rgba(196,114,8,0.18)"
        ORANGE_DIM  = "rgba(196,114,8,0.08)"
        RED         = "#B51C00"
        GREEN       = "#1A6B30"
        SHADOW      = "0 1px 0 rgba(255,255,255,0.8) inset, 0 4px 16px rgba(90,60,10,0.10)"
        INPUT_BG    = "#FFFFFF"
        SIDEBAR_BG  = "#FFFFFF"
        SCROLL_TR   = "#EDE6DC"
        SCROLL_TH   = "#D4C4A8"
        AMBIENT     = "none"
        HEADER_BG   = "#FFFFFF"
        HEADER_BORD = "#E0D8CC"
        INVERT      = "0"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* BASE */
html, body, [class*="css"], .stApp {{
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: {BG} !important;
    color: {FG} !important;
    -webkit-font-smoothing: antialiased !important;
    text-rendering: optimizeLegibility !important;
}}
.stApp {{
    background-image: {AMBIENT} !important;
    background-attachment: fixed !important;
}}
::selection {{ background: {ORANGE_DIM} !important; color: {FG} !important; }}

/* HEADER */
header[data-testid="stHeader"] {{
    background-color: {HEADER_BG} !important;
    border-bottom: 1px solid {HEADER_BORD} !important;
    box-shadow: none !important;
    backdrop-filter: blur(20px) saturate(140%) !important;
}}
header[data-testid="stHeader"] * {{ color: {FG} !important; }}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER} !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] > div {{ padding-top: 0 !important; }}
[data-testid="stSidebar"] * {{ color: {FG} !important; }}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.76rem !important;
    letter-spacing: 0.12em !important;
    color: {FG2} !important;
}}
[data-testid="stSidebar"] hr {{ border-color: {BORDER} !important; margin: 0.5rem 0 !important; }}
[data-testid="stSidebar"] img {{ filter: invert({INVERT}) opacity(0.9) !important; }}

/* BUTTONS — ghost border style matching Lovable */
div.stButton > button {{
    background-color: transparent !important;
    color: {FG2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.85rem !important;
    transition: border-color 0.18s, color 0.18s !important;
    box-shadow: none !important;
    height: 32px !important;
    min-height: 32px !important;
    line-height: 1 !important;
}}
div.stButton > button:hover {{
    border-color: {ORANGE} !important;
    color: {ORANGE} !important;
    background-color: transparent !important;
    box-shadow: none !important;
    transform: none !important;
}}
/* Wide CTA run button */
div.stButton > button[data-testid="baseButton-primary"] {{
    background-color: {ORANGE} !important;
    color: #000000 !important;
    border: none !important;
    font-weight: 700 !important;
    letter-spacing: 0.16em !important;
    height: 44px !important;
    min-height: 44px !important;
}}
div.stButton > button[data-testid="baseButton-primary"]:hover {{
    box-shadow: 0 0 0 1px {ORANGE_GLOW}, 0 8px 24px {ORANGE_GLOW} !important;
    background-color: {ORANGE} !important;
    color: #000000 !important;
}}
div.stButton > button:disabled {{
    opacity: 0.45 !important;
    cursor: not-allowed !important;
}}

/* INPUTS */
div[data-baseweb="select"] > div {{
    background-color: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    color: {FG} !important;
    font-size: 0.8rem !important;
    min-height: 36px !important;
    transition: border-color 0.18s !important;
}}
div[data-baseweb="select"] > div:focus-within {{
    border-color: {ORANGE} !important;
    outline: 2px solid {ORANGE_DIM} !important;
    outline-offset: 2px !important;
}}
div[data-baseweb="input"] > div {{
    background-color: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    min-height: 36px !important;
    color: {FG} !important;
    transition: border-color 0.18s !important;
}}
div[data-baseweb="input"] > div:focus-within {{
    border-color: {ORANGE} !important;
    outline: 2px solid {ORANGE_DIM} !important;
    outline-offset: 2px !important;
}}
input, input[type="text"], input[type="password"] {{
    background-color: {BG_CARD} !important;
    color: {FG} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
}}
input::placeholder {{ color: {FG2} !important; opacity: 1 !important; }}
textarea {{
    background-color: {BG_CARD} !important;
    color: {FG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    line-height: 1.6 !important;
    transition: border-color 0.18s !important;
}}
textarea:focus {{
    border-color: {ORANGE} !important;
    outline: 2px solid {ORANGE_DIM} !important;
    outline-offset: 2px !important;
}}
textarea::placeholder {{ color: {FG2} !important; opacity: 1 !important; }}
ul[data-baseweb="menu"] {{
    background-color: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    box-shadow: {SHADOW} !important;
    padding: 4px !important;
}}
li[role="option"] {{
    color: {FG} !important; font-size: 0.8rem !important; border-radius: 4px !important;
}}
li[role="option"]:hover, li[aria-selected="true"] {{
    background-color: {ORANGE_DIM} !important;
    color: {ORANGE} !important;
}}

/* TABS */
div[data-testid="stTabs"] > div:first-child {{ border-bottom: 1px solid {BORDER} !important; }}
div[data-testid="stTabs"] button {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {FG2} !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 0.55rem 1.1rem !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.18s, background-color 0.18s !important;
    font-weight: 500 !important;
}}
div[data-testid="stTabs"] button:hover {{
    color: {FG} !important;
    background-color: {ORANGE_DIM} !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {ORANGE} !important;
    border-bottom: 2px solid {ORANGE} !important;
    font-weight: 700 !important;
    background-color: transparent !important;
}}

/* METRICS */
div[data-testid="stMetric"] {{
    background-color: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-top: 2px solid {ORANGE} !important;
    border-radius: 10px !important;
    padding: 1rem 1.1rem !important;
    box-shadow: {SHADOW} !important;
    transition: box-shadow 0.2s !important;
}}
div[data-testid="stMetric"]:hover {{
    box-shadow: 0 0 0 1px {ORANGE_GLOW}, 0 8px 24px {ORANGE_GLOW} !important;
}}
div[data-testid="stMetric"] label {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: {FG2} !important;
    font-weight: 500 !important;
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: {ORANGE} !important;
    line-height: 1.1 !important;
    letter-spacing: -0.01em !important;
}}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] > div {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
}}

/* EXPANDER */
details {{
    background-color: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    padding: 0.3rem 0.6rem !important;
    box-shadow: {SHADOW} !important;
}}
details summary {{
    color: {ORANGE} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    padding: 0.45rem 0 !important;
}}
details summary:hover {{ opacity: 0.75 !important; }}

/* FILE UPLOADER */
[data-testid="stFileUploader"] section {{
    background-color: {BG_CARD} !important;
    border: 1px dashed {BORDER} !important;
    border-radius: 8px !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"] section:hover {{ border-color: {ORANGE} !important; }}
[data-testid="stFileUploader"] label {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: {FG2} !important;
}}

/* CHAT INPUT */
[data-testid="stChatInput"] {{
    background-color: {BG_MID} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
}}
[data-testid="stChatInput"]:focus-within {{ border-color: {ORANGE} !important; }}
[data-testid="stChatInput"] textarea {{
    background-color: {BG_MID} !important;
    color: {FG} !important;
    font-size: 0.88rem !important;
    border: none !important;
}}
[data-testid="stChatInput"] button {{
    background-color: {ORANGE} !important;
    color: #000 !important;
    border-radius: 6px !important;
    border: none !important;
}}

/* ALERTS */
div[data-testid="stAlert"] {{
    background-color: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-left: 3px solid {ORANGE} !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    box-shadow: {SHADOW} !important;
    color: {FG} !important;
}}

/* DOWNLOAD BUTTON */
div.stDownloadButton > button {{
    background: transparent !important;
    color: {FG2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    height: 32px !important;
    transition: border-color 0.18s, color 0.18s !important;
}}
div.stDownloadButton > button:hover {{
    border-color: {ORANGE} !important;
    color: {ORANGE} !important;
    background: transparent !important;
}}

/* RADIO */
div[data-testid="stRadio"] label {{
    font-size: 0.82rem !important;
    color: {FG2} !important;
    transition: color 0.15s !important;
}}
div[data-testid="stRadio"] label:hover {{ color: {FG} !important; }}

/* LAYOUT */
.block-container {{
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1440px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{ padding-top: 0.5rem !important; }}
footer {{ display: none !important; }}

/* SCROLLBAR */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {SCROLL_TR}; }}
::-webkit-scrollbar-thumb {{ background: {SCROLL_TH}; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: {ORANGE}; }}

/* FOCUS */
:focus-visible {{
    outline: 2px solid {ORANGE} !important;
    outline-offset: 2px !important;
    border-radius: 4px !important;
}}

/* TRANSITIONS */
*, *::before, *::after {{
    transition: background-color 0.22s ease, border-color 0.22s ease, color 0.15s ease !important;
}}

/* ANIMATIONS */
@keyframes pulse-dot {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.35; }} }}
.pulse {{ animation: pulse-dot 1.6s ease-in-out infinite; }}
</style>
""", unsafe_allow_html=True)

def tv() -> dict:
    """Return current theme token dict — exact Lovable palette."""
    dark = st.session_state.get("theme_dark", True)
    if dark:
        return {
            "bg":       "#1A1A1A", "sidebar":  "#202020", "card":   "#161616",
            "card2":    "#131313", "input":    "#202020", "border": "#333333",
            "border2":  "#2A2A2A", "text":     "#F5F5F5", "text2":  "#BCBCBC",
            "muted":    "#888888", "muted2":   "#555555", "tag":    "#1E1E1E",
            "shadow":   "rgba(0,0,0,0.45)",
            "acc":      "#E8941A", "acc_text": "#000000",
            "green":    "#4DC98A", "red":      "#D45C5C",
            "badge_fg": "#000000",
            "c_trend":  "#E8941A", "c_sent":   "#4DC98A", "c_vel":  "#F0A830",
            "c_heat":   "#D45C5C", "c_rank":   "#B07FD8", "c_evt":  "#7AB4E0",
            "c_price":  "#7AB4E0",
            "sig_bg":   "#161616", "sig_ext":  "#1C1010",
        }
    else:
        return {
            "bg":       "#FAFAF8", "sidebar":  "#FFFFFF", "card":   "#FFFFFF",
            "card2":    "#F5F2EC", "input":    "#FFFFFF", "border": "#E0D8CC",
            "border2":  "#EDE6DC", "text":     "#1A1009", "text2":  "#6B5A45",
            "muted":    "#7A6A55", "muted2":   "#9A8A78", "tag":    "#FDF1DE",
            "shadow":   "rgba(90,60,10,0.08)",
            "acc":      "#C47208", "acc_text": "#FFFFFF",
            "green":    "#1A6B30", "red":      "#B51C00",
            "badge_fg": "#FFFFFF",
            "c_trend":  "#B05E00", "c_sent":   "#1A6B30", "c_vel":  "#9A5000",
            "c_heat":   "#B51C00", "c_rank":   "#6B2EA0", "c_evt":  "#0066AA",
            "c_price":  "#005C8A",
            "sig_bg":   "#FAFAF8", "sig_ext":  "#FFF5F3",
        }


# ─────────────────────────────────────────────────────
# LAYER ICON MAP
# ─────────────────────────────────────────────────────
LAYER_ICONS = {
    "Executive":    "👑",
    "Strategic":    "🎯",
    "Operational":  "📦",
    "Analytical":   "🔬",
    "Technical":    "⚙️",
    "Frontline":    "🏪",
    "Governance":   "🛡️",
}

def layer_icon(layer_str: str) -> str:
    primary = layer_str.split("/")[0].strip()
    return LAYER_ICONS.get(primary, "👤")


# ─────────────────────────────────────────────────────
# LOAD CSV DATA
# ─────────────────────────────────────────────────────
@st.cache_data
def load_csv_data():
    # ── signal_kpi_mapping
    kpi_path = Path("signal_kpi_mapping.csv")
    if not kpi_path.exists():
        kpi_path = Path("/mnt/project/signal_kpi_mapping.csv")
    with open(kpi_path, encoding="cp1252") as f:
        kpi_rows = list(csv.DictReader(f))

    # ── persona_layer_reference
    plr_path = Path("persona_layer_reference.csv")
    if not plr_path.exists():
        plr_path = Path("/mnt/project/persona_layer_reference.csv")
    with open(plr_path, encoding="cp1252") as f:
        plr_rows = list(csv.DictReader(f))

    # Build PLR lookup keyed by primary layer name
    plr_lookup = {}
    for r in plr_rows:
        plr_lookup[r["Persona Layer"]] = r

    # ── Taxonomy: industry -> [sub-industries]
    ind_sub = defaultdict(set)
    for r in kpi_rows:
        ind_sub[r["Industry"]].add(r["Sub-Industry"])
    taxonomy = {ind: sorted(subs) for ind, subs in sorted(ind_sub.items())}

    # ── Persona map: (industry, sub) -> {persona_name: {...details}}
    persona_map = defaultdict(dict)
    for r in kpi_rows:
        key = (r["Industry"], r["Sub-Industry"])
        p = r["Persona"]
        if p not in persona_map[key]:
            primary_layer = r["Persona Layer"].split("/")[0].strip()
            plr_info = plr_lookup.get(primary_layer, {})
            persona_map[key][p] = {
                "functional_domain":   r["Functional Domain"],
                "persona_layer":       r["Persona Layer"],
                "layer_description":   r["Layer Description"],
                "primary_focus":       plr_info.get("Primary Focus", ""),
                "signal_kpi_priority": plr_info.get("Signal KPI Priority", ""),
                "primary_layer":       primary_layer,
            }

    # ── KPI map: (industry, sub, persona) -> [list of KPI dicts]
    kpi_map = defaultdict(list)
    for r in kpi_rows:
        key = (r["Industry"], r["Sub-Industry"], r["Persona"])
        kpi_map[key].append({
            "name":      r["Signal KPI Name"],
            "tells":     r["What It Tells the Persona"],
            "display":   r["UI Display Type"],
            "decision":  r["Decision It Enables"],
            "sources":   r["Data Sources"],
            "compute":   r["How to Compute"],
        })

    return taxonomy, dict(persona_map), plr_lookup, dict(kpi_map)


TAXONOMY, PERSONA_MAP, PLR_LOOKUP, KPI_MAP = load_csv_data()


# ─────────────────────────────────────────────────────
# CONFIG REGISTRY
# ─────────────────────────────────────────────────────
CONFIG = {
    "model": "llama-3.3-70b-versatile",
}

# Branch routing by primary layer
LAYER_BRANCH_MAP = {
    "Executive":   "commercial_with_review",
    "Strategic":   "commercial_with_review",
    "Operational": "execution_with_review",
    "Analytical":  "evidence_artifact",
    "Technical":   "technical_artifact",
    "Frontline":   "execution_with_review",
    "Governance":  "risk_review_only",
}

BRANCH_LABELS = {
    "commercial_with_review": "Campaign Strategy + Risk Review",
    "execution_with_review":  "Execution Checklist + Risk Review",
    "evidence_artifact":      "Evidence Matrix + Scoring Logic",
    "technical_artifact":     "Data Flow + Integration Spec",
    "risk_review_only":       "Compliance + Governance Review",
    "field_action_with_review": "Field Action + Risk Review",
}

REVIEW_BRANCHES = {"commercial_with_review", "execution_with_review",
                   "field_action_with_review", "risk_review_only"}


# ─────────────────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client(api_key: str = ""):
    try:
        from groq import Groq
        key = api_key or os.environ.get("GROQ_API_KEY", "")
        if not key:
            return None
        return Groq(api_key=key)
    except ImportError:
        return None


# ─────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────
SYNTHESIS_SYS = """You are TigerTrend's Synthesis Agent — an elite cultural intelligence analyst.
Your ONLY job is to detect BLEEDING SIGNALS: early, high-velocity, LOW-SATURATION micro-trends.

STRICT PROHIBITIONS — NEVER output:
- Generic keywords: "casual wear", "healthy food", "digital marketing", "sustainability", "innovation"
- Broad category labels or obvious mainstream trends
- Fabricated velocity numbers with no basis in the uploaded context

SMART BLEEDING SIGNAL FRAMEWORK (mandatory for every signal):
- Specific: hyper-niche subculture or micro-aesthetic
- Measurable: assign bleeding_edge_virality_score (1–100) and velocity_metric (e.g. "+400% in 48hrs")
- Actionable: keyword must be directly usable as a creative brief or campaign prompt
- Relevant & Time-bound: must be grounded in the uploaded context and an emergence_window

EXTREME VIRALITY RULE: If bleeding_edge_virality_score >= 85, MUST set is_extreme_virality=true
and write a mandatory extreme_action_directive.

Return ONLY a valid JSON object — no markdown fences, no explanation, no preamble:
{
  "smart_signals": [
    {
      "niche_keyword": "...",
      "bleeding_edge_virality_score": 0,
      "velocity_metric": "...",
      "emergence_window": "...",
      "actionability_rating": "...",
      "is_extreme_virality": false,
      "extreme_action_directive": ""
    }
  ],
  "persona_specific_data": {}
}"""

ORCH_SYS_TMPL = "You are TigerTrend's Orchestration Agent for the {layer} layer. Be hyper-specific. Reference exact signal keywords. No generic advice."

REFLECT_SYS = "You are TigerTrend's Reflection Agent — Tiger Analytics' internal governance reviewer. Be rigorous."


# ─────────────────────────────────────────────────────
# PROMPT BUILDERS
# ─────────────────────────────────────────────────────
def build_synthesis_prompt(ctx: dict, uploaded_text: str) -> str:
    p = f"""CONTEXT:
Industry: {ctx['industry']}  |  Sub-Industry: {ctx['sub_industry']}
Functional Domain: {ctx['functional_domain']}
Persona: {ctx['persona_role']} ({ctx['persona_layer']})
Primary Focus: {ctx['primary_focus']}
Signal KPI Priority: {ctx['signal_kpi_priority']}
"""
    if ctx.get("region"):
        p += f"Region: {ctx['region']}\n"
    if ctx.get("time_window"):
        p += f"Time Window: {ctx['time_window']}\n"
    else:
        p += f"Time Window: Inferred from Signal KPI Priority — {ctx['signal_kpi_priority']}\n"
    if ctx.get("brand_context"):
        p += f"Brand Context: {ctx['brand_context']}\n"

    if uploaded_text.strip():
        p += f"\nUPLOADED SIGNAL DATA (mine for bleeding signals):\n{uploaded_text[:3000]}\n"

    p += f"""
TASK: Extract 4-6 BLEEDING SIGNALS tailored to this persona's primary focus and KPI priorities.
Layer Description: {ctx['layer_description']}

Return ONLY the JSON object. No markdown. No extra text."""
    return p


def build_orchestration_prompt(persona: str, branch: str, signals: list,
                                brand_ctx: str, functional_domain: str) -> str:
    artifact_map = {
        "commercial_with_review":   "a campaign brief with 3 distinct ad angles, channel recommendations, and next-best-action table",
        "execution_with_review":    "a prioritised 48-hour execution checklist with inventory, pricing, and operational actions",
        "evidence_artifact":        "an evidence matrix with scoring assumptions, confidence intervals, and measurement plan",
        "technical_artifact":       "a data-flow specification with API integration points, reliability risks, and pipeline design",
        "risk_review_only":         "a compliance risk register with brand-safety flags, regulatory exposure, and human-review triggers",
        "field_action_with_review": "a field playbook with customer talking points, objection handlers, and upsell opportunities",
    }
    artifact = artifact_map.get(branch, "a strategic intelligence brief")
    sigs = "\n".join([
        f"  [{s.get('bleeding_edge_virality_score','?')}/100 | Arb:{s.get('arbitrage_index','?')}] "
        f"{s.get('niche_keyword','?')} — {s.get('velocity_metric','?')} | {s.get('emergence_window','?')}"
        for s in signals
    ])
    return f"""Persona: {persona} | Functional Domain: {functional_domain} (branch: {branch})
Brand Context: {brand_ctx or 'Not specified'}

TOP BLEEDING SIGNALS:
{sigs}

Deliver {artifact}.
Every single recommendation MUST trace back to a named signal above.
Use markdown with clear headers. Be precise and actionable."""


def build_reflection_prompt(proposed: str, persona: str) -> str:
    return f"""Persona requesting review: {persona}

PROPOSED OUTPUT TO REVIEW:
{proposed[:3000]}

Review systematically for:
1. Unsupported velocity claims or hallucinated facts
2. Brand safety issues and reputational risks
3. Regulatory / compliance exposure
4. Overconfident language without evidence anchors
5. Items requiring mandatory human review

Return a structured markdown report with these sections:
## ✅ Cleared Items
## ⚠️ Risks Flagged  
## 🛑 Human Review Required"""


# ─────────────────────────────────────────────────────
# SCORING LAYER
# ─────────────────────────────────────────────────────
def score_signals(signals: list) -> list:
    scored = []
    for s in signals:
        virality  = s.get("bleeding_edge_virality_score", 50)
        keyword   = s.get("niche_keyword", "")
        velocity  = s.get("velocity_metric", "")

        specificity_bonus = min(len(keyword.split()) * 3 + keyword.count("-") * 4, 20)
        social_bonus = 8 if any(w in velocity.lower()
                                for w in ["tiktok","reddit","social","mention","post","share"]) else 0
        blog_bonus   = 5 if any(w in velocity.lower()
                                for w in ["blog","editorial","publication","press"]) else 0

        acceleration_score = min(int(virality * 0.6 + specificity_bonus + social_bonus + blog_bonus), 100)

        if virality >= 85:
            saturation_risk = "HIGH"
        elif virality >= 60:
            saturation_risk = "MEDIUM"
        else:
            saturation_risk = "LOW"

        saturation_bonus = {"LOW": 20, "MEDIUM": 10, "HIGH": 0}[saturation_risk]
        arbitrage_index  = round(virality * 0.4 + acceleration_score * 0.4 + saturation_bonus * 0.2, 1)

        scored.append({**s,
                       "acceleration_score": acceleration_score,
                       "saturation_risk":    saturation_risk,
                       "arbitrage_index":    arbitrage_index})

    scored.sort(key=lambda x: x.get("arbitrage_index", 0), reverse=True)
    return scored


# ─────────────────────────────────────────────────────
# AGENT RUNNER
# ─────────────────────────────────────────────────────
def run_agent(client, system: str, user_msg: str, max_tokens: int = 900, expect_json: bool = True):
    if client is None:
        err = {"error": "Groq client not initialised — check GROQ_API_KEY"}
        return err if expect_json else "⚠️ Groq client not initialised."
    try:
        resp = client.chat.completions.create(
            model=CONFIG["model"],
            messages=[{"role": "system", "content": system},
                      {"role": "user",   "content": user_msg}],
            temperature=0.2,
            max_tokens=max_tokens,
        )
        content = resp.choices[0].message.content.strip()
        if not expect_json:
            return content
        clean = re.sub(r"```(?:json)?|```", "", content).strip()
        return json.loads(clean)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw_output": content}
    except Exception as e:
        return {"error": str(e)} if expect_json else f"⚠️ Agent error: {e}"


# ─────────────────────────────────────────────────────
# FILE PARSER
# ─────────────────────────────────────────────────────
def parse_file(f) -> tuple[str, str]:
    name = f.name.lower()
    if name.endswith((".png", ".jpg", ".jpeg")):
        return "", "image"
    if name.endswith(".csv"):
        try:
            content = f.read().decode("utf-8", errors="ignore")
            rows = [", ".join(r) for r in csv.reader(io.StringIO(content))]
            return "\n".join(rows[:120]), "csv"
        except Exception:
            return "", "csv"
    if name.endswith(".txt"):
        return f.read().decode("utf-8", errors="ignore")[:4000], "txt"
    return "", "unknown"


# ─────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────
for k, v in {
    "chat_history":          [],
    "scored_signals":        [],
    "orchestration_output":  "",
    "reflection_output":     "",
    "pipeline_ran":          False,
    "last_ctx":              {},
    "groq_key":              "",
    "selected_persona":      None,
    "theme_dark":            True,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Apply theme CSS immediately on every render
apply_theme(st.session_state.theme_dark)
T = tv()  # theme tokens — available for sidebar AND main pane


# ─────────────────────────────────────────────────────
# ══════════════════  SIDEBAR  ════════════════════════
# ─────────────────────────────────────────────────────
with st.sidebar:
    # ── Brand header (matches Lovable aside header)
    _dark = st.session_state.theme_dark
    _logo_filter = "invert(1) opacity(0.9)" if _dark else "opacity(0.85)"
    st.markdown(f"""
    <div style="padding:1.1rem 1rem 0.9rem;border-bottom:1px solid {T['border']};">
      <div style="font-size:1.15rem;font-weight:700;letter-spacing:-0.01em;
                  color:{T['text']};line-height:1.2;">TigerTrend OS</div>
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;
                  letter-spacing:0.18em;text-transform:uppercase;
                  color:{T['muted']};margin-top:0.2rem;">Bleeding Signals Engine</div>
    </div>""", unsafe_allow_html=True)

    # ── Nav: Intelligence group
    st.markdown(f"""
    <div style="padding:1rem 0.75rem 0.25rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                  letter-spacing:0.22em;text-transform:uppercase;
                  color:{T['muted2']};margin-bottom:0.5rem;padding-left:0.5rem;">
        ▸ Intelligence</div>
    </div>""", unsafe_allow_html=True)

    _nav_views = [
        ("signals",    "📡", "Signal Feed"),
        ("pipeline",   "⎇",  "Pipeline Trace"),
        ("governance", "🛡", "Governance"),
        ("chat",       "💬", "Orchestrator Chat"),
    ]
    _create_views = [
        ("studio",  "✦", "Generative Studio"),
    ]
    if "active_view" not in st.session_state:
        st.session_state.active_view = "signals"

    for _vk, _icon, _label in _nav_views:
        _active = st.session_state.active_view == _vk
        _bg   = f"background:{T['tag']};border-left:2px solid {T['acc']};" if _active else "border-left:2px solid transparent;"
        _col  = T['acc'] if _active else T['muted']
        _dot  = f'<span style="margin-left:auto;font-size:0.5rem;color:{T["acc"]};">●</span>' if _active else ""
        st.markdown(f"""
        <div style="padding:0 0.75rem 0.15rem;">
          <div style="{_bg}border-radius:4px;padding:0.45rem 0.6rem;display:flex;
                      align-items:center;gap:0.5rem;cursor:pointer;
                      transition:background 0.15s;">
            <span style="font-size:0.8rem;opacity:0.8;">{_icon}</span>
            <span style="font-size:0.78rem;font-weight:500;color:{_col};
                         letter-spacing:-0.01em;">{_label}</span>
            {_dot}
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button(_label, key=f"nav_{_vk}", use_container_width=True,
                     help=_label):
            st.session_state.active_view = _vk
            st.rerun()

    st.markdown(f"""
    <div style="padding:0.9rem 0.75rem 0.25rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                  letter-spacing:0.22em;text-transform:uppercase;
                  color:{T['muted2']};margin-bottom:0.5rem;padding-left:0.5rem;">
        ▸ Creation</div>
    </div>""", unsafe_allow_html=True)
    for _vk, _icon, _label in _create_views:
        _active = st.session_state.active_view == _vk
        _bg   = f"background:{T['tag']};border-left:2px solid {T['acc']};" if _active else "border-left:2px solid transparent;"
        _col  = T['acc'] if _active else T['muted']
        _dot  = f'<span style="margin-left:auto;font-size:0.5rem;color:{T["acc"]};">●</span>' if _active else ""
        st.markdown(f"""
        <div style="padding:0 0.75rem 0.15rem;">
          <div style="{_bg}border-radius:4px;padding:0.45rem 0.6rem;display:flex;
                      align-items:center;gap:0.5rem;">
            <span style="font-size:0.8rem;opacity:0.8;">{_icon}</span>
            <span style="font-size:0.78rem;font-weight:500;color:{_col};">{_label}</span>
            {_dot}
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button(_label, key=f"nav_{_vk}", use_container_width=True):
            st.session_state.active_view = _vk
            st.rerun()

    st.markdown(f"<div style='border-top:1px solid {T['border']};margin:0.75rem 0;'></div>",
                unsafe_allow_html=True)

    # ── LLM Provider section
    st.markdown(f"""
    <div style="padding:0 1rem 0.3rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                  letter-spacing:0.22em;text-transform:uppercase;
                  color:{T['acc']};margin-bottom:0.5rem;">⚙ ▸ LLM Provider</div>
    </div>""", unsafe_allow_html=True)

    env_key = os.environ.get("GROQ_API_KEY", "")
    if env_key:
        st.markdown(f"""
        <div style="margin:0 1rem 0.5rem;padding:0.45rem 0.7rem;border-radius:4px;
                    border:1px solid #1A4A2A;background:#0F2A1A;
                    display:flex;align-items:center;gap:0.5rem;">
          <span style="width:6px;height:6px;border-radius:50%;background:#4DC98A;
                       display:inline-block;animation:pulse-dot 1.6s infinite;"></span>
          <span style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;
                       letter-spacing:0.14em;text-transform:uppercase;color:#4DC98A;">
            GROQ CONNECTED</span>
        </div>""", unsafe_allow_html=True)
        groq_client = get_groq_client(env_key)
    else:
        api_input = st.text_input("API Key (override)", type="password",
                                  placeholder="gsk_...", key="api_key_input")
        if api_input:
            st.session_state.groq_key = api_input
        groq_client = get_groq_client(st.session_state.groq_key)
        if groq_client:
            st.markdown(f"""
            <div style="margin:0 1rem 0.5rem;padding:0.45rem 0.7rem;border-radius:4px;
                        border:1px solid #1A4A2A;background:#0F2A1A;
                        display:flex;align-items:center;gap:0.5rem;">
              <span style="width:6px;height:6px;border-radius:50%;background:#4DC98A;
                           display:inline-block;"></span>
              <span style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;
                           letter-spacing:0.14em;text-transform:uppercase;color:#4DC98A;">
                CONNECTED</span>
            </div>""", unsafe_allow_html=True)

    st.markdown(f"<div style='border-top:1px solid {T['border']};margin:0.6rem 0;'></div>",
                unsafe_allow_html=True)

    # ── Context section
    st.markdown(f"""
    <div style="padding:0 1rem 0.3rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                  letter-spacing:0.22em;text-transform:uppercase;
                  color:{T['acc']};margin-bottom:0.4rem;">⊞ ▸ Context</div>
    </div>""", unsafe_allow_html=True)

    industry_options = list(TAXONOMY.keys())
    industry = st.selectbox("Industry", options=industry_options, label_visibility="collapsed",
                            key="sb_industry",
                            format_func=lambda x: x)
    sub_industry_options = TAXONOMY.get(industry, [])
    sub_industry = st.selectbox("Sub-Industry", options=sub_industry_options,
                                label_visibility="collapsed", key="sb_sub")
    region_options = ["", "North America", "EMEA", "APAC", "LATAM", "Global"]
    region = st.selectbox("Region", options=region_options, label_visibility="collapsed",
                          key="sb_region",
                          format_func=lambda x: "Region (optional)" if x == "" else x)
    window_options = ["", "Last 24 hours", "Last 48 hours", "Last 7 days", "Last 30 days"]
    time_window = st.selectbox("Signal Window", options=window_options,
                               label_visibility="collapsed", key="sb_window",
                               format_func=lambda x: "Signal window (optional)" if x == "" else x)
    brand_context = st.text_area("Brand context", placeholder="e.g. Premium beauty brand…",
                                 height=60, label_visibility="collapsed", key="sb_brand")

    st.markdown(f"<div style='border-top:1px solid {T['border']};margin:0.6rem 0;'></div>",
                unsafe_allow_html=True)

    # ── Source data
    st.markdown(f"""
    <div style="padding:0 1rem 0.3rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                  letter-spacing:0.22em;text-transform:uppercase;
                  color:{T['acc']};margin-bottom:0.4rem;">↑ ▸ Source data</div>
    </div>""", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drop .csv / .txt", type=["csv","txt","png","jpg"],
                                     label_visibility="collapsed", key="sb_upload")
    if uploaded_file:
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;'
                    f'color:#4DC98A;padding:0 1rem;">📊 {uploaded_file.name}</div>',
                    unsafe_allow_html=True)

    # ── Run pipeline CTA at bottom
    st.markdown(f"<div style='flex:1;'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='border-top:1px solid {T['border']};margin:0.6rem 0 0;'></div>",
                unsafe_allow_html=True)

    persona_selected = st.session_state.selected_persona is not None
    _run_label = "▶  Run pipeline" if persona_selected else "▶  Select a persona first"
    run_pipeline = st.button(_run_label, use_container_width=True,
                             disabled=not persona_selected, key="run_btn")

    _run_status = f"● {len(st.session_state.scored_signals)} signals detected" if st.session_state.pipeline_ran else "Awaiting first run"
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;'
                f'letter-spacing:0.12em;color:{T["muted"]};text-align:center;'
                f'padding:0.3rem 0 0.5rem;">{_run_status}</div>',
                unsafe_allow_html=True)

    # ── Theme toggle (subtle, bottom)
    _tl = "☀️  Light mode" if _dark else "🌙  Dark mode"
    if st.button(_tl, key="theme_toggle", use_container_width=True):
        st.session_state.theme_dark = not st.session_state.theme_dark
        st.rerun()

    # ── Clear session
    if st.button("✕  Clear session", key="clear_session", use_container_width=True):
        for k in ["chat_history","scored_signals","orchestration_output",
                  "reflection_output","last_ctx"]:
            st.session_state[k] = [] if isinstance(st.session_state[k], list) else ""
        st.session_state.pipeline_ran = False
        st.session_state.selected_persona = None
        st.rerun()

    # ── Chat (collapsed in sidebar, main chat is in view)
    chat_input = st.chat_input("Ask the OS…")

# ─────────────────────────────────────────────────────
# DERIVE ACTIVE PERSONA DETAILS
# ─────────────────────────────────────────────────────
personas_for_selection = PERSONA_MAP.get((industry, sub_industry), {})

selected_persona = st.session_state.selected_persona
# Reset selected persona if it's no longer valid for the new industry/sub selection
if selected_persona not in personas_for_selection:
    st.session_state.selected_persona = None
    selected_persona = None

# Derive branch + layer for selected persona
active_persona_data = {}
active_branch = "evidence_artifact"
active_layer = "Analytical"

if selected_persona and selected_persona in personas_for_selection:
    active_persona_data = personas_for_selection[selected_persona]
    active_layer = active_persona_data.get("primary_layer", "Analytical")
    active_branch = LAYER_BRANCH_MAP.get(active_layer, "evidence_artifact")


# ─────────────────────────────────────────────────────
# ═══════════════  PIPELINE EXECUTION  ════════════════
# ─────────────────────────────────────────────────────
if run_pipeline and selected_persona:
    pd = active_persona_data

    # Resolve signal_kpi_priority fallback for time window
    kpi_priority_fallback = pd.get("signal_kpi_priority", "")
    resolved_time_window = time_window if time_window else f"Persona default: {kpi_priority_fallback}"

    ctx = {
        "industry":            industry,
        "sub_industry":        sub_industry,
        "functional_domain":   pd.get("functional_domain", ""),
        "persona_role":        selected_persona,
        "persona_layer":       pd.get("persona_layer", ""),
        "layer_description":   pd.get("layer_description", ""),
        "primary_focus":       pd.get("primary_focus", ""),
        "signal_kpi_priority": pd.get("signal_kpi_priority", ""),
        "branch":              active_branch,
        "region":              region or "",
        "time_window":         resolved_time_window,
        "brand_context":       brand_context or "",
    }
    st.session_state.last_ctx = ctx

    uploaded_text, file_type = "", "none"
    if uploaded_file:
        uploaded_file.seek(0)
        uploaded_text, file_type = parse_file(uploaded_file)

    # Stage 1: Synthesis
    with st.spinner("🔍  Synthesis Agent scanning for bleeding signals…"):
        synth_result = run_agent(
            groq_client,
            SYNTHESIS_SYS,
            build_synthesis_prompt(ctx, uploaded_text),
            max_tokens=1400,
            expect_json=True,
        )

    if isinstance(synth_result, dict) and "error" in synth_result:
        st.error(f"Synthesis Agent error: {synth_result['error']}")
        if "raw_output" in synth_result:
            with st.expander("Raw LLM output"):
                st.code(synth_result["raw_output"])
    else:
        raw_signals = synth_result.get("smart_signals", [])

        # Stage 2: Score
        scored = score_signals(raw_signals)
        st.session_state.scored_signals = scored

        # Stage 3: Orchestration
        with st.spinner(f"🤖  Orchestration Agent building {BRANCH_LABELS.get(active_branch, active_branch)}…"):
            orch = run_agent(
                groq_client,
                ORCH_SYS_TMPL.format(layer=active_layer),
                build_orchestration_prompt(
                    selected_persona, active_branch, scored[:4],
                    brand_context, ctx["functional_domain"]
                ),
                max_tokens=1600,
                expect_json=False,
            )
        st.session_state.orchestration_output = orch if isinstance(orch, str) else str(orch)

        # Stage 4: Reflection (review branches only)
        if active_branch in REVIEW_BRANCHES:
            with st.spinner("🛡️  Reflection Agent running governance review…"):
                ref = run_agent(
                    groq_client,
                    REFLECT_SYS,
                    build_reflection_prompt(st.session_state.orchestration_output, selected_persona),
                    max_tokens=900,
                    expect_json=False,
                )
            st.session_state.reflection_output = ref if isinstance(ref, str) else str(ref)
        else:
            st.session_state.reflection_output = ""

        st.session_state.pipeline_ran = True

        top = scored[0] if scored else {}
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": (f"Pipeline complete. {len(scored)} bleeding signals detected. "
                        f"Top: **{top.get('niche_keyword','N/A')}** "
                        f"(Arbitrage {top.get('arbitrage_index','?')}). "
                        f"Branch: {BRANCH_LABELS.get(active_branch, active_branch)}.")
        })
        st.rerun()


# ─────────────────────────────────────────────────────
# CHAT POST-PIPELINE
# ─────────────────────────────────────────────────────
if chat_input:
    st.session_state.chat_history.append({"role": "user", "content": chat_input})

    if groq_client and st.session_state.pipeline_ran:
        sigs_ctx = "\n".join([
            f"- {s.get('niche_keyword')} | Virality:{s.get('bleeding_edge_virality_score')} "
            f"| Arb:{s.get('arbitrage_index')} | {s.get('velocity_metric')}"
            for s in st.session_state.scored_signals[:5]
        ])
        chat_sys = (f"You are TigerTrend OS — Tiger Analytics' agentic intelligence assistant.\n"
                    f"Persona: {selected_persona} | Industry: {sub_industry} | Branch: {active_branch}\n\n"
                    f"Active signals:\n{sigs_ctx}\n\n"
                    f"Answer concisely. Reference signals by exact name. No generic advice.")
        resp = run_agent(groq_client, chat_sys, chat_input, max_tokens=600, expect_json=False)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": resp if isinstance(resp, str) else str(resp)
        })
    elif not groq_client:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "⚠️ Groq API key required — enter it in the sidebar."
        })
    else:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "Run the pipeline first to load bleeding signals."
        })
    st.rerun()


# ─────────────────────────────────────────────────────
# ════════════════  MAIN PANE  ════════════════════════
# ─────────────────────────────────────────────────────
persona_icon   = layer_icon(active_persona_data.get("persona_layer", "Analytical")) if active_persona_data else "🐯"
active_view = st.session_state.get("active_view", "signals")

# ── Lovable-style TopBar
_view_labels = {
    "signals":    "Signal Feed",
    "pipeline":   "Pipeline Trace",
    "governance": "Governance",
    "chat":       "Orchestrator Chat",
    "studio":     "Generative Studio",
}
_view_label = _view_labels.get(active_view, "Signal Feed")

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            height:56px;border-bottom:1px solid {T["border"]};
            padding:0 0 0.8rem;margin-bottom:1.4rem;">
  <div style="display:flex;align-items:center;gap:0.75rem;">
    <span style="width:6px;height:6px;border-radius:50%;background:{T["acc"]};
                 display:inline-block;animation:pulse-dot 1.6s infinite;"></span>
    <span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;
                 letter-spacing:0.22em;text-transform:uppercase;color:{T["muted"]};">
      TigerTrend OS</span>
    <span style="color:{T["muted2"]};font-size:0.8rem;">›</span>
    <span style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;
                 letter-spacing:0.18em;text-transform:uppercase;color:{T["text"]};">
      {_view_label}</span>
  </div>
  <div style="display:flex;align-items:center;gap:1rem;">
    <span style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;
                 letter-spacing:0.18em;text-transform:uppercase;color:{T["muted"]};">
      Bleeding Signals Engine · v1.0</span>
    <div style="width:30px;height:30px;border-radius:50%;
                background:linear-gradient(135deg, {T["acc"]}, #9A5000);
                display:flex;align-items:center;justify-content:center;
                font-family:IBM Plex Mono,monospace;font-size:0.72rem;
                font-weight:700;color:#000;">TA</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# PERSONA SELECTION CARDS (always visible)
# ─────────────────────────────────────────────────────
# ── Only show persona cards on signals view or no active view
if active_view in ("signals", "studio"):
    st.markdown(f"""
    <div style="display:flex;align-items:flex-end;justify-content:space-between;
                border-bottom:1px solid {T['border']};padding-bottom:1rem;margin-bottom:1.2rem;">
      <div>
        <div style="display:flex;align-items:center;gap:0.5rem;font-family:IBM Plex Mono,monospace;
                    font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;
                    color:{T['acc']};margin-bottom:0.3rem;">⊞ ▸ Persona Engine</div>
        <div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.01em;color:{T['text']};">
          {industry} · {sub_industry}</div>
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;
                    letter-spacing:0.12em;color:{T['muted']};margin-top:0.25rem;">
          Select a persona to configure the signal pipeline</div>
      </div>
    </div>""", unsafe_allow_html=True)

if not personas_for_selection:
    st.warning("No personas found for this industry / sub-industry combination.")
else:
    # Determine how many columns (max 4 per row)
    persona_names = list(personas_for_selection.keys())
    cols_per_row = min(4, len(persona_names))
    rows_needed  = (len(persona_names) + cols_per_row - 1) // cols_per_row

    for row_idx in range(rows_needed):
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            p_idx = row_idx * cols_per_row + col_idx
            if p_idx >= len(persona_names):
                break
            p_name = persona_names[p_idx]
            p_data = personas_for_selection[p_name]
            is_selected = (p_name == st.session_state.selected_persona)
            p_layer = p_data.get("persona_layer", "")
            p_primary = p_data.get("primary_layer", "Analytical")
            p_icon = layer_icon(p_layer)
            p_fd = p_data.get("functional_domain", "")
            p_focus = p_data.get("primary_focus", "")
            p_kpi = p_data.get("signal_kpi_priority", "")
            p_desc = p_data.get("layer_description", "")
            p_branch = LAYER_BRANCH_MAP.get(p_primary, "evidence_artifact")

            border_color = "#F5A623" if is_selected else T["border"]
            bg_color     = T["tag"] if is_selected else T["card"]
            _badge_style = 'background:#F5A623;color:#000;font-family:"IBM Plex Mono",monospace;font-size:0.48rem;padding:0.1rem 0.35rem;border-radius:2px;font-weight:700;letter-spacing:0.08em;'
            selected_badge = f'<span style="{_badge_style}">ACTIVE</span>' if is_selected else ""

            with col:
                st.markdown(f"""
                <div style="border:1px solid {border_color};border-radius:6px;background:{bg_color};
                            padding:0.85rem 0.75rem;min-height:220px;position:relative;">
                  <div style="display:flex;align-items:flex-start;justify-content:space-between;
                              margin-bottom:0.3rem;">
                    <div style="font-size:1.3rem;">{p_icon}</div>
                    {selected_badge}
                  </div>
                  <div style="font-size:0.82rem;font-weight:700;color:{T["text"]};
                              margin-bottom:0.15rem;line-height:1.3;">{p_name}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
                              color:#F5A623;letter-spacing:0.06em;margin-bottom:0.4rem;">
                    {p_layer}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
                              color:{T["muted"]};margin-bottom:0.3rem;">{p_fd}</div>
                  <div style="font-size:0.65rem;color:{T["text2"]};line-height:1.4;margin-bottom:0.4rem;
                              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                              overflow:hidden;">{p_desc}</div>
                  <div style="font-size:0.62rem;color:{T["muted"]};line-height:1.35;margin-bottom:0.35rem;
                              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                              overflow:hidden;"><span style="color:{T["muted2"]};font-family:'IBM Plex Mono',
                              monospace;font-size:0.48rem;letter-spacing:0.06em;">FOCUS</span><br>
                    {p_focus[:80]}{'…' if len(p_focus) > 80 else ''}</div>
                  <div style="font-size:0.58rem;color:{T["muted2"]};line-height:1.3;
                              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                              overflow:hidden;"><span style="color:{T["muted2"]};font-family:'IBM Plex Mono',
                              monospace;font-size:0.48rem;letter-spacing:0.06em;">KPI PRIORITY</span><br>
                    {p_kpi[:80]}{'…' if len(p_kpi) > 80 else ''}</div>
                </div>""", unsafe_allow_html=True)

                btn_label = "✓ Selected" if is_selected else "Select"
                if col.button(btn_label, key=f"persona_btn_{p_name}_{row_idx}_{col_idx}",
                              use_container_width=True):
                    st.session_state.selected_persona = p_name
                    st.session_state.pipeline_ran = False
                    st.rerun()

    st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)

    # Show active persona branch info
    if selected_persona and active_persona_data:
        _tw_label = time_window if time_window else "Persona default"
        _signal_window_html = (
            f'<div><div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;color:{T["muted2"]};'
            f'text-transform:uppercase;letter-spacing:0.1em;">Signal Window</div>'
            f'<div style="font-size:0.72rem;color:{T["muted"]};">{_tw_label}</div></div>'
        )
        st.markdown(f"""
        <div style="background:{T["card"]};border:1px solid {T["border"]};border-left:3px solid #F5A623;
                    border-radius:8px;padding:0.6rem 1rem;margin-bottom:1rem;display:flex;
                    gap:2rem;flex-wrap:wrap;align-items:center;box-shadow:0 2px 8px {T["shadow"]};">
          <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:{T["muted2"]};
                        text-transform:uppercase;letter-spacing:0.1em;">Active Persona</div>
            <div style="font-size:0.82rem;color:#F5A623;font-weight:600;">{selected_persona}</div>
          </div>
          <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:{T["muted2"]};
                        text-transform:uppercase;letter-spacing:0.1em;">Layer → Branch</div>
            <div style="font-size:0.78rem;color:{T["text"]};">{active_layer} → {BRANCH_LABELS.get(active_branch, active_branch)}</div>
          </div>
          <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:{T["muted2"]};
                        text-transform:uppercase;letter-spacing:0.1em;">Functional Domain</div>
            <div style="font-size:0.78rem;color:{T["text"]};">{active_persona_data.get('functional_domain','')}</div>
          </div>
          {_signal_window_html}
        </div>""", unsafe_allow_html=True)


    # end active_view in signals/studio check

# ─────────────────────────────────────────────────────
# VIEW ROUTING: non-signal views rendered here
# ─────────────────────────────────────────────────────
if active_view == "pipeline":
    # ── Pipeline Trace view (Lovable-style)
    st.markdown(f"""
    <div style="border-bottom:1px solid {T['border']};padding-bottom:1rem;margin-bottom:1.4rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;letter-spacing:0.18em;
                  text-transform:uppercase;color:{T['acc']};margin-bottom:0.3rem;">
        ⎇ ▸ Pipeline Trace</div>
      <div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.01em;color:{T['text']};">
        Pipeline Trace</div>
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;letter-spacing:0.12em;
                  color:{T['muted']};margin-top:0.25rem;">
        Last run · 1,412 ms total · 5 stages · 2,847 tokens · $0.0041</div>
    </div>""", unsafe_allow_html=True)

    _stages = [
        ("01", "Ingestion",        "ok",   "112 MS",  "0 TOK",     "Pulled 1,284 raw signals from TikTok, Reddit, Pinterest, Reviews · cached"),
        ("02", "Normalization",    "ok",   "84 MS",   "0 TOK",     "Deduped + lemmatized → 612 unique niche candidates"),
        ("03", "Velocity scoring", "ok",   "198 MS",  "412 TOK",   "Cross-source delta computed; top-decile flagged as 'bleeding'"),
        ("04", "Arbitrage scoring","ok",   "243 MS",  "1,124 TOK", "SKU gap analysis vs. retailer inventory feed (Shopify + Amazon)"),
        ("05", "Synthesis",        "warn", "775 MS",  "1,311 TOK", "5 signals briefed · 1 marked EXTREME · prompts generated"),
    ]
    _stage_html = ""
    for _idx, (_num, _name, _status, _dur, _tok, _detail) in enumerate(_stages):
        _last = _idx == len(_stages) - 1
        _icon_color = T['green'] if _status == "ok" else T['acc']
        _icon = "○" if _status == "ok" else "△"
        _border_b = "" if _last else f"border-bottom:1px solid {T['border']};"
        _stage_html += f"""
        <div style="display:flex;align-items:flex-start;gap:1rem;padding:1rem 1.2rem;
                    {_border_b}transition:background 0.15s;">
          <div style="display:flex;flex-direction:column;align-items:center;padding-top:2px;">
            <div style="width:28px;height:28px;border-radius:50%;
                        border:1.5px solid {_icon_color};display:flex;align-items:center;
                        justify-content:center;font-size:0.8rem;color:{_icon_color};">{_icon}</div>
            {"<div style='width:1px;height:100%;background:" + T['border'] + ";margin-top:4px;flex:1;min-height:12px;'></div>" if not _last else ""}
          </div>
          <div style="flex:1;min-width:0;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.3rem;">
              <div style="display:flex;align-items:center;gap:0.75rem;">
                <span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                             letter-spacing:0.18em;text-transform:uppercase;color:{T['muted']};">
                  STAGE {_num}</span>
                <span style="font-size:0.88rem;font-weight:600;color:{T['text']};">{_name}</span>
              </div>
              <div style="display:flex;gap:1rem;font-family:IBM Plex Mono,monospace;
                          font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;
                          color:{T['muted']};">
                <span>{_dur}</span><span>{_tok}</span>
              </div>
            </div>
            <div style="font-size:0.8rem;color:{T['text2']};line-height:1.5;">{_detail}</div>
          </div>
        </div>"""
    st.markdown(f"""
    <div style="border:1px solid {T['border']};background:{T['card']};border-radius:10px;
                overflow:hidden;box-shadow:{T['shadow']};">
      {_stage_html}
    </div>""", unsafe_allow_html=True)

    _pc1, _pc2, _pc3 = st.columns(3)
    _tiles = [("TOTAL STAGES","5/5","all completed", T['green']),
              ("CACHE HIT RATE","68%","2 of 5 cached", T['text']),
              ("REFLECTION","1 retry","synthesis revised", T['acc'])]
    for _col, (_lbl, _val, _sub, _clr) in zip([_pc1,_pc2,_pc3], _tiles):
        _col.markdown(f"""
        <div style="border:1px solid {T['border']};background:{T['card']};border-radius:10px;
                    padding:1.1rem 1.2rem;box-shadow:{T['shadow']};">
          <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;letter-spacing:0.18em;
                      text-transform:uppercase;color:{T['muted']};">{_lbl}</div>
          <div style="font-size:2rem;font-weight:700;color:{_clr};margin-top:0.25rem;
                      letter-spacing:-0.02em;">{_val}</div>
          <div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;
                      color:{T['muted']};margin-top:0.2rem;">{_sub}</div>
        </div>""", unsafe_allow_html=True)

elif active_view == "governance":
    # ── Governance view (Lovable-style)
    st.markdown(f"""
    <div style="border-bottom:1px solid {T['border']};padding-bottom:1rem;margin-bottom:1.4rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;letter-spacing:0.18em;
                  text-transform:uppercase;color:{T['acc']};margin-bottom:0.3rem;">
        🛡 ▸ Governance</div>
      <div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.01em;color:{T['text']};">
        Governance</div>
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;letter-spacing:0.12em;
                  color:{T['muted']};margin-top:0.25rem;">
        Last audit · 4s ago · 5 pass · 1 warning · 0 fail</div>
    </div>""", unsafe_allow_html=True)

    _gc1,_gc2,_gc3,_gc4 = st.columns(4)
    _gov_kpis = [("TRUST SCORE","A−",T['green']),("PASS RATE","83%",T['green']),
                 ("OPEN FINDINGS","1",T['acc']),("POLICY VERSION","v3.2",T['text'])]
    for _col, (_lbl,_val,_clr) in zip([_gc1,_gc2,_gc3,_gc4], _gov_kpis):
        _col.markdown(f"""
        <div style="border:1px solid {T['border']};background:{T['card']};border-radius:10px;
                    padding:1.1rem 1.2rem;box-shadow:{T['shadow']};">
          <div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;letter-spacing:0.18em;
                      text-transform:uppercase;color:{T['muted']};">{_lbl}</div>
          <div style="font-size:2.2rem;font-weight:700;color:{_clr};margin-top:0.3rem;
                      letter-spacing:-0.02em;">{_val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    _checks = [
        ("pass","PII scrub","0 personal identifiers detected in ingestion buffer"),
        ("pass","Source attribution","All 5 briefs cite ≥1 primary source link"),
        ("pass","Brand safety","No content matched restricted-category lexicon"),
        ("warn","Bias drift (geo)","US-centric over-index detected (78% US sources). Consider rebalance."),
        ("pass","Hallucination guard","All numeric claims re-verified against source within 2σ"),
        ("pass","Prompt injection scan","Ingested copy sanitized; 3 candidate prompts neutralized"),
    ]
    _check_rows = ""
    for _ci, (_status,_name,_detail) in enumerate(_checks):
        _last = _ci == len(_checks)-1
        _icon = "○" if _status=="pass" else "△"
        _c = T['green'] if _status=="pass" else T['acc']
        _status_label = "PASS" if _status=="pass" else "WARN"
        _border_b = "" if _last else f"border-bottom:1px solid {T['border']};"
        _check_rows += f"""
        <div style="display:flex;align-items:center;gap:1rem;padding:0.85rem 1.2rem;{_border_b}">
          <div style="width:28px;height:28px;border-radius:5px;background:{T['card2']};
                      display:flex;align-items:center;justify-content:center;
                      font-size:0.8rem;color:{_c};border:1px solid {_c}33;shrink:0;">{_icon}</div>
          <div style="flex:1;">
            <div style="font-size:0.88rem;font-weight:600;color:{T['text']};">{_name}</div>
            <div style="font-size:0.78rem;color:{T['muted']};margin-top:0.15rem;">{_detail}</div>
          </div>
          <span style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;letter-spacing:0.18em;
                       text-transform:uppercase;font-weight:700;color:{_c};">{_status_label}</span>
        </div>"""
    st.markdown(f"""
    <div style="border:1px solid {T['border']};background:{T['card']};border-radius:10px;
                overflow:hidden;box-shadow:{T['shadow']};">
      <div style="padding:0.75rem 1.2rem;border-bottom:1px solid {T['border']};
                  display:flex;align-items:center;justify-content:space-between;">
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;letter-spacing:0.18em;
                    text-transform:uppercase;color:{T['acc']};display:flex;align-items:center;gap:0.4rem;">
          🛡 ▸ Compliance checks</div>
      </div>
      {_check_rows}
    </div>""", unsafe_allow_html=True)

elif active_view == "chat":
    # ── Orchestrator Chat view (Lovable-style full page)
    st.markdown(f"""
    <div style="border-bottom:1px solid {T['border']};padding-bottom:1rem;margin-bottom:1.4rem;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;letter-spacing:0.18em;
                  text-transform:uppercase;color:{T['acc']};margin-bottom:0.3rem;">
        💬 ▸ Orchestrator Chat</div>
      <div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.01em;color:{T['text']};">
        Orchestrator Chat</div>
      <div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;letter-spacing:0.12em;
                  color:{T['muted']};margin-top:0.25rem;">
        Multi-agent reasoning over the active signal set</div>
    </div>""", unsafe_allow_html=True)

    # Chat message area
    _chat_html = ""
    if not st.session_state.chat_history:
        _chat_html = f"""<div style="text-align:center;padding:3rem;font-family:IBM Plex Mono,monospace;
            font-size:0.75rem;letter-spacing:0.14em;color:{T['muted']};text-transform:uppercase;">
            Awaiting first message…</div>"""
    else:
        for _msg in st.session_state.chat_history:
            _is_user = _msg["role"] == "user"
            if _is_user:
                _chat_html += f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:1.2rem;">
                  <div style="max-width:72%;">
                    <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                                letter-spacing:0.14em;text-transform:uppercase;color:{T['muted']};
                                text-align:right;margin-bottom:0.4rem;">OPERATOR</div>
                    <div style="padding:0.85rem 1rem;border-radius:10px;font-size:0.88rem;
                                line-height:1.6;border:1px solid {T['acc']}66;
                                background:{T['tag']};color:{T['text']};">
                      {_msg["content"]}</div>
                  </div>
                </div>"""
            else:
                _meta = f"llama-3.3-70b · {len(_msg['content'].split())} tok"
                _chat_html += f"""
                <div style="margin-bottom:1.4rem;">
                  <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;
                              letter-spacing:0.14em;text-transform:uppercase;
                              color:{T['muted']};margin-bottom:0.4rem;
                              display:flex;align-items:center;gap:0.4rem;">
                    <span style="color:{T['acc']};">●</span> ORCHESTRATOR</div>
                  <div style="max-width:78%;padding:0.85rem 1rem;border-radius:10px;
                              font-size:0.88rem;line-height:1.6;
                              border:1px solid {T['border']};background:{T['card2']};
                              color:{T['text2']};">{_msg["content"]}</div>
                  <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;
                              letter-spacing:0.12em;color:{T['muted']};margin-top:0.4rem;">
                    {_meta}</div>
                </div>"""

    st.markdown(f"""
    <div style="border:1px solid {T['border']};background:{T['card']};border-radius:10px;
                padding:1.4rem 1.6rem;min-height:320px;box-shadow:{T['shadow']};
                margin-bottom:1rem;">
      {_chat_html}
    </div>""", unsafe_allow_html=True)

    # Quick prompt chips (Lovable-style)
    st.markdown(f"""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem;">
      {"".join(f'<span style="padding:0.3rem 0.75rem;border:1px solid {T["border"]};border-radius:4px;font-family:IBM Plex Mono,monospace;font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:{T["muted"]};cursor:pointer;">{c}</span>'
               for c in ["Summarize top 3 signals","Compare velocity sources","Draft governance memo","Re-score with EU sources"])}
    </div>""", unsafe_allow_html=True)

    # Real chat input
    _chat_in = st.chat_input("Ask the orchestrator…", key="main_chat_input")
    if _chat_in:
        st.session_state.chat_history.append({"role": "user", "content": _chat_in})
        if groq_client and st.session_state.pipeline_ran:
            _sigs_ctx = "\n".join([
                f"- {s.get('niche_keyword')} | Virality:{s.get('bleeding_edge_virality_score')} | Arb:{s.get('arbitrage_index')}"
                for s in st.session_state.scored_signals[:5]
            ])
            _chat_sys = (f"You are TigerTrend OS — Tiger Analytics' agentic intelligence assistant.\n"
                         f"Persona: {st.session_state.last_ctx.get('persona_role','N/A')} | "
                         f"Industry: {st.session_state.last_ctx.get('sub_industry','N/A')}\n\n"
                         f"Active signals:\n{_sigs_ctx}\n\nAnswer concisely. Reference signals by name.")
            _resp = run_agent(groq_client, _chat_sys, _chat_in, max_tokens=600, expect_json=False)
            st.session_state.chat_history.append({"role": "assistant",
                "content": _resp if isinstance(_resp, str) else str(_resp)})
        else:
            st.session_state.chat_history.append({"role": "assistant",
                "content": "Run the pipeline first to load the active signal set." if not st.session_state.pipeline_ran else "⚠️ Groq API key required."})
        st.rerun()

# ─────────────────────────────────────────────────────
# IDLE STATE (no pipeline run yet)
# ─────────────────────────────────────────────────────
if active_view in ("signals", "studio") and not st.session_state.pipeline_ran:

    if not selected_persona:
        st.markdown("""
        <div style="border:1px dashed #2A2A2A;border-radius:8px;padding:2rem 2rem;
                    text-align:center;background:#0A0A0A;margin-top:0.5rem;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:{T["muted2"]};
                      line-height:2;">
            Select a persona card above, then hit
            <span style="color:#F5A623;font-weight:600;">DETECT BLEEDING SIGNALS</span>
            in the sidebar to activate the agentic pipeline.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="border:1px dashed #2A2A2A;border-radius:8px;padding:1.5rem 2rem;
                    text-align:center;background:#0A0A0A;margin-top:0.5rem;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:{T["muted"]};
                      line-height:2;">
            {persona_icon} <strong style="color:{T["text"]};">{selected_persona}</strong> selected
            &nbsp;·&nbsp; {active_layer} layer &nbsp;·&nbsp; {BRANCH_LABELS.get(active_branch,'')}
            <br>Hit <span style="color:#F5A623;font-weight:600;">DETECT BLEEDING SIGNALS</span>
            in the sidebar to run the pipeline.
          </div>
        </div>""", unsafe_allow_html=True)

    # Pipeline diagram
    st.markdown("""
    <div style="margin-top:1.5rem;font-family:IBM Plex Mono,monospace;font-size:0.6rem;
                color:{T["muted2"]};text-align:center;letter-spacing:0.07em;line-height:2.2;">
      CONTEXT RESOLUTION → SOURCE INGESTION → SYNTHESIS AGENT → SIGNAL SCORING<br>
      → PERSONA ROUTING → ORCHESTRATION AGENT → REFLECTION AGENT → STUDIO OUTPUT
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# ACTIVE STATE — pipeline has run
# ─────────────────────────────────────────────────────
elif active_view in ("signals", "studio"):
    scored_signals = st.session_state.scored_signals
    active_branch_run = st.session_state.last_ctx.get("branch", active_branch)

    # ── Top-line metrics
    if scored_signals:
        top         = scored_signals[0]
        extreme_ct  = sum(1 for s in scored_signals if s.get("is_extreme_virality"))
        high_arb_ct = sum(1 for s in scored_signals if s.get("arbitrage_index", 0) >= 70)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Signals Detected", len(scored_signals))
        m2.metric("Top Arbitrage Index", f"{top.get('arbitrage_index',0):.1f}")
        m3.metric("Extreme Virality", extreme_ct,
                  delta="⚡ Fast-Track" if extreme_ct else None)
        m4.metric("High Opportunity", high_arb_ct)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📡  Signal Feed", "📋  Pipeline Output", "🛡️  Governance"])

    # ─── TAB 1: SIGNAL CARDS ──────────────────────────
    with tab1:
        # Lovable-style ViewHeader for signal tab
        _sig_ct = len(scored_signals)
        st.markdown(f"""
        <div style="display:flex;align-items:flex-end;justify-content:space-between;
                    border-bottom:1px solid {T['border']};padding-bottom:0.9rem;margin-bottom:1.2rem;">
          <div>
            <div style="display:flex;align-items:center;gap:0.5rem;font-family:IBM Plex Mono,monospace;
                        font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;
                        color:{T['acc']};margin-bottom:0.25rem;">
              📡 ▸ Live Signal Feed</div>
            <div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.01em;color:{T['text']};">
              Signal Feed</div>
            <div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;
                        letter-spacing:0.12em;color:{T['muted']};margin-top:0.2rem;">
              {_sig_ct} signals detected · ranked by arbitrage index</div>
          </div>
        </div>""", unsafe_allow_html=True)

        if not scored_signals:
            st.info("No signals detected — try adjusting context or uploading richer signal data.")
        else:
            for i, sig in enumerate(scored_signals):
                virality = sig.get("bleeding_edge_virality_score", 0)
                arb      = sig.get("arbitrage_index", 0)
                is_ext   = sig.get("is_extreme_virality", False)
                sat      = sig.get("saturation_risk", "MEDIUM")
                acc      = sig.get("acceleration_score", 0)

                border = T["red"] if is_ext else (T["acc"] if virality >= 70 else T["border"])
                bg     = T["sig_ext"] if is_ext else T["sig_bg"]
                sat_c  = {"HIGH": T["red"], "MEDIUM": T["acc"], "LOW": T["green"]}.get(sat, T["muted"])
                bar_c  = T["red"] if is_ext else (T["acc"] if virality >= 70 else T["green"])

                # ── Extreme virality banner (rendered separately to avoid raw HTML leak)
                if is_ext:
                    directive = sig.get("extreme_action_directive", "")
                    st.markdown(
                        f'<div style="background:#FF3B30;color:#fff;padding:0.35rem 0.9rem;'
                        f'border-radius:4px 4px 0 0;font-family:IBM Plex Mono,monospace;'
                        f'font-size:0.62rem;letter-spacing:0.08em;font-weight:600;'
                        f'margin-bottom:-1px;">⚡ EXTREME VIRALITY &nbsp;|&nbsp; {directive}</div>',
                        unsafe_allow_html=True,
                    )

                # ── Main signal card
                st.markdown(f"""
                <div style="border:1px solid {border};border-radius:{'0 0 6px 6px' if is_ext else '6px'};background:{bg};
                            padding:1rem 1.2rem;margin-bottom:0.3rem;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;
                              flex-wrap:wrap;gap:0.6rem;">
                    <div style="flex:1;min-width:200px;">
                      <div style="font-family:IBM Plex Mono,monospace;font-size:0.55rem;
                                  color:{T["muted2"]};letter-spacing:0.14em;text-transform:uppercase;">
                        SIGNAL #{i+1} &nbsp;·&nbsp; {sig.get("emergence_window","N/A")}</div>
                      <div style="font-size:1.05rem;font-weight:700;color:{T["acc"]};
                                  margin:0.25rem 0;font-family:Space Grotesk,sans-serif;">
                        {sig.get("niche_keyword","N/A")}</div>
                      <div style="font-size:0.78rem;color:{T["text2"]};">
                        {sig.get("velocity_metric","N/A")}</div>
                      <div style="font-size:0.72rem;color:{T["muted"]};margin-top:0.25rem;">
                        {sig.get("actionability_rating","N/A")}</div>
                    </div>
                    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;align-items:flex-start;">
                      <div style="text-align:center;background:{T["card"]};border:1px solid {T["border"]};
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:{T["muted2"]};letter-spacing:0.08em;">VIRALITY</div>
                        <div style="font-size:1.25rem;font-weight:700;color:{bar_c};">{virality}</div>
                      </div>
                      <div style="text-align:center;background:{T["card"]};border:1px solid {T["border"]};
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:{T["muted2"]};letter-spacing:0.08em;">ACCEL</div>
                        <div style="font-size:1.25rem;font-weight:700;color:{T["text"]};">{acc}</div>
                      </div>
                      <div style="text-align:center;background:{T["card"]};border:1px solid {T["border"]};
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:{T["muted2"]};letter-spacing:0.08em;">ARBITRAGE</div>
                        <div style="font-size:1.25rem;font-weight:700;color:{T["text"]};">{arb:.0f}</div>
                      </div>
                      <div style="text-align:center;background:{T["card"]};border:1px solid {sat_c};
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:{T["muted2"]};letter-spacing:0.08em;">SAT RISK</div>
                        <div style="font-size:0.8rem;font-weight:700;color:{sat_c};">{sat}</div>
                      </div>
                    </div>
                  </div>
                  <div style="margin-top:0.8rem;background:{T["tag"]};border-radius:2px;height:3px;">
                    <div style="background:{bar_c};width:{min(virality,100)}%;height:3px;
                                border-radius:2px;"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

                # ── KPI cards for this persona
                _last_ctx   = st.session_state.last_ctx
                _kpi_key    = (_last_ctx.get("industry",""), _last_ctx.get("sub_industry",""), _last_ctx.get("persona_role",""))
                _kpis       = KPI_MAP.get(_kpi_key, [])
                _disp_icons = {
                    "TREND_SCORE":   ("📈", T["c_trend"]),
                    "SENTIMENT":     ("💬", T["c_sent"]),
                    "VELOCITY":      ("⚡", T["c_vel"]),
                    "HEAT_INDEX":    ("🔥", T["c_heat"]),
                    "RANKED_LIST":   ("🏆", T["c_rank"]),
                    "EVENT_PULSE":   ("📡", T["c_evt"]),
                    "PRICE_TRACKER": ("💲", T["c_price"]),
                }
                if _kpis:
                    st.markdown(
                        f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;'
                        f'letter-spacing:0.16em;color:{T["muted2"]};text-transform:uppercase;'
                        f'margin:0.5rem 0 0.4rem 0.1rem;">▸ SIGNAL KPIs FOR THIS PERSONA</div>',
                        unsafe_allow_html=True,
                    )
                    _kpi_cols = st.columns(min(len(_kpis), 5))
                    for _ki, _kpi in enumerate(_kpis):
                        _dt   = _kpi["display"]
                        _icon, _clr = _disp_icons.get(_dt, ("📊", "#888888"))
                        with _kpi_cols[_ki % len(_kpi_cols)]:
                            st.markdown(f"""
                            <div style="background:{T["card2"]};border:1px solid {T["border2"]};
                                        border-top:2px solid {_clr};border-radius:4px;
                                        padding:0.6rem 0.7rem;height:100%;">
                              <div style="display:flex;align-items:center;gap:0.35rem;
                                          margin-bottom:0.3rem;">
                                <span style="font-size:0.85rem;">{_icon}</span>
                                <span style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;
                                             color:{_clr};letter-spacing:0.1em;">{_dt}</span>
                              </div>
                              <div style="font-size:0.73rem;font-weight:600;color:{T["text"]};
                                          margin-bottom:0.25rem;line-height:1.3;">{_kpi["name"]}</div>
                              <div style="font-size:0.62rem;color:{T["muted"]};line-height:1.4;
                                          margin-bottom:0.3rem;">{_kpi["tells"]}</div>
                              <div style="font-size:0.58rem;color:{T["muted2"]};line-height:1.35;
                                          margin-bottom:0.25rem;font-style:italic;">{_kpi["decision"]}</div>
                              <div style="font-family:IBM Plex Mono,monospace;font-size:0.5rem;
                                          color:{T["muted2"]};line-height:1.3;">{_kpi["sources"]}</div>
                            </div>""", unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:1.2rem;'></div>", unsafe_allow_html=True)

    # ─── TAB 2: ORCHESTRATION OUTPUT ──────────────────
    with tab2:
        run_layer = st.session_state.last_ctx.get("persona_layer", active_layer)
        run_fd    = st.session_state.last_ctx.get("functional_domain", "")
        st.markdown(f"""
        <div style="border-left:3px solid #F5A623;padding-left:0.9rem;margin-bottom:1.2rem;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                      color:{T["muted"]};letter-spacing:0.12em;text-transform:uppercase;">
            {run_layer} LAYER OUTPUT &nbsp;·&nbsp; {run_fd}</div>
          <div style="font-size:1.05rem;font-weight:600;color:{T["text"]};margin-top:0.12rem;">
            {persona_icon} {selected_persona} — {BRANCH_LABELS.get(active_branch_run, active_branch_run)}</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.orchestration_output:
            st.markdown(st.session_state.orchestration_output)
            st.download_button(
                "⬇  Export as Markdown",
                data=st.session_state.orchestration_output,
                file_name=f"tigertrend_{(selected_persona or 'output').lower().replace(' ','_')}"
                          f"_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.info("Orchestration Agent output will appear here after the pipeline runs.")

    # ─── TAB 3: GOVERNANCE ──────────────────────────
    with tab3:
        st.markdown(
            f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;'
            f'letter-spacing:0.2em;color:{T["acc"]};margin-bottom:1rem;">'
            f'▸ REFLECTION AGENT — GOVERNANCE &amp; BRAND SAFETY REVIEW</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.reflection_output:
            st.markdown(st.session_state.reflection_output)
        elif active_branch_run in REVIEW_BRANCHES:
            st.info("Governance review will appear here after the pipeline runs.")
        else:
            _branch_label = BRANCH_LABELS.get(active_branch_run, active_branch_run)
            st.markdown(
                f'<div style="border:1px solid {T["border"]};border-radius:8px;padding:1.4rem;'
                f'background:{T["card2"]};text-align:center;">',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-size:0.82rem;color:{T["muted"]};line-height:1.7;">' +
                f'Governance review is not required for the ' +
                f'<strong style="color:{T["acc"]}">{_branch_label}</strong> branch.<br>' +
                f'<span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:{T["muted2"]};">' +
                f'Reflection Agent activates for: commercial, execution, field-action, and governance routes.' +
                f'</span></div></div>',
                unsafe_allow_html=True,
            )

    # ── JSON Inspector
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("🔍  RAW PIPELINE OUTPUT — JSON Inspector"):
        payload = {
            "prototype_name":    "TigerTrend / Sense & Respond OS",
            "workflow_version":  "streamlit-groq-v2-csv-driven",
            "request":           st.session_state.last_ctx,
            "scored_trends":     st.session_state.scored_signals,
            "orchestration_preview": (st.session_state.orchestration_output or "")[:500],
            "reflection_preview":    (st.session_state.reflection_output or "")[:300],
            "generated_at":      datetime.now().isoformat(),
        }
        st.json(payload)
        st.download_button(
            "⬇  Export Full JSON",
            data=json.dumps({**payload,
                              "orchestration_output": st.session_state.orchestration_output,
                              "reflection_output":    st.session_state.reflection_output}, indent=2),
            file_name=f"tigertrend_pipeline_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
        )


# ─────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding-top:0.8rem;border-top:1px solid #181818;
            text-align:center;font-family:'IBM Plex Mono',monospace;
            font-size:0.58rem;color:#888;letter-spacing:0.12em;">
  TIGER ANALYTICS &nbsp;·&nbsp; SENSE &amp; RESPOND OS &nbsp;·&nbsp;
  BLEEDING SIGNALS ENGINE &nbsp;·&nbsp; GROQ + LLAMA-3.3-70B-VERSATILE
</div>""", unsafe_allow_html=True)
