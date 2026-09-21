import yfinance as yf
import pandas as pd


# ==========================================================
# HELPERS
# ==========================================================

def safe_value(data, key, default=None):
    try:
        value = data.get(key, default)

        if value is None:
            return default

        return value

    except Exception:
        return default


def format_large_number(value):
    if value is None:
        return "N/A"

    try:
        value = float(value)

        if abs(value) >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"

        if abs(value) >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"

        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"

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


def format_ratio(value):
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.2f}"

    except Exception:
        return "N/A"


# ==========================================================
# HISTORICAL PRICE DATA
# ==========================================================

def get_price_history(ticker, period="1y"):
    """
    Retrieve historical daily stock prices for charts.

    Supported examples:
    1mo
    3mo
    6mo
    1y
    2y
    5y
    """

    ticker = ticker.strip().upper()

    if not ticker:
        return pd.DataFrame()

    try:
        stock = yf.Ticker(ticker)

        history = stock.history(
            period=period,
            interval="1d",
            auto_adjust=False,
        )

        if history.empty:
            return pd.DataFrame()

        history = history.reset_index()

        required_columns = [
            column
            for column in [
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
            if column in history.columns
        ]

        history = history[
            required_columns
        ].copy()

        if "Date" in history.columns:
            history["Date"] = pd.to_datetime(
                history["Date"]
            )

        return history

    except Exception as error:
        print(
            f"Price history error for {ticker}: {error}"
        )

        return pd.DataFrame()


# ==========================================================
# PRICE PERFORMANCE
# ==========================================================

def calculate_price_performance(stock):
    try:
        history = stock.history(
            period="1y",
            auto_adjust=False,
        )

        if history.empty:
            return {
                "one_month": None,
                "three_month": None,
                "six_month": None,
                "one_year": None,
            }

        close = history["Close"].dropna()

        if close.empty:
            return {
                "one_month": None,
                "three_month": None,
                "six_month": None,
                "one_year": None,
            }

        latest = float(
            close.iloc[-1]
        )

        def calculate_return(trading_days):

            if len(close) <= trading_days:
                return None

            old_price = float(
                close.iloc[
                    -trading_days - 1
                ]
            )

            if old_price == 0:
                return None

            return (
                latest / old_price
            ) - 1

        return {
            "one_month": calculate_return(21),

            "three_month": calculate_return(63),

            "six_month": calculate_return(126),

            "one_year": (
                (
                    latest
                    / float(close.iloc[0])
                )
                - 1
                if (
                    len(close) > 1
                    and float(close.iloc[0]) != 0
                )
                else None
            ),
        }

    except Exception:
        return {
            "one_month": None,
            "three_month": None,
            "six_month": None,
            "one_year": None,
        }


# ==========================================================
# FINANCIAL STATEMENT HELPERS
# ==========================================================

def get_statement_value(
    statement,
    possible_names,
):
    try:
        if (
            statement is None
            or statement.empty
        ):
            return None

        for name in possible_names:

            if name in statement.index:

                row = (
                    statement
                    .loc[name]
                    .dropna()
                )

                if not row.empty:
                    return float(
                        row.iloc[0]
                    )

        return None

    except Exception:
        return None


# ==========================================================
# MAIN COMPANY DATA ENGINE
# ==========================================================

def get_financial_data(ticker):

    ticker = (
        ticker
        .strip()
        .upper()
    )

    if not ticker:
        raise ValueError(
            "Ticker is required."
        )

    stock = yf.Ticker(ticker)

    try:
        info = stock.info

    except Exception:
        info = {}

    if not info:
        raise ValueError(
            f"No company data could be retrieved for {ticker}."
        )

    try:
        income_statement = (
            stock.financials
        )

    except Exception:
        income_statement = (
            pd.DataFrame()
        )

    try:
        cash_flow = (
            stock.cashflow
        )

    except Exception:
        cash_flow = (
            pd.DataFrame()
        )

    try:
        balance_sheet = (
            stock.balance_sheet
        )

    except Exception:
        balance_sheet = (
            pd.DataFrame()
        )

    performance = (
        calculate_price_performance(
            stock
        )
    )

    revenue = safe_value(
        info,
        "totalRevenue",
    )

    if revenue is None:

        revenue = get_statement_value(
            income_statement,
            [
                "Total Revenue",
                "Operating Revenue",
            ],
        )

    net_income = safe_value(
        info,
        "netIncomeToCommon",
    )

    if net_income is None:

        net_income = get_statement_value(
            income_statement,
            [
                "Net Income",
                "Net Income Common Stockholders",
            ],
        )

    operating_income = safe_value(
        info,
        "operatingIncome",
    )

    if operating_income is None:

        operating_income = get_statement_value(
            income_statement,
            [
                "Operating Income",
            ],
        )

    operating_margin = safe_value(
        info,
        "operatingMargins",
    )

    if (
        operating_margin is None
        and operating_income is not None
        and revenue
    ):

        operating_margin = (
            operating_income
            / revenue
        )

    operating_cash_flow = safe_value(
        info,
        "operatingCashflow",
    )

    if operating_cash_flow is None:

        operating_cash_flow = get_statement_value(
            cash_flow,
            [
                "Operating Cash Flow",
                "Total Cash From Operating Activities",
            ],
        )

    free_cash_flow = safe_value(
        info,
        "freeCashflow",
    )

    if free_cash_flow is None:

        free_cash_flow = get_statement_value(
            cash_flow,
            [
                "Free Cash Flow",
            ],
        )

    total_cash = safe_value(
        info,
        "totalCash",
    )

    if total_cash is None:

        total_cash = get_statement_value(
            balance_sheet,
            [
                (
                    "Cash Cash Equivalents And "
                    "Short Term Investments"
                ),
                "Cash And Cash Equivalents",
            ],
        )

    total_debt = safe_value(
        info,
        "totalDebt",
    )

    if total_debt is None:

        total_debt = get_statement_value(
            balance_sheet,
            [
                "Total Debt",
            ],
        )

    company_data = {

        "ticker": ticker,

        "company_name": safe_value(
            info,
            "longName",
            ticker,
        ),

        "sector": safe_value(
            info,
            "sector",
            "N/A",
        ),

        "industry": safe_value(
            info,
            "industry",
            "N/A",
        ),

        "currency": safe_value(
            info,
            "currency",
            "USD",
        ),

        # MARKET DATA

        "current_price": safe_value(
            info,
            "currentPrice",
        ),

        "previous_close": safe_value(
            info,
            "previousClose",
        ),

        "market_cap": safe_value(
            info,
            "marketCap",
        ),

        "enterprise_value": safe_value(
            info,
            "enterpriseValue",
        ),

        "fifty_two_week_high": safe_value(
            info,
            "fiftyTwoWeekHigh",
        ),

        "fifty_two_week_low": safe_value(
            info,
            "fiftyTwoWeekLow",
        ),

        # PERFORMANCE

        "one_month_return": (
            performance[
                "one_month"
            ]
        ),

        "three_month_return": (
            performance[
                "three_month"
            ]
        ),

        "six_month_return": (
            performance[
                "six_month"
            ]
        ),

        "one_year_return": (
            performance[
                "one_year"
            ]
        ),

        # FUNDAMENTALS

        "revenue": revenue,

        "revenue_growth": safe_value(
            info,
            "revenueGrowth",
        ),

        "net_income": net_income,

        "operating_margin": (
            operating_margin
        ),

        "profit_margin": safe_value(
            info,
            "profitMargins",
        ),

        "operating_cash_flow": (
            operating_cash_flow
        ),

        "free_cash_flow": (
            free_cash_flow
        ),

        "total_cash": total_cash,

        "total_debt": total_debt,

        # PER SHARE

        "trailing_eps": safe_value(
            info,
            "trailingEps",
        ),

        "forward_eps": safe_value(
            info,
            "forwardEps",
        ),

        # VALUATION

        "trailing_pe": safe_value(
            info,
            "trailingPE",
        ),

        "forward_pe": safe_value(
            info,
            "forwardPE",
        ),

        "price_to_sales": safe_value(
            info,
            "priceToSalesTrailing12Months",
        ),

        "price_to_book": safe_value(
            info,
            "priceToBook",
        ),

        "enterprise_to_revenue": safe_value(
            info,
            "enterpriseToRevenue",
        ),

        "enterprise_to_ebitda": safe_value(
            info,
            "enterpriseToEbitda",
        ),

        # RISK / CONTEXT

        "beta": safe_value(
            info,
            "beta",
        ),

        "shares_outstanding": safe_value(
            info,
            "sharesOutstanding",
        ),
    }

    return company_data


# ==========================================================
# AI-FRIENDLY FINANCIAL CONTEXT
# ==========================================================

def build_financial_context(data):

    return f"""
QUANTITATIVE COMPANY DATA

Company:
{data.get("company_name")}

Ticker:
{data.get("ticker")}

Sector:
{data.get("sector")}

Industry:
{data.get("industry")}

MARKET DATA

Current / Most Recent Price:
{format_large_number(data.get("current_price"))}

Market Capitalization:
{format_large_number(data.get("market_cap"))}

Enterprise Value:
{format_large_number(data.get("enterprise_value"))}

52-Week High:
{format_large_number(data.get("fifty_two_week_high"))}

52-Week Low:
{format_large_number(data.get("fifty_two_week_low"))}

PRICE PERFORMANCE

1 Month:
{format_percent(data.get("one_month_return"))}

3 Months:
{format_percent(data.get("three_month_return"))}

6 Months:
{format_percent(data.get("six_month_return"))}

1 Year:
{format_percent(data.get("one_year_return"))}

FUNDAMENTALS

Revenue:
{format_large_number(data.get("revenue"))}

Revenue Growth:
{format_percent(data.get("revenue_growth"))}

Net Income:
{format_large_number(data.get("net_income"))}

Operating Margin:
{format_percent(data.get("operating_margin"))}

Profit Margin:
{format_percent(data.get("profit_margin"))}

Operating Cash Flow:
{format_large_number(data.get("operating_cash_flow"))}

Free Cash Flow:
{format_large_number(data.get("free_cash_flow"))}

Cash:
{format_large_number(data.get("total_cash"))}

Debt:
{format_large_number(data.get("total_debt"))}

PER SHARE

Trailing EPS:
{format_ratio(data.get("trailing_eps"))}

Forward EPS:
{format_ratio(data.get("forward_eps"))}

VALUATION

Trailing P/E:
{format_ratio(data.get("trailing_pe"))}

Forward P/E:
{format_ratio(data.get("forward_pe"))}

Price / Sales:
{format_ratio(data.get("price_to_sales"))}

Price / Book:
{format_ratio(data.get("price_to_book"))}

Enterprise Value / Revenue:
{format_ratio(data.get("enterprise_to_revenue"))}

Enterprise Value / EBITDA:
{format_ratio(data.get("enterprise_to_ebitda"))}

RISK CONTEXT

Beta:
{format_ratio(data.get("beta"))}
"""


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    test_ticker = "AAPL"

    print(
        f"\nTesting financial data engine "
        f"for {test_ticker}...\n"
    )

    data = get_financial_data(
        test_ticker
    )

    print(
        build_financial_context(
            data
        )
    )

    print(
        "\nTesting historical price data...\n"
    )

    history = get_price_history(
        test_ticker,
        period="1y",
    )

    if history.empty:

        print(
            "Historical price data unavailable."
        )

    else:

        print(
            history.tail()
        )

        print(
            f"\nHistorical rows retrieved: "
            f"{len(history)}"
        )

    print(
        "\nFinancial data engine "
        "loaded successfully."
    )