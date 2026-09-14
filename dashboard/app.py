"""
dashboard/app.py
-----------------
Dashboard Streamlit pour le projet marketing.optimization (M8 - Person 6).

Lancer avec :
    streamlit run dashboard/app.py

Schémas réels des fichiers (confirmés le 14/09/2026) :
- customer_segments.csv : Customer_ID, Cluster, PC1, PC2, Age, Total_Spent,
  Nb_Purchases, Avg_Basket, Nb_Distinct_Categories
- segment_profiles.csv  : Cluster, Persona_Name, Size_pct, Avg_Age,
  Dominant_Gender, Avg_Spend, Avg_Basket, Avg_Purchase_Frequency,
  Favorite_Category, Preferred_Channel, Persona_Description, Recommendation
- campaign_kpis.csv     : Campaign_ID, Channel, Start_Date, End_Date,
  Duration_days, Budget, Impressions, Clicks, Conversions, CTR,
  Conversion_Rate, CPC, CPA, Estimated_Revenue, ROI
- churn_clv_predictions.csv : Customer_ID, Cluster, Churn_Probability,
  Churn_Prediction, Risk_Segment (pas de CLV calculée)
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# Only strip padding when embedded in an iframe
if st.query_params.get("embed") == "true":
    st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
        }
    </style>
    """, unsafe_allow_html=True) 

st.set_page_config(page_title="Marketing Optimization Dashboard", layout="wide")


@st.cache_data
def load_data():
    data = {}
    files = {
        "customers": "data/processed/customers_clean.csv",
        "products": "data/processed/products_clean.csv",
        "sales": "data/processed/sales_clean.csv",
        "segments": "data/processed/customer_segments.csv",
        "profiles": "data/processed/segment_profiles.csv",
        "campaigns": "data/processed/campaign_kpis.csv",
        "churn": "data/processed/churn_clv_predictions.csv",
    }
    missing = []
    for key, path in files.items():
        try:
            data[key] = pd.read_csv(path)
        except FileNotFoundError:
            missing.append(path)
            data[key] = pd.DataFrame()
    return data, missing


data, missing_files = load_data()

if missing_files:
    st.warning("Fichiers manquants : " + ", ".join(missing_files))

st.title("📊 Marketing Optimization — Dashboard")

tab_overview, tab_segments, tab_campaigns, tab_churn, tab_strategy = st.tabs(
    ["Vue d'ensemble", "Segments", "Campagnes", "Churn", "Stratégie"]
)

# -------------------------------------------------------------------------
# Onglet 1 : Vue d'ensemble
# -------------------------------------------------------------------------
with tab_overview:
    st.subheader("Indicateurs clés")
    col1, col2, col3, col4 = st.columns(4)
    if not data["sales"].empty and "Total_Amount" in data["sales"].columns:
        col1.metric("Chiffre d'affaires total", f"{data['sales']['Total_Amount'].sum():,.0f} €")
        col2.metric("Nombre de ventes", len(data["sales"]))
    if not data["customers"].empty:
        col3.metric("Nombre de clients", len(data["customers"]))
    if not data["campaigns"].empty and "ROI" in data["campaigns"].columns:
        col4.metric("ROI moyen campagnes", f"{data['campaigns']['ROI'].mean():.0f} %")

    if not data["sales"].empty and "Channel" in data["sales"].columns:
        sales_by_channel = data["sales"].groupby("Channel")["Total_Amount"].sum().reset_index()
        fig = px.bar(sales_by_channel, x="Channel", y="Total_Amount", title="CA par canal de vente")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------------
# Onglet 2 : Segments / Personas
# -------------------------------------------------------------------------
with tab_segments:
    st.subheader("Segments clients (personas)")

    if not data["profiles"].empty:
        display_cols = [c for c in [
            "Cluster", "Persona_Name", "Size_pct", "Avg_Age", "Dominant_Gender",
            "Avg_Spend", "Favorite_Category", "Preferred_Channel",
        ] if c in data["profiles"].columns]
        st.dataframe(data["profiles"][display_cols], use_container_width=True)

        fig = px.bar(
            data["profiles"], x="Persona_Name", y="Size_pct",
            title="Taille de chaque segment (% de la clientèle)", color="Persona_Name",
        )
        st.plotly_chart(fig, use_container_width=True)

        selected_persona = st.selectbox("Filtrer par persona", data["profiles"]["Persona_Name"].tolist())
        profile_row = data["profiles"][data["profiles"]["Persona_Name"] == selected_persona].iloc[0]
        cluster_id = profile_row["Cluster"]

        st.markdown(f"**Description :** {profile_row.get('Persona_Description', '—')}")
        st.markdown(f"**Recommandation  :** {profile_row.get('Recommendation', '—')}")

        if not data["segments"].empty and not data["customers"].empty:
            customers_in_segment = data["segments"][data["segments"]["Cluster"] == cluster_id]
            merged = customers_in_segment.merge(data["customers"], on="Customer_ID", suffixes=("", "_dup"))
            st.write(f"Clients dans le segment **{selected_persona}** ({len(merged)} clients) :")
            st.dataframe(merged, use_container_width=True)
    else:
        st.info("Pas encore de données de segments.")

# -------------------------------------------------------------------------
# Onglet 3 : Campagnes
# -------------------------------------------------------------------------
with tab_campaigns:
    st.subheader("Performance des campagnes")

    if not data["campaigns"].empty:
        st.dataframe(data["campaigns"], use_container_width=True)

        available_metrics = [c for c in ["CTR", "CPC", "CPA", "ROI", "Conversion_Rate"] if c in data["campaigns"].columns]
        metric = st.selectbox("KPI à visualiser", available_metrics)
        fig = px.bar(
            data["campaigns"], x="Channel", y=metric,
            title=f"{metric} par canal", color="Channel",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas encore de données de campagnes.")

# -------------------------------------------------------------------------
# Onglet 4 : Churn
# -------------------------------------------------------------------------
with tab_churn:
    st.subheader("Risque de churn par client")

    if not data["churn"].empty and not data["customers"].empty:
        merged = data["churn"].merge(data["customers"], on="Customer_ID", suffixes=("", "_dup"))
        st.dataframe(merged, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            risk_counts = merged["Risk_Segment"].value_counts().reset_index()
            risk_counts.columns = ["Risk_Segment", "Nombre_Clients"]
            fig = px.bar(
                risk_counts, x="Risk_Segment", y="Nombre_Clients",
                title="Clients par niveau de risque", color="Risk_Segment",
                category_orders={"Risk_Segment": ["Low", "Medium", "High"]},
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if "Total_Spent" in merged.columns:
                fig = px.scatter(
                    merged, x="Churn_Probability", y="Total_Spent",
                    title="Churn vs dépense totale", color="Risk_Segment",
                )
                st.plotly_chart(fig, use_container_width=True)

        st.write("⚠️ Clients à haut risque (priorité rétention) :")
        st.dataframe(merged[merged["Risk_Segment"] == "High"], use_container_width=True)
    else:
        st.info("Pas encore de données de churn.")

# -------------------------------------------------------------------------
# Onglet 5 : Stratégie (M7) — le cœur du travail
# -------------------------------------------------------------------------
with tab_strategy:
    st.subheader("Recommandations stratégiques par segment")

    if data["profiles"].empty:
        st.info("Pas encore de profils de segments.")
    else:
        # ROI moyen par canal (pour croiser avec le canal préféré de chaque persona)
        roi_by_channel = {}
        if not data["campaigns"].empty and "ROI" in data["campaigns"].columns:
            roi_by_channel = data["campaigns"].groupby("Channel")["ROI"].mean().to_dict()

        # Churn moyen par cluster
        churn_by_cluster = {}
        risk_by_cluster = {}
        if not data["churn"].empty:
            churn_by_cluster = data["churn"].groupby("Cluster")["Churn_Probability"].mean().to_dict()
            risk_by_cluster = data["churn"].groupby("Cluster")["Risk_Segment"].agg(
                lambda x: x.value_counts().idxmax()
            ).to_dict()

        for _, row in data["profiles"].iterrows():
            cluster_id = row["Cluster"]
            preferred_channel = row.get("Preferred_Channel", None)
            channel_roi = roi_by_channel.get(preferred_channel)
            avg_churn = churn_by_cluster.get(cluster_id)
            dominant_risk = risk_by_cluster.get(cluster_id)

            with st.expander(f"📌 {row['Persona_Name']} — {row.get('Size_pct', 0):.0f}% de la clientèle"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Dépense moyenne", f"{row.get('Avg_Spend', 0):.0f} €")
                col2.metric("Churn moyen (segment)", f"{avg_churn*100:.0f} %" if avg_churn is not None else "—")
                col3.metric(f"ROI canal préféré ({preferred_channel})", f"{channel_roi:.0f} %" if channel_roi is not None else "—")

                st.markdown(f"**Profil :** {row.get('Persona_Description', '—')}")
                st.markdown(f"**Recommandation Person 3 (persona) :** {row.get('Recommendation', '—')}")

                # Recommandation M7 enrichie : croise churn + ROI canal
                st.markdown("**Recommandation M7 (stratégie enrichie) :**")
                if avg_churn is not None and avg_churn > 0.5:
                    st.write(
                        f"🔴 Segment à risque de churn élevé ({avg_churn*100:.0f}%) — "
                        f"priorité rétention. Canal {preferred_channel} recommandé "
                        f"(ROI moyen {channel_roi:.0f}%)." if channel_roi else
                        f"🔴 Segment à risque de churn élevé ({avg_churn*100:.0f}%) — priorité rétention."
                    )
                elif channel_roi is not None and channel_roi > 300:
                    st.write(
                        f"🟢 Segment stable avec un canal très rentable ({preferred_channel}, "
                        f"ROI {channel_roi:.0f}%) — opportunité d'investissement/upsell."
                    )
                else:
                    st.write("🟡 Segment à surveiller — pas de signal fort, maintenir le budget actuel.")
