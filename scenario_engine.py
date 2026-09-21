from financial_data import get_financial_data


# ==========================================================
# HELPERS
# ==========================================================

def safe_float(value):
    try:
        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def percentage_change(new_value, old_value):
    if (
        new_value is None
        or old_value is None
        or old_value == 0
    ):
        return None

    return (
        (new_value / old_value) - 1
    )


def format_money(value):
    if value is None:
        return "N/A"

    try:
        value = float(value)

        if abs(value) >= 1_000_000_000_000:
            return (
                f"${value / 1_000_000_000_000:.2f}T"
            )

        if abs(value) >= 1_000_000_000:
            return (
                f"${value / 1_000_000_000:.2f}B"
            )

        if abs(value) >= 1_000_000:
            return (
                f"${value / 1_000_000:.2f}M"
            )

        return f"${value:,.2f}"

    except Exception:
        return "N/A"


def format_percent(value):
    if value is None:
        return "N/A"

    try:
        return f"{float(value) * 100:.2f}%"

    except Exception:
        return "N/A"


# ==========================================================
# SCENARIO MODEL
# ==========================================================

def run_financial_scenario(
    ticker,
    revenue_change_pct=0.0,
    operating_margin_change_points=0.0,
    fcf_margin_change_points=0.0,
):
    """
    Run a transparent financial sensitivity scenario.

    PARAMETERS

    ticker:
        Stock ticker such as AAPL.

    revenue_change_pct:
        Percentage change in total company revenue.

        Example:
        -10 means revenue falls 10%.
         5 means revenue rises 5%.

    operating_margin_change_points:
        Change in operating margin in percentage points.

        Example:
        -1.5 means a 30% operating margin becomes 28.5%.

    fcf_margin_change_points:
        Change in free-cash-flow margin in percentage points.

        Example:
        -2 means a 25% FCF margin becomes 23%.

    IMPORTANT:
    These are user-supplied scenario assumptions.
    They are NOT forecasts.
    """

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError(
            "Ticker is required."
        )

    data = get_financial_data(
        ticker
    )

    revenue = safe_float(
        data.get("revenue")
    )

    operating_margin = safe_float(
        data.get("operating_margin")
    )

    free_cash_flow = safe_float(
        data.get("free_cash_flow")
    )

    if revenue is None:
        raise ValueError(
            f"Revenue data is unavailable for {ticker}."
        )

    # ------------------------------------------------------
    # Convert user assumptions
    # ------------------------------------------------------

    revenue_change = (
        safe_float(revenue_change_pct)
        or 0.0
    ) / 100

    operating_margin_change = (
        safe_float(
            operating_margin_change_points
        )
        or 0.0
    ) / 100

    fcf_margin_change = (
        safe_float(
            fcf_margin_change_points
        )
        or 0.0
    ) / 100

    # ------------------------------------------------------
    # REVENUE SCENARIO
    # ------------------------------------------------------

    scenario_revenue = (
        revenue
        * (1 + revenue_change)
    )

    revenue_difference = (
        scenario_revenue
        - revenue
    )

    # ------------------------------------------------------
    # OPERATING INCOME SCENARIO
    # ------------------------------------------------------

    if operating_margin is not None:

        current_operating_income = (
            revenue
            * operating_margin
        )

        scenario_operating_margin = (
            operating_margin
            + operating_margin_change
        )

        scenario_operating_income = (
            scenario_revenue
            * scenario_operating_margin
        )

        operating_income_difference = (
            scenario_operating_income
            - current_operating_income
        )

        operating_income_change_pct = (
            percentage_change(
                scenario_operating_income,
                current_operating_income,
            )
        )

    else:

        current_operating_income = None
        scenario_operating_margin = None
        scenario_operating_income = None
        operating_income_difference = None
        operating_income_change_pct = None

    # ------------------------------------------------------
    # FREE CASH FLOW SCENARIO
    # ------------------------------------------------------

    if (
        free_cash_flow is not None
        and revenue != 0
    ):

        current_fcf_margin = (
            free_cash_flow
            / revenue
        )

        scenario_fcf_margin = (
            current_fcf_margin
            + fcf_margin_change
        )

        scenario_free_cash_flow = (
            scenario_revenue
            * scenario_fcf_margin
        )

        fcf_difference = (
            scenario_free_cash_flow
            - free_cash_flow
        )

        fcf_change_pct = (
            percentage_change(
                scenario_free_cash_flow,
                free_cash_flow,
            )
        )

    else:

        current_fcf_margin = None
        scenario_fcf_margin = None
        scenario_free_cash_flow = None
        fcf_difference = None
        fcf_change_pct = None

    # ------------------------------------------------------
    # RESULTS
    # ------------------------------------------------------

    result = {

        "ticker": ticker,

        "company_name": data.get(
            "company_name",
            ticker,
        ),

        # USER ASSUMPTIONS

        "assumptions": {

            "revenue_change_pct":
                revenue_change_pct,

            "operating_margin_change_points":
                operating_margin_change_points,

            "fcf_margin_change_points":
                fcf_margin_change_points,
        },

        # CURRENT REVENUE

        "current_revenue":
            revenue,

        # SCENARIO REVENUE

        "scenario_revenue":
            scenario_revenue,

        "revenue_difference":
            revenue_difference,

        "revenue_change":
            revenue_change,

        # CURRENT OPERATING PERFORMANCE

        "current_operating_margin":
            operating_margin,

        "current_operating_income":
            current_operating_income,

        # SCENARIO OPERATING PERFORMANCE

        "scenario_operating_margin":
            scenario_operating_margin,

        "scenario_operating_income":
            scenario_operating_income,

        "operating_income_difference":
            operating_income_difference,

        "operating_income_change_pct":
            operating_income_change_pct,

        # CURRENT CASH FLOW

        "current_free_cash_flow":
            free_cash_flow,

        "current_fcf_margin":
            current_fcf_margin,

        # SCENARIO CASH FLOW

        "scenario_fcf_margin":
            scenario_fcf_margin,

        "scenario_free_cash_flow":
            scenario_free_cash_flow,

        "fcf_difference":
            fcf_difference,

        "fcf_change_pct":
            fcf_change_pct,
    }

    return result


# ==========================================================
# AI-FRIENDLY SCENARIO CONTEXT
# ==========================================================

def build_scenario_context(result):
    """
    Convert deterministic scenario results into a
    structured block that can later be supplied to the AI.
    """

    assumptions = result.get(
        "assumptions",
        {},
    )

    return f"""
DETERMINISTIC FINANCIAL SCENARIO

Company:
{result.get("company_name")}

Ticker:
{result.get("ticker")}

IMPORTANT:
This is a sensitivity analysis based on user-supplied
assumptions. It is NOT a forecast.

USER-SUPPLIED ASSUMPTIONS

Revenue Change:
{assumptions.get("revenue_change_pct", 0):.2f}%

Operating Margin Change:
{assumptions.get("operating_margin_change_points", 0):.2f}
percentage points

Free Cash Flow Margin Change:
{assumptions.get("fcf_margin_change_points", 0):.2f}
percentage points


REVENUE

Current Revenue:
{format_money(result.get("current_revenue"))}

Scenario Revenue:
{format_money(result.get("scenario_revenue"))}

Revenue Difference:
{format_money(result.get("revenue_difference"))}

Revenue Change:
{format_percent(result.get("revenue_change"))}


OPERATING PERFORMANCE

Current Operating Margin:
{format_percent(result.get("current_operating_margin"))}

Scenario Operating Margin:
{format_percent(result.get("scenario_operating_margin"))}

Current Operating Income:
{format_money(result.get("current_operating_income"))}

Scenario Operating Income:
{format_money(result.get("scenario_operating_income"))}

Operating Income Difference:
{format_money(result.get("operating_income_difference"))}

Operating Income Change:
{format_percent(result.get("operating_income_change_pct"))}


FREE CASH FLOW

Current FCF Margin:
{format_percent(result.get("current_fcf_margin"))}

Scenario FCF Margin:
{format_percent(result.get("scenario_fcf_margin"))}

Current Free Cash Flow:
{format_money(result.get("current_free_cash_flow"))}

Scenario Free Cash Flow:
{format_money(result.get("scenario_free_cash_flow"))}

Free Cash Flow Difference:
{format_money(result.get("fcf_difference"))}

Free Cash Flow Change:
{format_percent(result.get("fcf_change_pct"))}
"""


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    test_ticker = "AAPL"

    print(
        "\nTesting Financial Scenario Engine...\n"
    )

    test_result = run_financial_scenario(
        ticker=test_ticker,

        # Example hypothetical assumptions only
        revenue_change_pct=-10,

        operating_margin_change_points=-1.5,

        fcf_margin_change_points=-2.0,
    )

    print(
        build_scenario_context(
            test_result
        )
    )

    print(
        "\nScenario engine loaded successfully."
    )