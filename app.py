import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Red Hidráulica", layout="wide")

st.title("Visualización y Cálculo de Red Hidráulica")

st.markdown("Sube un archivo Excel con los datos de los nodos y tuberías.")

uploaded_file = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    try:
        nodos = pd.read_excel(xls, sheet_name="NODOS")
        tramos = pd.read_excel(xls, sheet_name="TRAMOS")

        st.subheader("Datos de Nodos")
        st.dataframe(nodos)

        st.subheader("Datos de Tuberías")
        st.dataframe(tramos)

        st.subheader("Red Hidráulica - Vista Interactiva")

        G = nx.DiGraph()

        for _, row in nodos.iterrows():
            G.add_node(row["ID"], label=row["ID"], title=f'Cota: {row["Cota"]} m', level=row["ID"])

        for _, row in tramos.iterrows():
            G.add_edge(row["Desde"], row["Hasta"], title=f'L: {row["Longitud"]} m, C: {row["C"]}, D: {row["Diametro"]} m')

        net = Network(height="600px", width="100%", directed=True)
        net.from_nx(G)
        net.repulsion()

        net.save_graph(f"{base_dir}/network.html")

        with open(f"{base_dir}/network.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=650)

    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
