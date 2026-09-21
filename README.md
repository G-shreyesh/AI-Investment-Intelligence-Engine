# 🧠 AI Investment Intelligence Engine

An evidence-first AI investment research platform that combines **live web evidence, quantitative financial data, scenario analysis, portfolio analytics, and AI reasoning** to help users investigate market claims and understand how real-world events may affect companies and portfolios.

Rather than simply summarizing financial news, the system follows a structured research process:

**Market Information → Evidence Verification → Company Exposure → Financial Materiality → Scenario Analysis → Portfolio Impact**

---

## 🚀 Core Features

### 🔎 Investigate a Market Claim
Analyze a market claim using live web evidence.

- Searches for current supporting and contradicting evidence
- Prioritizes primary and high-quality sources
- Separates verified facts from analytical inference
- Highlights uncertainty and insufficient evidence
- Produces an evidence-backed AI research analysis

### 📈 Stock Impact Analysis
Explore how a market event could affect a specific company.

The engine evaluates the causal chain:

**Event → Company Exposure → Revenue → Margins → Free Cash Flow → Valuation**

Includes:

- Live evidence retrieval
- Company financial snapshot
- Revenue and profitability metrics
- Cash flow and balance-sheet context
- Valuation metrics
- Historical stock performance
- AI-generated financial impact analysis

### 🧪 Scenario Analysis
Run deterministic financial sensitivity scenarios using user-defined assumptions.

Users can modify:

- Revenue growth/change
- Operating margin
- Free cash flow margin

The engine calculates the resulting changes in:

- Revenue
- Operating income
- Free cash flow

Scenario results are displayed through quantitative comparisons and interactive visualizations.

> Scenario analysis represents user-defined sensitivity assumptions and is not a forecast.

### 💼 Portfolio Impact Analysis
Analyze how a market event may propagate across multiple holdings.

Features include:

- Custom portfolio weights
- Automatic equal weighting when weights are not supplied
- Portfolio allocation visualization
- Holding-level financial metrics
- Cross-company comparisons
- Weighted portfolio indicators
- AI analysis of direct and second-order effects

---

## 📊 Quantitative Financial Intelligence

The engine integrates company-level financial data including:

- Market capitalization
- Enterprise value
- Revenue and revenue growth
- Net income
- Operating margin
- Profit margin
- Operating cash flow
- Free cash flow
- Cash and debt
- EPS
- Forward and trailing P/E
- Price-to-sales
- Price-to-book
- EV/Revenue
- EV/EBITDA
- Beta
- 52-week price range
- 1M / 3M / 6M / 1Y stock performance

Historical price data is also visualized directly in the application.

---

## 🌐 Evidence Quality Engine

Sources are automatically classified and ranked before being supplied to the AI analysis layer.

| Source Type | Priority |
|---|---:|
| Primary Sources — SEC, government, regulators | 100 |
| Official Company Sources | 90 |
| High-Quality Financial & News Sources | 75 |
| Other Sources | 50 |
| Lower-Priority Sources | 25 |

Source priority improves evidence selection but is **not treated as proof by itself**.

The system is designed to distinguish between:

- **Verified Fact**
- **Analytical Inference**
- **Assumption**
- **Unknown / Insufficient Evidence**

---

## 📄 AI Research Reports

Research results can be exported as professional PDF reports containing:

- Research question
- AI analysis
- Quantitative financial context
- Scenario results when applicable
- Portfolio information when applicable
- Evidence and source trail
- Research disclosure
- Page numbering and structured formatting

---

## 🏗️ Architecture

```text
User Research Question
        │
        ▼
Live Evidence Retrieval
        │
        ▼
Source Classification & Ranking
        │
        ▼
Quantitative Financial Data
        │
        ▼
Financial / Scenario Engine
        │
        ▼
AI Reasoning Layer
        │
        ▼
Investment Research Analysis
        │
        ├── Evidence Trail
        ├── Interactive Visualizations
        └── PDF Research Report
```

---

## 🛠️ Technology Stack

- **Python**
- **Streamlit**
- **OpenAI API**
- **Tavily Search API**
- **yfinance**
- **Pandas**
- **NumPy**
- **Plotly**
- **ReportLab**
- **python-dotenv**

---

## 📁 Project Structure

```text
AI-Investment-Intelligence-Engine/
│
├── app.py
├── evidence_engine.py
├── financial_data.py
├── scenario_engine.py
├── requirements.txt
├── .gitignore
└── README.md
```

### `app.py`
Streamlit application, user interface, visualizations, research modes, and PDF report generation.

### `evidence_engine.py`
Live evidence retrieval, source classification, evidence ranking, quantitative context integration, and AI analysis.

### `financial_data.py`
Company fundamentals, valuation metrics, market data, and historical stock-price retrieval.

### `scenario_engine.py`
Deterministic financial sensitivity calculations based on user-defined assumptions.

---

## ⚙️ Local Setup

Clone the repository:

```bash
git clone https://github.com/G-shreyesh/AI-Investment-Intelligence-Engine.git
cd AI-Investment-Intelligence-Engine
```

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```text
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Run the application:

```bash
streamlit run app.py
```

---

## 🔐 Security

API credentials are stored locally through environment variables and are excluded from version control through `.gitignore`.

Never commit API keys or `.env` files to a public repository.

---

## 🎯 Design Philosophy

The platform is built around an **evidence-first approach to investment research**.

Instead of attempting to predict stock prices, it focuses on understanding:

1. What happened?
2. What evidence supports or contradicts the claim?
3. How exposed is the company?
4. Which financial drivers could be affected?
5. How material could the impact be?
6. What assumptions drive different scenarios?
7. How could the effect propagate across a portfolio?

The goal is to make AI-generated financial research more **transparent, evidence-grounded, quantitative, and explainable**.

---

## ⚠️ Disclaimer

This application is designed for **research and educational purposes only**.

It does not provide investment advice, financial recommendations, or BUY/SELL/HOLD signals. Scenario results are sensitivity analyses based on user-defined assumptions and should not be interpreted as forecasts of future financial performance or stock prices.

---

## 👤 Author

**Shreyesh Gaddamwar**

Master's in Quantitative Finance  
University of Massachusetts Dartmouth