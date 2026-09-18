from pathlib import Path
import json
import html
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed"
OUTPUT = ROOT / "docs" / "index.html"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATA FILES
# ============================================================

FILES = {
    "customers": "customers_clean.csv",
    "products": "products_clean.csv",
    "sales": "sales_clean.csv",
    "segments": "customer_segments.csv",
    "profiles": "segment_profiles.csv",
    "campaigns": "campaign_kpis.csv",
    "churn": "churn_clv_predictions.csv",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    data = {}

    for key, filename in FILES.items():
        path = DATA_DIR / filename

        if path.exists():
            data[key] = pd.read_csv(path)
            print(f"✓ Loaded: {filename}")
        else:
            print(f"⚠ Missing: {path}")
            data[key] = pd.DataFrame()

    return data


data = load_data()


# ============================================================
# DATAFRAME → JSON-SAFE PYTHON OBJECT
# ============================================================

def dataframe_to_records(df):
    if df.empty:
        return []

    result = df.astype(object).where(pd.notna(df), None)

    # Convert numpy/pandas scalar types to native Python types
    records = result.to_dict(orient="records")

    for record in records:
        for key, value in record.items():
            if hasattr(value, "item"):
                try:
                    record[key] = value.item()
                except Exception:
                    pass

    return records


embedded_data = {
    key: dataframe_to_records(df)
    for key, df in data.items()
}


# ============================================================
# OVERVIEW KPIs
# ============================================================

sales = data["sales"]
customers = data["customers"]
campaigns = data["campaigns"]

total_revenue = 0
sales_count = 0
customers_count = len(customers)
average_roi = 0

if not sales.empty and "Total_Amount" in sales.columns:
    total_revenue = sales["Total_Amount"].sum()
    sales_count = len(sales)

if not campaigns.empty and "ROI" in campaigns.columns:
    average_roi = campaigns["ROI"].mean()


# ============================================================
# HELPERS
# ============================================================

def format_number(value, decimals=0):
    if value is None:
        return "—"

    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def safe_json(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
    )


# ============================================================
# HTML
#
# IMPORTANT:
# This is a NORMAL Python string, NOT an f-string.
# Therefore JavaScript ${...} and { ... } are safe.
# ============================================================

HTML = r"""
<!DOCTYPE html>

<html lang="fr">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Marketing Optimization Dashboard</title>

<link
    rel="icon"
    href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>"
>

<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
}

body {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background: #f5f7fb;
    color: #172033;
}


/* =========================================================
   HEADER
========================================================= */

.header {
    background: white;
    padding: 28px 40px;
    border-bottom: 1px solid #e5e7eb;
}

.header h1 {
    margin: 0;
    font-size: 28px;
}

.header p {
    margin: 6px 0 0;
    color: #6b7280;
}


/* =========================================================
   LAYOUT
========================================================= */

.container {
    max-width: 1500px;
    margin: auto;
    padding: 30px 40px;
}


/* =========================================================
   TABS
========================================================= */

.tabs {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    margin-bottom: 25px;
}

.tab-button {
    border: none;
    background: white;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    color: #4b5563;
    white-space: nowrap;
}

.tab-button:hover {
    background: #eef2ff;
}

.tab-button.active {
    background: #111827;
    color: white;
}

.tab {
    display: none;
}

.tab.active {
    display: block;
}


/* =========================================================
   TYPOGRAPHY
========================================================= */

h2 {
    margin-top: 0;
}

h3 {
    margin-top: 0;
}


/* =========================================================
   METRICS
========================================================= */

.metrics {
    display: grid;
    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 18px;
    margin-bottom: 25px;
}

.metric {
    background: white;
    border-radius: 12px;
    padding: 22px;

    box-shadow:
        0 1px 3px rgba(0,0,0,.05);
}

.metric-label {
    color: #6b7280;
    font-size: 14px;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 27px;
    font-weight: 700;
}


/* =========================================================
   CARDS
========================================================= */

.card {
    background: white;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 25px;

    box-shadow:
        0 1px 3px rgba(0,0,0,.05);
}


/* =========================================================
   CHARTS
========================================================= */

.chart {
    width: 100%;
    min-height: 420px;
}


/* =========================================================
   TABLES
========================================================= */

.table-wrapper {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

th {
    text-align: left;
    background: #f9fafb;
    font-weight: 600;
    white-space: nowrap;
}

th,
td {
    padding: 10px 12px;
    border-bottom: 1px solid #e5e7eb;
}


/* =========================================================
   SELECT
========================================================= */

select {
    padding: 10px 14px;
    border: 1px solid #d1d5db;
    border-radius: 7px;
    background: white;
    font-size: 14px;
}


/* =========================================================
   GRID
========================================================= */

.grid-2 {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 20px;
}


/* =========================================================
   STRATEGY / PERSONAS
========================================================= */

.persona {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    margin-bottom: 15px;
    overflow: hidden;
    background: white;
}

.persona-header {
    padding: 16px 20px;
    background: #fafafa;
    font-weight: 700;
    cursor: pointer;
}

.persona-header:hover {
    background: #f3f4f6;
}

.persona-content {
    display: none;
    padding: 20px;
}

.persona.open .persona-content {
    display: block;
}

.strategy-metrics {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));

    gap: 15px;
    margin: 15px 0;
}

.strategy-metric {
    background: #f9fafb;
    padding: 15px;
    border-radius: 8px;
}

.strategy-metric strong {
    display: block;
    font-size: 20px;
    margin-top: 5px;
}

.recommendation {
    padding: 15px;
    background: #f9fafb;
    border-radius: 8px;
    margin-top: 10px;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 900px) {

    .container {
        padding: 20px;
    }

    .header {
        padding: 22px;
    }

    .metrics {
        grid-template-columns:
            repeat(2, 1fr);
    }

    .grid-2 {
        grid-template-columns: 1fr;
    }

}

@media (max-width: 600px) {

    .metrics {
        grid-template-columns: 1fr;
    }

    .strategy-metrics {
        grid-template-columns: 1fr;
    }

}

</style>

</head>


<body>


<header class="header">

    <h1>📊 Marketing Optimization</h1>

    <p>
        Customer Intelligence & Campaign Performance Dashboard
    </p>

</header>


<main class="container">


<!-- =========================================================
     TABS
========================================================= -->

<div class="tabs">

    <button
        class="tab-button active"
        onclick="openTab('overview', this)"
    >
        Vue d'ensemble
    </button>

    <button
        class="tab-button"
        onclick="openTab('segments', this)"
    >
        Segments
    </button>

    <button
        class="tab-button"
        onclick="openTab('campaigns', this)"
    >
        Campagnes
    </button>

    <button
        class="tab-button"
        onclick="openTab('churn', this)"
    >
        Churn
    </button>

    <button
        class="tab-button"
        onclick="openTab('strategy', this)"
    >
        Stratégie
    </button>

</div>


<!-- =========================================================
     OVERVIEW
========================================================= -->

<section
    id="overview"
    class="tab active"
>

    <h2>Indicateurs clés</h2>

    <div class="metrics">

        <div class="metric">

            <div class="metric-label">
                Chiffre d'affaires total
            </div>

            <div class="metric-value">
                __TOTAL_REVENUE__ €
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                Nombre de ventes
            </div>

            <div class="metric-value">
                __SALES_COUNT__
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                Nombre de clients
            </div>

            <div class="metric-value">
                __CUSTOMERS_COUNT__
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                ROI moyen campagnes
            </div>

            <div class="metric-value">
                __AVERAGE_ROI__ %
            </div>

        </div>

    </div>


    <div class="card">

        <h3>CA par canal de vente</h3>

        <div
            id="salesChart"
            class="chart"
        ></div>

    </div>

</section>


<!-- =========================================================
     SEGMENTS
========================================================= -->

<section
    id="segments"
    class="tab"
>

    <h2>Segments clients (personas)</h2>


    <div class="card">

        <div class="table-wrapper">

            <table id="profilesTable"></table>

        </div>

    </div>


    <div class="card">

        <h3>
            Taille de chaque segment
        </h3>

        <div
            id="segmentsChart"
            class="chart"
        ></div>

    </div>


    <div class="card">

        <h3>Filtrer par persona</h3>

        <select
            id="personaSelect"
            onchange="showPersona()"
        ></select>

        <div
            id="personaDetails"
            style="margin-top:20px;"
        ></div>

    </div>

</section>


<!-- =========================================================
     CAMPAIGNS
========================================================= -->

<section
    id="campaigns"
    class="tab"
>

    <h2>Performance des campagnes</h2>


    <div class="card">

        <div class="table-wrapper">

            <table id="campaignsTable"></table>

        </div>

    </div>


    <div class="card">

        <label>
            <strong>KPI à visualiser</strong>
        </label>

        <br><br>

        <select
            id="metricSelect"
            onchange="drawCampaignChart()"
        >

            <option value="CTR">CTR</option>

            <option value="CPC">CPC</option>

            <option value="CPA">CPA</option>

            <option value="ROI">ROI</option>

            <option value="Conversion_Rate">
                Conversion Rate
            </option>

        </select>


        <div
            id="campaignChart"
            class="chart"
        ></div>

    </div>

</section>


<!-- =========================================================
     CHURN
========================================================= -->

<section
    id="churn"
    class="tab"
>

    <h2>Risque de churn par client</h2>


    <div class="card">

        <div class="table-wrapper">

            <table id="churnTable"></table>

        </div>

    </div>


    <div class="grid-2">

        <div class="card">

            <h3>
                Clients par niveau de risque
            </h3>

            <div
                id="riskChart"
                class="chart"
            ></div>

        </div>


        <div class="card">

            <h3>
                Churn vs dépense totale
            </h3>

            <div
                id="churnScatter"
                class="chart"
            ></div>

        </div>

    </div>


    <div class="card">

        <h3>
            ⚠️ Clients à haut risque
            (priorité rétention)
        </h3>

        <div class="table-wrapper">

            <table id="highRiskTable"></table>

        </div>

    </div>

</section>


<!-- =========================================================
     STRATEGY
========================================================= -->

<section
    id="strategy"
    class="tab"
>

    <h2>
        Recommandations stratégiques par segment
    </h2>

    <div id="strategyContainer"></div>

</section>


</main>


<script>


// ============================================================
// DATA EMBEDDED BY PYTHON
// ============================================================

const DATA = __DATA__;


// ============================================================
// TAB HANDLING
// ============================================================

function openTab(tabId, button) {

    document
        .querySelectorAll(".tab")
        .forEach(function(tab) {
            tab.classList.remove("active");
        });

    document
        .querySelectorAll(".tab-button")
        .forEach(function(btn) {
            btn.classList.remove("active");
        });

    document
        .getElementById(tabId)
        .classList.add("active");

    button.classList.add("active");

    setTimeout(function() {
        window.dispatchEvent(
            new Event("resize")
        );
    }, 50);
}


// ============================================================
// HTML ESCAPING
// ============================================================

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ============================================================
// TABLE RENDERING
// ============================================================

function renderTable(
    elementId,
    rows,
    columns
) {

    var table =
        document.getElementById(elementId);

    if (!rows || rows.length === 0) {

        table.innerHTML =
            "<tbody>" +
            "<tr>" +
            "<td>Pas de données.</td>" +
            "</tr>" +
            "</tbody>";

        return;
    }

    if (!columns) {
        columns = Object.keys(rows[0]);
    }

    var output = "<thead><tr>";

    columns.forEach(function(column) {

        output +=
            "<th>" +
            escapeHtml(column) +
            "</th>";

    });

    output += "</tr></thead><tbody>";


    rows.forEach(function(row) {

        output += "<tr>";

        columns.forEach(function(column) {

            var value = row[column];

            if (
                value === null ||
                value === undefined
            ) {
                value = "—";
            }

            output +=
                "<td>" +
                escapeHtml(value) +
                "</td>";

        });

        output += "</tr>";

    });


    output += "</tbody>";

    table.innerHTML = output;
}


// ============================================================
// SALES CHART
// ============================================================

function drawSalesChart() {

    var sales = DATA.sales;

    if (
        !sales ||
        sales.length === 0 ||
        !("Channel" in sales[0]) ||
        !("Total_Amount" in sales[0])
    ) {
        return;
    }


    var totals = {};


    sales.forEach(function(row) {

        var channel = row.Channel;

        var amount =
            Number(row.Total_Amount) || 0;

        totals[channel] =
            (totals[channel] || 0) +
            amount;

    });


    Plotly.newPlot(
        "salesChart",
        [{
            x: Object.keys(totals),

            y: Object.values(totals),

            type: "bar"
        }],
        {
            margin: {
                t: 20,
                r: 20,
                b: 60,
                l: 70
            },

            yaxis: {
                title: "Chiffre d'affaires"
            },

            xaxis: {
                title: "Canal"
            },

            paper_bgcolor: "white",

            plot_bgcolor: "white"
        },
        {
            responsive: true,
            displaylogo: false
        }
    );
}


// ============================================================
// SEGMENTS CHART
// ============================================================

function drawSegmentsChart() {

    var profiles = DATA.profiles;

    if (!profiles || profiles.length === 0) {
        return;
    }


    Plotly.newPlot(
        "segmentsChart",
        [{
            x: profiles.map(
                function(x) {
                    return x.Persona_Name;
                }
            ),

            y: profiles.map(
                function(x) {
                    return Number(x.Size_pct) || 0;
                }
            ),

            type: "bar"
        }],
        {
            margin: {
                t: 20,
                r: 20,
                b: 100,
                l: 60
            },

            yaxis: {
                title: "Taille (%)"
            },

            xaxis: {
                tickangle: -35
            }
        },
        {
            responsive: true,
            displaylogo: false
        }
    );
}


// ============================================================
// PERSONAS
// ============================================================

function initializePersonas() {

    var profiles = DATA.profiles;

    var select =
        document.getElementById(
            "personaSelect"
        );

    if (!profiles || profiles.length === 0) {
        return;
    }


    profiles.forEach(function(profile) {

        var option =
            document.createElement("option");

        option.value =
            profile.Persona_Name;

        option.textContent =
            profile.Persona_Name;

        select.appendChild(option);

    });


    showPersona();
}


function showPersona() {

    var select =
        document.getElementById(
            "personaSelect"
        );

    if (!select.value) {
        return;
    }


    var selected =
        select.value;


    var profile =
        DATA.profiles.find(
            function(x) {
                return x.Persona_Name === selected;
            }
        );


    if (!profile) {
        return;
    }


    var cluster =
        profile.Cluster;


    var customersInSegment =
        DATA.segments.filter(
            function(x) {
                return String(x.Cluster) ===
                    String(cluster);
            }
        );


    var customersMap = {};


    DATA.customers.forEach(
        function(customer) {

            customersMap[
                String(customer.Customer_ID)
            ] = customer;

        }
    );


    var merged =
        customersInSegment.map(
            function(segment) {

                return Object.assign(
                    {},
                    segment,
                    customersMap[
                        String(segment.Customer_ID)
                    ] || {}
                );

            }
        );


    var html = "";


    html +=
        "<h3>" +
        escapeHtml(profile.Persona_Name) +
        "</h3>";


    html +=
        "<p>" +
        "<strong>Description :</strong> " +
        escapeHtml(
            profile.Persona_Description || "—"
        ) +
        "</p>";


    html +=
        "<p>" +
        "<strong>Recommandation :</strong> " +
        escapeHtml(
            profile.Recommendation || "—"
        ) +
        "</p>";


    html +=
        "<h3>" +
        "Clients dans le segment " +
        "(" + merged.length + " clients)" +
        "</h3>";


    html +=
        '<div class="table-wrapper">' +
        '<table id="personaCustomers"></table>' +
        "</div>";


    document.getElementById(
        "personaDetails"
    ).innerHTML = html;


    renderTable(
        "personaCustomers",
        merged
    );
}


// ============================================================
// CAMPAIGN CHART
// ============================================================

function drawCampaignChart() {

    var campaigns = DATA.campaigns;

    if (
        !campaigns ||
        campaigns.length === 0
    ) {
        return;
    }


    var metric =
        document.getElementById(
            "metricSelect"
        ).value;


    Plotly.newPlot(
        "campaignChart",
        [{
            x: campaigns.map(
                function(x) {
                    return x.Channel;
                }
            ),

            y: campaigns.map(
                function(x) {
                    return Number(x[metric]) || 0;
                }
            ),

            type: "bar"
        }],
        {
            margin: {
                t: 20,
                r: 20,
                b: 70,
                l: 70
            },

            yaxis: {
                title: metric
            },

            xaxis: {
                title: "Canal"
            }
        },
        {
            responsive: true,
            displaylogo: false
        }
    );
}


// ============================================================
// CHURN DATA
// ============================================================

function buildChurnData() {

    var customersMap = {};


    DATA.customers.forEach(
        function(customer) {

            customersMap[
                String(customer.Customer_ID)
            ] = customer;

        }
    );


    return DATA.churn.map(
        function(churn) {

            return Object.assign(
                {},
                churn,
                customersMap[
                    String(churn.Customer_ID)
                ] || {}
            );

        }
    );
}


// ============================================================
// RISK CHART
// ============================================================

function drawRiskChart(churnData) {

    var counts = {};


    churnData.forEach(function(row) {

        var risk =
            row.Risk_Segment || "Unknown";

        counts[risk] =
            (counts[risk] || 0) + 1;

    });


    var order = [
        "Low",
        "Medium",
        "High"
    ];


    var labels =
        order.filter(
            function(x) {
                return counts[x] !== undefined;
            }
        );


    Plotly.newPlot(
        "riskChart",
        [{
            x: labels,

            y: labels.map(
                function(x) {
                    return counts[x];
                }
            ),

            type: "bar"
        }],
        {
            margin: {
                t: 20,
                r: 20,
                b: 60,
                l: 60
            },

            yaxis: {
                title: "Nombre de clients"
            }
        },
        {
            responsive: true,
            displaylogo: false
        }
    );
}


// ============================================================
// CHURN SCATTER
// ============================================================

function drawChurnScatter(churnData) {

    var filtered =
        churnData.filter(
            function(x) {

                return (
                    x.Churn_Probability !== undefined &&
                    x.Total_Spent !== undefined
                );

            }
        );


    if (filtered.length === 0) {
        return;
    }


    var riskLevels =
        Array.from(
            new Set(
                filtered.map(
                    function(x) {
                        return x.Risk_Segment;
                    }
                )
            )
        );


    var traces =
        riskLevels.map(
            function(risk) {

                var rows =
                    filtered.filter(
                        function(x) {
                            return x.Risk_Segment === risk;
                        }
                    );


                return {

                    x: rows.map(
                        function(x) {
                            return Number(
                                x.Churn_Probability
                            );
                        }
                    ),

                    y: rows.map(
                        function(x) {
                            return Number(
                                x.Total_Spent
                            );
                        }
                    ),

                    mode: "markers",

                    type: "scatter",

                    name: risk
                };

            }
        );


    Plotly.newPlot(
        "churnScatter",
        traces,
        {
            margin: {
                t: 20,
                r: 20,
                b: 60,
                l: 70
            },

            xaxis: {
                title: "Probabilité de churn"
            },

            yaxis: {
                title: "Dépense totale"
            }
        },
        {
            responsive: true,
            displaylogo: false
        }
    );
}


// ============================================================
// STRATEGY
// ============================================================

function buildStrategy() {

    var profiles = DATA.profiles;
    var campaigns = DATA.campaigns;
    var churn = DATA.churn;


    var roiByChannel = {};


    campaigns.forEach(function(row) {

        var channel = row.Channel;

        var roi = Number(row.ROI);

        if (
            !channel ||
            Number.isNaN(roi)
        ) {
            return;
        }


        if (!roiByChannel[channel]) {
            roiByChannel[channel] = [];
        }


        roiByChannel[channel].push(roi);

    });


    Object.keys(roiByChannel)
        .forEach(function(channel) {

            var values =
                roiByChannel[channel];

            roiByChannel[channel] =
                values.reduce(
                    function(a, b) {
                        return a + b;
                    },
                    0
                ) / values.length;

        });


    var churnByCluster = {};
    var riskByCluster = {};


    churn.forEach(function(row) {

        var cluster =
            String(row.Cluster);


        var probability =
            Number(
                row.Churn_Probability
            );


        if (!Number.isNaN(probability)) {

            if (!churnByCluster[cluster]) {
                churnByCluster[cluster] = [];
            }

            churnByCluster[cluster].push(
                probability
            );

        }


        if (!riskByCluster[cluster]) {
            riskByCluster[cluster] = [];
        }

        riskByCluster[cluster].push(
            row.Risk_Segment
        );

    });


    Object.keys(churnByCluster)
        .forEach(function(cluster) {

            var values =
                churnByCluster[cluster];

            churnByCluster[cluster] =
                values.reduce(
                    function(a, b) {
                        return a + b;
                    },
                    0
                ) / values.length;

        });


    Object.keys(riskByCluster)
        .forEach(function(cluster) {

            var values =
                riskByCluster[cluster];

            var counts = {};


            values.forEach(
                function(value) {

                    counts[value] =
                        (counts[value] || 0) + 1;

                }
            );


            riskByCluster[cluster] =
                Object.entries(counts)
                    .sort(
                        function(a, b) {
                            return b[1] - a[1];
                        }
                    )[0][0];

        });


    var output = "";


    profiles.forEach(function(row) {

        var cluster =
            String(row.Cluster);


        var preferredChannel =
            row.Preferred_Channel;


        var channelROI =
            roiByChannel[
                preferredChannel
            ];


        var avgChurn =
            churnByCluster[cluster];


        var strategy = "";


        if (
            avgChurn !== undefined &&
            avgChurn > 0.5
        ) {

            strategy =
                "🔴 Segment à risque de churn élevé (" +
                (avgChurn * 100).toFixed(0) +
                "%) — priorité rétention.";


            if (channelROI !== undefined) {

                strategy +=
                    " Canal " +
                    escapeHtml(preferredChannel) +
                    " recommandé (ROI moyen " +
                    channelROI.toFixed(0) +
                    "%).";

            }

        }

        else if (
            channelROI !== undefined &&
            channelROI > 300
        ) {

            strategy =
                "🟢 Segment stable avec un canal très rentable (" +
                escapeHtml(preferredChannel) +
                ", ROI " +
                channelROI.toFixed(0) +
                "%) — opportunité d'investissement/upsell.";

        }

        else {

            strategy =
                "🟡 Segment à surveiller — pas de signal fort, " +
                "maintenir le budget actuel.";

        }


        output +=
            '<div class="persona">';


        output +=
            '<div class="persona-header" ' +
            'onclick="this.parentElement.classList.toggle(\'open\')">';


        output +=
            "📌 " +
            escapeHtml(row.Persona_Name) +
            " — " +
            Number(row.Size_pct || 0).toFixed(0) +
            "% de la clientèle";


        output +=
            "</div>";


        output +=
            '<div class="persona-content">';


        output +=
            '<div class="strategy-metrics">';


        output +=
            '<div class="strategy-metric">' +
            "Dépense moyenne" +
            "<strong>" +
            Number(row.Avg_Spend || 0).toFixed(0) +
            " €" +
            "</strong>" +
            "</div>";


        output +=
            '<div class="strategy-metric">' +
            "Churn moyen (segment)" +
            "<strong>" +
            (
                avgChurn !== undefined
                    ? (avgChurn * 100).toFixed(0) + " %"
                    : "—"
            ) +
            "</strong>" +
            "</div>";


        output +=
            '<div class="strategy-metric">' +
            "ROI canal préféré" +
            "<strong>" +
            (
                channelROI !== undefined
                    ? channelROI.toFixed(0) + " %"
                    : "—"
            ) +
            "</strong>" +
            "</div>";


        output +=
            "</div>";


        output +=
            "<p>" +
            "<strong>Profil :</strong> " +
            escapeHtml(
                row.Persona_Description || "—"
            ) +
            "</p>";


        output +=
            "<p>" +
            "<strong>Recommandation Persona :</strong> " +
            escapeHtml(
                row.Recommendation || "—"
            ) +
            "</p>";


        output +=
            '<div class="recommendation">' +
            "<strong>" +
            "Recommandation M7 " +
            "(stratégie enrichie) :" +
            "</strong>" +
            "<p>" +
            strategy +
            "</p>" +
            "</div>";


        output +=
            "</div>" +
            "</div>";

    });


    document.getElementById(
        "strategyContainer"
    ).innerHTML = output;
}


// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        // Overview
        drawSalesChart();


        // Segments

        var profileColumns = [
            "Cluster",
            "Persona_Name",
            "Size_pct",
            "Avg_Age",
            "Dominant_Gender",
            "Avg_Spend",
            "Favorite_Category",
            "Preferred_Channel"
        ];


        if (
            DATA.profiles &&
            DATA.profiles.length
        ) {

            profileColumns =
                profileColumns.filter(
                    function(column) {
                        return column in DATA.profiles[0];
                    }
                );

        }


        renderTable(
            "profilesTable",
            DATA.profiles,
            profileColumns
        );


        drawSegmentsChart();

        initializePersonas();


        // Campaigns

        renderTable(
            "campaignsTable",
            DATA.campaigns
        );

        drawCampaignChart();


        // Churn

        var churnData =
            buildChurnData();


        renderTable(
            "churnTable",
            churnData
        );


        drawRiskChart(
            churnData
        );


        drawChurnScatter(
            churnData
        );


        // High risk

        renderTable(
            "highRiskTable",
            churnData.filter(
                function(x) {
                    return x.Risk_Segment === "High";
                }
            )
        );


        // Strategy

        buildStrategy();

    }
);

</script>

</body>

</html>
"""


# ============================================================
# INJECT PYTHON VALUES
# ============================================================

HTML = HTML.replace(
    "__TOTAL_REVENUE__",
    format_number(total_revenue)
)

HTML = HTML.replace(
    "__SALES_COUNT__",
    format_number(sales_count)
)

HTML = HTML.replace(
    "__CUSTOMERS_COUNT__",
    format_number(customers_count)
)

HTML = HTML.replace(
    "__AVERAGE_ROI__",
    format_number(average_roi)
)

HTML = HTML.replace(
    "__DATA__",
    safe_json(embedded_data)
)


# ============================================================
# WRITE OUTPUT
# ============================================================

OUTPUT.write_text(
    HTML,
    encoding="utf-8"
)


# ============================================================
# DONE
# ============================================================

size_mb = OUTPUT.stat().st_size / (1024 * 1024)

print()
print("=" * 60)
print("STATIC DASHBOARD GENERATED SUCCESSFULLY")
print("=" * 60)
print(f"Output : {OUTPUT}")
print(f"Size   : {size_mb:.2f} MB")
print()
print("The dashboard data is embedded directly in index.html.")
print("=" * 60)
