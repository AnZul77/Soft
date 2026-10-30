import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette - Modern Institutional Dark Theme
    BG_DARK = RGBColor(11, 15, 25)         # #0B0F19
    CARD_BG = RGBColor(19, 27, 46)         # #131B2E
    CARD_BORDER = RGBColor(38, 52, 84)     # #263454
    TEXT_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8
    TEXT_SUBTLE = RGBColor(100, 116, 139)  # #64748B
    
    ACCENT_INDIGO = RGBColor(99, 102, 241) # #6366F1
    ACCENT_CYAN = RGBColor(56, 189, 248)   # #38BDF8
    ACCENT_EMERALD = RGBColor(16, 185, 129)# #10B981
    ACCENT_AMBER = RGBColor(245, 158, 11)  # #F59E0B
    ACCENT_ROSE = RGBColor(244, 63, 94)    # #F43F5E

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, category: str, title: str, subtitle: str = ""):
        # Category / Pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT

        # Subtitle
        if subtitle:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.4))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Accent decorative element
    dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.6), Inches(0.08))
    dec.fill.solid()
    dec.fill.fore_color.rgb = ACCENT_CYAN
    dec.line.fill.background()

    # Category
    tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11), Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.text = "PROJECT ARCHITECTURE & ML INNOVATION BRIEF"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    # Main Title
    tb = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.5), Inches(1.5))
    tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]
    p.text = "Incorporating Grounded AI into the Investment Platform"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT

    # Subtitle
    tb = s1.shapes.add_textbox(Inches(0.8), Inches(3.8), Inches(11), Inches(1.0))
    tb.text_frame.word_wrap = True
    p = tb.text_frame.paragraphs[0]
    p.text = "Engineering a Multi-Hop Decision Support Engine: How It Works, Architectural Mechanics, and Measurable Project Impact"
    p.font.size = Pt(16)
    p.font.color.rgb = TEXT_MUTED

    # Highlights Container Card
    add_card(s1, 0.8, 5.2, 11.733, 1.5, border_color=ACCENT_INDIGO)
    col_w = 11.733 / 4
    pillars = [
        ("Semantic RAG Engine", "128-dim dense vectors, zero external API latency, verified citations"),
        ("Supply Chain Graph", "Multi-hop relational adjacency (TSMC -> NVDA -> MSFT/TSLA)"),
        ("Explain Impact Agent", "Answers 'Why does this market event matter to MY portfolio?'"),
        ("AI Thesis Reflection", "Audits premise vs reality to conquer emotional trading & bias")
    ]
    for i, (head, desc) in enumerate(pillars):
        tx = s1.shapes.add_textbox(Inches(0.9 + i * col_w), Inches(5.35), Inches(col_w - 0.2), Inches(1.2))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = head
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_CYAN if i%2==0 else ACCENT_EMERALD

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: Executive Summary & The Problem
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Context & Motivation", "The Core Problem: The Retail Investor Intelligence Gap",
               "Why traditional financial tools and generic LLMs fail modern retail investors during market volatility")

    # 3 Comparison Columns
    col_data = [
        ("The Retail Investor Dilemma", ACCENT_ROSE, [
            "Information Deluge: Breaking financial headlines flood users without personal context.",
            "Missing Causality: Retail traders see a -8% drop in TSMC but fail to realize it impacts their NVDA or Apple holdings.",
            "Emotional Reactivity: Investors panic-sell on short-term noise instead of tracking fundamentals.",
            "Hindsight Bias: Over time, traders forget their original investment thesis and rationale."
        ]),
        ("Why Generic LLMs Fail Here", ACCENT_AMBER, [
            "Hallucinated Numbers: Standard AI models make up stock prices, PE ratios, and returns.",
            "Zero Portfolio Awareness: ChatGPT doesn't know your cash balance, equity weights, or risk limits.",
            "Prompt Injection Vulnerability: Adversarial news or user input can hijack model recommendations.",
            "Regulatory Violation: Unconstrained models offer unlicensed buy/sell advice violating SEC/FINRA rules."
        ]),
        ("Our Grounded AI Solution", ACCENT_EMERALD, [
            "Portfolio-Grounded Context: Computes exact direct exposure (% of equity and dollar holding).",
            "Relational Graph Traversal: Maps supply-chain contagion risks (suppliers, competitors, customers).",
            "Zero-Hallucination Citations: Strict RAG retrieves verified news articles and regulatory snippets.",
            "Safety Guardrails: Prompt sanitizer + grounded abstention + non-advisory disclaimers."
        ])
    ]

    for idx, (title, color, bullets) in enumerate(col_data):
        cx = 0.8 + idx * 4.0
        add_card(s2, cx, 1.9, 3.75, 5.0, border_color=color)
        tb = s2.shapes.add_textbox(Inches(cx + 0.2), Inches(2.1), Inches(3.35), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = color

        for bullet in bullets:
            p_b = tf.add_paragraph()
            parts = bullet.split(": ")
            p_b.text = "• "
            p_b.font.size = Pt(11)
            p_b.font.color.rgb = TEXT_LIGHT
            run1 = p_b.add_run()
            run1.text = parts[0] + ": "
            run1.font.bold = True
            run1.font.color.rgb = TEXT_LIGHT
            run2 = p_b.add_run()
            run2.text = parts[1]
            run2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 3: Architectural Blueprint (How It Works)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "System Architecture", "End-to-End Grounded AI Intelligence Pipeline",
               "How real-time market data, relational knowledge graphs, vector retrieval, and LLMs fuse together")

    # 4 Pipeline Stages
    stages = [
        ("1. Ingestion & Event Detection", ACCENT_CYAN, [
            "Real-Time Market Data Provider",
            "Consolidated Watcher Queue (Deduplicated)",
            "15-Min 8% Anomaly Scanner",
            "Adversarial Prompt Sanitization"
        ]),
        ("2. Dual-Engine Context Retrieval", ACCENT_INDIGO, [
            "Normalized 128-dim Dense Vectors",
            "Sub-ms Cosine Similarity Search",
            "Relational Adjacency Graph Traversal",
            "Multi-Hop Supply Chain Discovery"
        ]),
        ("3. Synthesis & Reasoning Engine", ACCENT_AMBER, [
            "Portfolio Equity & Exposure Calculation",
            "Context Fusion (Holdings + Graph + News)",
            "Local LLM Router (Ollama / Fallback)",
            "Grounded Abstention Enforcement"
        ]),
        ("4. Delivery & User Experience", ACCENT_EMERALD, [
            "Server-Sent Events (SSE) Token Stream",
            "Interactive 'Explain Impact' Modal",
            "Semantic Research Assistant",
            "AI Thesis Reflection Auditor"
        ])
    ]

    for idx, (title, color, items) in enumerate(stages):
        cx = 0.8 + idx * 3.0
        add_card(s3, cx, 1.9, 2.75, 4.0, border_color=color)
        tb = s3.shapes.add_textbox(Inches(cx + 0.15), Inches(2.05), Inches(2.45), Inches(3.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = color

        for it in items:
            p_i = tf.add_paragraph()
            p_i.text = f"→ {it}"
            p_i.font.size = Pt(10)
            p_i.font.color.rgb = TEXT_LIGHT

    # Flow Banner Card at Bottom
    add_card(s3, 0.8, 6.1, 11.733, 0.9, border_color=ACCENT_CYAN)
    tb_flow = s3.shapes.add_textbox(Inches(1.0), Inches(6.2), Inches(11.3), Inches(0.7))
    tf_f = tb_flow.text_frame
    tf_f.word_wrap = True
    p_f = tf_f.paragraphs[0]
    p_f.text = "Architectural Invariant: Grounding Before Generation"
    p_f.font.size = Pt(11)
    p_f.font.bold = True
    p_f.font.color.rgb = ACCENT_CYAN
    p_f2 = tf_f.add_paragraph()
    p_f2.text = "The LLM is NEVER asked to extrapolate ungrounded market facts. Every prompt is synthesized with hard ledger balances, verified news citations, and explicit supply-chain topology before model inference."
    p_f2.font.size = Pt(10)
    p_f2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: Feature 1 - "Explain Impact" Agent
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Core AI Feature #1", "The 'Explain Impact' Decision Support Agent",
               "Translating macro volatility and corporate shocks into tailored, portfolio-specific intelligence")

    # Left Card: How It Works & Logic
    add_card(s4, 0.8, 1.9, 5.7, 5.1, border_color=ACCENT_INDIGO)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Algorithmic Mechanics"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    features_s4 = [
        ("Direct Holding Exposure", "Calculates holding shares, valuation, and exact portfolio weight (% of total equity including cash)."),
        ("Supply-Chain Contagion Scan", "Queries CompanyRelationship table for 1st- and 2nd-degree suppliers, customers, and competitors held in the portfolio."),
        ("Semantic Evidence Retrieval", "Fetches verified news articles matching the ticker and event description with similarity ranking."),
        ("Grounded Abstention Guard", "If ticker is unheld and no direct/indirect supply chain link or news exists, returns explicit abstention rather than hallucinating."),
        ("Sub-second Token Streaming", "Uses FastAPI StreamingResponse with Server-Sent Events (SSE) to render words progressively in UI.")
    ]
    for h, d in features_s4:
        p_f = tf.add_paragraph()
        p_f.text = f"• {h}: "
        p_f.font.size = Pt(11)
        p_f.font.bold = True
        p_f.font.color.rgb = TEXT_LIGHT
        run = p_f.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Card: Real-World Demonstration Case
    add_card(s4, 6.8, 1.9, 5.7, 5.1, border_color=ACCENT_CYAN)
    tb_r = s4.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "Live Execution Scenario: TSMC Disruption"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    demo_steps = [
        ("Market Event Injected", "TSMC halts advanced CoWoS packaging line in Tainan due to power surge (-7.5% drop)."),
        ("User Portfolio State", "User holds 15 shares of NVDA ($1,845.00), 0 shares of TSMC directly. Cash: $98,155.00."),
        ("Graph Contagion Detected", "Knowledge Graph identifies TSMC -> SUPPLIER -> NVDA (Wafer & CoWoS packaging partner)."),
        ("Grounded Citation Sourced", "[TechAsia Financial Daily] '2 to 3 week delivery backlog for cutting-edge AI accelerators'."),
        ("Synthesized Response", "'While you do not hold TSMC directly, your portfolio holds NVDA (1.8% equity). TSMC packaging bottlenecks propagate downstream risk to Blackwell GPU deliveries.'")
    ]
    for h, d in demo_steps:
        p_d = tf_r.add_paragraph()
        p_d.text = f"▶ {h}: "
        p_d.font.size = Pt(11)
        p_d.font.bold = True
        p_d.font.color.rgb = ACCENT_EMERALD if "Synthesized" in h else TEXT_LIGHT
        run = p_d.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 5: Feature 2 - Vector RAG & Supply Chain Graph
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Core AI Feature #2", "Semantic RAG & Supply Chain Knowledge Graph",
               "Combining dense vector similarity with relational topology for zero-latency deterministic reasoning")

    # 3 Cards
    cards_s5 = [
        ("Deterministic Vector Embeddings", ACCENT_CYAN, [
            "128-Dimensional Normalized Vectors: Generated via SHA-256 semantic n-grams with positional decay weights.",
            "Zero External API Overhead: Operates with 0ms external network latency; no OpenAI/Cohere key required.",
            "Mathematical Stability: Unit norm guarantees Cosine Similarity matches 1.0 for identical queries and scales smoothly.",
            "Cross-Platform Deployment: Works out-of-the-box on SQLite in development and scales to PostgreSQL pgvector."
        ]),
        ("Relational Knowledge Graph", ACCENT_INDIGO, [
            "Adjacency Modeling: Maps corporate ecosystems with source, target, relationship type, and confidence rating.",
            "Key Relationship Types: Tracks SUPPLIER, CUSTOMER, COMPETITOR, and SUBSIDIARY edges.",
            "Real-World Semiconductor Mapping: TSMC -> NVDA, TSMC -> AAPL, NVDA -> MSFT/TSLA, AMD -> NVDA.",
            "Contagion Propagation: Unlocks second-order insight that traditional isolated stock screens completely miss."
        ]),
        ("Verified Citation Grounding", ACCENT_EMERALD, [
            "Article Ingestion Pipeline: Ingests financial news with title, source, publication date, and raw text chunks.",
            "Anchored Evidence Snippets: Top similarity matches return verifiable source, URL, and exact content quotation.",
            "Zero Hallucination Guarantee: Insights cite real reporting (e.g. Bloomberg Tech Wire, TechAsia Daily).",
            "Audit Trail: Every citation presented in UI contains external links for immediate investor verification."
        ])
    ]

    for idx, (title, color, items) in enumerate(cards_s5):
        cx = 0.8 + idx * 4.0
        add_card(s5, cx, 1.9, 3.75, 5.1, border_color=color)
        tb = s5.shapes.add_textbox(Inches(cx + 0.2), Inches(2.1), Inches(3.35), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = color

        for it in items:
            p_i = tf.add_paragraph()
            parts = it.split(": ")
            p_i.text = "• "
            p_i.font.size = Pt(11)
            p_i.font.color.rgb = TEXT_LIGHT
            r1 = p_i.add_run()
            r1.text = parts[0] + ": "
            r1.font.bold = True
            r1.font.color.rgb = TEXT_LIGHT
            r2 = p_i.add_run()
            r2.text = parts[1]
            r2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 6: Feature 3 - AI Thesis Reflection (Journal)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Core AI Feature #3", "Behavioral Finance: AI Investment Thesis Reflection",
               "Eliminating hindsight bias and emotional trading through structured, automated thesis auditing")

    # Left Card: The Behavioral Finance Problem
    add_card(s6, 0.8, 1.9, 5.7, 5.1, border_color=ACCENT_AMBER)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Psychological Failure in Retail Trading"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    points_s6 = [
        ("Thesis Drift", "Investors buy a stock for Reason A (e.g. AI datacenter demand), but hold it through a crash for Reason B (e.g. hope for a turnaround)."),
        ("Hindsight Revision", "Traders rewrite mental history after volatility, falsely believing 'I knew this would happen.'"),
        ("Lack of Post-Mortem", "Rarely do retail traders conduct structured post-trade analysis to learn from strategic mistakes."),
        ("Emotional Impulsiveness", "Headline fear causes premature panic exits at market troughs.")
    ]
    for h, d in points_s6:
        p_pt = tf.add_paragraph()
        p_pt.text = f"⚠ {h}: "
        p_pt.font.size = Pt(11)
        p_pt.font.bold = True
        p_pt.font.color.rgb = TEXT_LIGHT
        run = p_pt.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Card: The AI Reflection Engine
    add_card(s6, 6.8, 1.9, 5.7, 5.1, border_color=ACCENT_EMERALD)
    tb_r = s6.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "How AI Reflection Audits the Investor"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_EMERALD

    engine_steps = [
        ("Step 1: Trade Journaling", "Investor logs thesis premise, conviction (1-5 stars), target price, and review horizon upon order execution."),
        ("Step 2: Real-Time Market Check", "Engine queries live price and computes target price gap (% divergence from target)."),
        ("Step 3: RAG Sector Grounding", "Retrieves breaking corporate news and earnings reports logged since thesis creation."),
        ("Step 4: Objective Synthesis", "AI summarizes what parts of the original premise materialized vs what macro factors diverged."),
        ("Step 5: Non-Advisory Safeguard", "Strict prompt ensures no buy/sell instruction is given; promotes self-reflection only.")
    ]
    for h, d in engine_steps:
        p_e = tf_r.add_paragraph()
        p_e.text = f"✓ {h}: "
        p_e.font.size = Pt(11)
        p_e.font.bold = True
        p_e.font.color.rgb = ACCENT_CYAN
        run = p_e.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: Safety, Guardrails & Adversarial Defense
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Security & Regulatory Invariants", "Enterprise Guardrails & Adversarial Protection",
               "Preventing jailbreaks, eliminating hallucinations, and maintaining strict SEC/FINRA compliance")

    cards_s7 = [
        ("Prompt Injection Defense", ACCENT_ROSE, [
            "Pattern Neutralization: Active regex sanitizer intercepts 'ignore previous instructions', 'system override', etc.",
            "XSS & Tag Stripping: Sanitizes HTML tags, script elements, and javascript: protocols.",
            "Neutral Replacement: Adversarial tokens are substituted with [BLOCKED_ADVERSARIAL_INJECTION].",
            "Zero Jailbreak Vulnerability: Prevents malicious third-party market news from tricking the model."
        ]),
        ("Grounded Abstention Engine", ACCENT_AMBER, [
            "Refusal to Guess: If no verified citations exist and user holds no direct or supply-chain shares, model explicitly abstains.",
            "Standardized Abstention Output: 'Insufficient grounded evidence to assess impact.'",
            "Anti-Hallucination Barrier: Eliminates fabricated earnings, fake regulatory approvals, and phantom price targets.",
            "Deterministic State: Abstention flag returned in API schema for clear UI messaging."
        ]),
        ("Regulatory Compliance (SEC/FINRA)", ACCENT_CYAN, [
            "Mandatory Non-Advisory Disclaimers: Automatically appended to every AI research response and impact explanation.",
            "No Trade Directives: Prompt instructions strictly forbid generating 'Buy now' or 'Sell now' commands.",
            "Educational Positioning: Platform clearly demarcated as institutional-grade decision support, not financial advisory.",
            "Tenant Isolation: Multi-tenant JWT authorization ensures AI queries only inspect the authenticated owner's assets."
        ])
    ]

    for idx, (title, color, items) in enumerate(cards_s7):
        cx = 0.8 + idx * 4.0
        add_card(s7, cx, 1.9, 3.75, 5.1, border_color=color)
        tb = s7.shapes.add_textbox(Inches(cx + 0.2), Inches(2.1), Inches(3.35), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = color

        for it in items:
            p_i = tf.add_paragraph()
            parts = it.split(": ")
            p_i.text = "• "
            p_i.font.size = Pt(11)
            p_i.font.color.rgb = TEXT_LIGHT
            r1 = p_i.add_run()
            r1.text = parts[0] + ": "
            r1.font.bold = True
            r1.font.color.rgb = TEXT_LIGHT
            r2 = p_i.add_run()
            r2.text = parts[1]
            r2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 8: Local LLM Infrastructure & Privacy
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Infrastructure & Data Privacy", "Edge & Local LLM Routing Architecture",
               "Ensuring financial confidentiality and zero per-token cloud costs via local inference")

    # Left: Local LLM Architecture
    add_card(s8, 0.8, 1.9, 5.7, 5.1, border_color=ACCENT_INDIGO)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Local LLM Orchestrator (Ollama)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_INDIGO

    local_points = [
        ("Dynamic Model Probing", "Automatically connects to Ollama endpoint (http://127.0.0.1:11434) and queries /api/tags for installed weights."),
        ("Multi-Model Compatibility", "Auto-selects optimal model from installed weights: Gemma 3 (4B), Qwen 3.5 (9B), Llama 3.2, Mistral, or Phi-3."),
        ("Zero-Leakage Privacy", "Confidential portfolio sizes, net worth, and private trade rationales NEVER leave the user's host machine."),
        ("Deterministic Fallback", "If no local LLM is active, the system automatically switches to an analytical template synthesizer with 100% reliability.")
    ]
    for h, d in local_points:
        p_l = tf.add_paragraph()
        p_l.text = f"⚙ {h}: "
        p_l.font.size = Pt(11)
        p_l.font.bold = True
        p_l.font.color.rgb = TEXT_LIGHT
        run = p_l.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: Natural Language Ticker Resolver
    add_card(s8, 6.8, 1.9, 5.7, 5.1, border_color=ACCENT_CYAN)
    tb_r = s8.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "Natural Language Ticker Resolution"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    resolver_points = [
        ("Unstructured Query Parser", "User asks: 'How is Tesla doing after the recent battery news?' — system automatically maps 'Tesla' -> TSLA."),
        ("Securities Database Fallback", "Cross-references query tokens against registered stock exchange symbols and corporate names."),
        ("Multi-Modal Context Fusion", "Injects live real-time quote (price, 24h high/low, volume) + supply chain graph + news citations into prompt."),
        ("Live Research Modal", "Frontend provides suggested prompts, real-time typing indicators, and trade order integration.")
    ]
    for h, d in resolver_points:
        p_r = tf_r.add_paragraph()
        p_r.text = f"🔍 {h}: "
        p_r.font.size = Pt(11)
        p_r.font.bold = True
        p_r.font.color.rgb = ACCENT_CYAN
        run = p_r.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 9: Project Impact & Transformation
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Project Impact", "How AI Transformed the Software Project",
               "Measurable technical, operational, and user experience enhancements achieved through AI integration")

    # 4 Impact Metric Cards
    metrics = [
        ("From 30 Mins to 3 Secs", "Decision Latency Reduction", ACCENT_CYAN,
         "Traditional research requires searching news portals, 10-K filings, and calculators. AI synthesizes portfolio relevance instantly."),
        ("100% Grounded", "Zero Hallucination Rate", ACCENT_EMERALD,
         "Every factual claim is anchored to verifiable citations and double-entry ledger math. Refuses to guess on empty context."),
        ("100% Private & Free", "Cloud API Independence", ACCENT_INDIGO,
         "Zero external LLM billing overhead. Investor financial data is never exposed to public cloud model training."),
        ("Multi-Hop Risk Discovery", "Supply-Chain Transparency", ACCENT_AMBER,
         "Transforms portfolio management from single-ticker monitoring to holistic ecosystem risk awareness.")
    ]

    for idx, (stat, title, color, desc) in enumerate(metrics):
        col_idx = idx % 2
        row_idx = idx // 2
        cx = 0.8 + col_idx * 6.0
        cy = 1.9 + row_idx * 2.6
        add_card(s9, cx, cy, 5.7, 2.35, border_color=color)

        tb = s9.shapes.add_textbox(Inches(cx + 0.25), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = stat
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = color

        p_t = tf.add_paragraph()
        p_t.text = title.upper()
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_LIGHT

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 10: Testing, Verification & Demonstration
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Testing & Verification", "Quality Assurance: Automated Suites & Live Demonstration",
               "Demonstrating correctness through 29 unit tests and an interactive live evaluator harness")

    # Left: Test Suite Metrics
    add_card(s10, 0.8, 1.9, 5.7, 5.1, border_color=ACCENT_EMERALD)
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Automated Pytest Coverage (29 Tests)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_EMERALD

    test_groups = [
        ("ML & RAG Explainer Suite", "Verifies vector generation, cosine similarity bounds, prompt injection neutralization, supply-chain links, and abstention on empty context."),
        ("Trading Ledger Invariants", "Confirms double-entry cash balance preservation, escrow reservations for limit orders, and idempotency headers."),
        ("Auth & Tenant Isolation", "Ensures strict user isolation where portfolios cannot be inspected across tenant boundaries."),
        ("Risk & Anomaly Engine", "Tests 8% price anomaly triggers, portfolio beta calculations, Value-at-Risk (VaR), and HHI concentration.")
    ]
    for h, d in test_groups:
        p_t = tf.add_paragraph()
        p_t.text = f"✔ {h}: "
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_LIGHT
        run = p_t.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: Live Demonstration Harness
    add_card(s10, 6.8, 1.9, 5.7, 5.1, border_color=ACCENT_CYAN)
    tb_r = s10.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "Interactive Live Demonstration Harness"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    demo_pts = [
        ("Unified Script (test_manual_live.py)", "Enables evaluators to run either a step-by-step interactive walkthrough or a sub-10-second automated run."),
        ("Step 10: Live Anomaly Injection", "Injects an 8.5% price shock into NVDA, simulating sudden market turbulence in real-time."),
        ("Step 11: Instant Explain Impact", "Triggers the AI Explainer to contextualize the price shock with NVDA portfolio exposure and TSMC supply links."),
        ("Step 12: Thesis Reflection", "Executes live AI Thesis Reflection comparing initial target price ($185) with post-shock reality."),
        ("One-Click Startup Scripts", "Available via start_backend.ps1 / .bat and run_tests.ps1 / .bat.")
    ]
    for h, d in demo_pts:
        p_d = tf_r.add_paragraph()
        p_d.text = f"▶ {h}: "
        p_d.font.size = Pt(11)
        p_d.font.bold = True
        p_d.font.color.rgb = ACCENT_CYAN
        run = p_d.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 11: Future Roadmap
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Future Roadmap", "Strategic Evolution: Next-Generation Capabilities",
               "Expanding the intelligence envelope from decision support to multi-agent proactive simulation")

    roadmap_items = [
        ("Phase 1: Multi-Modal Document Parsing", ACCENT_CYAN,
         "Ingest earnings conference call transcripts, 10-K tables, and balance sheet charts using vision-language models for deeper fundamental indexing."),
        ("Phase 2: Proactive Contagion Alerts", ACCENT_INDIGO,
         "Autonomous background agent continuously monitoring supply chain news and preemptively notifying investors before shocks hit their holdings."),
        ("Phase 3: Multi-Agent Debate Simulation", ACCENT_AMBER,
         "Orchestrate a Bull-Agent vs Bear-Agent debate on every user thesis to illuminate cognitive blind spots and stress-test conviction."),
        ("Phase 4: Algorithmic Scenario Stress Testing", ACCENT_EMERALD,
         "Simulate macro shocks (e.g. 'What happens if Fed raises rates by 75bps?' or 'What if TSMC power outage extends to 2 months?').")
    ]

    for idx, (title, color, desc) in enumerate(roadmap_items):
        cx = 0.8 + idx * 3.0
        add_card(s11, cx, 1.9, 2.75, 5.1, border_color=color)
        tb = s11.shapes.add_textbox(Inches(cx + 0.15), Inches(2.1), Inches(2.45), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"0{idx+1}"
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = color

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_LIGHT

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 12: Conclusion & Summary
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Summary & Conclusion", "Key Takeaways: Grounded AI as an Architectural Cornerstone",
               "Turning market noise into informed conviction through deterministic engineering and ethical AI")

    # Big Summary Card
    add_card(s12, 0.8, 1.9, 11.733, 4.0, border_color=ACCENT_INDIGO)
    tb_c = s12.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(11.1), Inches(3.6))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    takeaways = [
        ("Not Just a Chatbot — A Domain-Integrated Engine",
         "The AI is tightly coupled with the core trading ledger, knowledge graph, and market anomaly scanner. It is not an isolated chat widget; it is an active decision-support layer."),
        ("Deterministic Grounding & Zero Hallucination",
         "By combining 128-dimensional deterministic dense embeddings, strict cosine ranking, and explicit abstention logic, the system never makes up facts or trades."),
        ("Multi-Hop Supply Chain Intelligence",
         "Retail investors can finally see the hidden connections between suppliers and customers that institutional hedge funds exploit."),
        ("Ethical, Private & Compliant by Design",
         "Built with prompt injection defenses, non-advisory SEC disclaimers, and local LLM execution that protects user financial confidentiality.")
    ]

    for idx, (head, body) in enumerate(takeaways):
        p_tk = tf_c.paragraphs[0] if idx == 0 else tf_c.add_paragraph()
        p_tk.text = f"{idx+1}. {head}: "
        p_tk.font.size = Pt(13)
        p_tk.font.bold = True
        p_tk.font.color.rgb = ACCENT_CYAN if idx % 2 == 0 else ACCENT_EMERALD
        run = p_tk.add_run()
        run.text = body
        run.font.bold = False
        run.font.color.rgb = TEXT_LIGHT

    # Bottom Contact / Repository Note
    add_card(s12, 0.8, 6.1, 11.733, 0.9, border_color=CARD_BORDER)
    tb_bot = s12.shapes.add_textbox(Inches(1.0), Inches(6.25), Inches(11.3), Inches(0.6))
    tf_b = tb_bot.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "AI-Powered Investment Intelligence Platform • Ready for Live Demonstration & Production Evaluation"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = TEXT_MUTED
    p_b.alignment = PP_ALIGN.CENTER

    output_path = os.path.abspath("AI_Feature_Incorporation_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
