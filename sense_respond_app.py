import streamlit as st
import json
import pandas as pd
import re
import os
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# GUARD: require groq
# ─────────────────────────────────────────────────────────────────────────────
try:
    from groq import Groq
except ImportError:
    st.error("CRITICAL: 'groq' library missing. Run: pip install groq")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & BRANDING
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="TigerTrend | Sense & Respond",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    st.logo("tiger_logo.png", icon_image="tiger_logo.png")
except Exception:
    pass

# defined css
def inject_css():
    css_file = Path(__file__).resolve().parent / "style.css"
    if css_file.exists():
        css = css_file.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"style.css not found at {css_file}; custom Streamlit styles were not loaded.")


inject_css()

# ══════════════════════════════════════════════════════════════════════════════
# 2. TAXONOMY  (matches n8n 00_Config_Registry)
# ══════════════════════════════════════════════════════════════════════════════
TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Retail": {
        "Fashion & Apparel":      ["Merchandising & Buying", "Demand Forecasting", "Pricing & Promotions", "Supply Chain & Sourcing", "Marketing & Campaign Mgmt", "Customer Analytics"],
        "Grocery & Supermarket":  ["Category Management", "Promotions & Trade Marketing", "Replenishment & Ordering", "Supplier Management", "Store Operations"],
        "Beauty & Cosmetics":     ["Product Development & Innovation", "Influencer & Content Marketing", "Loyalty & CRM", "Assortment Planning", "Trade Marketing"],
        "E-commerce Marketplace": ["Seller/Vendor Management", "Pricing Algorithms", "Customer Acquisition", "Logistics & Fulfillment", "Reviews & Ratings"],
    },
    "CPG & FMCG": {
        "Food & Beverage":        ["Trade Promotion Management", "Revenue Growth Management", "Demand Sensing", "Innovation Pipeline", "Shopper Marketing"],
        "Beauty & Personal Care": ["Brand Marketing", "R&D & Formulation", "Consumer Insights", "Influencer & Digital", "Pricing & Promo"],
        "Packaged Foods":         ["Revenue Growth Management", "Trade Promotions", "Demand Planning", "Supply Network", "Sustainability"],
        "Household Products":     ["Category Development", "Trade Marketing", "Demand Planning", "Retailer Collaboration", "Cost Optimization"],
    },
    "Banking & Financial Services": {
        "Retail Banking":    ["Customer Acquisition & Onboarding", "Fraud Detection", "Digital Banking", "Churn & Retention", "Credit Risk"],
        "Wealth Management": ["Portfolio Management", "Client Advisory", "Risk Profiling", "Compliance & Suitability"],
        "FinTech":           ["Product & Engineering", "Growth & Acquisition", "Fraud & Identity", "Lending & Credit"],
        "Insurance":         ["Underwriting", "Claims Management", "Actuarial & Pricing", "Fraud Detection", "Customer Retention"],
    },
    "Healthcare & Life Sciences": {
        "Pharmaceuticals":    ["Drug R&D & Pipeline", "Market Access & Pricing", "Medical Affairs", "Regulatory Affairs", "Sales Force Effectiveness"],
        "Hospitals & Providers": ["Clinical Operations", "Patient Experience", "Revenue Cycle Management", "Quality & Safety"],
        "Medical Devices":    ["Product Engineering", "Regulatory & Quality", "Clinical Evidence", "Sales & Distribution"],
    },
    "Technology & SaaS": {
        "SaaS Platforms":   ["Customer Success", "Growth & PLG", "Revenue Operations", "Pricing & Packaging"],
        "AI Platforms":     ["ML Engineering & Research", "Go-to-Market", "Ethics & Safety", "Data Engineering"],
        "Cybersecurity":    ["Threat Intelligence", "SOC Operations", "Compliance & GRC", "Sales Engineering"],
    },
    "Manufacturing": {
        "Automotive":         ["Production Planning", "Supply Chain & Procurement", "Quality Management", "EV Transition", "Dealer Network"],
        "Semiconductor":      ["Fab Operations", "Yield Engineering", "Supply Chain & Materials", "R&D & IP"],
        "Industrial Equipment": ["Predictive Maintenance", "Engineering & Product Dev", "OEM & Channel Sales", "Service & Parts"],
    },
    "Logistics & Supply Chain": {
        "3PL":              ["Warehouse Management", "Transportation Management", "Network Design", "Customer Operations"],
        "Last-Mile Delivery": ["Delivery Route Optimization", "Driver Experience", "Customer Communication", "Urban Logistics"],
        "Freight Forwarding": ["Ocean & Air Freight Operations", "Customs & Compliance", "Quoting & Pricing", "Trade Lane Development"],
    },
}

# ── Persona layer definitions (7 layers from our mapping work) ──────────────
PERSONA_LAYERS = {
    "Executive":    {"color": "#1E293B", "bg": "#E2E8F0", "desc": "C-level and C-1 leaders setting direction and approving strategy", "freq": "Quarterly / major shifts"},
    "Strategic":    {"color": "#4C1D95", "bg": "#EDE9FE", "desc": "Directors and VPs translating strategy into plans and roadmaps",   "freq": "Monthly / category shifts"},
    "Operational":  {"color": "#92400E", "bg": "#FEF3C7", "desc": "Managers owning functional KPIs and day-to-day operations",        "freq": "Weekly / in-market moves"},
    "Analytical":   {"color": "#1D4ED8", "bg": "#DBEAFE", "desc": "Analysts and data scientists producing insight from data",         "freq": "Daily to weekly / raw signals"},
    "Technical":    {"color": "#065F46", "bg": "#D1FAE5", "desc": "Engineers and specialists building and maintaining systems",        "freq": "Ad hoc / precision signals"},
    "Frontline":    {"color": "#9A3412", "bg": "#FFEDD5", "desc": "Customer-facing and field execution roles",                        "freq": "Real-time / local signals"},
    "Governance":   {"color": "#831843", "bg": "#FCE7F3", "desc": "Risk, compliance, legal and regulatory oversight roles",           "freq": "Forward-looking / 3-18 month horizon"},
}

# ── Persona role → layer mapping (subset; extend as needed) ─────────────────
ROLE_TO_LAYER: Dict[str, str] = {
    # Executive
    "Chief Marketing Officer": "Executive", "Chief Supply Chain Officer": "Executive",
    "Chief Digital Officer": "Executive",   "Chief Risk Officer": "Executive",
    # Strategic
    "Brand Strategist": "Strategic", "Revenue Growth Manager": "Strategic",
    "Head of Merchandising": "Strategic", "Innovation Manager": "Strategic",
    "VP of Marketing": "Strategic", "Director of Procurement": "Strategic",
    "Content Acquisition Manager": "Strategic", "Market Access Manager": "Strategic",
    # Operational
    "Merchandiser": "Operational", "Marketing Manager": "Operational",
    "Trade Marketing Manager": "Operational", "Supply Chain Manager": "Operational",
    "Category Manager": "Operational", "Promotions Manager": "Operational",
    "CRM/Loyalty Manager": "Operational", "Brand Manager": "Operational",
    "Demand Planner": "Operational", "Product Manager": "Operational",
    "Pricing Manager": "Operational", "Key Account Manager": "Operational",
    "Customer Success Manager": "Operational",
    # Analytical
    "Data Analyst": "Analytical", "Pricing Analyst": "Analytical",
    "Consumer Insights Analyst": "Analytical", "Fraud Analyst": "Analytical",
    "Yield Analyst": "Analytical", "Revenue Assurance Manager": "Analytical",
    "Demand Sensing Analyst": "Analytical", "Churn Analyst": "Analytical",
    # Technical
    "ML Engineer": "Technical", "R&D Scientist": "Technical",
    "Process Engineer": "Technical", "Infrastructure Engineer": "Technical",
    "Yield Engineer": "Technical", "Data Engineer": "Technical",
    # Frontline
    "Store Manager": "Frontline", "Beauty Advisor": "Frontline",
    "Branch Manager": "Frontline", "Field Service Manager": "Frontline",
    "Sales Engineer": "Frontline",
    # Governance
    "Compliance Manager": "Governance", "Regulatory Affairs Manager": "Governance",
    "EHS Manager": "Governance", "Risk Analyst": "Governance",
    "AI Ethics Analyst": "Governance", "Trust & Safety Analyst": "Governance",
}

# ── n8n route branch mapping (mirrors 00_Config_Registry) ───────────────────
LAYER_TO_BRANCH: Dict[str, str] = {
    "Executive":    "commercial_with_review",
    "Strategic":    "commercial_with_review",
    "Operational":  "execution_with_review",
    "Analytical":   "evidence_artifact",
    "Technical":    "technical_artifact",
    "Frontline":    "field_action_with_review",
    "Governance":   "risk_review_only",
}

# ── Urgency levels ────────────────────────────────────────────────────────────
URGENCY = {
    "action":  {"label": "Action Now",  "bar": "sig-bar-action",  "badge": "badge-action",  "icon": "🔴"},
    "monitor": {"label": "Monitor",     "bar": "sig-bar-monitor", "badge": "badge-monitor", "icon": "🟡"},
    "horizon": {"label": "Horizon",     "bar": "sig-bar-horizon", "badge": "badge-horizon", "icon": "🟢"},
}

# ── UI display type meta ──────────────────────────────────────────────────────
UI_TYPE_META = {
    "TREND_SCORE":   {"label": "Trend Score",    "color": "#0369A1", "bg": "#E0F2FE"},
    "RANKED_LIST":   {"label": "Ranked List",    "color": "#166534", "bg": "#F0FDF4"},
    "HEAT_INDEX":    {"label": "Heat Index",     "color": "#9A3412", "bg": "#FFF7ED"},
    "SENTIMENT":     {"label": "Sentiment",      "color": "#7E22CE", "bg": "#FDF4FF"},
    "PRICE_TRACKER": {"label": "Price Tracker",  "color": "#991B1B", "bg": "#FEF2F2"},
    "EVENT_PULSE":   {"label": "Event Pulse",    "color": "#0C4A6E", "bg": "#F0F9FF"},
    "VELOCITY":      {"label": "Velocity",       "color": "#78350F", "bg": "#FFFBEB"},
}

# ══════════════════════════════════════════════════════════════════════════════
# 3. PROMPT LIBRARY  (anti-hallucination, grounded, structured)
# ══════════════════════════════════════════════════════════════════════════════

def build_synthesis_prompt(industry: str, sub_industry: str, domain: str,
                            persona_role: str, persona_layer: str,
                            region: str, time_window: str, brand_context: str) -> str:
    """
    Synthesis agent prompt.
    Rules that reduce hallucination:
      - Only draw from the evidence sources provided (no fabrication).
      - Use source IDs (S1, S2 …) to cite claims.
      - If a field cannot be grounded in evidence, write UNKNOWN.
      - No invented brand names, figures, or quotes.
      - Confidence must reflect actual source diversity, not optimism.
    """
    return f"""
        You are an autonomous market crawler for Tiger Analytics.

        TASK
        Identify 3 to 5 distinct, early-stage market signals from the EVIDENCE SOURCES provided below.
        Each signal must be directly traceable to at least one source in the evidence pack.

        CRITICAL REFINEMENT: THE "EAR-TO-THE-GROUND" KEYWORD ENGINE
        Strictly forbid generic keywords (e.g., "casual wear," "tech gadget"). You must only operate on hyper-niche, "ear-to-the-ground" cultural signals (e.g., "gorpcore utility vest," "clean-girl slick back").


        BUSINESS CONTEXT
        - Industry: {industry}
        - Sub-industry: {sub_industry}
        - Functional domain: {domain}
        - Persona role: {persona_role} ({persona_layer} layer)
        - Region: {region}
        - Time window: {time_window}
        - Brand context: {brand_context if brand_context else "Not provided"}

        STRICT RULES — FOLLOW EVERY ONE
        1. Every trend you identify MUST cite the source IDs that support it (e.g. "source_ids": ["S1","S4"]).
        2. Do NOT invent brand names, statistics, product names, or quotes.
        3. If you cannot find evidence for a field, write the string "UNKNOWN" — never fabricate.
        4. "niche_keyword" must be a specific phrase found in or strongly implied by the sources — not a generic category label. Bad example: "sustainable beauty". Good example: "waterless shampoo bars Gen Z TikTok".
        5. "confidence" must be LOW if only 1 source supports the trend, MEDIUM if 2-3, HIGH only if 4+ diverse sources agree.
        6. "emergence_window" must be based on actual publication dates in the sources, not assumed.
        7. "saturation_risk" must be LOW if the trend appears only in niche blogs/Reddit, MEDIUM if also in trade press, HIGH if already in mass-market news.
        8. Do not repeat the same trend with different wording.
        9. The "hero_insight" must be a single sentence that is directly supported by the evidence — no speculation.

        REQUIRED OUTPUT — return ONLY valid JSON, no markdown, no preamble:
        {{
            "hero_insight": "1-sentence macro trend revelation.",
            "trending_keywords": {{"Keyword One": 98, "Keyword Two": 85, "Keyword Three": 77}},
            "candidate_trends": [
                    {{
                    "niche_keyword": "string (hyper-niche subculture/aesthetic)",
                    "signal_summary": "string — 1-2 sentences explaining what the signal is and why it matters for {domain}",
                    "source_ids": ["S1", "S2"],
                    "bleeding_edge_virality_score": integer (1-100),
                    "velocity_metric": "string (e.g., +1200% mentions in 12h)",
                    "emergence_window": "string — e.g. 'past 7 days' or 'past 30 days', based on source dates",
                    "saturation_risk": "LOW | MEDIUM | HIGH",
                    "actionability_rating": "string (High - Ready for generation)",
                    "is_extreme_virality": boolean (true if score > 90 and velocity is exponential),
                    "extreme_action_directive": "string (Mandatory fast-track directive if extreme, else empty string)",
                    "ui_display_type": "TREND_SCORE | RANKED_LIST | HEAT_INDEX | SENTIMENT | PRICE_TRACKER | EVENT_PULSE | VELOCITY"
                    }}
                ]
        }}"""



def build_orchestration_prompt(industry: str, sub_industry: str, domain: str,
                                persona_role: str, persona_layer: str,
                                branch: str, scored_trends: list,
                                brand_context: str) -> str:
    """
    Orchestration agent prompt.
    Converts scored trends into persona-specific action artifacts.
    Anti-hallucination rules: grounded in trends provided, no invented data.
    """
    branch_instruction = {
        "commercial_with_review": f"You are advising a {persona_role} (Executive or Strategic layer). Produce board-ready recommendations, campaign territory ideas, and competitive positioning actions. Each recommendation must reference a specific trend from the input.",
        "execution_with_review":  f"You are advising a {persona_role} (Operational layer). Produce a prioritised execution checklist with specific in-week actions. Each action must be traceable to a specific trend.",
        "evidence_artifact":      f"You are advising a {persona_role} (Analytical layer). Produce an evidence matrix with scoring logic, assumptions, data gaps, and a measurement plan. Cite source evidence for every claim.",
        "technical_artifact":     f"You are advising a {persona_role} (Technical layer). Produce a data flow specification, API or integration expectations, reliability considerations, and technical risks. Reference specific trends.",
        "field_action_with_review": f"You are advising a {persona_role} (Frontline layer). Produce customer-facing talking points, objection handling, upsell opportunities, and local market actions. Ground each point in a specific trend.",
        "risk_review_only":       f"You are advising a {persona_role} (Governance layer). Review the trends for compliance risk, unsupported claims, brand safety issues, privacy implications, and required human review flags.",
    }.get(branch, f"You are advising a {persona_role}. Produce actionable recommendations grounded in the trends.")

    trends_text = json.dumps(scored_trends, indent=2)

    return f"""
        You are a strategic intelligence orchestrator for Tiger Analytics.

        ROLE INSTRUCTION
        {branch_instruction}

        BUSINESS CONTEXT
        - Industry: {industry} / {sub_industry}
        - Functional domain: {domain}
        - Brand context: {brand_context if brand_context else "Not provided"}

        SCORED TRENDS (your only permitted source of facts)
        {trends_text}

        CRITICAL RULES FOR IMAGES: 
        For 'persona_deliverables', the 'image_prompt' MUST be a description of a physical photograph or object based specifically on the hyper-niche SMART signals provided (e.g., "A highly detailed, photorealistic 8k studio photography of a mycelium leather trench coat, NO TEXT").


        STRICT RULES
        1. Every deliverable, recommendation, or risk you surface MUST reference the niche_keyword of a specific trend from the list above.
        2. Do NOT invent statistics, competitor names, campaign names, or product details not present in the trends.
        3. If a trend has HIGH saturation_risk, explicitly flag it as "late-cycle" in your output.
        4. Urgency assignment rules:
        - "action": saturation_risk=LOW AND confidence=HIGH AND arbitrage_index >= 0.7
        - "monitor": confidence=MEDIUM OR saturation_risk=MEDIUM
        - "horizon": confidence=LOW OR saturation_risk=HIGH (trend already mainstream)
        5. summaryMetrics values must be directional signals (e.g. "↑ Rising fast"), NOT fabricated percentages.
        6. Return ONLY valid JSON, no markdown, no preamble.

        REQUIRED OUTPUT:
        {{
        "trend_implication": "string — 2-3 sentence strategic framing of what these signals mean for {domain}, grounded in the trends",
        "summaryMetrics": [
            {{
            "label": "string — metric name relevant to {domain}",
            "value": "string — directional signal e.g. '↑ Rising', '⚠ Watch', '↓ Cooling'",
            "trend": "string — brief qualifier e.g. 'vs prior month'",
            "status": "positive | negative | neutral"
            }}
        ],
        "signal_cards": [
            {{
            "title": "string — signal name (use niche_keyword)",
            "ui_display_type": "string — from TREND_SCORE | RANKED_LIST | HEAT_INDEX | SENTIMENT | PRICE_TRACKER | EVENT_PULSE | VELOCITY",
            "value": "string — headline figure or label e.g. '87 / 100' or 'Accelerating'",
            "delta": "string — change description e.g. '+12pts this week'",
            "direction": "up | down | flat",
            "urgency": "action | monitor | horizon",
            "insight": "string — 2-3 sentence interpretation grounded in the trend evidence",
            "data_source": "string — source types used e.g. 'Reddit RSS + Google News RSS + Glossy'",
            "suggested_action": "string — one specific, persona-appropriate action the {persona_role} should take"
            }}
        ],
        "strategic_pillars": [
            {{
            "title": "string",
            "description": "string — grounded in at least one trend"
            }}
        ],
        
        "persona_deliverables": [ {{"title": "string", "description": "string", "image_prompt": "string"}} ],
        "chatQuickStart": [
            "string — relevant question the {persona_role} would ask about these signals",
            "string",
            "string"
        ]
        }}"""


def build_reflection_prompt(industry: str, sub_industry: str, domain: str,
                             persona_role: str, proposed_output: dict) -> str:
    """
    Reflection / governance agent prompt.
    Checks the orchestration output for unsupported claims, bias, brand risk.
    """
    output_text = json.dumps(proposed_output, indent=2)
    return f"""You are a governance and quality-review agent for Tiger Analytics.

        YOUR TASK
        Review the proposed output below for the following issues:
        1. Unsupported claims — statements made without grounding in the evidence trends.
        2. Overconfidence — claims stated as certain when confidence is LOW or MEDIUM.
        3. Brand safety — messaging that could cause reputational harm.
        4. Regulatory or compliance risk — claims that could breach advertising, data, or industry regulations.
        5. Privacy risk — any signals that rely on or imply individual-level tracking.

        CONTEXT
        - Industry: {industry} / {sub_industry}
        - Functional domain: {domain}
        - Persona role: {persona_role}

        PROPOSED OUTPUT TO REVIEW
        {output_text}

        STRICT RULES
        1. Do NOT rewrite the output — only flag issues.
        2. For each issue found, cite the exact field and text that is problematic.
        3. If no issues are found in a category, write "CLEAR".
        4. Your confidence_in_review must be HIGH only if you can point to a specific rule, regulation, or logical error.
        5. Return ONLY valid JSON, no markdown, no preamble.

        REQUIRED OUTPUT:
        {{
        "review_passed": true | false,
        "unsupported_claims": ["string — quote the exact claim and explain why it is unsupported" | "CLEAR"],
        "overconfidence_flags": ["string" | "CLEAR"],
        "brand_safety_flags": ["string" | "CLEAR"],
        "compliance_flags": ["string" | "CLEAR"],
        "privacy_flags": ["string" | "CLEAR"],
        "recommended_edits": ["string — specific suggested fix" | "NONE"],
        "human_review_required": true | false,
        "confidence_in_review": "LOW | MEDIUM | HIGH"
        }}"""


def build_chat_system_prompt(industry: str, sub_industry: str, domain: str,
                              persona_role: str, persona_layer: str,
                              signal_cards: list, brand_context: str) -> str:
    """
    System prompt for the chat agent.
    Grounded in the actual signal cards shown on screen.
    """
    cards_text = json.dumps(signal_cards, indent=2) if signal_cards else "No signals loaded yet."
    layer_cfg = PERSONA_LAYERS.get(persona_layer, PERSONA_LAYERS["Operational"])

    return f"""You are Sense AI — an external market intelligence agent built by Tiger Analytics.

        YOUR USER
        - Role: {persona_role} ({persona_layer} layer)
        - Layer description: {layer_cfg['desc']}
        - Industry: {industry} / {sub_industry}
        - Functional domain: {domain}
        - Brand context: {brand_context if brand_context else "Not provided"}

        SIGNALS CURRENTLY ON SCREEN
        {cards_text}

        YOUR JOB
        Answer questions about the signals above. Help the user interpret trends, understand urgency levels, 
        compare signals, and decide what action to take next.

        STRICT RULES
        1. Only reference facts from the signal cards shown above or well-established public knowledge.
        2. Do NOT invent statistics, brand names, product details, or competitor data.
        3. If the user asks about something not covered by the signals, say so clearly and offer what you can from the signals.
        4. Tailor your language and depth to a {persona_layer} persona — {layer_cfg['desc']}.
        5. Keep responses concise and action-oriented. End every response with one clear next step.
        6. Never use the phrases "As an AI language model" or "I cannot browse the internet."
        """

# ══════════════════════════════════════════════════════════════════════════════
# 4. BACKEND ENGINES
# ══════════════════════════════════════════════════════════════════════════════

def call_groq(client: Groq, system_prompt: str, user_content: str,
              temperature: float = 0.2, max_tokens: int = 1200) -> Optional[dict]:
    """
    Single reusable Groq caller (mirrors 01_Agent_Runner).
    Returns parsed JSON dict or None on failure.
    """
    try:
        resp = client.chat.completions.create(
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": user_content},
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        raw = resp.choices[0].message.content
        return json.loads(raw)
    except json.JSONDecodeError as e:
        st.warning(f"JSON parse error from Groq: {e}")
        return None
    except Exception as e:
        st.warning(f"Groq call failed: {e}")
        return None


def simulate_source_ingestion(industry: str, sub_industry: str,
                               domain: str, region: str) -> list:
    """
    Mirrors 02_Source_Ingestion from n8n.
    Simulates a 17-source evidence pack across 5 source type categories:
      - industry_blog   (trade press)
      - reddit_rss      (Reddit communities)
      - google_news     (mainstream news)
      - tiktok          (TikTok hashtag/creator signals)
      - instagram       (Instagram hashtag/Reel signals)
      - threads         (Threads conversation signals)
 
    In production: replace with real n8n webhook results.
    Each source has a consistent schema:
      id, source_type, source_name, platform_signal_type,
      title, snippet, engagement_signal, date
    """
    mock_sources = [
 
        # ── Industry / Trade Press ────────────────────────────────────────────
        {
            "id": "S1",
            "source_type": "industry_blog",
            "source_name": "Glossy",
            "platform_signal_type": "editorial_article",
            "title": f"How {sub_industry} brands are rethinking {domain} strategy in {region}",
            "snippet": f"Early signals from {sub_industry} indicate a structural shift toward hyper-targeted micro-communities over mass-market channels. Brands investing early in niche community engagement are reporting higher conversion rates.",
            "engagement_signal": "N/A — editorial",
            "date": "2026-05-10",
        },
        {
            "id": "S2",
            "source_type": "industry_blog",
            "source_name": "Retail Dive",
            "platform_signal_type": "editorial_article",
            "title": f"Technology adoption in {domain} — what early movers are doing differently",
            "snippet": f"Operators using real-time signal tools in {domain} are adjusting strategy 2–3 weeks ahead of competitors still relying on lagging sales data. First-mover advantage in {sub_industry} is increasingly driven by speed of insight.",
            "engagement_signal": "N/A — editorial",
            "date": "2026-05-07",
        },
        {
            "id": "S3",
            "source_type": "industry_blog",
            "source_name": "Vogue Business",
            "platform_signal_type": "editorial_article",
            "title": f"Sustainability expectations reshaping {sub_industry} product development",
            "snippet": "Consumers and investors are applying simultaneous pressure on brands for verifiable sustainability claims backed by data, not aspirational messaging. Brands with auditable supply chains are gaining consideration share.",
            "engagement_signal": "N/A — editorial",
            "date": "2026-05-06",
        },
 
        # ── Reddit ────────────────────────────────────────────────────────────
        {
            "id": "S4",
            "source_type": "reddit_rss",
            "source_name": "Reddit",
            "platform_signal_type": "community_thread",
            "title": f"r/{sub_industry.replace(' ', '')} — community actively debating {domain} changes",
            "snippet": f"High-engagement Reddit thread with 1.2k upvotes discussing niche product variants in {sub_industry}. Community is using specific terminology not yet appearing in mainstream advertising — strong leading indicator of emerging consumer language.",
            "engagement_signal": "1.2k upvotes, 340 comments, 94% upvote ratio",
            "date": "2026-05-13",
        },
        {
            "id": "S5",
            "source_type": "reddit_rss",
            "source_name": "Reddit",
            "platform_signal_type": "community_thread",
            "title": f"Price sensitivity and brand loyalty debate in r/{industry.replace(' ', '')}",
            "snippet": "Consumer language shifting from brand loyalty to active value comparison. Multiple threads documenting switching intent, with users citing specific price thresholds and feature trade-offs. Volume of switching-intent posts up 3× vs. prior month.",
            "engagement_signal": "890 upvotes, 210 comments",
            "date": "2026-05-14",
        },
 
        # ── Google News / Mainstream ──────────────────────────────────────────
        {
            "id": "S6",
            "source_type": "google_news",
            "source_name": "Google News",
            "platform_signal_type": "news_aggregation",
            "title": f"{industry} market update: {sub_industry} segment sees accelerating interest in {region}",
            "snippet": f"Trade analysts note accelerating consumer interest in {sub_industry} categories in {region}, with early traction in specialist channels before mass-market retailers. Category search volume up 28% MoM per Google Trends data.",
            "engagement_signal": "High news velocity — 47 related articles in 7 days",
            "date": "2026-05-11",
        },
        {
            "id": "S7",
            "source_type": "google_news",
            "source_name": "Reuters",
            "platform_signal_type": "wire_news",
            "title": f"Regulatory and trade developments affecting {industry} supply chain in {region}",
            "snippet": "New trade and sustainability regulations coming into force in Q3 2026 could materially affect sourcing strategies and landed cost assumptions. Legal analysts flagging 60-day compliance window for most affected operators.",
            "engagement_signal": "N/A — wire news",
            "date": "2026-05-08",
        },
        {
            "id": "S8",
            "source_type": "google_news",
            "source_name": "Bloomberg",
            "platform_signal_type": "financial_news",
            "title": f"Input cost volatility and margin pressure across {industry}",
            "snippet": "Raw material and logistics cost pressures are compressing operating margins sector-wide. Analyst consensus expects continued volatility through Q3, forcing pricing strategy reviews and accelerating nearshoring conversations.",
            "engagement_signal": "N/A — financial news",
            "date": "2026-05-05",
        },
 
        # ── TikTok ────────────────────────────────────────────────────────────
        {
            "id": "S9",
            "source_type": "tiktok",
            "source_name": "TikTok",
            "platform_signal_type": "hashtag_trend",
            "title": f"#{sub_industry.replace(' ', '').lower()} trending — rapid hashtag acceleration in {region}",
            "snippet": f"#{sub_industry.replace(' ', '').lower()} hashtag accumulating 4.2M views in past 7 days, up from 800k the prior week — a 5.25× acceleration. Creator content focussed on specific product formats not yet stocked by mainstream retailers. Strong 'discovery' pattern consistent with early-stage trend.",
            "engagement_signal": "4.2M views, 380k likes, 92k shares, 18k saves in 7 days",
            "date": "2026-05-14",
        },
        {
            "id": "S10",
            "source_type": "tiktok",
            "source_name": "TikTok",
            "platform_signal_type": "creator_signal",
            "title": f"Mid-tier creators (100k–500k followers) driving {domain} conversation on TikTok",
            "snippet": f"Cluster of 14 mid-tier creators in the {sub_industry} space posting similar content formats around {domain} themes within the same 72-hour window — a coordinated organic signal pattern historically predictive of category breakout. None are paid by major brands yet.",
            "engagement_signal": "Avg 280k views per video, 8.4% engagement rate (benchmark: 3.2%)",
            "date": "2026-05-13",
        },
        {
            "id": "S11",
            "source_type": "tiktok",
            "source_name": "TikTok",
            "platform_signal_type": "comment_sentiment",
            "title": f"TikTok comment analysis: {sub_industry} consumer intent signals",
            "snippet": f"NLP analysis of top 500 comments on {sub_industry}-related TikTok content reveals purchase-intent language ('need this', 'where to buy', 'just ordered') in 34% of comments — significantly above the 12% platform benchmark. Strongest signal in 18–28 age cohort.",
            "engagement_signal": "Purchase-intent comment rate: 34% vs. 12% benchmark",
            "date": "2026-05-12",
        },
 
        # ── Instagram ─────────────────────────────────────────────────────────
        {
            "id": "S12",
            "source_type": "instagram",
            "source_name": "Instagram",
            "platform_signal_type": "hashtag_trend",
            "title": f"Instagram Reels driving {sub_industry} discovery in {region}",
            "snippet": f"Instagram Reels content tagged #{sub_industry.replace(' ', '').lower()} receiving 2.8M impressions this week, with save rate of 6.1% indicating high purchase consideration. Dominant content format: 'before/after' and 'unboxing' — both historically correlated with new product adoption curves.",
            "engagement_signal": "2.8M impressions, 6.1% save rate, 4.3% share rate",
            "date": "2026-05-13",
        },
        {
            "id": "S13",
            "source_type": "instagram",
            "source_name": "Instagram",
            "platform_signal_type": "influencer_signal",
            "title": f"Nano and micro influencers leading {domain} conversation ahead of macro influencers",
            "snippet": f"Nano influencers (5k–20k followers) in the {sub_industry} category are posting {domain}-related content at 3× the rate of macro influencers, with 2.4× higher engagement rates. This inversion of typical influencer cascade patterns suggests genuine grassroots consumer movement rather than paid campaign activity.",
            "engagement_signal": "Nano influencer avg engagement: 7.8% vs. macro avg 1.9%",
            "date": "2026-05-11",
        },
        {
            "id": "S14",
            "source_type": "instagram",
            "source_name": "Instagram",
            "platform_signal_type": "stories_poll_signal",
            "title": f"Instagram Stories polls reveal consumer preference shift in {sub_industry}",
            "snippet": f"Aggregated data from public Instagram Stories polls in the {sub_industry} category show 67% of respondents preferring emerging product formats over established category leaders — a 22-point shift vs. equivalent polls 6 months ago. Strongest shift in the 25–34 demographic.",
            "engagement_signal": "12.4k poll responses aggregated, 67% emerging format preference",
            "date": "2026-05-10",
        },
 
        # ── Threads ───────────────────────────────────────────────────────────
        {
            "id": "S15",
            "source_type": "threads",
            "source_name": "Threads",
            "platform_signal_type": "conversation_thread",
            "title": f"Threads conversations surfacing critical {sub_industry} consumer perspectives",
            "snippet": f"Threads posts from verified industry professionals and engaged consumers in {sub_industry} are surfacing specific product criticisms and feature requests not appearing in formal review platforms. Recurring themes: ingredient transparency, packaging frustration, and demand for accessible price-points in premium formats.",
            "engagement_signal": "Top thread: 4.2k replies, 8.9k reposts in 48 hours",
            "date": "2026-05-14",
        },
        {
            "id": "S16",
            "source_type": "threads",
            "source_name": "Threads",
            "platform_signal_type": "brand_conversation",
            "title": f"Competitor brand comparison conversations accelerating on Threads",
            "snippet": f"Unprompted brand comparison threads in the {sub_industry} space are generating significantly higher engagement than brand-owned content. Consumers explicitly naming switching triggers and unmet needs. Three competitor brands mentioned negatively in >40% of comparison threads.",
            "engagement_signal": "Avg 1.8k replies per comparison thread, 72% organic (non-paid)",
            "date": "2026-05-12",
        },
        {
            "id": "S17",
            "source_type": "threads",
            "source_name": "Threads",
            "platform_signal_type": "expert_discourse",
            "title": f"Industry experts debating {domain} strategy shifts on Threads",
            "snippet": f"Cluster of {industry} practitioners with 10k–80k Threads followers actively debating {domain} strategy in public threads. Consensus emerging around 3 key themes: speed-to-market pressure, data-driven localisation, and the decline of broad demographic targeting in favour of psychographic micro-segments.",
            "engagement_signal": "Expert thread cluster: 6.7k total replies, high repost-to-like ratio (0.38)",
            "date": "2026-05-09",
        },
    ]
    return mock_sources


def score_trends(candidate_trends: list) -> list:
    """
    Mirrors the Score Acceleration + Saturation node in n8n.
    Deterministic scoring — no LLM call needed.
    """
    confidence_weight = {"LOW": 0.3, "MEDIUM": 0.6, "HIGH": 0.9}
    saturation_bonus  = {"LOW": 0.4, "MEDIUM": 0.2, "HIGH": 0.0}
    urgency_map = {
        ("HIGH", "LOW"):    "action",
        ("HIGH", "MEDIUM"): "monitor",
        ("MEDIUM", "LOW"):  "monitor",
        ("MEDIUM", "MEDIUM"): "monitor",
        ("HIGH", "HIGH"):   "horizon",
        ("MEDIUM", "HIGH"): "horizon",
        ("LOW", "LOW"):     "horizon",
        ("LOW", "MEDIUM"):  "horizon",
        ("LOW", "HIGH"):    "horizon",
    }

    scored = []
    for t in candidate_trends:
        conf     = t.get("confidence", "MEDIUM")
        sat      = t.get("saturation_risk", "MEDIUM")
        n_sources = len(t.get("source_ids", []))

        # Specificity bonus: longer keywords are more niche
        specificity = min(len(t.get("niche_keyword", "").split()) * 0.05, 0.2)
        acc_score   = round(confidence_weight[conf] + saturation_bonus[sat] + specificity + min(n_sources * 0.04, 0.2), 3)
        arb_index   = round((confidence_weight[conf] * 0.5 + saturation_bonus[sat] * 0.3 + specificity * 0.2), 3)
        urgency     = urgency_map.get((conf, sat), "monitor")

        scored.append({
            **t,
            "acceleration_score": acc_score,
            "saturation_risk":    sat,
            "arbitrage_index":    arb_index,
            "urgency":            urgency,
        })

    # Sort by arbitrage_index descending
    return sorted(scored, key=lambda x: x["arbitrage_index"], reverse=True)


def run_full_pipeline(
    client: Groq,
    industry: str, sub_industry: str, domain: str, persona_role: str,
    persona_layer: str, region: str, time_window: str, brand_context: str,
) -> dict:
    """
    End-to-end pipeline mirroring 03_Main_Trend_Discovery in n8n.
    Returns the final output dict.
    """
    branch = LAYER_TO_BRANCH.get(persona_layer, "execution_with_review")

    # Step 1 — Source ingestion (simulate n8n 02_Source_Ingestion)
    sources = simulate_source_ingestion(industry, sub_industry, domain, region)
    sources_text = json.dumps(sources, indent=2)

    # Step 2 — Synthesis agent
    synthesis_sys = build_synthesis_prompt(
        industry, sub_industry, domain, persona_role, persona_layer,
        region, time_window, brand_context,
    )
    synthesis_result = call_groq(
        client,
        system_prompt=synthesis_sys,
        user_content=f"EVIDENCE SOURCES:\n{sources_text}",
        temperature=0.2,
        max_tokens=1200,
    )
    if not synthesis_result:
        synthesis_result = {
            "hero_insight": "Signal synthesis is unavailable. Please retry.",
            "candidate_trends": [],
        }

    # Step 3 — Score trends
    scored_trends = score_trends(synthesis_result.get("candidate_trends", []))

    # Step 4 — Orchestration agent
    orch_sys = build_orchestration_prompt(
        industry, sub_industry, domain, persona_role, persona_layer,
        branch, scored_trends, brand_context,
    )
    orch_result = call_groq(
        client,
        system_prompt=orch_sys,
        user_content="Generate the persona-specific action artifact based on the scored trends.",
        temperature=0.25,
        max_tokens=1400,
    )

    # Step 5 — Reflection agent (only for branches that need review)
    reflection_result = None
    if branch in ("commercial_with_review", "execution_with_review",
                  "field_action_with_review", "risk_review_only"):
        ref_sys = build_reflection_prompt(
            industry, sub_industry, domain, persona_role, orch_result or {}
        )
        reflection_result = call_groq(
            client,
            system_prompt=ref_sys,
            user_content="Review the proposed output.",
            temperature=0.1,
            max_tokens=600,
        )

    return {
        "hero_insight":      synthesis_result.get("hero_insight", ""),
        "scored_trends":     scored_trends,
        "orchestration":     orch_result or {},
        "reflection":        reflection_result,
        "branch":            branch,
        "sources_ingested":  len(sources),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 5. SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
defaults = {
    "pipeline_result":   None,
    "chat_history":      [],
    "pending_prompt":    None,
    "expanded_card":     None,
    "persona_layer":     None,
    "persona_role":      None,
    "industry":          None,
    "sub_industry":      None,
    "domain":            None,
    "brand_context":     "",
    "region":            "Global",
    "time_window":       "last 7 days",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# 6. SIDEBAR — CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='font-size:18px; font-weight:800; color:#0F172A; margin-bottom:4px;'>
        TigerTrend
    </div>
    <div style='font-size:11px; color:#94A3B8; margin-bottom:20px; text-transform:uppercase; letter-spacing:0.08em;'>
        Sense & Respond Intelligence
    </div>
    """, unsafe_allow_html=True)

    # ── Step 1: Industry cascade ─────────────────────────────────────────────
    st.markdown("#### 1 · Market Context")
    industry = st.selectbox("Industry", [""] + list(TAXONOMY.keys()), key="sel_industry")
    sub_industries = list(TAXONOMY.get(industry, {}).keys()) if industry else []
    sub_industry = st.selectbox("Sub-industry", [""] + sub_industries, key="sel_sub", disabled=not industry)
    domains = TAXONOMY.get(industry, {}).get(sub_industry, []) if sub_industry else []
    domain = st.selectbox("Functional Domain", [""] + domains, key="sel_domain", disabled=not sub_industry)

    st.divider()

    # ── Step 2: Persona ──────────────────────────────────────────────────────
    st.markdown("#### 2 · Your Persona")
    all_roles = sorted(set(ROLE_TO_LAYER.keys()))
    persona_role = st.selectbox("Role", [""] + all_roles, key="sel_role", disabled=not domain)

    if persona_role:
        persona_layer = ROLE_TO_LAYER.get(persona_role, "Operational")
        layer_cfg     = PERSONA_LAYERS[persona_layer]
        st.markdown(f"""
        <div style='background:{layer_cfg["bg"]}; border-radius:8px; padding:10px 12px; margin-top:6px;'>
            <span style='font-size:11px; font-weight:700; color:{layer_cfg["color"]};'>{persona_layer} Layer</span><br>
            <span style='font-size:11px; color:#64748B;'>{layer_cfg["desc"]}</span><br>
            <span style='font-size:10px; color:#94A3B8; margin-top:4px; display:block;'>🔄 Refresh frequency: {layer_cfg["freq"]}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        persona_layer = "Operational"

    st.divider()

    # ── Step 3: Optional context ─────────────────────────────────────────────
    st.markdown("#### 3 · Optional Context")
    region       = st.selectbox("Region", ["Global", "North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa"])
    time_window  = st.selectbox("Time Window", ["last 7 days", "last 14 days", "last 30 days"])
    brand_context = st.text_area("Brand / Product Context", placeholder="e.g. Premium beauty brand targeting Gen Z in North America…", height=80)

    st.divider()

    # ── API key + run ────────────────────────────────────────────────────────
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Add GROQ_API_KEY to .streamlit/secrets.toml")
        st.stop()

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    can_run = bool(industry and sub_industry and domain and persona_role)
    if st.button("⚡  Run Signal Discovery", type="primary", use_container_width=True, disabled=not can_run):
        with st.spinner(f"Running pipeline for {persona_layer} persona…"):
            result = run_full_pipeline(
                client, industry, sub_industry, domain, persona_role,
                persona_layer, region, time_window, brand_context,
            )
            st.session_state.pipeline_result  = result
            st.session_state.persona_layer     = persona_layer
            st.session_state.persona_role      = persona_role
            st.session_state.industry          = industry
            st.session_state.sub_industry      = sub_industry
            st.session_state.domain            = domain
            st.session_state.brand_context     = brand_context
            st.session_state.region            = region
            st.session_state.time_window       = time_window
            st.session_state.chat_history      = []
            st.session_state.expanded_card     = None

    if not can_run:
        missing = []
        if not industry:     missing.append("Industry")
        if not sub_industry: missing.append("Sub-industry")
        if not domain:       missing.append("Domain")
        if not persona_role: missing.append("Role")
        st.caption(f"Complete: {', '.join(missing)}")

# ══════════════════════════════════════════════════════════════════════════════
# 7. MAIN PANE
# ══════════════════════════════════════════════════════════════════════════════

if not st.session_state.pipeline_result:
    # ── Empty state ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style='padding:6rem 2rem; text-align:center; color:#94A3B8;'>
        <div style='font-size:40px; margin-bottom:12px;'>◈</div>
        <div style='font-size:18px; font-weight:700; color:#CBD5E1; margin-bottom:8px;'>Configure your intelligence view</div>
        <div style='font-size:14px;'>Select Industry → Sub-industry → Domain → Role in the sidebar, then hit Run.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Unpack session ────────────────────────────────────────────────────────────
res           = st.session_state.pipeline_result
orch          = res.get("orchestration", {})
reflection    = res.get("reflection")
scored_trends = res.get("scored_trends", [])
signal_cards  = orch.get("signal_cards", [])
p_layer       = st.session_state.persona_layer
p_role        = st.session_state.persona_role
p_cfg         = PERSONA_LAYERS.get(p_layer, PERSONA_LAYERS["Operational"])
ind           = st.session_state.industry
sub           = st.session_state.sub_industry
dom           = st.session_state.domain

col_dash, col_chat = st.columns([3, 1.25], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# 7A. DASHBOARD COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_dash:

    # ── Persona context banner ────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:{p_cfg["bg"]}; border:1.5px solid {p_cfg["color"]}30;
                border-radius:12px; padding:14px 18px; margin-bottom:18px;
                display:flex; align-items:center; gap:14px;'>
        <div style='flex:1;'>
            <span style='font-size:13px; font-weight:700; color:{p_cfg["color"]};'>{p_role}</span>
            <span style='font-size:12px; color:#64748B;'> · {p_layer} Layer · {p_cfg["desc"]}</span>
        </div>
        <div style='text-align:right; font-size:11px; color:#94A3B8;'>
            {ind} › {sub}<br>
            <span style='color:{p_cfg["color"]}; font-weight:600;'>{dom}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Governance reflection alert ───────────────────────────────────────────
    if reflection and not reflection.get("review_passed", True):
        flags = [f for f in [
            reflection.get("unsupported_claims", "CLEAR"),
            reflection.get("brand_safety_flags", "CLEAR"),
            reflection.get("compliance_flags", "CLEAR"),
        ] if f != "CLEAR"]
        if flags:
            with st.expander("⚠️ Governance review flagged issues — click to review", expanded=False):
                st.warning("The reflection agent found the following issues in the generated output:")
                for flag_list in flags:
                    if isinstance(flag_list, list):
                        for f in flag_list:
                            st.markdown(f"- {f}")
                    else:
                        st.markdown(f"- {flag_list}")
                if reflection.get("human_review_required"):
                    st.error("🚨 Human review required before acting on these signals.")

    # ── Hero insight ──────────────────────────────────────────────────────────
    hero = res.get("hero_insight", "")
    if hero:
        st.markdown(f"""
        <div style='background:#FFFFFF; border-left:4px solid #F48221; border:1px solid #E2E8F0;
                    border-left:4px solid #F48221; border-radius:10px; padding:16px 18px; margin-bottom:18px;'>
            <div style='font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;
                        color:#F48221; margin-bottom:6px;'>Macro Signal · {st.session_state.time_window}</div>
            <div style='font-size:15px; color:#0F172A; line-height:1.55;'>{hero}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Summary metrics ───────────────────────────────────────────────────────
    metrics = orch.get("summaryMetrics", [])
    if metrics:
        m_cols = st.columns(min(len(metrics), 3), gap="medium")
        for i, m in enumerate(metrics[:3]):
            status_color = {"positive": "#059669", "negative": "#DC2626", "neutral": "#64748B"}.get(m.get("status", "neutral"), "#64748B")
            with m_cols[i]:
                st.markdown(f"""
                <div style='background:#FFFFFF; padding:16px 18px; border-radius:12px;
                            border:1px solid #E2E8F0; box-shadow:0 1px 4px rgba(0,0,0,0.04);'>
                    <div style='font-size:12px; font-weight:600; color:#64748B; margin-bottom:6px;'>{m.get("label","")}</div>
                    <div style='font-size:22px; font-weight:800; color:#0F172A; margin-bottom:4px;'>{m.get("value","")}</div>
                    <div style='font-size:11px; color:{status_color}; font-weight:600;'>{m.get("trend","")}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Urgency legend ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap;'>
        <span style='font-size:11px; color:#94A3B8; align-self:center;'>Signal urgency:</span>
        <span class='badge-action'>🔴 Action Now — act within 48 hrs</span>
        <span class='badge-monitor'>🟡 Monitor — watch weekly</span>
        <span class='badge-horizon'>🟢 Horizon — strategic awareness</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Signal cards ──────────────────────────────────────────────────────────
    st.markdown(f"**Live Signal Dashboard** · {len(signal_cards)} signals · Sources: {res.get('sources_ingested', 0)} ingested")
    st.markdown("")

    if signal_cards:
        card_cols = st.columns(2, gap="medium")
        for idx, card in enumerate(signal_cards):
            urgency_key = card.get("urgency", "monitor")
            urg         = URGENCY.get(urgency_key, URGENCY["monitor"])
            ui_type     = card.get("ui_display_type", "TREND_SCORE")
            ui_meta     = UI_TYPE_META.get(ui_type, UI_TYPE_META["TREND_SCORE"])
            direction   = card.get("direction", "flat")
            delta_color = "#DC2626" if direction == "up" else ("#059669" if direction == "down" else "#64748B")
            delta_arrow = "▲" if direction == "up" else ("▼" if direction == "down" else "→")

            with card_cols[idx % 2]:
                with st.container(border=True):
                    # Header row
                    h1, h2 = st.columns([3, 2])
                    with h1:
                        st.markdown(f"**{card.get('title','')}**")
                    with h2:
                        st.markdown(f"""
                        <div style='text-align:right;'>
                            <span style='font-size:10px; font-weight:700; color:{ui_meta["color"]};
                                         background:{ui_meta["bg"]}; padding:2px 8px; border-radius:99px;
                                         border:1px solid {ui_meta["color"]}30;'>{ui_meta["label"]}</span>
                            &nbsp;
                            <span class='{urg["badge"]}'>{urg["icon"]} {urg["label"]}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    # Value + delta
                    st.markdown(f"""
                    <div style='margin:8px 0;'>
                        <span style='font-size:24px; font-weight:800; color:#0F172A; font-family:monospace;'>
                            {card.get("value","")}
                        </span>
                        &nbsp;
                        <span style='font-size:12px; color:{delta_color}; font-weight:600;'>
                            {delta_arrow} {card.get("delta","")}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Expand / collapse
                    card_key = f"card_{idx}"
                    expanded = st.session_state.expanded_card == card_key
                    toggle_label = "▲ Hide detail" if expanded else "▼ Show insight & action"
                    if st.button(toggle_label, key=f"toggle_{idx}", type="secondary", use_container_width=False):
                        st.session_state.expanded_card = None if expanded else card_key
                        st.rerun()

                    if expanded:
                        st.markdown(f"""
                        <div style='border-top:1px solid #F1F5F9; margin-top:8px; padding-top:10px;'>
                            <div style='font-size:12.5px; color:#334155; line-height:1.65; margin-bottom:10px;'>
                                {card.get("insight","")}
                            </div>
                            <div style='font-size:10px; font-weight:700; text-transform:uppercase;
                                        letter-spacing:0.07em; color:#94A3B8; margin-bottom:3px;'>Data sources</div>
                            <div style='font-size:11px; color:#0369A1; font-style:italic; margin-bottom:10px;'>
                                {card.get("data_source","")}
                            </div>
                            <div style='font-size:10px; font-weight:700; text-transform:uppercase;
                                        letter-spacing:0.07em; color:#94A3B8; margin-bottom:3px;'>Suggested action</div>
                            <div style='font-size:12px; color:#15803D; font-weight:600;'>
                                → {card.get("suggested_action","")}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("No signal cards generated. Try running the pipeline again or check your Groq API key.")

    # ── Trend implication ─────────────────────────────────────────────────────
    implication = orch.get("trend_implication", "")
    if implication:
        st.markdown("")
        with st.container(border=True):
            st.markdown("##### Strategic Implication")
            st.markdown(f"<div style='color:#475569; font-size:14px; line-height:1.65;'>{implication}</div>",
                        unsafe_allow_html=True)

    # ── Strategic pillars ─────────────────────────────────────────────────────
    pillars = orch.get("strategic_pillars", [])
    if pillars:
        st.markdown("#### Strategic Pillars")
        p_cols = st.columns(min(len(pillars), 3), gap="medium")
        for i, pillar in enumerate(pillars[:3]):
            with p_cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{pillar.get('title','')}**")
                    st.markdown(f"<div style='font-size:13px; color:#64748B; line-height:1.5;'>{pillar.get('description','')}</div>",
                                unsafe_allow_html=True)

    # ── Arbitrage scores (transparency panel) ────────────────────────────────
    if scored_trends:
        with st.expander("📊 Scoring transparency — arbitrage index & saturation risk", expanded=False):
            score_data = []
            for t in scored_trends:
                score_data.append({
                    "Signal":             t.get("niche_keyword", ""),
                    "Confidence":         t.get("confidence", ""),
                    "Accel. Score":       t.get("acceleration_score", 0),
                    "Saturation Risk":    t.get("saturation_risk", ""),
                    "Arbitrage Index":    t.get("arbitrage_index", 0),
                    "Urgency":            t.get("urgency", ""),
                })
            st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True)
            st.caption("Scoring is deterministic (no LLM). Arbitrage index = confidence × 0.5 + saturation bonus × 0.3 + specificity × 0.2")

    # ── n8n route used ────────────────────────────────────────────────────────
    st.markdown("")
    st.markdown(f"<div style='font-size:11px; color:#94A3B8;'>n8n branch: <code>{res.get('branch','')}</code> · Persona layer: <code>{p_layer}</code></div>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 7B. CHAT COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_chat:
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        # Chat header
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:10px; margin-bottom:14px;'>
            <div style='width:30px; height:30px; border-radius:99px;
                        background:linear-gradient(135deg,#6366F1,#8B5CF6);
                        display:flex; align-items:center; justify-content:center;
                        font-size:14px; color:white;'>✦</div>
            <div>
                <div style='font-size:13px; font-weight:700; color:#0F172A;'>Sense AI Agent</div>
                <div style='font-size:11px; color:#94A3B8;'>{p_role} · {p_layer}</div>
            </div>
            <div style='margin-left:auto; width:7px; height:7px; border-radius:99px;
                        background:#10B981; box-shadow:0 0 0 2px #10B98140;'></div>
        </div>
        """, unsafe_allow_html=True)

        # Build system prompt from live signal cards
        chat_sys = build_chat_system_prompt(
            ind, sub, dom, p_role, p_layer,
            signal_cards, st.session_state.brand_context,
        )

        # Message history
        chat_container = st.container(height=480, border=False)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(f"""
                <div style='background:#F8FAFC; border-radius:10px; padding:12px 14px;
                            border:1px solid #E2E8F0; font-size:12.5px; color:#334155;
                            line-height:1.6; margin-bottom:12px;'>
                    Hi! I'm your Sense AI agent. I have the <strong>{dom}</strong> signal
                    dashboard loaded for a <strong>{p_role}</strong>. Ask me to dig deeper
                    into any signal, compare trends, or explain what an urgency rating means
                    for your context.
                </div>
                """, unsafe_allow_html=True)

                # Quick starts
                quick_starts = orch.get("chatQuickStart", [
                    f"Which signal needs my attention most urgently?",
                    f"What does the horizon-level signal mean for {dom}?",
                    f"How should I brief my team on these signals?",
                ])
                st.markdown("<div style='font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.07em; color:#94A3B8; margin-bottom:6px;'>Quick start</div>", unsafe_allow_html=True)
                for i, qs in enumerate(quick_starts[:3]):
                    if st.button(qs, key=f"qs_{i}", type="secondary", use_container_width=True):
                        st.session_state.chat_history.append({"role": "user", "content": qs})
                        st.session_state.pending_prompt = qs
                        st.rerun()
            else:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        # Artifact upload
        with st.popover("➕ Attach file", use_container_width=True):
            st.caption("PNG, JPG, CSV · max 200 MB")
            uploaded = st.file_uploader("Upload", accept_multiple_files=True,
                                        type=["png", "jpg", "jpeg", "csv"],
                                        label_visibility="collapsed")
            if uploaded and st.button("Process", type="primary", use_container_width=True):
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"I've received {len(uploaded)} file(s). What would you like to do with them?",
                })
                st.rerun()

        # Chat input
        prompt = st.chat_input("Ask about any signal…")
        active_prompt = prompt or st.session_state.pending_prompt

        if active_prompt:
            st.session_state.pending_prompt = None
            if prompt:
                st.session_state.chat_history.append({"role": "user", "content": active_prompt})

            with chat_container:
                if prompt:
                    with st.chat_message("user"):
                        st.markdown(active_prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Analysing signals…"):
                        # Build messages history for Groq (not using json_object mode for chat)
                        history_msgs = [{"role": "system", "content": chat_sys}]
                        for h in st.session_state.chat_history[:-1]:
                            history_msgs.append({"role": h["role"], "content": h["content"]})
                        history_msgs.append({"role": "user", "content": active_prompt})

                        try:
                            chat_resp = client.chat.completions.create(
                                messages=history_msgs,
                                model="llama-3.3-70b-versatile",
                                temperature=0.35,
                                max_tokens=600,
                            )
                            reply = re.sub(r"<think>.*?</think>", "", chat_resp.choices[0].message.content, flags=re.DOTALL).strip()
                        except Exception as e:
                            reply = f"Signal connection lost ({e}). Please retry."

                        st.markdown(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})

            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:left; color:#94A3B8; font-size:11px; font-weight:600;
            border-top:1px solid #E2E8F0; padding-top:1.5rem; margin-top:2rem;
            text-transform:uppercase; letter-spacing:0.05em;'>
    © 2022–2026, Tiger Analytics Inc. All rights reserved. &nbsp;·&nbsp;
    <span style='font-weight:400; letter-spacing:0;'>Powered by Experience Consulting Team</span>
</div>
""", unsafe_allow_html=True)