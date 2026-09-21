import streamlit as st
import re
import plotly.graph_objects as go
from io import BytesIO
from xml.sax.saxutils import escape
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from evidence_engine import (
    analyze_claim,
    analyze_stock_impact,
    analyze_scenario,
    analyze_portfolio_impact,
)

from financial_data import (
    get_financial_data,
    get_price_history,
    format_large_number,
    format_percent,
    format_ratio,
)

from scenario_engine import (
    run_financial_scenario,
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Investment Intelligence Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .main-title {
        font-size: 2.6rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    .company-header {
        padding: 18px;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        margin-bottom: 15px;
    }

    .hero-panel {
        padding: 28px 30px;
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 18px;
        margin-bottom: 20px;
        background: rgba(128,128,128,0.055);
    }

    .hero-kicker {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.65;
        margin-bottom: 8px;
    }

    .hero-heading {
        font-size: 1.65rem;
        font-weight: 750;
        line-height: 1.25;
        margin-bottom: 8px;
    }

    .hero-copy {
        font-size: 1rem;
        line-height: 1.6;
        opacity: 0.78;
        max-width: 950px;
    }

    .feature-card {
        min-height: 150px;
        padding: 18px;
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 14px;
        background: rgba(128,128,128,0.035);
    }

    .feature-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .feature-copy {
        font-size: 0.88rem;
        line-height: 1.5;
        opacity: 0.72;
    }

    .architecture-panel {
        padding: 16px 18px;
        border: 1px solid rgba(128,128,128,0.20);
        border-radius: 14px;
        margin-top: 12px;
        margin-bottom: 22px;
    }

    .architecture-flow {
        font-size: 0.92rem;
        line-height: 1.8;
        font-weight: 600;
        opacity: 0.82;
    }

    .results-banner {
        padding: 18px 20px;
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 14px;
        background: rgba(128,128,128,0.045);
        margin-bottom: 16px;
    }

    .results-title {
        font-size: 1.15rem;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .results-copy {
        font-size: 0.9rem;
        opacity: 0.72;
        line-height: 1.5;
    }

    .evidence-note {
        padding: 12px 14px;
        border-left: 3px solid rgba(128,128,128,0.55);
        background: rgba(128,128,128,0.04);
        border-radius: 8px;
        margin: 8px 0 14px 0;
        font-size: 0.88rem;
        opacity: 0.82;
    }

    .company-name {
        font-size: 1.35rem;
        font-weight: 700;
    }

    .company-details {
        opacity: 0.7;
        margin-top: 4px;
    }

    .source-primary,
    .source-official,
    .source-high,
    .source-other,
    .source-low {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .source-primary {
        background: rgba(34,197,94,0.16);
    }

    .source-official {
        background: rgba(59,130,246,0.16);
    }

    .source-high {
        background: rgba(168,85,247,0.16);
    }

    .source-other {
        background: rgba(148,163,184,0.16);
    }

    .source-low {
        background: rgba(245,158,11,0.16);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    '<div class="main-title">🧠 AI Investment Intelligence Engine</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Live evidence + quantitative financial data + AI-powered
    investment research.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

st.markdown(
    """
    <div class="hero-panel">
        <div class="hero-kicker">Evidence-Driven Investment Research</div>
        <div class="hero-heading">
            From market information to financial impact.
        </div>
        <div class="hero-copy">
            Investigate market claims, trace events into company fundamentals,
            stress-test financial scenarios, and evaluate portfolio exposure
            using live evidence, quantitative data, and structured AI reasoning.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)

with feature_col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">🔎 Market Claim Intelligence</div>
            <div class="feature-copy">
                Test financial narratives against current evidence,
                source quality, counter-evidence, and uncertainty.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">📈 Stock Impact Research</div>
            <div class="feature-copy">
                Trace real-world events through company exposure,
                revenue, margins, cash flow, risk, and valuation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">🧪 Scenario Modeling</div>
            <div class="feature-copy">
                Apply user-controlled assumptions and compare current
                financials with deterministic scenario outcomes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col4:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-title">💼 Portfolio Intelligence</div>
            <div class="feature-copy">
                Compare holdings, weights, financial characteristics,
                and event exposure across a multi-stock portfolio.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="architecture-panel">
        <div class="hero-kicker">Research Architecture</div>
        <div class="architecture-flow">
            Live Evidence → Source Verification → Financial Data →
            Quantitative Analysis → AI Reasoning → Downloadable Research Report
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Choose a research mode from the sidebar to begin. "
    "The engine separates retrieved evidence, quantitative context, "
    "analytical inference, assumptions, and uncertainty."
)

st.divider()


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("Research Console")

    st.caption(
        "Choose a research mode and provide the relevant inputs."
    )

    st.divider()

    mode = st.radio(
        "Research Mode",
        [
            "🔎 Investigate a Market Claim",
            "📈 How Does This Affect My Stock?",
            "🧪 Scenario Analysis",
            "💼 Portfolio Impact",
        ],
    )

    st.divider()

    if mode != "💼 Portfolio Impact":

        ticker = st.text_input(
            "Stock Ticker",
            placeholder="AAPL",
        ).upper().strip()

    else:

        ticker = ""

    st.divider()

    st.caption("Research Architecture")

    st.markdown(
        """
        **Live Evidence**  
        ↓  
        **Source Quality**  
        ↓  
        **Quantitative Financial Data**  
        ↓  
        **AI Financial Reasoning**  
        ↓  
        **Impact Analysis**
        """
    )


# ==========================================================
# FINANCIAL DATA CACHE
# ==========================================================

@st.cache_data(
    ttl=900,
    show_spinner=False,
)
def load_financial_data(ticker):

    return get_financial_data(
        ticker
    )


@st.cache_data(
    ttl=900,
    show_spinner=False,
)
def load_price_history(
    ticker,
    period,
):

    return get_price_history(
        ticker,
        period=period,
    )


# ==========================================================
# FORMATTING HELPERS
# ==========================================================

def format_price(value):

    if value is None:
        return "N/A"

    try:
        return f"${float(value):,.2f}"

    except Exception:
        return "N/A"


def format_change(value):

    if value is None:
        return "N/A"

    try:

        value = float(value) * 100

        if value > 0:
            return f"+{value:.2f}%"

        return f"{value:.2f}%"

    except Exception:
        return "N/A"


# ==========================================================
# PRICE CHART
# ==========================================================

def display_price_chart(ticker):

    st.subheader(
        "📈 Stock Price Performance"
    )

    period_label = st.segmented_control(
        "Chart Period",
        options=[
            "1M",
            "3M",
            "6M",
            "1Y",
        ],
        default="1Y",
        key=f"chart_period_{ticker}",
    )

    period_mapping = {
        "1M": "1mo",
        "3M": "3mo",
        "6M": "6mo",
        "1Y": "1y",
    }

    selected_period = period_mapping.get(
        period_label,
        "1y",
    )

    history = load_price_history(
        ticker,
        selected_period,
    )

    if history.empty:

        st.warning(
            f"Historical price data for {ticker} "
            "is currently unavailable."
        )

        return

    if (
        "Date" not in history.columns
        or "Close" not in history.columns
    ):

        st.warning(
            "Historical price data could not be "
            "displayed."
        )

        return

    chart_data = history.dropna(
        subset=["Date", "Close"]
    ).copy()

    if chart_data.empty:

        st.warning(
            "No valid historical closing prices "
            "were returned."
        )

        return

    first_price = float(
        chart_data["Close"].iloc[0]
    )

    last_price = float(
        chart_data["Close"].iloc[-1]
    )

    if first_price != 0:

        period_return = (
            last_price / first_price
        ) - 1

    else:

        period_return = None

    top1, top2, top3 = st.columns(3)

    top1.metric(
        "Period Start",
        format_price(
            first_price
        ),
    )

    top2.metric(
        "Latest Close",
        format_price(
            last_price
        ),
    )

    top3.metric(
        f"{period_label} Return",
        format_change(
            period_return
        ),
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=chart_data["Date"],
            y=chart_data["Close"],
            mode="lines",
            name=ticker,
            hovertemplate=(
                "%{x|%b %d, %Y}"
                "<br>"
                "Close: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title=(
            f"{ticker} Closing Price — "
            f"{period_label}"
        ),
        xaxis_title=None,
        yaxis_title="Price",
        hovermode="x unified",
        height=430,
        margin=dict(
            l=10,
            r=10,
            t=55,
            b=10,
        ),
        showlegend=False,
    )

    figure.update_xaxes(
        showgrid=False,
        rangeslider_visible=False,
    )

    figure.update_yaxes(
        tickprefix="$",
        tickformat=",.2f",
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": False,
        },
    )

    st.caption(
        "Historical prices are shown for research context. "
        "Past performance does not establish future performance."
    )


# ==========================================================
# FINANCIAL SNAPSHOT
# ==========================================================

def display_financial_snapshot(ticker):

    if not ticker:
        return

    try:

        data = load_financial_data(
            ticker
        )

    except Exception:

        st.warning(
            f"Financial data for {ticker} "
            "is currently unavailable."
        )

        return

    company_name = data.get(
        "company_name",
        ticker,
    )

    sector = data.get(
        "sector",
        "N/A",
    )

    industry = data.get(
        "industry",
        "N/A",
    )

    st.markdown(
        f"""
        <div class="company-header">

            <div class="company-name">
                {company_name} ({ticker})
            </div>

            <div class="company-details">
                {sector} • {industry}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        "📊 Financial Snapshot"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Price",
        format_price(
            data.get("current_price")
        ),
    )

    c2.metric(
        "Market Cap",
        format_large_number(
            data.get("market_cap")
        ),
    )

    c3.metric(
        "Revenue",
        format_large_number(
            data.get("revenue")
        ),
    )

    c4.metric(
        "Revenue Growth",
        format_percent(
            data.get("revenue_growth")
        ),
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Operating Margin",
        format_percent(
            data.get("operating_margin")
        ),
    )

    c6.metric(
        "Free Cash Flow",
        format_large_number(
            data.get("free_cash_flow")
        ),
    )

    c7.metric(
        "Forward P/E",
        format_ratio(
            data.get("forward_pe")
        ),
    )

    c8.metric(
        "1-Year Performance",
        format_change(
            data.get("one_year_return")
        ),
    )

    with st.expander(
        "View More Financial Metrics"
    ):

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                "#### Profitability"
            )

            st.metric(
                "Net Income",
                format_large_number(
                    data.get("net_income")
                ),
            )

            st.metric(
                "Profit Margin",
                format_percent(
                    data.get("profit_margin")
                ),
            )

            st.metric(
                "Operating Cash Flow",
                format_large_number(
                    data.get(
                        "operating_cash_flow"
                    )
                ),
            )

        with col2:

            st.markdown(
                "#### Balance Sheet"
            )

            st.metric(
                "Cash",
                format_large_number(
                    data.get("total_cash")
                ),
            )

            st.metric(
                "Debt",
                format_large_number(
                    data.get("total_debt")
                ),
            )

            st.metric(
                "Enterprise Value",
                format_large_number(
                    data.get(
                        "enterprise_value"
                    )
                ),
            )

        with col3:

            st.markdown(
                "#### Valuation & Risk"
            )

            st.metric(
                "Trailing P/E",
                format_ratio(
                    data.get("trailing_pe")
                ),
            )

            st.metric(
                "Price / Sales",
                format_ratio(
                    data.get(
                        "price_to_sales"
                    )
                ),
            )

            st.metric(
                "Beta",
                format_ratio(
                    data.get("beta")
                ),
            )

        st.markdown(
            "#### Market Performance"
        )

        p1, p2, p3, p4 = st.columns(4)

        p1.metric(
            "1 Month",
            format_change(
                data.get(
                    "one_month_return"
                )
            ),
        )

        p2.metric(
            "3 Months",
            format_change(
                data.get(
                    "three_month_return"
                )
            ),
        )

        p3.metric(
            "6 Months",
            format_change(
                data.get(
                    "six_month_return"
                )
            ),
        )

        p4.metric(
            "1 Year",
            format_change(
                data.get(
                    "one_year_return"
                )
            ),
        )

        st.markdown(
            "#### Trading Range"
        )

        r1, r2 = st.columns(2)

        r1.metric(
            "52-Week Low",
            format_price(
                data.get(
                    "fifty_two_week_low"
                )
            ),
        )

        r2.metric(
            "52-Week High",
            format_price(
                data.get(
                    "fifty_two_week_high"
                )
            ),
        )

    st.caption(
        "Market and company metrics are retrieved from "
        "Yahoo Finance and may be delayed, unavailable, "
        "or revised."
    )

    st.divider()

    display_price_chart(
        ticker
    )

    st.divider()



# ==========================================================
# QUANTITATIVE SCENARIO DISPLAY
# ==========================================================

def display_quantitative_scenario(result):
    st.subheader("📊 Quantitative Scenario Results")

    st.caption(
        "These are deterministic sensitivity calculations based on "
        "your selected assumptions. They are not forecasts."
    )

    current_revenue = result.get("current_revenue")
    scenario_revenue = result.get("scenario_revenue")
    current_operating_income = result.get("current_operating_income")
    scenario_operating_income = result.get("scenario_operating_income")
    current_fcf = result.get("current_free_cash_flow")
    scenario_fcf = result.get("scenario_free_cash_flow")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Scenario Revenue",
        format_large_number(scenario_revenue),
        delta=format_change(result.get("revenue_change")),
    )

    c2.metric(
        "Scenario Operating Income",
        format_large_number(scenario_operating_income),
        delta=format_change(result.get("operating_income_change_pct")),
    )

    c3.metric(
        "Scenario Free Cash Flow",
        format_large_number(scenario_fcf),
        delta=format_change(result.get("fcf_change_pct")),
    )

    st.markdown("#### Current vs. Scenario")

    categories = []
    current_values = []
    scenario_values = []

    comparisons = [
        ("Revenue", current_revenue, scenario_revenue),
        ("Operating Income", current_operating_income, scenario_operating_income),
        ("Free Cash Flow", current_fcf, scenario_fcf),
    ]

    for label, current_value, scenario_value in comparisons:
        if current_value is not None and scenario_value is not None:
            categories.append(label)
            current_values.append(float(current_value) / 1_000_000_000)
            scenario_values.append(float(scenario_value) / 1_000_000_000)

    if categories:
        figure = go.Figure()

        figure.add_trace(
            go.Bar(
                name="Current",
                x=categories,
                y=current_values,
                hovertemplate="%{x}<br>Current: $%{y:,.2f}B<extra></extra>",
            )
        )

        figure.add_trace(
            go.Bar(
                name="Scenario",
                x=categories,
                y=scenario_values,
                hovertemplate="%{x}<br>Scenario: $%{y:,.2f}B<extra></extra>",
            )
        )

        figure.update_layout(
            barmode="group",
            yaxis_title="USD Billions",
            height=430,
            margin=dict(l=10, r=10, t=30, b=10),
            legend_title=None,
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={"displaylogo": False},
        )

    with st.expander("View Scenario Calculation Details"):
        d1, d2 = st.columns(2)

        with d1:
            st.markdown("#### Current")
            st.metric("Revenue", format_large_number(current_revenue))
            st.metric(
                "Operating Margin",
                format_percent(result.get("current_operating_margin")),
            )
            st.metric(
                "Operating Income",
                format_large_number(current_operating_income),
            )
            st.metric(
                "FCF Margin",
                format_percent(result.get("current_fcf_margin")),
            )
            st.metric(
                "Free Cash Flow",
                format_large_number(current_fcf),
            )

        with d2:
            st.markdown("#### Scenario")
            st.metric("Revenue", format_large_number(scenario_revenue))
            st.metric(
                "Operating Margin",
                format_percent(result.get("scenario_operating_margin")),
            )
            st.metric(
                "Operating Income",
                format_large_number(scenario_operating_income),
            )
            st.metric(
                "FCF Margin",
                format_percent(result.get("scenario_fcf_margin")),
            )
            st.metric(
                "Free Cash Flow",
                format_large_number(scenario_fcf),
            )

    st.info(
        "The scenario engine applies your assumptions mechanically to "
        "retrieved company financial data. The AI analysis evaluates "
        "the broader scenario and evidence separately."
    )



# ==========================================================
# RESEARCH REPORT + PDF EXPORT
# ==========================================================

def _safe_text(value):
    """Normalize Unicode punctuation so ReportLab's built-in fonts render cleanly."""
    if value is None:
        return ""

    value = str(value)

    replacements = {
        "\u2010": "-",   # hyphen
        "\u2011": "-",   # non-breaking hyphen
        "\u2012": "-",   # figure dash
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2212": "-",   # minus sign
        "\u00ad": "-",   # soft hyphen
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u00a0": " ",   # non-breaking space
    }

    for original, replacement in replacements.items():
        value = value.replace(original, replacement)

    return escape(value)


def _pdf_paragraph(value, style):
    """Safely convert plain text into a ReportLab paragraph."""
    safe = _safe_text(value).replace("\n", "<br/>")
    return Paragraph(safe, style)


def _markdown_blocks_for_pdf(text, body_style, heading_style, bullet_style):
    """Convert common AI Markdown into clean ReportLab flowables."""
    flowables = []
    lines = (text or "No analysis was returned.").splitlines()
    paragraph_lines = []

    def flush_paragraph():
        if paragraph_lines:
            joined = " ".join(line.strip() for line in paragraph_lines if line.strip())
            if joined:
                # Preserve simple bold Markdown.
                safe = _safe_text(joined)
                safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
                flowables.append(Paragraph(safe, body_style))
            paragraph_lines.clear()

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            flush_paragraph()
            continue

        if line.startswith("### "):
            flush_paragraph()
            flowables.append(
                Paragraph(_safe_text(line[4:]), heading_style)
            )
        elif line.startswith("## "):
            flush_paragraph()
            flowables.append(
                Paragraph(_safe_text(line[3:]), heading_style)
            )
        elif line.startswith("# "):
            flush_paragraph()
            flowables.append(
                Paragraph(_safe_text(line[2:]), heading_style)
            )
        elif line.startswith(("- ", "* ")):
            flush_paragraph()
            safe = _safe_text(line[2:])
            safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
            flowables.append(
                Paragraph(f"• {safe}", bullet_style)
            )
        else:
            paragraph_lines.append(line)

    flush_paragraph()
    return flowables


def _report_source_rows(sources, cell_style, header_style):
    rows = [
        [
            Paragraph("#", header_style),
            Paragraph("SOURCE TYPE", header_style),
            Paragraph("SOURCE", header_style),
        ]
    ]

    for number, source in enumerate(sources or [], start=1):
        title = source.get("title", "Untitled Source")
        source_type = source.get("source_type", "OTHER")
        domain = source.get("domain", "")
        url = source.get("url", "")

        label = title if not domain else f"{title} ({domain})"
        if url:
            label = f'{_safe_text(label)}<br/><font size="6.8">{_safe_text(url)}</font>'
        else:
            label = _safe_text(label)

        rows.append(
            [
                Paragraph(str(number), cell_style),
                Paragraph(_safe_text(source_type), cell_style),
                Paragraph(label, cell_style),
            ]
        )

    return rows


def build_research_report_pdf(
    report_title,
    research_question,
    analysis,
    sources,
    ticker=None,
    financial_data=None,
    scenario_result=None,
    portfolio_financials=None,
    normalized_weights=None,
):
    """Create a polished investment-research PDF entirely in memory."""

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title=report_title,
        author="AI Investment Intelligence Engine",
    )

    styles = getSampleStyleSheet()

    navy = colors.HexColor("#14213D")
    blue = colors.HexColor("#2F5DA8")
    pale_blue = colors.HexColor("#EEF4FB")
    light_gray = colors.HexColor("#F4F6F8")
    border = colors.HexColor("#D9DEE5")
    muted = colors.HexColor("#5D6673")
    dark = colors.HexColor("#20242A")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=navy,
        spaceAfter=7,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        leading=12,
        textColor=muted,
        spaceAfter=16,
    )

    section_style = ParagraphStyle(
        "ReportSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=15,
        textColor=navy,
        spaceBefore=12,
        spaceAfter=7,
        keepWithNext=True,
    )

    analysis_heading_style = ParagraphStyle(
        "AnalysisHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=blue,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13.5,
        textColor=dark,
        spaceAfter=7,
    )

    bullet_style = ParagraphStyle(
        "ReportBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-7,
        spaceAfter=4,
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=10,
        textColor=muted,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=9.5,
        textColor=dark,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=table_cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    story = []

    # ---------- Cover / report identity ----------
    story.append(Spacer(1, 8))
    story.append(Paragraph("AI INVESTMENT INTELLIGENCE ENGINE", subtitle_style))
    story.append(Paragraph(_safe_text(report_title), title_style))

    generated = datetime.now().strftime("%B %d, %Y • %I:%M %p")
    identity = f"Generated {generated}"
    if ticker:
        identity = f"{_safe_text(ticker)}  |  {identity}"

    story.append(Paragraph(identity, subtitle_style))

    overview_data = [
        [
            Paragraph("<b>RESEARCH QUESTION / EVENT</b>", table_cell_style)
        ],
        [
            _pdf_paragraph(research_question, body_style)
        ],
    ]
    overview_table = Table(overview_data, colWidths=[6.55 * inch])
    overview_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), pale_blue),
                ("BOX", (0, 0), (-1, -1), 0.6, border),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(overview_table)
    story.append(Spacer(1, 8))

    # ---------- Financial snapshot ----------
    if financial_data:
        story.append(Paragraph("Financial Snapshot", section_style))

        financial_rows = [
            ["Metric", "Value", "Metric", "Value"],
            [
                "Company",
                financial_data.get("company_name", ticker or "N/A"),
                "Price",
                format_price(financial_data.get("current_price")),
            ],
            [
                "Market Cap",
                format_large_number(financial_data.get("market_cap")),
                "Revenue",
                format_large_number(financial_data.get("revenue")),
            ],
            [
                "Revenue Growth",
                format_percent(financial_data.get("revenue_growth")),
                "Operating Margin",
                format_percent(financial_data.get("operating_margin")),
            ],
            [
                "Free Cash Flow",
                format_large_number(financial_data.get("free_cash_flow")),
                "Forward P/E",
                format_ratio(financial_data.get("forward_pe")),
            ],
            [
                "Beta",
                format_ratio(financial_data.get("beta")),
                "1-Year Performance",
                format_change(financial_data.get("one_year_return")),
            ],
        ]

        financial_table = Table(
            financial_rows,
            colWidths=[1.25 * inch, 2.0 * inch, 1.35 * inch, 1.95 * inch],
            repeatRows=1,
        )
        financial_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
                    ("GRID", (0, 0), (-1, -1), 0.35, border),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(financial_table)

    # ---------- Scenario ----------
    if scenario_result:
        story.append(Paragraph("Quantitative Scenario", section_style))
        story.append(
            Paragraph(
                "Sensitivity analysis based on user-supplied assumptions; "
                "these values are not forecasts.",
                small_style,
            )
        )
        story.append(Spacer(1, 5))

        scenario_rows = [
            ["Metric", "Current", "Scenario"],
            [
                "Revenue",
                format_large_number(scenario_result.get("current_revenue")),
                format_large_number(scenario_result.get("scenario_revenue")),
            ],
            [
                "Operating Margin",
                format_percent(scenario_result.get("current_operating_margin")),
                format_percent(scenario_result.get("scenario_operating_margin")),
            ],
            [
                "Operating Income",
                format_large_number(scenario_result.get("current_operating_income")),
                format_large_number(scenario_result.get("scenario_operating_income")),
            ],
            [
                "FCF Margin",
                format_percent(scenario_result.get("current_fcf_margin")),
                format_percent(scenario_result.get("scenario_fcf_margin")),
            ],
            [
                "Free Cash Flow",
                format_large_number(scenario_result.get("current_free_cash_flow")),
                format_large_number(scenario_result.get("scenario_free_cash_flow")),
            ],
        ]

        scenario_table = Table(
            scenario_rows,
            colWidths=[2.25 * inch, 2.15 * inch, 2.15 * inch],
            repeatRows=1,
        )
        scenario_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
                    ("GRID", (0, 0), (-1, -1), 0.35, border),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(scenario_table)

    # ---------- Portfolio ----------
    if portfolio_financials:
        story.append(Paragraph("Portfolio Financial Overview", section_style))

        portfolio_rows = [
            [
                "Ticker",
                "Weight",
                "Revenue Growth",
                "Operating Margin",
                "Beta",
                "Forward P/E",
            ]
        ]

        for company in portfolio_financials:
            portfolio_ticker = company.get("ticker", "")
            weight = (
                (normalized_weights or {}).get(
                    portfolio_ticker,
                    company.get("weight", 0),
                )
                * 100
            )

            portfolio_rows.append(
                [
                    portfolio_ticker,
                    f"{weight:.1f}%",
                    format_percent(company.get("revenue_growth")),
                    format_percent(company.get("operating_margin")),
                    format_ratio(company.get("beta")),
                    format_ratio(company.get("forward_pe")),
                ]
            )

        portfolio_table = Table(
            portfolio_rows,
            colWidths=[
                0.72 * inch,
                0.72 * inch,
                1.3 * inch,
                1.3 * inch,
                0.8 * inch,
                1.05 * inch,
            ],
            repeatRows=1,
        )
        portfolio_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.2),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
                    ("GRID", (0, 0), (-1, -1), 0.35, border),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(portfolio_table)

    # ---------- AI research analysis ----------
    story.append(Paragraph("Research Analysis", section_style))
    story.extend(
        _markdown_blocks_for_pdf(
            analysis,
            body_style,
            analysis_heading_style,
            bullet_style,
        )
    )

    # ---------- Evidence ----------
    story.append(PageBreak())
    story.append(Paragraph("Evidence & Sources", section_style))
    story.append(
        Paragraph(
            "Sources are classified to make the research trail easier to inspect. "
            "Classification is not a truth score; relevance, recency, specificity, "
            "and direct support should still be evaluated.",
            small_style,
        )
    )
    story.append(Spacer(1, 8))

    source_rows = _report_source_rows(
        sources,
        table_cell_style,
        table_header_style,
    )

    if len(source_rows) == 1:
        story.append(
            Paragraph(
                "No evidence sources were returned for this analysis.",
                body_style,
            )
        )
    else:
        source_table = Table(
            source_rows,
            colWidths=[0.35 * inch, 1.25 * inch, 4.95 * inch],
            repeatRows=1,
        )
        source_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), navy),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
                    ("GRID", (0, 0), (-1, -1), 0.3, border),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(source_table)

    story.append(Spacer(1, 16))
    story.append(Paragraph("Important Disclosure", section_style))
    story.append(
        Paragraph(
            "Research and educational use only. This report does not provide "
            "personalized investment recommendations. Financial and market data "
            "may be delayed, unavailable, or revised. Scenario values are "
            "sensitivity calculations based on user-supplied assumptions and are "
            "not forecasts. AI-generated analysis should be reviewed against the "
            "underlying evidence before use.",
            small_style,
        )
    )

    def add_page_number(canvas, document):
        canvas.saveState()
        width, _ = letter
        canvas.setStrokeColor(border)
        canvas.setLineWidth(0.4)
        canvas.line(
            document.leftMargin,
            0.48 * inch,
            width - document.rightMargin,
            0.48 * inch,
        )
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(muted)
        canvas.drawString(
            document.leftMargin,
            0.30 * inch,
            "AI Investment Intelligence Engine",
        )
        canvas.drawRightString(
            width - document.rightMargin,
            0.30 * inch,
            f"Page {document.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    buffer.seek(0)
    return buffer.getvalue()


def display_pdf_download(
    result,
    report_title,
    research_question,
    file_name,
    ticker=None,
    financial_data=None,
    scenario_result=None,
    portfolio_financials=None,
    normalized_weights=None,
):
    analysis = result.get("analysis", "")
    sources = result.get("sources", [])

    pdf_bytes = build_research_report_pdf(
        report_title=report_title,
        research_question=research_question,
        analysis=analysis,
        sources=sources,
        ticker=ticker,
        financial_data=financial_data,
        scenario_result=scenario_result,
        portfolio_financials=portfolio_financials,
        normalized_weights=normalized_weights,
    )

    st.download_button(
        "📄 Download Research Report PDF",
        data=pdf_bytes,
        file_name=file_name,
        mime="application/pdf",
        use_container_width=True,
    )


# ==========================================================
# SOURCE QUALITY HELPERS
# ==========================================================

def source_badge(source_type):

    source_type = (
        source_type
        or "OTHER"
    )

    if source_type == "PRIMARY":
        css_class = "source-primary"

    elif source_type == "OFFICIAL COMPANY":
        css_class = "source-official"

    elif source_type == "HIGH QUALITY":
        css_class = "source-high"

    elif source_type == "LOWER PRIORITY":
        css_class = "source-low"

    else:
        css_class = "source-other"

    return (
        f'<span class="{css_class}">'
        f'{source_type}'
        f'</span>'
    )


def source_statistics(sources):

    total = len(sources)

    primary = sum(
        1
        for source in sources
        if source.get(
            "source_type"
        ) == "PRIMARY"
    )

    official = sum(
        1
        for source in sources
        if source.get(
            "source_type"
        ) == "OFFICIAL COMPANY"
    )

    high_quality = sum(
        1
        for source in sources
        if source.get(
            "source_type"
        ) == "HIGH QUALITY"
    )

    return (
        total,
        primary,
        official,
        high_quality,
    )


# ==========================================================
# DISPLAY RESEARCH RESULTS
# ==========================================================

def display_results(
    result,
    success_message,
):

    analysis = result.get(
        "analysis",
        "",
    )

    sources = result.get(
        "sources",
        [],
    )

    st.success(
        success_message
    )

    st.markdown(
        """
        <div class="results-banner">
            <div class="results-title">Research Output</div>
            <div class="results-copy">
                The analysis below combines retrieved evidence, company
                financial context, quantitative reasoning, counter-evidence,
                and uncertainty. Source quality is shown separately so the
                research trail remains inspectable.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        "🧠 Research Analysis"
    )

    st.markdown(
        analysis
    )

    st.divider()

    st.subheader(
        "🔎 Evidence Quality"
    )

    (
        total,
        primary,
        official,
        high_quality,
    ) = source_statistics(
        sources
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Sources Retrieved",
        total,
    )

    c2.metric(
        "Primary",
        primary,
    )

    c3.metric(
        "Official Company",
        official,
    )

    c4.metric(
        "Established Financial / News",
        high_quality,
    )

    stronger_sources = (
        primary
        + official
        + high_quality
    )

    if total:
        stronger_share = (
            stronger_sources / total
        ) * 100

        st.progress(
            min(
                stronger_share / 100,
                1.0,
            )
        )

        st.caption(
            f"{stronger_share:.0f}% of retrieved sources are classified "
            "as primary, official-company, or established financial/news "
            "sources."
        )

    st.markdown(
        """
        <div class="evidence-note">
            Source classification is a research aid, not a truth score.
            Evidence should still be evaluated for relevance, recency,
            specificity, and whether it actually supports the claim being made.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(
        "📚 Evidence Trail"
    )

    if not sources:

        st.warning(
            "No supporting evidence sources were retrieved."
        )

        return

    for number, source in enumerate(
        sources,
        start=1,
    ):

        title = source.get(
            "title",
            "Untitled Source",
        )

        url = source.get(
            "url",
            "",
        )

        content = source.get(
            "content",
            "",
        )

        domain = source.get(
            "domain",
            "",
        )

        source_type = source.get(
            "source_type",
            "OTHER",
        )

        expander_label = (
            f"{number}. [{source_type}] {title}"
        )

        with st.expander(
            expander_label
        ):

            st.markdown(
                source_badge(
                    source_type
                ),
                unsafe_allow_html=True,
            )

            if domain:

                st.caption(
                    f"Domain: {domain}"
                )

            if url:

                st.markdown(
                    f"[Open original source ↗]({url})"
                )

            if content:

                st.markdown(
                    "**Retrieved evidence**"
                )

                st.write(
                    content[:1800]
                )


# ==========================================================
# MODE 1 — CLAIM INVESTIGATION
# ==========================================================

if mode == "🔎 Investigate a Market Claim":

    st.header(
        "🔎 Investigate a Market Claim"
    )

    st.markdown(
        """
        Test a market narrative, financial claim, or
        investment thesis against current evidence.
        """
    )

    if ticker:

        display_financial_snapshot(
            ticker
        )

    claim = st.text_area(
        "Claim to Investigate",
        placeholder=(
            "Example: Apple's services business is becoming "
            "more important to its financial performance."
        ),
        height=160,
    )

    investigate = st.button(
        "Investigate Claim",
        type="primary",
        use_container_width=True,
    )

    if investigate:

        if not claim.strip():

            st.warning(
                "Enter a claim to investigate."
            )

        else:

            with st.spinner(
                "Retrieving evidence and "
                "evaluating the claim..."
            ):

                try:

                    result = analyze_claim(
                        claim=claim,
                        ticker=(
                            ticker
                            if ticker
                            else None
                        ),
                    )

                    display_results(
                        result,
                        "Evidence investigation complete.",
                    )

                    claim_financial_data = (
                        load_financial_data(ticker)
                        if ticker
                        else None
                    )

                    display_pdf_download(
                        result=result,
                        report_title="Market Claim Investigation Report",
                        research_question=claim,
                        file_name=(
                            f"{ticker}_claim_research_report.pdf"
                            if ticker
                            else "market_claim_research_report.pdf"
                        ),
                        ticker=(ticker if ticker else None),
                        financial_data=claim_financial_data,
                    )

                except Exception as error:

                    st.error(
                        "The investigation could not "
                        "be completed."
                    )

                    st.exception(
                        error
                    )


# ==========================================================
# MODE 2 — STOCK IMPACT
# ==========================================================

elif mode == "📈 How Does This Affect My Stock?":

    st.header(
        "📈 How Does This Affect My Stock?"
    )

    st.markdown(
        """
        Trace how a real-world market event could transmit
        into a company's financial performance and valuation.
        """
    )

    if ticker:

        display_financial_snapshot(
            ticker
        )

    event = st.text_area(
        "Market Event or Development",
        placeholder=(
            "Example: New tariffs are introduced on electronics "
            "and components imported from China."
        ),
        height=160,
    )

    analyze = st.button(
        "Analyze Stock Impact",
        type="primary",
        use_container_width=True,
    )

    if analyze:

        if not ticker:

            st.warning(
                "Enter a stock ticker in the sidebar."
            )

        elif not event.strip():

            st.warning(
                "Enter a market event."
            )

        else:

            with st.spinner(
                f"Researching potential impact on {ticker}..."
            ):

                try:

                    result = analyze_stock_impact(
                        event=event,
                        ticker=ticker,
                    )

                    display_results(
                        result,
                        f"{ticker} impact analysis complete.",
                    )

                    display_pdf_download(
                        result=result,
                        report_title=f"{ticker} Stock Impact Research Report",
                        research_question=event,
                        file_name=f"{ticker}_stock_impact_report.pdf",
                        ticker=ticker,
                        financial_data=load_financial_data(ticker),
                    )

                except Exception as error:

                    st.error(
                        "Stock-impact analysis could "
                        "not be completed."
                    )

                    st.exception(
                        error
                    )


# ==========================================================
# MODE 3 — SCENARIO ANALYSIS
# ==========================================================

elif mode == "🧪 Scenario Analysis":

    st.header("🧪 Scenario Analysis")

    st.markdown(
        """
        Stress-test a hypothetical economic, industry, or company scenario
        against the company's current financial position. The numerical
        model uses only the assumptions you select below.
        """
    )

    if ticker:
        display_financial_snapshot(ticker)

    scenario = st.text_area(
        "Hypothetical Scenario",
        placeholder=(
            "Example: Demand weakens in a major market while input costs "
            "increase, pressuring revenue and margins."
        ),
        height=150,
    )

    st.subheader("🎛️ Financial Scenario Assumptions")

    st.caption(
        "You control the financial assumptions. The AI does not choose "
        "these percentages."
    )

    assumption_col1, assumption_col2, assumption_col3 = st.columns(3)

    with assumption_col1:
        revenue_change_pct = st.slider(
            "Revenue Change (%)",
            min_value=-50.0,
            max_value=50.0,
            value=0.0,
            step=1.0,
            help="Percentage change applied to current company revenue.",
        )

    with assumption_col2:
        operating_margin_change_points = st.slider(
            "Operating Margin Change (percentage points)",
            min_value=-15.0,
            max_value=15.0,
            value=0.0,
            step=0.5,
            help="Example: -1.5 changes a 30% margin to 28.5%.",
        )

    with assumption_col3:
        fcf_margin_change_points = st.slider(
            "FCF Margin Change (percentage points)",
            min_value=-15.0,
            max_value=15.0,
            value=0.0,
            step=0.5,
            help="Change applied to the current free-cash-flow margin.",
        )

    st.markdown(
        f"""
        **Selected assumptions:** Revenue **{revenue_change_pct:+.1f}%** ·
        Operating margin **{operating_margin_change_points:+.1f} pp** ·
        FCF margin **{fcf_margin_change_points:+.1f} pp**
        """
    )

    run_scenario = st.button(
        "Run Quantitative Scenario + AI Analysis",
        type="primary",
        use_container_width=True,
    )

    if run_scenario:

        if not ticker:
            st.warning("Enter a stock ticker in the sidebar.")

        elif not scenario.strip():
            st.warning("Enter a hypothetical scenario.")

        else:
            try:
                with st.spinner(
                    f"Calculating financial sensitivity for {ticker}..."
                ):
                    quantitative_result = run_financial_scenario(
                        ticker=ticker,
                        revenue_change_pct=revenue_change_pct,
                        operating_margin_change_points=(
                            operating_margin_change_points
                        ),
                        fcf_margin_change_points=fcf_margin_change_points,
                    )

                display_quantitative_scenario(quantitative_result)

                st.divider()
                st.subheader("🧠 Evidence-Based Scenario Interpretation")

                scenario_with_assumptions = f"""
{scenario}

USER-SUPPLIED QUANTITATIVE ASSUMPTIONS:
- Revenue change: {revenue_change_pct:+.1f}%
- Operating margin change: {operating_margin_change_points:+.1f} percentage points
- Free cash flow margin change: {fcf_margin_change_points:+.1f} percentage points

Treat these percentages as hypothetical user-supplied assumptions, not
verified facts or forecasts. Analyze mechanisms that could make the
scenario more or less plausible. Do not invent additional numerical
impacts.
"""

                with st.spinner(
                    f"Researching evidence and interpreting the scenario "
                    f"for {ticker}..."
                ):
                    result = analyze_scenario(
                        scenario=scenario_with_assumptions,
                        ticker=ticker,
                    )

                display_results(
                    result,
                    "Quantitative and evidence-based scenario analysis complete.",
                )

                display_pdf_download(
                    result=result,
                    report_title=f"{ticker} Scenario Analysis Report",
                    research_question=scenario,
                    file_name=f"{ticker}_scenario_analysis_report.pdf",
                    ticker=ticker,
                    financial_data=load_financial_data(ticker),
                    scenario_result=quantitative_result,
                )

            except Exception as error:
                st.error("Scenario analysis could not be completed.")
                st.exception(error)


# ==========================================================
# MODE 4 — PORTFOLIO IMPACT
# ==========================================================

elif mode == "💼 Portfolio Impact":

    st.header("💼 Portfolio Impact")

    st.markdown(
        """
        Analyze how one market event could propagate across multiple
        portfolio holdings using portfolio weights, company fundamentals,
        market sensitivity, and live evidence.
        """
    )

    portfolio_input = st.text_input(
        "Portfolio Tickers",
        placeholder="AAPL, MSFT, NVDA, AMZN",
    )

    event = st.text_area(
        "Market Event or Development",
        placeholder=(
            "Example: New restrictions are introduced on advanced "
            "semiconductor exports."
        ),
        height=150,
    )

    st.subheader("⚖️ Portfolio Weights")

    st.caption(
        "Optional: enter portfolio weights as TICKER: WEIGHT%. "
        "If left blank, the holdings will be treated as equally weighted "
        "for the quantitative portfolio view."
    )

    position_information = st.text_area(
        "Portfolio Weights / Positions",
        placeholder=(
            "AAPL: 40%\n"
            "MSFT: 30%\n"
            "NVDA: 20%\n"
            "AMZN: 10%"
        ),
        height=120,
    )

    analyze_portfolio = st.button(
        "Analyze Portfolio Impact",
        type="primary",
        use_container_width=True,
    )

    if analyze_portfolio:

        tickers = [
            item.strip().upper()
            for item in portfolio_input.split(",")
            if item.strip()
        ]

        if not tickers:

            st.warning(
                "Enter at least one portfolio ticker."
            )

        elif not event.strip():

            st.warning(
                "Enter a market event."
            )

        else:

            try:
                # ------------------------------------------------------
                # PARSE PORTFOLIO WEIGHTS
                # ------------------------------------------------------
                weights = {}

                if position_information.strip():
                    for line in position_information.splitlines():
                        if ":" not in line:
                            continue

                        raw_ticker, raw_weight = line.split(":", 1)
                        parsed_ticker = raw_ticker.strip().upper()

                        try:
                            parsed_weight = float(
                                raw_weight.strip().replace("%", "")
                            )
                        except ValueError:
                            continue

                        if parsed_ticker in tickers:
                            weights[parsed_ticker] = parsed_weight

                if not weights:
                    equal_weight = 100 / len(tickers)
                    weights = {
                        portfolio_ticker: equal_weight
                        for portfolio_ticker in tickers
                    }
                else:
                    missing_tickers = [
                        portfolio_ticker
                        for portfolio_ticker in tickers
                        if portfolio_ticker not in weights
                    ]

                    if missing_tickers:
                        st.warning(
                            "Weights were not provided for: "
                            + ", ".join(missing_tickers)
                            + ". Those holdings are shown with 0% weight."
                        )
                        for portfolio_ticker in missing_tickers:
                            weights[portfolio_ticker] = 0.0

                total_weight = sum(weights.values())

                if total_weight <= 0:
                    st.error(
                        "Portfolio weights must add to more than 0%."
                    )
                    st.stop()

                normalized_weights = {
                    portfolio_ticker: (
                        weight / total_weight
                    )
                    for portfolio_ticker, weight in weights.items()
                }

                # ------------------------------------------------------
                # PORTFOLIO OVERVIEW
                # ------------------------------------------------------
                st.divider()
                st.subheader("📊 Portfolio Overview")

                overview1, overview2, overview3 = st.columns(3)

                overview1.metric(
                    "Holdings",
                    len(tickers),
                )

                overview2.metric(
                    "Entered Weight",
                    f"{total_weight:.1f}%",
                )

                largest_holding = max(
                    normalized_weights,
                    key=normalized_weights.get,
                )

                overview3.metric(
                    "Largest Holding",
                    (
                        f"{largest_holding} "
                        f"{normalized_weights[largest_holding] * 100:.1f}%"
                    ),
                )

                if abs(total_weight - 100) > 0.01:
                    st.info(
                        f"Entered weights total {total_weight:.1f}%. "
                        "For quantitative comparisons, the app normalized "
                        "them to 100% while preserving relative weights."
                    )

                # ------------------------------------------------------
                # ALLOCATION CHART
                # ------------------------------------------------------
                allocation_figure = go.Figure(
                    data=[
                        go.Pie(
                            labels=list(normalized_weights.keys()),
                            values=[
                                value * 100
                                for value in normalized_weights.values()
                            ],
                            hole=0.48,
                            textinfo="label+percent",
                            hovertemplate=(
                                "%{label}<br>"
                                "Portfolio Weight: %{percent}"
                                "<extra></extra>"
                            ),
                        )
                    ]
                )

                allocation_figure.update_layout(
                    title="Portfolio Allocation",
                    height=430,
                    margin=dict(
                        l=10,
                        r=10,
                        t=60,
                        b=10,
                    ),
                    showlegend=True,
                )

                st.plotly_chart(
                    allocation_figure,
                    use_container_width=True,
                    config={
                        "displaylogo": False,
                    },
                )

                # ------------------------------------------------------
                # LOAD COMPANY FINANCIAL DATA
                # ------------------------------------------------------
                with st.spinner(
                    "Loading financial data for portfolio holdings..."
                ):
                    portfolio_financials = []

                    for portfolio_ticker in tickers:
                        try:
                            company_data = load_financial_data(
                                portfolio_ticker
                            )

                            portfolio_financials.append(
                                {
                                    "ticker": portfolio_ticker,
                                    "company_name": company_data.get(
                                        "company_name",
                                        portfolio_ticker,
                                    ),
                                    "weight": normalized_weights.get(
                                        portfolio_ticker,
                                        0,
                                    ),
                                    "market_cap": company_data.get(
                                        "market_cap"
                                    ),
                                    "revenue": company_data.get(
                                        "revenue"
                                    ),
                                    "revenue_growth": company_data.get(
                                        "revenue_growth"
                                    ),
                                    "operating_margin": company_data.get(
                                        "operating_margin"
                                    ),
                                    "free_cash_flow": company_data.get(
                                        "free_cash_flow"
                                    ),
                                    "forward_pe": company_data.get(
                                        "forward_pe"
                                    ),
                                    "beta": company_data.get(
                                        "beta"
                                    ),
                                    "one_year_return": company_data.get(
                                        "one_year_return"
                                    ),
                                }
                            )

                        except Exception:
                            portfolio_financials.append(
                                {
                                    "ticker": portfolio_ticker,
                                    "company_name": portfolio_ticker,
                                    "weight": normalized_weights.get(
                                        portfolio_ticker,
                                        0,
                                    ),
                                    "market_cap": None,
                                    "revenue": None,
                                    "revenue_growth": None,
                                    "operating_margin": None,
                                    "free_cash_flow": None,
                                    "forward_pe": None,
                                    "beta": None,
                                    "one_year_return": None,
                                }
                            )

                # ------------------------------------------------------
                # HOLDING CARDS
                # ------------------------------------------------------
                st.subheader("🏢 Holdings & Financial Exposure")

                for company in portfolio_financials:
                    with st.expander(
                        (
                            f"{company['ticker']} — "
                            f"{company['company_name']} "
                            f"({company['weight'] * 100:.1f}% weight)"
                        )
                    ):
                        h1, h2, h3, h4 = st.columns(4)

                        h1.metric(
                            "Market Cap",
                            format_large_number(
                                company["market_cap"]
                            ),
                        )

                        h2.metric(
                            "Revenue Growth",
                            format_percent(
                                company["revenue_growth"]
                            ),
                        )

                        h3.metric(
                            "Operating Margin",
                            format_percent(
                                company["operating_margin"]
                            ),
                        )

                        h4.metric(
                            "Free Cash Flow",
                            format_large_number(
                                company["free_cash_flow"]
                            ),
                        )

                        h5, h6, h7 = st.columns(3)

                        h5.metric(
                            "Forward P/E",
                            format_ratio(
                                company["forward_pe"]
                            ),
                        )

                        h6.metric(
                            "Beta",
                            format_ratio(
                                company["beta"]
                            ),
                        )

                        h7.metric(
                            "1-Year Performance",
                            format_change(
                                company["one_year_return"]
                            ),
                        )

                # ------------------------------------------------------
                # FINANCIAL COMPARISON CHART
                # ------------------------------------------------------
                st.subheader("📈 Portfolio Financial Comparison")

                comparison_metric = st.selectbox(
                    "Comparison Metric",
                    [
                        "Revenue Growth",
                        "Operating Margin",
                        "1-Year Performance",
                        "Beta",
                        "Forward P/E",
                    ],
                    key="portfolio_comparison_metric",
                )

                metric_mapping = {
                    "Revenue Growth": "revenue_growth",
                    "Operating Margin": "operating_margin",
                    "1-Year Performance": "one_year_return",
                    "Beta": "beta",
                    "Forward P/E": "forward_pe",
                }

                selected_key = metric_mapping[
                    comparison_metric
                ]

                chart_tickers = []
                chart_values = []

                for company in portfolio_financials:
                    value = company.get(selected_key)

                    if value is None:
                        continue

                    value = float(value)

                    if selected_key in {
                        "revenue_growth",
                        "operating_margin",
                        "one_year_return",
                    }:
                        value *= 100

                    chart_tickers.append(
                        company["ticker"]
                    )
                    chart_values.append(
                        value
                    )

                if chart_values:
                    comparison_figure = go.Figure()

                    comparison_figure.add_trace(
                        go.Bar(
                            x=chart_tickers,
                            y=chart_values,
                            hovertemplate=(
                                "%{x}<br>"
                                + comparison_metric
                                + ": %{y:,.2f}"
                                + (
                                    "%"
                                    if selected_key in {
                                        "revenue_growth",
                                        "operating_margin",
                                        "one_year_return",
                                    }
                                    else ""
                                )
                                + "<extra></extra>"
                            ),
                        )
                    )

                    y_axis_title = (
                        "Percent"
                        if selected_key in {
                            "revenue_growth",
                            "operating_margin",
                            "one_year_return",
                        }
                        else comparison_metric
                    )

                    comparison_figure.update_layout(
                        title=(
                            f"{comparison_metric} Across Holdings"
                        ),
                        yaxis_title=y_axis_title,
                        xaxis_title=None,
                        height=420,
                        margin=dict(
                            l=10,
                            r=10,
                            t=55,
                            b=10,
                        ),
                        showlegend=False,
                    )

                    st.plotly_chart(
                        comparison_figure,
                        use_container_width=True,
                        config={
                            "displaylogo": False,
                        },
                    )

                # ------------------------------------------------------
                # WEIGHTED PORTFOLIO INDICATORS
                # ------------------------------------------------------
                st.subheader("🧮 Weighted Portfolio Indicators")

                def weighted_average(key):
                    numerator = 0.0
                    denominator = 0.0

                    for company in portfolio_financials:
                        value = company.get(key)
                        weight = company.get("weight", 0)

                        if value is None:
                            continue

                        try:
                            value = float(value)
                        except (TypeError, ValueError):
                            continue

                        numerator += value * weight
                        denominator += weight

                    if denominator == 0:
                        return None

                    return numerator / denominator

                weighted_growth = weighted_average(
                    "revenue_growth"
                )
                weighted_margin = weighted_average(
                    "operating_margin"
                )
                weighted_beta = weighted_average(
                    "beta"
                )
                weighted_forward_pe = weighted_average(
                    "forward_pe"
                )
                weighted_one_year = weighted_average(
                    "one_year_return"
                )

                w1, w2, w3, w4, w5 = st.columns(5)

                w1.metric(
                    "Weighted Revenue Growth",
                    format_percent(
                        weighted_growth
                    ),
                )

                w2.metric(
                    "Weighted Operating Margin",
                    format_percent(
                        weighted_margin
                    ),
                )

                w3.metric(
                    "Weighted Beta",
                    format_ratio(
                        weighted_beta
                    ),
                )

                w4.metric(
                    "Weighted Forward P/E",
                    format_ratio(
                        weighted_forward_pe
                    ),
                )

                w5.metric(
                    "Weighted 1Y Performance",
                    format_change(
                        weighted_one_year
                    ),
                )

                st.caption(
                    "Weighted indicators are descriptive portfolio "
                    "summaries based on available company metrics and "
                    "normalized portfolio weights. They are not forecasts."
                )

                # ------------------------------------------------------
                # AI + LIVE EVIDENCE ANALYSIS
                # ------------------------------------------------------
                st.divider()
                st.subheader("🧠 Event Impact Research")

                with st.spinner(
                    "Researching the event across portfolio holdings..."
                ):
                    result = analyze_portfolio_impact(
                        event=event,
                        tickers=tickers,
                        position_sizes=(
                            position_information
                            if position_information.strip()
                            else None
                        ),
                    )

                display_results(
                    result,
                    "Portfolio-impact analysis complete.",
                )

                display_pdf_download(
                    result=result,
                    report_title="Portfolio Impact Research Report",
                    research_question=event,
                    file_name="portfolio_impact_research_report.pdf",
                    portfolio_financials=portfolio_financials,
                    normalized_weights=normalized_weights,
                )

            except Exception as error:

                st.error(
                    "Portfolio analysis could not be completed."
                )

                st.exception(
                    error
                )


# ==========================================================
# METHODOLOGY
# ==========================================================

st.divider()

with st.expander(
    "🔬 Research Methodology"
):

    st.markdown(
        """
### Investment Intelligence Architecture

The engine does not begin with an investment conclusion.

It follows:

**Research Question / Market Event**

↓

**Live Evidence Retrieval**

↓

**Source Classification & Quality Prioritization**

↓

**Quantitative Company Data**

↓

**Historical Market Data**

↓

**Verified Facts vs. Inference vs. Assumptions**

↓

**Financial Transmission Analysis**

↓

**Counter-Evidence & Uncertainty**

↓

**Research Conclusion**

↓

**Downloadable Research Report**

---

### Quantitative Layer

The engine can incorporate:

- Market capitalization
- Revenue and revenue growth
- Profitability
- Operating margins
- Cash generation
- Liquidity and debt
- EPS
- Valuation multiples
- Historical price performance
- Beta

Missing financial metrics are not automatically estimated.

---

### Source Hierarchy

**Primary Sources**  
SEC filings, regulators and government data

↓

**Official Company Sources**  
Investor relations, earnings releases and company disclosures

↓

**Established Financial & News Sources**

↓

**Other Sources**

↓

**Lower-Priority / User-Generated Sources**

Source classification is a research aid and does not
guarantee that any individual source is accurate.
"""
    )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "AI Investment Intelligence Engine • "
    "Evidence + Financial Data + AI Reasoning"
)

st.caption(
    "For research and educational purposes only. "
    "The application does not provide personalized "
    "investment recommendations."
)