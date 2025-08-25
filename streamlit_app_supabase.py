import streamlit as st
import pandas as pd
from supabase import create_client
import os
from datetime import datetime

st.set_page_config(page_title="Vinted CRM (Supabase)", page_icon="🧾", layout="wide")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

st.title("Vinted CRM – Inventaire (Base Supabase)")

st.markdown("""
Cette app lit/écrit dans **Supabase Postgres**. Le scraping s'exécute automatiquement toutes les 30 minutes via **GitHub Actions** et met à jour la table `items`.
""")

def fetch_items():
    return client.table("items").select("*").order("created_at", desc=True).execute().data

with st.sidebar:
    st.header("Export")
    data = fetch_items()
    df = pd.DataFrame(data)
    st.download_button("📤 Export CSV", df.to_csv(index=False).encode("utf-8"), "export.csv", "text/csv")

st.subheader("📦 Inventaire")
items = fetch_items()
if items:
    df = pd.DataFrame(items)
    cols = ["id","title","brand","size","price_eur","cost_eur","margin_eur","status","sku","item_url","image_url","notes","created_at","updated_at"]
    df = df[[c for c in cols if c in df.columns]]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### ✏️ Mettre à jour un article")
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_id = st.number_input("ID de l'article", step=1, min_value=0)
    with col2:
        new_status = st.selectbox("Nouveau statut", ["(inchangé)","en_stock","reserve","vendu"])
        cost = st.text_input("Coût d'achat (optionnel)")
    with col3:
        sku = st.text_input("SKU (optionnel)")
        notes = st.text_input("Notes (optionnel)")

    if st.button("Appliquer"):
        fields = {}
        if new_status != "(inchangé)":
            fields["status"] = new_status
        if cost.strip():
            try:
                fields["cost_eur"] = float(cost.replace(",", "."))
            except:
                st.warning("Format coût invalide (ex: 12.50)")
        if sku.strip():
            fields["sku"] = sku.strip()
        if notes.strip():
            fields["notes"] = notes.strip()
        if fields and sel_id:
            current = client.table("items").select("price_eur").eq("id", int(sel_id)).single().execute().data
            if current and current.get("price_eur") is not None and fields.get("cost_eur") is not None:
                fields["margin_eur"] = round(current["price_eur"] - fields["cost_eur"], 2)
            res = client.table("items").update(fields).eq("id", int(sel_id)).execute()
            st.success("Mise à jour effectuée ✅")
        else:
            st.info("Rien à mettre à jour.")

    st.markdown("### 🗑️ Supprimer un article")
    del_id = st.number_input("ID à supprimer", step=1, min_value=0, key="del")
    if st.button("Supprimer"):
        if del_id:
            client.table("items").delete().eq("id", int(del_id)).execute()
            st.success("Article supprimé.")
else:
    st.info("Aucun article en base pour l'instant.")
