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
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --tiger-orange: #F5A623;
    --tiger-dark:   #0D0D0D;
    --tiger-mid:    #1A1A1A;
    --tiger-card:   #111111;
    --tiger-border: #2A2A2A;
    --tiger-text:   #E8E8E8;
    --tiger-muted:  #888888;
    --tiger-red:    #FF3B30;
    --tiger-green:  #30D158;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: var(--tiger-dark) !important;
    color: var(--tiger-text) !important;
}

header[data-testid="stHeader"] {
    background-color: var(--tiger-orange) !important;
    border-bottom: 2px solid #c8860f !important;
}
header[data-testid="stHeader"] * { color: var(--tiger-dark) !important; }

[data-testid="stSidebar"] {
    background-color: var(--tiger-mid) !important;
    border-right: 1px solid var(--tiger-border) !important;
}
[data-testid="stSidebar"] * { color: var(--tiger-text) !important; }

div.stButton > button {
    background-color: #111111 !important;
    color: var(--tiger-orange) !important;
    border: 1px solid var(--tiger-orange) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.18s ease !important;
}
div.stButton > button:hover {
    background-color: var(--tiger-orange) !important;
    color: #000 !important;
    box-shadow: 0 0 12px rgba(245,166,35,0.45) !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background-color: #1C1C1C !important;
    border-color: var(--tiger-border) !important;
    color: var(--tiger-text) !important;
}
textarea {
    background-color: #1C1C1C !important;
    color: var(--tiger-text) !important;
    border: 1px solid var(--tiger-border) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}

div[data-testid="stTabs"] button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    color: var(--tiger-muted) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--tiger-orange) !important;
    border-bottom: 2px solid var(--tiger-orange) !important;
}

div[data-testid="stMetric"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.14em !important;
    color: var(--tiger-muted) !important;
    text-transform: uppercase !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--tiger-orange) !important;
}

details summary {
    color: var(--tiger-orange) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--tiger-mid); }
::-webkit-scrollbar-thumb { background: var(--tiger-border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--tiger-orange); }
</style>
""", unsafe_allow_html=True)


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
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────
# ══════════════════  SIDEBAR  ════════════════════════
# ─────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("""
    <div style="padding:0.6rem 0 1rem;border-bottom:1px solid #2A2A2A;margin-bottom:1rem;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
                  letter-spacing:0.22em;color:#F5A623;text-transform:uppercase;">
        SENSE &amp; RESPOND OS</div>
      <div style="font-size:1.05rem;font-weight:700;color:#E8E8E8;margin-top:0.2rem;">
        Bleeding Signals Engine</div>
    </div>""", unsafe_allow_html=True)

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
                'letter-spacing:0.18em;color:#F5A623;margin-bottom:0.5rem;">▸ CONTEXT</div>',
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
                'letter-spacing:0.18em;color:#F5A623;margin-bottom:0.5rem;">▸ SIGNAL UPLOAD</div>',
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
                'letter-spacing:0.18em;color:#F5A623;margin-bottom:0.5rem;">▸ COMMAND INTERFACE</div>',
                unsafe_allow_html=True)

    chat_box = st.container(height=260)
    with chat_box:
        if not st.session_state.chat_history:
            st.markdown('<div style="font-size:0.75rem;color:#444;font-style:italic;">'
                        'Awaiting first signal…</div>', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            clr   = "#F5A623" if msg["role"] == "assistant" else "#E8E8E8"
            label = "OS" if msg["role"] == "assistant" else "YOU"
            st.markdown(f"""
            <div style="margin-bottom:0.55rem;">
              <span style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                           color:{clr};letter-spacing:0.1em;">{label}</span>
              <div style="font-size:0.76rem;color:#CCC;margin-top:0.1rem;
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
            border-bottom:1px solid #2A2A2A;padding-bottom:0.9rem;margin-bottom:1.4rem;">
  <div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;
                letter-spacing:0.22em;color:#F5A623;text-transform:uppercase;">
      TIGER ANALYTICS / SENSE &amp; RESPOND OS</div>
    <div style="font-size:1.5rem;font-weight:700;color:#E8E8E8;margin-top:0.1rem;">
      {selected_display} Studio</div>
  </div>
  <div style="text-align:right;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#444;
                letter-spacing:0.1em;">{industry_label.upper()} / {sub_industry.upper()}</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                color:#666;margin-top:0.15rem;">{datetime.now().strftime("%d %b %Y  %H:%M")}</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
# PERSONA SELECTION CARDS (always visible)
# ─────────────────────────────────────────────────────
st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;'
            'letter-spacing:0.2em;color:#F5A623;margin-bottom:0.9rem;">'
            f'▸ PERSONA ENGINE — {industry} / {sub_industry}</div>',
            unsafe_allow_html=True)

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

            border_color = "#F5A623" if is_selected else "#2A2A2A"
            bg_color     = "#1A1000" if is_selected else "#111111"
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
                  <div style="font-size:0.82rem;font-weight:700;color:#E8E8E8;
                              margin-bottom:0.15rem;line-height:1.3;">{p_name}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
                              color:#F5A623;letter-spacing:0.06em;margin-bottom:0.4rem;">
                    {p_layer}</div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;
                              color:#888;margin-bottom:0.3rem;">{p_fd}</div>
                  <div style="font-size:0.65rem;color:#AAA;line-height:1.4;margin-bottom:0.4rem;
                              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                              overflow:hidden;">{p_desc}</div>
                  <div style="font-size:0.62rem;color:#666;line-height:1.35;margin-bottom:0.35rem;
                              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                              overflow:hidden;"><span style="color:#555;font-family:'IBM Plex Mono',
                              monospace;font-size:0.48rem;letter-spacing:0.06em;">FOCUS</span><br>
                    {p_focus[:80]}{'…' if len(p_focus) > 80 else ''}</div>
                  <div style="font-size:0.58rem;color:#555;line-height:1.3;
                              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                              overflow:hidden;"><span style="color:#444;font-family:'IBM Plex Mono',
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
        _mono2 = "IBM Plex Mono"
        _signal_window_html = (
            f'<div><div style="font-family:{_mono2},monospace;font-size:0.52rem;color:#555;'
            f'text-transform:uppercase;letter-spacing:0.1em;">Signal Window</div>'
            f'<div style="font-size:0.72rem;color:#888;">{_tw_label}</div></div>'
        )
        st.markdown(f"""
        <div style="background:#111;border:1px solid #2A2A2A;border-left:3px solid #F5A623;
                    border-radius:4px;padding:0.5rem 0.9rem;margin-bottom:1rem;display:flex;
                    gap:2rem;flex-wrap:wrap;align-items:center;">
          <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#555;
                        text-transform:uppercase;letter-spacing:0.1em;">Active Persona</div>
            <div style="font-size:0.82rem;color:#F5A623;font-weight:600;">{selected_persona}</div>
          </div>
          <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#555;
                        text-transform:uppercase;letter-spacing:0.1em;">Layer → Branch</div>
            <div style="font-size:0.78rem;color:#E8E8E8;">{active_layer} → {BRANCH_LABELS.get(active_branch, active_branch)}</div>
          </div>
          <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.52rem;color:#555;
                        text-transform:uppercase;letter-spacing:0.1em;">Functional Domain</div>
            <div style="font-size:0.78rem;color:#E8E8E8;">{active_persona_data.get('functional_domain','')}</div>
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
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#444;
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
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#666;
                      line-height:2;">
            {persona_icon} <strong style="color:#E8E8E8;">{selected_persona}</strong> selected
            &nbsp;·&nbsp; {active_layer} layer &nbsp;·&nbsp; {BRANCH_LABELS.get(active_branch,'')}
            <br>Hit <span style="color:#F5A623;font-weight:600;">DETECT BLEEDING SIGNALS</span>
            in the sidebar to run the pipeline.
          </div>
        </div>""", unsafe_allow_html=True)

    # Pipeline diagram
    st.markdown("""
    <div style="margin-top:1.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
                color:#2A2A2A;text-align:center;letter-spacing:0.07em;line-height:2.2;">
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
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;'
                    'letter-spacing:0.2em;color:#F5A623;margin-bottom:1rem;">'
                    '▸ CULTURAL INTELLIGENCE ALERTS — LIVE SIGNAL FEED</div>',
                    unsafe_allow_html=True)

        if not scored_signals:
            st.info("No signals detected — try adjusting context or uploading richer signal data.")
        else:
            for i, sig in enumerate(scored_signals):
                virality = sig.get("bleeding_edge_virality_score", 0)
                arb      = sig.get("arbitrage_index", 0)
                is_ext   = sig.get("is_extreme_virality", False)
                sat      = sig.get("saturation_risk", "MEDIUM")
                acc      = sig.get("acceleration_score", 0)

                border = "#FF3B30" if is_ext else ("#F5A623" if virality >= 70 else "#2A2A2A")
                bg     = "#1A0808" if is_ext else "#0F0F0F"
                sat_c  = {"HIGH": "#FF3B30", "MEDIUM": "#F5A623", "LOW": "#30D158"}.get(sat, "#888")
                bar_c  = "#FF3B30" if is_ext else ("#F5A623" if virality >= 70 else "#30D158")

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
                                  color:#444;letter-spacing:0.14em;text-transform:uppercase;">
                        SIGNAL #{i+1} &nbsp;·&nbsp; {sig.get("emergence_window","N/A")}</div>
                      <div style="font-size:1.05rem;font-weight:700;color:#F5A623;
                                  margin:0.25rem 0;font-family:Space Grotesk,sans-serif;">
                        {sig.get("niche_keyword","N/A")}</div>
                      <div style="font-size:0.78rem;color:#AAA;">
                        {sig.get("velocity_metric","N/A")}</div>
                      <div style="font-size:0.72rem;color:#666;margin-top:0.25rem;">
                        {sig.get("actionability_rating","N/A")}</div>
                    </div>
                    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;align-items:flex-start;">
                      <div style="text-align:center;background:#111;border:1px solid #2A2A2A;
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:#444;letter-spacing:0.08em;">VIRALITY</div>
                        <div style="font-size:1.25rem;font-weight:700;color:{bar_c};">{virality}</div>
                      </div>
                      <div style="text-align:center;background:#111;border:1px solid #2A2A2A;
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:#444;letter-spacing:0.08em;">ACCEL</div>
                        <div style="font-size:1.25rem;font-weight:700;color:#E8E8E8;">{acc}</div>
                      </div>
                      <div style="text-align:center;background:#111;border:1px solid #2A2A2A;
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:#444;letter-spacing:0.08em;">ARBITRAGE</div>
                        <div style="font-size:1.25rem;font-weight:700;color:#E8E8E8;">{arb:.0f}</div>
                      </div>
                      <div style="text-align:center;background:#111;border:1px solid {sat_c};
                                  border-radius:4px;padding:0.45rem 0.7rem;min-width:65px;">
                        <div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;
                                    color:#444;letter-spacing:0.08em;">SAT RISK</div>
                        <div style="font-size:0.8rem;font-weight:700;color:{sat_c};">{sat}</div>
                      </div>
                    </div>
                  </div>
                  <div style="margin-top:0.8rem;background:#1A1A1A;border-radius:2px;height:3px;">
                    <div style="background:{bar_c};width:{min(virality,100)}%;height:3px;
                                border-radius:2px;"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

                # ── KPI cards for this persona
                _last_ctx   = st.session_state.last_ctx
                _kpi_key    = (_last_ctx.get("industry",""), _last_ctx.get("sub_industry",""), _last_ctx.get("persona_role",""))
                _kpis       = KPI_MAP.get(_kpi_key, [])
                _disp_icons = {
                    "TREND_SCORE":  ("📈", "#F5A623"),
                    "SENTIMENT":    ("💬", "#30D158"),
                    "VELOCITY":     ("⚡", "#FF9F0A"),
                    "HEAT_INDEX":   ("🔥", "#FF3B30"),
                    "RANKED_LIST":  ("🏆", "#BF5AF2"),
                    "EVENT_PULSE":  ("📡", "#32ADE6"),
                    "PRICE_TRACKER":("💲", "#64D2FF"),
                }
                if _kpis:
                    st.markdown(
                        '<div style="font-family:IBM Plex Mono,monospace;font-size:0.52rem;'
                        'letter-spacing:0.16em;color:#444;text-transform:uppercase;'
                        'margin:0.5rem 0 0.4rem 0.1rem;">▸ SIGNAL KPIs FOR THIS PERSONA</div>',
                        unsafe_allow_html=True,
                    )
                    _kpi_cols = st.columns(min(len(_kpis), 5))
                    for _ki, _kpi in enumerate(_kpis):
                        _dt   = _kpi["display"]
                        _icon, _clr = _disp_icons.get(_dt, ("📊", "#888888"))
                        with _kpi_cols[_ki % len(_kpi_cols)]:
                            st.markdown(f"""
                            <div style="background:#0F0F0F;border:1px solid #1E1E1E;
                                        border-top:2px solid {_clr};border-radius:4px;
                                        padding:0.6rem 0.7rem;height:100%;">
                              <div style="display:flex;align-items:center;gap:0.35rem;
                                          margin-bottom:0.3rem;">
                                <span style="font-size:0.85rem;">{_icon}</span>
                                <span style="font-family:IBM Plex Mono,monospace;font-size:0.48rem;
                                             color:{_clr};letter-spacing:0.1em;">{_dt}</span>
                              </div>
                              <div style="font-size:0.73rem;font-weight:600;color:#E8E8E8;
                                          margin-bottom:0.25rem;line-height:1.3;">{_kpi["name"]}</div>
                              <div style="font-size:0.62rem;color:#888;line-height:1.4;
                                          margin-bottom:0.3rem;">{_kpi["tells"]}</div>
                              <div style="font-size:0.58rem;color:#555;line-height:1.35;
                                          margin-bottom:0.25rem;font-style:italic;">{_kpi["decision"]}</div>
                              <div style="font-family:IBM Plex Mono,monospace;font-size:0.5rem;
                                          color:#3A3A3A;line-height:1.3;">{_kpi["sources"]}</div>
                            </div>""", unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:1.2rem;'></div>", unsafe_allow_html=True)

        # ── Imagen 3 Studio
        st.markdown("---")
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;'
                    'letter-spacing:0.18em;color:#F5A623;margin-bottom:0.6rem;">'
                    '▸ IMAGEN 3 GENERATIVE STUDIO</div>', unsafe_allow_html=True)

        if scored_signals:
            ic1, ic2, ic3 = st.columns([2, 1, 1])
            with ic1:
                img_signal = st.selectbox(
                    "Signal for generation",
                    [s.get("niche_keyword","") for s in scored_signals],
                )
            with ic2:
                inf_id = st.text_input("Influencer ID", value="INF001")
            with ic3:
                trend_id_val = st.text_input("Trend ID", value="TRD001")

            if st.button("🎨  Generate with Imagen 3", use_container_width=True):
                script = Path("scripts/generate_trend_image.py")
                if script.exists():
                    import subprocess
                    with st.spinner("Calling Imagen 3…"):
                        r = subprocess.run(
                            ["python", str(script),
                             "--influencer-id", inf_id,
                             "--trend-id", trend_id_val],
                            capture_output=True, text=True, timeout=120)
                    if r.returncode == 0:
                        st.success("✅ Imagen 3 generation complete")
                        st.code(r.stdout)
                        for p in list(Path("outputs").glob("*.png"))[:3] if Path("outputs").exists() else []:
                            st.image(str(p), caption=p.name, use_container_width=True)
                    else:
                        st.warning(f"Script error:\n{r.stderr}")
                else:
                    st.info("ℹ️ `scripts/generate_trend_image.py` not found. "
                            "Place it in your project root to enable Imagen 3.")

        # ── VTO
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;'
                    'letter-spacing:0.18em;color:#F5A623;margin:1rem 0 0.6rem;">'
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
                      color:#666;letter-spacing:0.12em;text-transform:uppercase;">
            {run_layer} LAYER OUTPUT &nbsp;·&nbsp; {run_fd}</div>
          <div style="font-size:1.05rem;font-weight:600;color:#E8E8E8;margin-top:0.12rem;">
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
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.62rem;'
                    'letter-spacing:0.2em;color:#F5A623;margin-bottom:1rem;">'
                    '▸ REFLECTION AGENT — GOVERNANCE &amp; BRAND SAFETY REVIEW</div>',
                    unsafe_allow_html=True)

        if st.session_state.reflection_output:
            st.markdown(st.session_state.reflection_output)
        elif active_branch_run in REVIEW_BRANCHES:
            st.info("Governance review will appear here after the pipeline runs.")
        else:
            st.markdown(f"""
            <div style="border:1px solid #2A2A2A;border-radius:6px;padding:1.2rem;
                        background:#0F0F0F;text-align:center;">
              <div style="font-size:0.82rem;color:#666;">
                Governance review is not required for the
                <strong style="color:#F5A623;">{BRANCH_LABELS.get(active_branch_run, active_branch_run)}</strong>
                branch.<br>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#444;">
                  Reflection Agent activates for: commercial, execution,
                  field-action, and governance routes.
                </span>
              </div>
            </div>""", unsafe_allow_html=True)

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
            font-size:0.58rem;color:#2A2A2A;letter-spacing:0.12em;">
  TIGER ANALYTICS &nbsp;·&nbsp; SENSE &amp; RESPOND OS &nbsp;·&nbsp;
  BLEEDING SIGNALS ENGINE &nbsp;·&nbsp; GROQ + LLAMA-3.3-70B-VERSATILE
</div>""", unsafe_allow_html=True)