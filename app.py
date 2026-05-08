# -*- coding: utf-8 -*-
"""
Phase 2 – Task 2: Retail Store Sales — Interactive Dash Dashboard
Authors: Leen Haroun (202210930) & Sondos Sukkarieh (202210895)
"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import os

# ── Load & clean data ──────────────────────────────────────────────────────────
df = pd.read_csv("retail_store_sales.csv")
df.columns = df.columns.str.strip()
df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], dayfirst=True, errors="coerce")
df["Year"]  = df["Transaction Date"].dt.year
df["Month"] = df["Transaction Date"].dt.month
df["Total Spent"]    = pd.to_numeric(df["Total Spent"],    errors="coerce")
df["Quantity"]       = pd.to_numeric(df["Quantity"],       errors="coerce")
df["Price Per Unit"] = pd.to_numeric(df["Price Per Unit"], errors="coerce")
df = df.dropna(subset=["Total Spent", "Category", "Transaction Date"])

CATEGORIES     = sorted(df["Category"].dropna().unique())
LOCATIONS      = sorted(df["Location"].dropna().unique())
PAYMENT_METHODS = sorted(df["Payment Method"].dropna().unique())
YEARS          = sorted(df["Year"].dropna().unique().astype(int))

# ── Colour palette ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":      "#f4f6fb",
    "card":    "#ffffff",
    "primary": "#4361ee",
    "accent":  "#f72585",
    "text":    "#2b2d42",
    "subtle":  "#8d99ae",
}

PALETTE = px.colors.qualitative.Bold

# ── Dash app ───────────────────────────────────────────────────────────────────
app = Dash(__name__, title="Retail BI Dashboard")
server = app.server   # expose Flask server for gunicorn

# ── Layout ─────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={"fontFamily": "Segoe UI, Arial, sans-serif", "backgroundColor": COLORS["bg"],
           "minHeight": "100vh", "padding": "0 0 40px"},
    children=[

        # ── Header ──────────────────────────────────────────────────────────
        html.Div(
            style={"background": f"linear-gradient(135deg, {COLORS['primary']}, #3a0ca3)",
                   "color": "#fff", "padding": "28px 40px 22px", "marginBottom": "28px",
                   "boxShadow": "0 4px 18px rgba(67,97,238,.35)"},
            children=[
                html.H1("🛒 Retail Store Sales Dashboard",
                        style={"margin": 0, "fontSize": "1.9rem", "fontWeight": 700}),
                html.P("Phase 2 – Task 2  |  Leen Haroun & Sondos Sukkarieh",
                       style={"margin": "6px 0 0", "opacity": .75, "fontSize": ".9rem"}),
            ]
        ),

        # ── Filter panel ────────────────────────────────────────────────────
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "24px",
                   "padding": "0 40px 20px"},
            children=[

                # Category dropdown
                html.Div([
                    html.Label("📦 Product Category", style={"fontWeight": 600,
                               "color": COLORS["text"], "display": "block", "marginBottom": 6}),
                    dcc.Dropdown(
                        id="dd-category",
                        options=[{"label": "All Categories", "value": "ALL"}] +
                                [{"label": c, "value": c} for c in CATEGORIES],
                        value="ALL", clearable=False,
                        style={"minWidth": 240}
                    )
                ]),

                # Location radio
                html.Div([
                    html.Label("📍 Location", style={"fontWeight": 600,
                               "color": COLORS["text"], "display": "block", "marginBottom": 6}),
                    dcc.RadioItems(
                        id="radio-location",
                        options=[{"label": " All", "value": "ALL"}] +
                                [{"label": f" {l}", "value": l} for l in LOCATIONS],
                        value="ALL", inline=True,
                        inputStyle={"marginRight": 5},
                        labelStyle={"marginRight": 18, "cursor": "pointer",
                                    "color": COLORS["text"]}
                    )
                ]),

                # Payment method checklist
                html.Div([
                    html.Label("💳 Payment Method", style={"fontWeight": 600,
                               "color": COLORS["text"], "display": "block", "marginBottom": 6}),
                    dcc.Checklist(
                        id="check-payment",
                        options=[{"label": f" {p}", "value": p} for p in PAYMENT_METHODS],
                        value=PAYMENT_METHODS, inline=True,
                        inputStyle={"marginRight": 5},
                        labelStyle={"marginRight": 18, "cursor": "pointer",
                                    "color": COLORS["text"]}
                    )
                ]),

                # Year range slider
                html.Div([
                    html.Label("📅 Year Range", style={"fontWeight": 600,
                               "color": COLORS["text"], "display": "block", "marginBottom": 6}),
                    dcc.RangeSlider(
                        id="slider-year",
                        min=YEARS[0], max=YEARS[-1],
                        value=[YEARS[0], YEARS[-1]],
                        marks={y: str(y) for y in YEARS},
                        step=1, allowCross=False,
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={"minWidth": 280}),
            ]
        ),

        # ── KPI cards ───────────────────────────────────────────────────────
        html.Div(id="kpi-row",
                 style={"display": "flex", "gap": "20px", "padding": "0 40px 24px",
                        "flexWrap": "wrap"}),

        # ── Charts row 1 ────────────────────────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "padding": "0 40px 20px",
                   "flexWrap": "wrap"},
            children=[
                html.Div(dcc.Graph(id="chart-bar-category"),
                         style={"flex": "1 1 480px", "background": COLORS["card"],
                                "borderRadius": 12, "boxShadow": "0 2px 10px rgba(0,0,0,.07)",
                                "padding": "8px"}),
                html.Div(dcc.Graph(id="chart-pie-payment"),
                         style={"flex": "1 1 360px", "background": COLORS["card"],
                                "borderRadius": 12, "boxShadow": "0 2px 10px rgba(0,0,0,.07)",
                                "padding": "8px"}),
            ]
        ),

        # ── Charts row 2 ────────────────────────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "padding": "0 40px 20px",
                   "flexWrap": "wrap"},
            children=[
                html.Div(dcc.Graph(id="chart-line-trend"),
                         style={"flex": "1 1 480px", "background": COLORS["card"],
                                "borderRadius": 12, "boxShadow": "0 2px 10px rgba(0,0,0,.07)",
                                "padding": "8px"}),
                html.Div(dcc.Graph(id="chart-scatter"),
                         style={"flex": "1 1 360px", "background": COLORS["card"],
                                "borderRadius": 12, "boxShadow": "0 2px 10px rgba(0,0,0,.07)",
                                "padding": "8px"}),
            ]
        ),

        # ── Chart row 3: heatmap full width ─────────────────────────────────
        html.Div(
            style={"padding": "0 40px 20px"},
            children=[
                html.Div(dcc.Graph(id="chart-heatmap"),
                         style={"background": COLORS["card"], "borderRadius": 12,
                                "boxShadow": "0 2px 10px rgba(0,0,0,.07)", "padding": "8px"}),
            ]
        ),
    ]
)


# ── Shared filter helper ───────────────────────────────────────────────────────
def apply_filters(category, location, payment, year_range):
    dff = df[df["Year"].between(year_range[0], year_range[1])]
    if category != "ALL":
        dff = dff[dff["Category"] == category]
    if location != "ALL":
        dff = dff[dff["Location"] == location]
    if payment:
        dff = dff[dff["Payment Method"].isin(payment)]
    return dff


# ── Main callback — all charts + KPIs ─────────────────────────────────────────
@app.callback(
    [Output("kpi-row",          "children"),
     Output("chart-bar-category", "figure"),
     Output("chart-pie-payment",  "figure"),
     Output("chart-line-trend",   "figure"),
     Output("chart-scatter",      "figure"),
     Output("chart-heatmap",      "figure")],
    [Input("dd-category",   "value"),
     Input("radio-location","value"),
     Input("check-payment", "value"),
     Input("slider-year",   "value")],
)
def update_all(category, location, payment, year_range):
    dff = apply_filters(category, location, payment, year_range)

    # ── KPI cards ──────────────────────────────────────────────────────────
    def kpi_card(icon, label, value, color):
        return html.Div([
            html.Div(icon,  style={"fontSize": "1.6rem"}),
            html.Div(value, style={"fontSize": "1.55rem", "fontWeight": 700,
                                   "color": color, "margin": "4px 0 2px"}),
            html.Div(label, style={"fontSize": ".78rem", "color": COLORS["subtle"],
                                   "fontWeight": 500}),
        ], style={"background": COLORS["card"], "borderRadius": 12, "padding": "18px 24px",
                  "boxShadow": "0 2px 10px rgba(0,0,0,.07)", "flex": "1 1 160px",
                  "minWidth": 140, "textAlign": "center"})

    total_sales   = dff["Total Spent"].sum()
    total_txn     = len(dff)
    avg_basket    = dff["Total Spent"].mean() if total_txn else 0
    total_qty     = dff["Quantity"].sum()

    kpis = [
        kpi_card("💰", "Total Revenue",    f"${total_sales:,.0f}", COLORS["primary"]),
        kpi_card("🧾", "Transactions",     f"{total_txn:,}",       "#3a0ca3"),
        kpi_card("🛍️", "Avg. Basket",     f"${avg_basket:,.1f}",  COLORS["accent"]),
        kpi_card("📦", "Units Sold",       f"{total_qty:,.0f}",    "#4cc9f0"),
    ]

    # ── Chart 1: Bar — Total Sales by Category ─────────────────────────────
    cat_sum = (dff.groupby("Category", as_index=False)
               .agg(Total_Sales=("Total Spent", "sum"),
                    Transactions=("Transaction ID", "count"))
               .sort_values("Total_Sales"))

    fig_bar = px.bar(
        cat_sum, x="Total_Sales", y="Category", orientation="h",
        color="Category", color_discrete_sequence=PALETTE,
        title="Total Sales by Category",
        labels={"Total_Sales": "Total Sales ($)", "Category": ""},
        hover_data={"Total_Sales": ":,.2f", "Transactions": ":,", "Category": False},
    )
    fig_bar.update_layout(template="plotly_white", showlegend=False,
                          title_x=.5, margin=dict(l=10, r=10, t=44, b=10))

    # ── Chart 2: Pie — Payment Method share ───────────────────────────────
    pay_sum = (dff.groupby("Payment Method", as_index=False)
               .agg(Total_Sales=("Total Spent","sum"),
                    Transactions=("Transaction ID","count")))

    fig_pie = px.pie(
        pay_sum, names="Payment Method", values="Total_Sales",
        color_discrete_sequence=PALETTE,
        title="Revenue by Payment Method",
        hover_data={"Transactions": True},
        hole=0.38,
    )
    fig_pie.update_layout(template="plotly_white", title_x=.5,
                          margin=dict(l=10, r=10, t=44, b=10))

    # ── Chart 3: Line — Monthly revenue trend by location ─────────────────
    if not dff.empty:
        dff2 = dff.copy()
        dff2["Month_Dt"] = dff2["Transaction Date"].dt.to_period("M").dt.to_timestamp()
        trend = (dff2.groupby(["Month_Dt","Location"], as_index=False)
                 .agg(Total_Sales=("Total Spent","sum"),
                      Transactions=("Transaction ID","count"))
                 .sort_values("Month_Dt"))
    else:
        trend = pd.DataFrame(columns=["Month_Dt","Location","Total_Sales","Transactions"])

    fig_line = px.line(
        trend, x="Month_Dt", y="Total_Sales", color="Location",
        markers=True, color_discrete_sequence=PALETTE,
        title="Monthly Revenue Trend by Location",
        labels={"Month_Dt": "Month", "Total_Sales": "Total Sales ($)", "Location": "Location"},
        hover_data={"Total_Sales": ":,.2f", "Transactions": ":,"},
    )
    fig_line.update_layout(
        template="plotly_white", title_x=.5,
        hovermode="x unified",
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
        margin=dict(l=10, r=10, t=44, b=40),
        legend_title_text="Location"
    )

    # ── Chart 4: Scatter — Price vs Total Spent (bubble = Quantity) ────────
    fig_scat = px.scatter(
        dff, x="Price Per Unit", y="Total Spent", size="Quantity",
        color="Payment Method", color_discrete_sequence=PALETTE,
        title="Price Per Unit vs Total Spent",
        labels={"Price Per Unit": "Price Per Unit ($)", "Total Spent": "Total Spent ($)"},
        hover_data={"Category": True, "Item": True, "Quantity": True, "Location": True},
        opacity=0.65,
    )
    fig_scat.update_layout(template="plotly_white", title_x=.5,
                           margin=dict(l=10, r=10, t=44, b=10),
                           legend_title_text="Payment")

    # ── Chart 5: Heatmap — Category × Payment Method avg revenue ──────────
    pivot = (dff.groupby(["Category","Payment Method"])["Total Spent"]
             .mean().unstack(fill_value=0).round(2))

    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        aspect="auto",
        title="Avg. Revenue Heatmap: Category × Payment Method",
        labels={"x": "Payment Method", "y": "Category", "color": "Avg Revenue ($)"},
        text_auto=".0f",
    )
    fig_heat.update_layout(template="plotly_white", title_x=.5,
                           margin=dict(l=10, r=10, t=44, b=10),
                           coloraxis_colorbar=dict(title="Avg ($)"))

    return kpis, fig_bar, fig_pie, fig_line, fig_scat, fig_heat


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
