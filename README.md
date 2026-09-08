# Marketing Optimization 📊

A **customer segmentation & marketing optimization project**, built by a team of 6, that turns raw customer, product, sales, and marketing data into actionable strategy: clusters, personas, campaign KPIs, churn/CLV predictions, a live dashboard, and a final report + presentation.

Use this README as the entry point of the repository — it explains what the project does, how it's organized, how to set it up, and how the 6 work packages fit together.

---

## 🎯 What this project does

Starting from 4 raw datasets (`customers_data.csv`, `products_data.csv`, `sales_data.csv`, `marketing_data.csv`), the team:

1. Cleans and explores the data
2. Segments customers into clusters (K-means / PCA)
3. Turns clusters into marketing personas
4. Evaluates marketing campaign performance (CTR, CPC, CPA, ROI)
5. Predicts customer churn or lifetime value (CLV)
6. Builds a per-segment digital marketing strategy
7. Deploys an interactive Streamlit dashboard
8. Delivers a final report (Word/PDF) and an oral presentation (PowerPoint)

This maps directly onto modules **M1–M9** of the project brief, split across **6 team members** (see [`00_MASTER_marketing.optimization.md`](./00_MASTER_marketing.optimization.md) for the full breakdown).

---

## 👥 Team roles at a glance

| # | Member | Covers | Spec file |
|---|--------|--------|-----------|
| 1 | Person 1 | M1 Strategic scoping + M2 Data exploration | `01_marketing.optimization_person1_data_exploration.md` |
| 2 | Person 2 | M3 Segmentation / clustering | `02_marketing.optimization_person2_segmentation_clustering.md` |
| 3 | Person 3 | M4 Persona profiling | `03_marketing.optimization_person3_persona_profiling.md` |
| 4 | Person 4 | M5 Campaign performance analysis | `04_marketing.optimization_person4_campaign_analysis.md` |
| 5 | Person 5 | M6 Churn / CLV prediction | `05_marketing.optimization_person5_churn_clv_prediction.md` |
| 6 | Person 6 | M7 Strategy + M8 Dashboard + M9 Final report & presentation | `06_marketing.optimization_person6_strategy_dashboard_presentation.md` |

⚠️ Person 6 is the pivot: their work only closes out once the other 5 have delivered. Everyone should read [`00_MASTER_marketing.optimization.md`](./00_MASTER_marketing.optimization.md) first — it defines the **data contract** every output file must respect so the 6 pieces merge without friction.

---

## 📂 Project Structure

```
marketing.optimization/
│
├── data/
│   ├── raw/                        # Original datasets, never modified
│   │   ├── customers_data.csv
│   │   ├── products_data.csv
│   │   ├── sales_data.csv
│   │   └── marketing_data.csv
│   │
│   └── processed/                  # Cleaned / feature-engineered data (per-module contract)
│       ├── customers_clean.csv         ← Person 1
│       ├── products_clean.csv          ← Person 1
│       ├── sales_clean.csv             ← Person 1
│       ├── customer_segments.csv       ← Person 2
│       ├── segment_profiles.csv        ← Person 3
│       ├── campaign_kpis.csv           ← Person 4
│       └── churn_clv_predictions.csv   ← Person 5
│
├── notebooks/                      # One notebook per module
│   ├── 01_exploration.ipynb            ← Person 1
│   ├── 02_segmentation.ipynb           ← Person 2
│   ├── 03_personas.ipynb               ← Person 3
│   ├── 04_campaigns.ipynb              ← Person 4
│   ├── 05_prediction.ipynb             ← Person 5
│   └── 06_strategy_dashboard.ipynb     ← Person 6
│
├── reports/                        # Written deliverables
│   ├── M1_strategic_note.pdf           ← Person 1
│   ├── M4_personas.pdf                 ← Person 3
│   ├── M5_campaign_analysis.pdf        ← Person 4
│   ├── M7_digital_strategy.pdf         ← Person 6
│   └── final_report.docx / .pdf        ← Person 6 (merges everything)
│
├── dashboard/
│   └── app.py                      # Streamlit dashboard ← Person 6
│
├── presentation/
│   └── final_pitch.pptx            # Final oral presentation ← Person 6
│
├── docs/                           # The 7 project spec files (this documentation set)
│   ├── 00_MASTER_marketing.optimization.md
│   ├── 01_marketing.optimization_person1_data_exploration.md
│   ├── 02_marketing.optimization_person2_segmentation_clustering.md
│   ├── 03_marketing.optimization_person3_persona_profiling.md
│   ├── 04_marketing.optimization_person4_campaign_analysis.md
│   ├── 05_marketing.optimization_person5_churn_clv_prediction.md
│   └── 06_marketing.optimization_person6_strategy_dashboard_presentation.md
│
├── requirements.txt                # Python dependencies (shared across the team)
├── config.py                       # Shared paths (RAW_DIR, PROCESSED_DIR, REPORTS_DIR...)
├── README.md                       # This file
└── .gitignore                      # Ignore venv, __pycache__, checkpoints, etc.
```

---

## ⚙️ Setup

Every team member should follow the **same setup** so notebooks, paths, and dependencies stay compatible.

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/marketing.optimization.git
cd marketing.optimization
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

* On Linux/Mac:
  ```bash
  source .venv/bin/activate
  ```
* On Windows:
  ```bash
  .venv\Scripts\activate
  ```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet, the first person to set up the repo (usually Person 1) creates it:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy \
            plotly streamlit jupyterlab openpyxl xgboost \
            python-docx python-pptx fpdf2 statsmodels shap
pip freeze > requirements.txt
```

### 5. Place the raw data

Put the 4 provided CSV files into `data/raw/`:
```
data/raw/customers_data.csv
data/raw/products_data.csv
data/raw/sales_data.csv
data/raw/marketing_data.csv
```

You're good to go 🚀 — open Jupyter (`jupyter lab`) or Kaggle-linked notebooks and start with your assigned module.

---

## 🧭 How to work on this project

1. **Read `docs/00_MASTER_marketing.optimization.md` first.** It defines the data contract (exact column names each module must output) — this is what lets 6 people's work merge without conflict.
2. **Find your role** in the team table above, and open your matching spec file in `docs/` — it contains your full task breakdown, methodology, environment setup, expected output format, checklist, and a ready-to-use LLM master prompt.
3. **Work in your own notebook** under `notebooks/`, never inside someone else's.
4. **Drop your output file(s)** into `data/processed/` using the exact file name and columns defined in the contract.
5. **Run the self-check checklist** at the end of your spec file before considering your part "done."
6. Person 6 collects everything, verifies the merge (see the verification script in the MASTER file), and builds the dashboard, final report, and presentation.

---

## ✅ Final deliverables checklist

- [ ] Customer segmentation and detailed profiles
- [ ] Campaign analyses and recommendations
- [ ] Predictive AI models (churn or customer value)
- [ ] Interactive dashboard (`dashboard/app.py`)
- [ ] Final report (`reports/final_report.docx` or `.pdf`)
- [ ] Oral presentation (`presentation/final_pitch.pptx`)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE.md).