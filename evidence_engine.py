import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

from financial_data import (
    get_financial_data,
    build_financial_context,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY was not found.")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY was not found.")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

MODEL = "gpt-5-mini"


# ==========================================================
# SOURCE QUALITY SYSTEM
# ==========================================================

PRIMARY_DOMAINS = {
    "sec.gov",
    "federalreserve.gov",
    "bls.gov",
    "bea.gov",
    "treasury.gov",
    "commerce.gov",
    "ftc.gov",
    "justice.gov",
    "whitehouse.gov",
    "congress.gov",
}

HIGH_QUALITY_DOMAINS = {
    "reuters.com",
    "apnews.com",
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "cnbc.com",
    "finance.yahoo.com",
    "morningstar.com",
}

LOWER_PRIORITY_DOMAINS = {
    "reddit.com",
    "quora.com",
    "medium.com",
}


def get_domain(url):
    try:
        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:
        return ""


def domain_matches(domain, target):
    return (
        domain == target
        or domain.endswith("." + target)
    )


def classify_source(url):
    domain = get_domain(url)

    if any(
        domain_matches(domain, item)
        for item in PRIMARY_DOMAINS
    ):
        return "PRIMARY", 100

    if (
        "/investor" in url.lower()
        or "/investors" in url.lower()
        or "/newsroom" in url.lower()
        or "/ir/" in url.lower()
    ):
        return "OFFICIAL COMPANY", 90

    if any(
        domain_matches(domain, item)
        for item in HIGH_QUALITY_DOMAINS
    ):
        return "HIGH QUALITY", 75

    if any(
        domain_matches(domain, item)
        for item in LOWER_PRIORITY_DOMAINS
    ):
        return "LOWER PRIORITY", 25

    return "OTHER", 50


# ==========================================================
# SEARCH
# ==========================================================

def run_search(query, max_results=5):
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
    )

    return response.get("results", [])


def process_results(results):
    processed = []

    for result in results:
        url = result.get("url", "")

        if not url:
            continue

        source_type, quality_score = classify_source(url)

        processed.append(
            {
                "title": result.get("title", ""),
                "url": url,
                "content": result.get("content", ""),
                "domain": get_domain(url),
                "source_type": source_type,
                "quality_score": quality_score,
            }
        )

    return processed


def deduplicate_and_rank(results, limit=18):
    seen_urls = set()
    unique_results = []

    for result in results:
        url = result.get("url")

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        unique_results.append(result)

    unique_results.sort(
        key=lambda item: item.get(
            "quality_score",
            0,
        ),
        reverse=True,
    )

    return unique_results[:limit]


def search_multiple_queries(queries, limit=18):
    all_results = []

    for query in queries:
        try:
            raw_results = run_search(
                query=query,
                max_results=5,
            )

            processed = process_results(
                raw_results
            )

            all_results.extend(processed)

        except Exception as error:
            print(
                f"Search error for '{query}': {error}"
            )

    return deduplicate_and_rank(
        all_results,
        limit=limit,
    )


# ==========================================================
# FORMAT EVIDENCE
# ==========================================================

def format_evidence(results):
    evidence_text = ""

    for index, result in enumerate(
        results,
        start=1,
    ):
        evidence_text += f"""
SOURCE {index}

TITLE:
{result.get("title", "")}

DOMAIN:
{result.get("domain", "")}

SOURCE CLASS:
{result.get("source_type", "")}

INTERNAL SOURCE PRIORITY:
{result.get("quality_score", "")}

URL:
{result.get("url", "")}

CONTENT:
{result.get("content", "")[:2500]}

------------------------------------------------------------
"""

    return evidence_text


# ==========================================================
# QUANTITATIVE FINANCIAL DATA
# ==========================================================

def get_quantitative_context(ticker):
    """
    Retrieve quantitative company data without allowing
    a data-provider failure to break the research engine.
    """

    if not ticker:
        return (
            "No ticker was supplied. "
            "Quantitative company data is unavailable."
        )

    try:
        financial_data = get_financial_data(ticker)

        return build_financial_context(
            financial_data
        )

    except Exception as error:
        print(
            f"Financial data error for {ticker}: {error}"
        )

        return (
            f"Quantitative company data for {ticker} "
            "could not be retrieved."
        )


def get_portfolio_financial_context(tickers):
    contexts = []

    for ticker in tickers:
        context = get_quantitative_context(ticker)

        contexts.append(
            f"""
============================================================
COMPANY: {ticker}
============================================================

{context}
"""
        )

    return "\n".join(contexts)


# ==========================================================
# COMMON ANALYSIS RULES
# ==========================================================

COMMON_RULES = """
EVIDENCE RULES:

1. Use ONLY the supplied evidence and supplied quantitative
   company data for factual claims.

2. Never invent:
   - facts
   - statistics
   - financial figures
   - quotations
   - sources
   - URLs

3. Clearly distinguish:

   VERIFIED FACT
   = directly supported by supplied evidence or reported
     quantitative company data.

   ANALYTICAL INFERENCE
   = a reasonable interpretation derived from evidence.

   ASSUMPTION
   = something not established as fact.

   UNKNOWN
   = evidence is insufficient.

4. If evidence does not establish something,
   explicitly say "Insufficient evidence."

5. Evidence quality matters.

Generally give greater evidentiary weight to:

   SEC / regulators / government
   ↓
   Official company filings and investor relations
   ↓
   Established financial and news organizations
   ↓
   Other sources
   ↓
   Forums / user-generated commentary

6. Source priority is a screening aid, not proof that
   a source is correct.

7. Multiple independent credible sources are stronger
   than repetition of the same claim.

8. Company statements can be authoritative about
   company-reported information but may still represent
   management's perspective.

9. Distinguish current evidence from historical evidence.

10. Do not convert uncertainty into certainty.

11. Do not provide BUY, SELL or HOLD recommendations.

12. Do not tell the user what security to purchase or sell.

13. Do not state that a stock WILL rise or fall.

14. Explain financial transmission mechanisms rather than
    pretending to predict market prices with certainty.
"""


QUANTITATIVE_RULES = """
QUANTITATIVE DATA RULES:

1. Treat the supplied quantitative company data as financial
   context. It is not proof that the user's event or claim
   occurred.

2. Use quantitative data where relevant to understand:
   - company scale
   - revenue
   - revenue growth
   - profitability
   - margins
   - cash generation
   - liquidity
   - debt
   - valuation
   - recent price performance
   - market sensitivity

3. Do not fabricate numerical impacts.

4. Do not claim an event will change revenue, EPS, margins,
   free cash flow, valuation, or stock price by a specific
   amount unless the supplied information supports the
   calculation.

5. Clearly distinguish reported financial metrics from
   analytical inference.

6. A valuation multiple does not by itself establish that a
   security is overvalued or undervalued.

7. Historical price performance does not establish how a
   security will respond to a future event.

8. Missing or unavailable financial metrics must not be
   estimated unless there is enough supplied information to
   calculate them transparently.

9. If quantitative data conflicts with narrative evidence,
   identify the discrepancy rather than silently choosing one.

10. Avoid false precision.
"""


# ==========================================================
# OPENAI
# ==========================================================

def run_ai_analysis(prompt):
    response = openai_client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text


# ==========================================================
# MODE 1 — MARKET CLAIM
# ==========================================================

def analyze_claim(claim, ticker=None):
    queries = [
        claim,
        f"{claim} evidence",
        f"{claim} latest financial evidence",
        f"{claim} contrary evidence",
    ]

    if ticker:
        queries.extend(
            [
                f"{ticker} {claim}",
                f"{ticker} {claim} financial impact",
                f"{ticker} investor relations {claim}",
            ]
        )

    evidence = search_multiple_queries(
        queries,
        limit=18,
    )

    if not evidence:
        return {
            "analysis": (
                "Insufficient evidence was retrieved."
            ),
            "sources": [],
        }

    evidence_text = format_evidence(evidence)

    if ticker:
        financial_context = get_quantitative_context(
            ticker
        )
    else:
        financial_context = (
            "No ticker was supplied. "
            "Company-specific quantitative data is unavailable."
        )

    prompt = f"""
You are an evidence-first financial research analyst.

CLAIM:
{claim}

TICKER:
{ticker if ticker else "Not specified"}

LIVE EVIDENCE:
{evidence_text}

CURRENT QUANTITATIVE COMPANY DATA:
{financial_context}

{COMMON_RULES}

{QUANTITATIVE_RULES}

Analyze whether the evidence supports, contradicts,
qualifies, or fails to establish the claim.

If a ticker was supplied, use quantitative financial
information only where it materially helps evaluate the
claim.

Use these sections:

## Executive Summary

## Claim Breakdown

Separate factual components, opinions, predictions
and assumptions.

## Verified Facts

## Evidence Supporting the Claim

## Evidence Contradicting the Claim

## Evidence Gaps

## Source Quality Assessment

Discuss which sources deserve the greatest weight and why.

## Quantitative Financial Context

If company data is available, identify the most relevant
metrics and explain why they matter.

## Financial Materiality

## Potential Stock Impact

## What Would Change the Conclusion

## Bottom Line
"""

    return {
        "analysis": run_ai_analysis(prompt),
        "sources": evidence,
    }


# ==========================================================
# MODE 2 — STOCK IMPACT
# ==========================================================

def analyze_stock_impact(event, ticker):
    if not ticker:
        return {
            "analysis": "A stock ticker is required.",
            "sources": [],
        }

    queries = [
        f"{event} latest developments",
        f"{ticker} {event}",
        f"{ticker} exposure {event}",
        f"{ticker} investor relations {event}",
        f"{ticker} revenue exposure {event}",
        f"{ticker} costs margins {event}",
        f"{ticker} supply chain geographic exposure",
        f"{ticker} latest financial results investor relations",
    ]

    evidence = search_multiple_queries(
        queries,
        limit=20,
    )

    if not evidence:
        return {
            "analysis": (
                "Insufficient evidence was retrieved."
            ),
            "sources": [],
        }

    evidence_text = format_evidence(evidence)

    financial_context = get_quantitative_context(
        ticker
    )

    prompt = f"""
You are an evidence-first investment research analyst.

TICKER:
{ticker}

EVENT:
{event}

LIVE EVIDENCE:
{evidence_text}

CURRENT QUANTITATIVE COMPANY DATA:
{financial_context}

{COMMON_RULES}

{QUANTITATIVE_RULES}

First establish whether the event is verified.

Then determine whether {ticker} has meaningful exposure.

Where evidence supports it, trace:

EVENT
→ COMPANY EXPOSURE
→ BUSINESS SEGMENTS / GEOGRAPHIES
→ REVENUE
→ COSTS
→ MARGINS
→ CASH FLOW
→ VALUATION CONSIDERATIONS

Use the quantitative company data to establish the
company's current financial position and scale.

Do NOT mechanically repeat every available metric.
Select the metrics that actually matter to the event.

Identify both negative and positive transmission channels.

Actively look for evidence that weakens the obvious
headline narrative.

Use these sections:

## Executive Summary

## Event Verification

## Verified Company Exposure

## Current Financial Position

Identify the most decision-relevant quantitative metrics.

## Transmission Mechanism

## Revenue Impact

## Cost & Margin Impact

## Cash Flow Impact

## Balance-Sheet Considerations

## Valuation Considerations

## Potential Stock Impact

### Short-Term Market Considerations

### Long-Term Fundamental Considerations

## Second-Order Effects

## Offsetting Factors

## Evidence Against the Initial Narrative

## Key Uncertainties

## What to Watch Next

## Bottom Line
"""

    return {
        "analysis": run_ai_analysis(prompt),
        "sources": evidence,
    }


# ==========================================================
# MODE 3 — SCENARIO ANALYSIS
# ==========================================================

def analyze_scenario(scenario, ticker):
    if not ticker:
        return {
            "analysis": "A stock ticker is required.",
            "sources": [],
        }

    queries = [
        f"{ticker} latest financial results investor relations",
        f"{ticker} annual report revenue segments margins",
        f"{ticker} exposure {scenario}",
        f"{ticker} risks {scenario}",
        f"{ticker} industry outlook {scenario}",
        f"{ticker} financial sensitivity {scenario}",
    ]

    evidence = search_multiple_queries(
        queries,
        limit=20,
    )

    if not evidence:
        return {
            "analysis": (
                "Insufficient evidence was retrieved."
            ),
            "sources": [],
        }

    evidence_text = format_evidence(evidence)

    financial_context = get_quantitative_context(
        ticker
    )

    prompt = f"""
You are conducting evidence-based financial scenario analysis.

TICKER:
{ticker}

HYPOTHETICAL SCENARIO:
{scenario}

CURRENT EVIDENCE:
{evidence_text}

CURRENT QUANTITATIVE COMPANY DATA:
{financial_context}

{COMMON_RULES}

{QUANTITATIVE_RULES}

The scenario is HYPOTHETICAL.

Do not describe the hypothetical scenario as an
existing fact.

First establish the company's actual current exposure
using evidence and quantitative financial information.

Then evaluate the scenario.

Explicitly separate:

VERIFIED FACTS

USER-SUPPLIED SCENARIO ASSUMPTIONS

ANALYTICAL INFERENCES

UNKNOWN VARIABLES

Use current revenue, margins, cash flow, liquidity,
debt, valuation and other supplied metrics where they
are relevant to understanding sensitivity.

Do not fabricate precise revenue, EPS, margin,
cash-flow, valuation or stock-price changes.

If numerical sensitivity cannot be derived from the
supplied information, explain the mechanism and direction
instead.

Use these sections:

## Executive Summary

## Scenario Definition

## Verified Current Company Exposure

## Current Financial Position

Identify the quantitative starting point most relevant
to the scenario.

## Key Assumptions

## Transmission Mechanism

## Revenue Sensitivity

## Margin Sensitivity

## Cash Flow Implications

## Balance-Sheet Resilience

## Valuation Considerations

## Less-Adverse / Upside Path

## Central Analytical Path

This is an analytical pathway, NOT a forecast.

## More-Adverse / Downside Path

## Second-Order Effects

## Key Sensitivities

## Evidence Gaps

## What Would Invalidate This Analysis

## Bottom Line
"""

    return {
        "analysis": run_ai_analysis(prompt),
        "sources": evidence,
    }


# ==========================================================
# MODE 4 — PORTFOLIO IMPACT
# ==========================================================

def analyze_portfolio_impact(
    event,
    tickers,
    position_sizes=None,
):
    clean_tickers = []

    for ticker in tickers:
        ticker = ticker.strip().upper()

        if ticker and ticker not in clean_tickers:
            clean_tickers.append(ticker)

    if not clean_tickers:
        return {
            "analysis": (
                "At least one ticker is required."
            ),
            "sources": [],
        }

    ticker_string = ", ".join(clean_tickers)

    queries = [
        f"{event} latest developments",
    ]

    for ticker in clean_tickers:
        queries.extend(
            [
                f"{ticker} {event}",
                f"{ticker} exposure {event}",
                f"{ticker} investor relations latest financial results",
            ]
        )

    evidence = search_multiple_queries(
        queries,
        limit=28,
    )

    if not evidence:
        return {
            "analysis": (
                "Insufficient evidence was retrieved."
            ),
            "sources": [],
        }

    evidence_text = format_evidence(evidence)

    portfolio_financial_context = (
        get_portfolio_financial_context(
            clean_tickers
        )
    )

    if position_sizes:
        portfolio_information = position_sizes

    else:
        portfolio_information = """
No position sizes were supplied.

Do not assume portfolio weights.

Do not calculate weighted portfolio effects,
dollar gains or dollar losses.
"""

    prompt = f"""
You are an evidence-first portfolio research analyst.

PORTFOLIO:
{ticker_string}

POSITION INFORMATION:
{portfolio_information}

EVENT:
{event}

LIVE EVIDENCE:
{evidence_text}

QUANTITATIVE COMPANY DATA FOR PORTFOLIO HOLDINGS:
{portfolio_financial_context}

{COMMON_RULES}

{QUANTITATIVE_RULES}

Analyze how the event could propagate across the holdings.

For each company separately determine:

EVENT
→ COMPANY EXPOSURE
→ REVENUE / COSTS
→ MARGINS
→ CASH FLOW
→ BALANCE SHEET
→ VALUATION CONSIDERATIONS

Use the supplied quantitative company data to compare
the financial characteristics of the holdings where
relevant.

For example, differences in scale, growth, profitability,
cash generation, leverage, valuation or recent market
performance may affect how an event transmits through
different companies.

Do not assume that companies in the same industry have
identical exposure.

Then evaluate portfolio-level relationships.

Do not invent portfolio weights.

Do not invent correlations.

Do not calculate dollar losses or gains unless the user
supplied sufficient position information and the supplied
data supports the calculation.

Do not predict exact portfolio returns.

Use these sections:

## Executive Summary

## Event Verification

## Portfolio Exposure Overview

## Quantitative Portfolio Context

Compare only the financial characteristics that are
relevant to the event.

## Company-by-Company Analysis

Analyze each ticker separately.

## Shared Risk Factors

## Different Transmission Channels

## Potential Portfolio Offsets

## Concentration Considerations

## Second-Order Effects

## Evidence Against the Initial Narrative

## Key Uncertainties

## What to Watch Next

## Bottom Line
"""

    return {
        "analysis": run_ai_analysis(prompt),
        "sources": evidence,
    }


# ==========================================================
# BACKEND CHECK
# ==========================================================

if __name__ == "__main__":
    print("\nAI INVESTMENT INTELLIGENCE ENGINE\n")

    print("Evidence system: ACTIVE")
    print("Source classification: ACTIVE")
    print("Source ranking: ACTIVE")
    print("Primary-source preference: ACTIVE")
    print("Quantitative financial data: ACTIVE")

    print("\nAvailable engines:")
    print("1. Market Claim Investigation")
    print("2. Stock Impact Analysis")
    print("3. Scenario Analysis")
    print("4. Portfolio Impact Analysis")

    print("\nBackend loaded successfully.")