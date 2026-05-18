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
    """Inject full CSS with correct theme tokens."""
    if dark:
        tokens = {
            "bg":         "#0D0D0D",
            "sidebar_bg": "#111111",
            "card_bg":    "#141414",
            "card_bg2":   "#0F0F0F",
            "input_bg":   "#1A1A1A",
            "border":     "#2A2A2A",
            "border2":    "#1E1E1E",
            "text":       "#E8E8E8",
            "text2":      "#AAAAAA",
            "muted":      "#666666",
            "muted2":     "#444444",
            "header_text":"#0D0D0D",
            "divider":    "#1E1E1E",
            "tag_bg":     "#1C1C1C",
            "shadow":     "rgba(0,0,0,0.6)",
            "glow":       "rgba(245,166,35,0.35)",
            "metric_bg":  "#111111",
            "scroll_track":"#111111",
            "scroll_thumb":"#2A2A2A",
            "badge_text": "#0D0D0D",
            "invert_logo":"0",
        }
    else:
        tokens = {
            "bg":         "#F7F4EF",
            "sidebar_bg": "#FFFFFF",
            "card_bg":    "#FFFFFF",
            "card_bg2":   "#FDF9F3",
            "input_bg":   "#FFFFFF",
            "border":     "#E2D9CC",
            "border2":    "#EDE6DC",
            "text":       "#1A1009",
            "text2":      "#4A3B2A",
            "muted":      "#7A6A55",
            "muted2":     "#B0A090",
            "header_text":"#1A1009",
            "divider":    "#E8DDD0",
            "tag_bg":     "#FDF1DE",
            "shadow":     "rgba(90,60,10,0.12)",
            "glow":       "rgba(245,166,35,0.25)",
            "metric_bg":  "#FFFFFF",
            "scroll_track":"#EDE6DC",
            "scroll_thumb":"#D4C4A8",
            "badge_text": "#FFFFFF",
            "invert_logo":"0",
        }

    t = tokens
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Base */
html, body, [class*="css"], .stApp, .main, section.main {{
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: {t["bg"]} !important;
    color: {t["text"]} !important;
}}

/* ── Header bar */
header[data-testid="stHeader"] {{
    background: linear-gradient(90deg, #F5A623 0%, #E8941A 100%) !important;
    border-bottom: 2px solid #D4840E !important;
    box-shadow: 0 2px 12px {t["shadow"]} !important;
}}
header[data-testid="stHeader"] * {{ color: {t["header_text"]} !important; }}

/* ── Sidebar */
[data-testid="stSidebar"] {{
    background-color: {t["sidebar_bg"]} !important;
    border-right: 1px solid {t["border"]} !important;
    box-shadow: 2px 0 16px {t["shadow"]} !important;
}}
[data-testid="stSidebar"] * {{ color: {t["text"]} !important; }}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label {{
    color: {t["text2"]} !important;
    font-size: 0.82rem !important;
}}

/* ── Sidebar section labels */
[data-testid="stSidebar"] hr {{
    border-color: {t["border"]} !important;
    margin: 0.6rem 0 !important;
}}

/* ── Buttons */
div.stButton > button {{
    background-color: transparent !important;
    color: #F5A623 !important;
    border: 1.5px solid #F5A623 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 4px {t["shadow"]} !important;
}}
div.stButton > button:hover {{
    background: linear-gradient(135deg, #F5A623, #E8941A) !important;
    color: {t["badge_text"]} !important;
    box-shadow: 0 4px 16px {t["glow"]} !important;
    transform: translateY(-1px) !important;
    border-color: transparent !important;
}}
div.stButton > button:active {{
    transform: translateY(0px) !important;
    box-shadow: 0 1px 6px {t["glow"]} !important;
}}

/* ── Primary / CTA button (detect signals) */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, #F5A623 0%, #E8941A 100%) !important;
    color: {t["badge_text"]} !important;
    border: none !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
}}
div.stButton > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, #FFBE4D 0%, #F5A623 100%) !important;
    box-shadow: 0 6px 20px {t["glow"]} !important;
}}

/* ── Select / Input / Textarea */
div[data-baseweb="select"] > div {{
    background-color: {t["input_bg"]} !important;
    border: 1px solid {t["border"]} !important;
    border-radius: 6px !important;
    color: {t["text"]} !important;
    transition: border-color 0.18s !important;
}}
div[data-baseweb="select"] > div:focus-within {{
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 2px {t["glow"]} !important;
}}
div[data-baseweb="input"] > div {{
    background-color: {t["input_bg"]} !important;
    border: 1px solid {t["border"]} !important;
    border-radius: 6px !important;
    color: {t["text"]} !important;
}}
div[data-baseweb="input"] > div:focus-within {{
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 2px {t["glow"]} !important;
}}
input, input[type="text"], input[type="password"] {{
    background-color: {t["input_bg"]} !important;
    color: {t["text"]} !important;
}}
textarea {{
    background-color: {t["input_bg"]} !important;
    color: {t["text"]} !important;
    border: 1px solid {t["border"]} !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    transition: border-color 0.18s !important;
}}
textarea:focus {{
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 2px {t["glow"]} !important;
    outline: none !important;
}}

/* ── Selectbox dropdown list */
ul[data-baseweb="menu"] {{
    background-color: {t["card_bg"]} !important;
    border: 1px solid {t["border"]} !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 24px {t["shadow"]} !important;
}}
li[role="option"] {{
    color: {t["text"]} !important;
    font-size: 0.82rem !important;
}}
li[role="option"]:hover, li[aria-selected="true"] {{
    background-color: {t["tag_bg"]} !important;
    color: #F5A623 !important;
}}

/* ── Tabs */
div[data-testid="stTabs"] {{
    border-bottom: 1px solid {t["border"]} !important;
}}
div[data-testid="stTabs"] button {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    color: {t["muted"]} !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 0.5rem 1.2rem !important;
    transition: color 0.18s !important;
    text-transform: uppercase !important;
}}
div[data-testid="stTabs"] button:hover {{
    color: #F5A623 !important;
    background-color: {t["tag_bg"]} !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: #F5A623 !important;
    border-bottom: 2px solid #F5A623 !important;
    font-weight: 700 !important;
}}

/* ── Metric cards */
div[data-testid="stMetric"] {{
    background-color: {t["metric_bg"]} !important;
    border: 1px solid {t["border"]} !important;
    border-radius: 10px !important;
    padding: 0.9rem 1rem !important;
    border-top: 3px solid #F5A623 !important;
    box-shadow: 0 2px 8px {t["shadow"]} !important;
    transition: box-shadow 0.2s !important;
}}
div[data-testid="stMetric"]:hover {{
    box-shadow: 0 4px 16px {t["glow"]} !important;
}}
div[data-testid="stMetric"] label {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.16em !important;
    color: {t["muted"]} !important;
    text-transform: uppercase !important;
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #F5A623 !important;
    line-height: 1.1 !important;
}}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
}}

/* ── Expander */
details {{
    background-color: {t["card_bg2"]} !important;
    border: 1px solid {t["border"]} !important;
    border-radius: 8px !important;
    padding: 0.2rem 0.5rem !important;
}}
details summary {{
    color: #F5A623 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    padding: 0.4rem 0 !important;
}}
details summary:hover {{ opacity: 0.8 !important; }}

/* ── Radio buttons */
div[data-testid="stRadio"] label {{
    color: {t["text2"]} !important;
    font-size: 0.82rem !important;
    transition: color 0.15s !important;
}}
div[data-testid="stRadio"] label:hover {{ color: #F5A623 !important; }}

/* ── File uploader */
[data-testid="stFileUploader"] {{
    background-color: {t["card_bg2"]} !important;
    border: 1.5px dashed {t["border"]} !important;
    border-radius: 8px !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: #F5A623 !important;
}}

/* ── Chat input */
[data-testid="stChatInput"] > div {{
    background-color: {t["input_bg"]} !important;
    border: 1px solid {t["border"]} !important;
    border-radius: 8px !important;
}}
[data-testid="stChatInput"] > div:focus-within {{
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 2px {t["glow"]} !important;
}}

/* ── Alert / info boxes */
div[data-testid="stAlert"] {{
    border-radius: 8px !important;
    border-left: 4px solid #F5A623 !important;
    font-size: 0.82rem !important;
}}

/* ── Download button */
div.stDownloadButton > button {{
    background: transparent !important;
    color: #F5A623 !important;
    border: 1px solid {t["border"]} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.08em !important;
    border-radius: 6px !important;
}}
div.stDownloadButton > button:hover {{
    border-color: #F5A623 !important;
    background-color: {t["tag_bg"]} !important;
}}

/* ── Scrollbar */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {t["scroll_track"]}; border-radius: 3px; }}
::-webkit-scrollbar-thumb {{ background: {t["scroll_thumb"]}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: #F5A623; }}

/* ── Smooth transitions on theme switch */
*, *::before, *::after {{
    transition: background-color 0.25s ease, border-color 0.25s ease, color 0.15s ease !important;
}}

/* ── Main content padding */
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# THEME VARIABLE HELPER
# ─────────────────────────────────────────────────────
def tv() -> dict:
    """Return current theme token dict for inline HTML use."""
    dark = st.session_state.get("theme_dark", True)
    if dark:
        return {
            "bg":        "#0D0D0D", "sidebar":  "#111111", "card":    "#141414",
            "card2":     "#0F0F0F", "input":    "#1A1A1A", "border":  "#2A2A2A",
            "border2":   "#1E1E1E", "text":     "#E8E8E8", "text2":   "#AAAAAA",
            "muted":     "#888888", "muted2":   "#555555", "tag":     "#1C1C1C",
            "shadow":    "rgba(0,0,0,0.5)",
            "acc":       "#F5A623", "acc_text": "#000000",
            "green":     "#30D158", "red":      "#FF3B30",
            "badge_fg":  "#000000",
            # KPI type colours — vivid on dark
            "c_trend":   "#F5A623", "c_sent":   "#30D158", "c_vel":   "#FF9F0A",
            "c_heat":    "#FF3B30", "c_rank":   "#BF5AF2", "c_evt":   "#32ADE6",
            "c_price":   "#64D2FF",
            # signal card backgrounds
            "sig_bg":    "#0F0F0F", "sig_ext":  "#1A0808",
        }
    else:
        return {
            "bg":        "#F7F4EF", "sidebar":  "#FFFFFF", "card":    "#FFFFFF",
            "card2":     "#FDF9F3", "input":    "#FFFFFF", "border":  "#E2D9CC",
            "border2":   "#EDE6DC", "text":     "#1A1009", "text2":   "#4A3B2A",
            "muted":     "#6B5A45", "muted2":   "#9A8A78", "tag":     "#FDF1DE",
            "shadow":    "rgba(90,60,10,0.10)",
            "acc":       "#C47208", "acc_text": "#FFFFFF",
            "green":     "#1A6B30", "red":      "#B51C00",
            "badge_fg":  "#FFFFFF",
            # KPI type colours — darker/richer on light bg for legibility
            "c_trend":   "#B05E00", "c_sent":   "#1A6B30", "c_vel":   "#9A5000",
            "c_heat":    "#B51C00", "c_rank":   "#6B2EA0", "c_evt":   "#0066AA",
            "c_price":   "#005C8A",
            # signal card backgrounds — warm tinted on light
            "sig_bg":    "#FAFAF8", "sig_ext":  "#FFF5F3",
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
- Actionable: keyword must be directly usable as an Imagen 3 generation prompt
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

    _is_dark = st.session_state.theme_dark
    _border_col = "#2A2A2A" if _is_dark else "#E2D9CC"
    _title_col  = "#E8E8E8" if _is_dark else "#1A1009"
    st.markdown(f"""
    <div style="padding:0.6rem 0 0.8rem;border-bottom:1px solid {_border_col};margin-bottom:0.8rem;
                display:flex;align-items:center;justify-content:space-between;">
      <div>
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;
                    letter-spacing:0.22em;color:#F5A623;text-transform:uppercase;">
          SENSE &amp; RESPOND OS</div>
        <div style="font-size:1.05rem;font-weight:700;color:{_title_col};margin-top:0.15rem;">
          Bleeding Signals Engine</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Theme toggle
    _tc1, _tc2 = st.columns([1, 1])
    with _tc1:
        st.markdown(
            f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;'
            f'letter-spacing:0.14em;color:#F5A623;padding-top:0.45rem;">THEME</div>',
            unsafe_allow_html=True,
        )
    with _tc2:
        _theme_label = "🌙 Dark" if st.session_state.theme_dark else "☀️ Light"
        if st.button(_theme_label, key="theme_toggle", use_container_width=True):
            st.session_state.theme_dark = not st.session_state.theme_dark
            st.rerun()

    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    # ── API Key
    env_key = os.environ.get("GROQ_API_KEY", "")
    if env_key:
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.68rem;'
                    'color:#30D158;margin-bottom:0.5rem;">● GROQ CONNECTED</div>',
                    unsafe_allow_html=True)
        groq_client = get_groq_client(env_key)
    else:
        api_input = st.text_input("🔑 Groq API Key", type="password",
                                  placeholder="gsk_...", key="api_key_input")
        if api_input:
            st.session_state.groq_key = api_input
        groq_client = get_groq_client(st.session_state.groq_key)
        if groq_client:
            st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.68rem;'
                        'color:#30D158;">● CONNECTED</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── CONTEXT
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
                f'letter-spacing:0.18em;color:{T["acc"]};margin-bottom:0.5rem;">▸ CONTEXT</div>',
                unsafe_allow_html=True)

    # Industry dropdown (from CSV)
    industry_options = list(TAXONOMY.keys())
    industry = st.selectbox("Industry", options=industry_options)

    # Sub-industry — filtered to selected industry
    sub_industry_options = TAXONOMY.get(industry, [])
    sub_industry = st.selectbox("Sub-Industry", options=sub_industry_options)

    # Region — optional (blank = not specified)
    region_options = ["", "North America", "EMEA", "APAC", "LATAM", "Global"]
    region = st.selectbox(
        "Region (optional)",
        options=region_options,
        format_func=lambda x: "— Not specified —" if x == "" else x,
    )

    # Signal Window — optional; falls back to KPI priority for persona
    window_options = ["", "Last 24 hours", "Last 48 hours", "Last 7 days", "Last 30 days"]
    time_window = st.selectbox(
        "Signal Window (optional)",
        options=window_options,
        format_func=lambda x: "— Use persona default —" if x == "" else x,
    )

    # Brand Context — optional
    brand_context = st.text_area(
        "Brand Context (optional)",
        placeholder="e.g. Premium beauty brand targeting Gen Z…",
        height=64,
    )

    st.markdown("---")

    # ── FILE UPLOAD
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
                f'letter-spacing:0.18em;color:{T["acc"]};margin-bottom:0.5rem;">▸ SIGNAL UPLOAD</div>',
                unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop signal data",
        type=["png", "jpg", "jpeg", "csv", "txt"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        icon_map = {"png": "🖼️", "jpg": "🖼️", "jpeg": "🖼️", "csv": "📊", "txt": "📄"}
        _mono = "IBM Plex Mono"
        _icon = icon_map.get(ext, "📎")
        st.markdown(
            f'<div style="font-family:{_mono},monospace;font-size:0.7rem;'
            f'color:#30D158;">{_icon} {uploaded_file.name}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:0.7rem;'></div>", unsafe_allow_html=True)

    # Only enable run if a persona is selected
    persona_selected = st.session_state.selected_persona is not None
    run_label = "⚡  DETECT BLEEDING SIGNALS" if persona_selected else "⚡  SELECT A PERSONA FIRST"
    run_pipeline = st.button(run_label, use_container_width=True, disabled=not persona_selected)

    st.markdown("---")

    # ── CHAT
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.65rem;'
                f'letter-spacing:0.18em;color:{T["acc"]};margin-bottom:0.5rem;">▸ COMMAND INTERFACE</div>',
                unsafe_allow_html=True)

    chat_box = st.container(height=260)
    with chat_box:
        if not st.session_state.chat_history:
            st.markdown(
                    f'<div style="font-size:0.75rem;color:{T["muted2"]};font-style:italic;">'
                    f'Awaiting first signal…</div>',
                    unsafe_allow_html=True,
                )
        for msg in st.session_state.chat_history:
            clr   = "#F5A623" if msg["role"] == "assistant" else T["text"]
            label = "OS" if msg["role"] == "assistant" else "YOU"
            st.markdown(f"""
            <div style="margin-bottom:0.55rem;">
              <span style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                           color:{clr};letter-spacing:0.1em;">{label}</span>
              <div style="font-size:0.76rem;color:#777777;margin-top:0.1rem;
                          line-height:1.45;">{msg['content']}</div>
            </div>""", unsafe_allow_html=True)

    chat_input = st.chat_input("Ask the OS…")

    if st.button("🗑  Clear Session", use_container_width=True):
        for k in ["chat_history", "scored_signals", "orchestration_output",
                  "reflection_output", "last_ctx"]:
            st.session_state[k] = [] if isinstance(st.session_state[k], list) else ""
        st.session_state.pipeline_ran = False
        st.session_state.selected_persona = None
        st.rerun()


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
industry_label = industry

# ── OS Header
selected_display = f"{persona_icon} {selected_persona}" if selected_persona else "Select a Persona →"
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            border-bottom:1px solid {T["border"]};padding-bottom:0.9rem;margin-bottom:1.4rem;">
  <div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                letter-spacing:0.22em;color:#F5A623;text-transform:uppercase;">
      TIGER ANALYTICS / SENSE &amp; RESPOND OS</div>
    <div style="font-size:1.5rem;font-weight:700;color:{T["text"]};margin-top:0.1rem;">
      {selected_display} Studio</div>
  </div>
  <div style="text-align:right;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:{T["muted2"]};
                letter-spacing:0.1em;">{industry_label.upper()} / {sub_industry.upper()}</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                color:{T["muted"]};margin-top:0.15rem;">{datetime.now().strftime("%d %b %Y  %H:%M")}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# PERSONA SELECTION CARDS (always visible)
# ─────────────────────────────────────────────────────
st.markdown(
    f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;'
    f'letter-spacing:0.2em;color:#F5A623;margin-bottom:0.9rem;">'
    f'▸ PERSONA ENGINE — {industry} / {sub_industry}</div>',
    unsafe_allow_html=True,
)

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


# ─────────────────────────────────────────────────────
# IDLE STATE (no pipeline run yet)
# ─────────────────────────────────────────────────────
if not st.session_state.pipeline_ran:

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
else:
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

    tab1, tab2, tab3 = st.tabs(["📡  Bleeding Signals", "📋  Persona Output", "🛡️  Governance Review"])

    # ─── TAB 1: SIGNAL CARDS ──────────────────────────
    with tab1:
        st.markdown(
            f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;'
            f'letter-spacing:0.2em;color:{T["acc"]};margin-bottom:1rem;">'
            f'▸ CULTURAL INTELLIGENCE ALERTS — LIVE SIGNAL FEED</div>',
            unsafe_allow_html=True,
        )

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

        # ── Imagen 3 Studio
        st.markdown("---")
        st.markdown(
            '<div style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;'
            f'letter-spacing:0.18em;color:{T["acc"]};margin-bottom:0.6rem;">'
            f'▸ IMAGEN 3 GENERATIVE STUDIO</div>',
            unsafe_allow_html=True,
        )

        if scored_signals:
            # ── API key input
            gcp_key = st.text_input(
                "Google API Key (Imagen 3)",
                type="password",
                placeholder="AIza...",
                help="Get a key at https://aistudio.google.com/app/apikey — Gemini/Imagen access required.",
                key="gcp_api_key",
            )

            ic1, ic2 = st.columns([3, 1])
            with ic1:
                img_signal = st.selectbox(
                    "Signal keyword (auto-used as prompt base)",
                    [s.get("niche_keyword", "") for s in scored_signals],
                    key="imagen_signal_select",
                )
            with ic2:
                img_count = st.selectbox("Images", [1, 2, 4], index=1, key="imagen_count")

            # Prompt builder
            _last_ctx_img = st.session_state.last_ctx
            _default_prompt = (
                f"{img_signal}, "
                f"{_last_ctx_img.get('sub_industry','')}, "
                f"high-fashion editorial photography, "
                f"cinematic lighting, ultra-detailed, 4K"
            )
            img_prompt = st.text_area(
                "Generation prompt (editable)",
                value=_default_prompt,
                height=72,
                key="imagen_prompt",
            )

            if st.button("🎨  Generate with Imagen 3", use_container_width=True):
                if not gcp_key:
                    st.warning("Enter your Google API Key above to use Imagen 3.")
                else:
                    import requests as _req, base64 as _b64, io as _io
                    from PIL import Image as _PILImage

                    _url = (
                        f"https://generativelanguage.googleapis.com/v1beta/models/"
                        f"imagen-3.0-generate-002:predict?key={gcp_key}"
                    )
                    _payload = {
                        "instances": [{"prompt": img_prompt}],
                        "parameters": {
                            "sampleCount": img_count,
                            "aspectRatio": "16:9",
                            "safetyFilterLevel": "block_some",
                            "personGeneration": "allow_adult",
                        },
                    }

                    with st.spinner("🎨 Calling Imagen 3 API…"):
                        try:
                            _resp = _req.post(_url, json=_payload, timeout=60)
                            if _resp.status_code == 200:
                                _data = _resp.json()
                                _predictions = _data.get("predictions", [])
                                if _predictions:
                                    st.success(f"✅ {len(_predictions)} image(s) generated")
                                    _img_cols = st.columns(len(_predictions))
                                    for _pi, _pred in enumerate(_predictions):
                                        _b64_data = _pred.get("bytesBase64Encoded", "")
                                        if _b64_data:
                                            _img_bytes = _b64.b64decode(_b64_data)
                                            _pil_img = _PILImage.open(_io.BytesIO(_img_bytes))
                                            with _img_cols[_pi]:
                                                st.image(_pil_img, use_container_width=True)
                                                st.download_button(
                                                    "⬇ Download",
                                                    data=_img_bytes,
                                                    file_name=f"imagen_{img_signal[:30].replace(' ','_')}_{_pi+1}.png",
                                                    mime="image/png",
                                                    key=f"dl_img_{i}_{_pi}",
                                                )
                                else:
                                    st.warning("API returned no predictions. Check your prompt or quota.")
                                    st.json(_data)
                            elif _resp.status_code == 400:
                                _err = _resp.json().get("error", {})
                                st.error(f"Bad request — {_err.get('message', _resp.text)}")
                            elif _resp.status_code == 401:
                                st.error("Invalid API key — check your Google API Key.")
                            elif _resp.status_code == 403:
                                st.error("Access denied — ensure Imagen API is enabled for your key at https://aistudio.google.com.")
                            elif _resp.status_code == 429:
                                st.error("Rate limit hit — wait a moment and try again.")
                            else:
                                st.error(f"API error {_resp.status_code}: {_resp.text[:400]}")
                        except Exception as _e:
                            st.error(f"Request failed: {_e}")

        # ── VTO
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;'
                    f'letter-spacing:0.18em;color:{T["acc"]};margin:1rem 0 0.6rem;">'
                    '▸ VIRTUAL TRY-ON (Google VTO)</div>', unsafe_allow_html=True)

        vc1, vc2 = st.columns(2)
        with vc1:
            vto_src = st.file_uploader("Source (person)", type=["png","jpg","jpeg"], key="vto_src")
        with vc2:
            vto_ref = st.file_uploader("Reference (garment)", type=["png","jpg","jpeg"], key="vto_ref")

        if st.button("👕  Run Virtual Try-On", use_container_width=True):
            if vto_src and vto_ref:
                script = Path("scripts/run_virtual_tryon.py")
                if script.exists():
                    import subprocess, tempfile as _tf
                    with _tf.TemporaryDirectory() as td:
                        sp = Path(td) / vto_src.name
                        rp = Path(td) / vto_ref.name
                        od = Path(td) / "out"; od.mkdir()
                        sp.write_bytes(vto_src.read())
                        rp.write_bytes(vto_ref.read())
                        with st.spinner("Running Google VTO API…"):
                            r = subprocess.run(
                                ["python", str(script),
                                 "--source", str(sp),
                                 "--reference", str(rp),
                                 "--output-dir", str(od)],
                                capture_output=True, text=True, timeout=180)
                        if r.returncode == 0:
                            imgs = list(od.glob("*.png")) + list(od.glob("*.jpg"))
                            if imgs:
                                st.success("✅ Virtual Try-On complete")
                                vcols = st.columns(len(imgs))
                                for idx, ip in enumerate(imgs):
                                    with vcols[idx]:
                                        st.image(str(ip), caption=ip.name, use_container_width=True)
                            else:
                                st.warning("VTO ran but no output images found.")
                                st.code(r.stdout)
                        else:
                            st.error(f"VTO error:\n{r.stderr}")
                else:
                    st.info("ℹ️ `scripts/run_virtual_tryon.py` not found in project root.")
            else:
                st.warning("Upload both source and reference images.")

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
