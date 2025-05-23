import streamlit as st
import pandas as pd
import numpy as np
import math
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Diseño de Redes Hidráulicas - Hazen-Williams")

uploaded_file = st.file_uploader("📄 Cargar archivo Excel con red hidráulica", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("🔢 Datos de Entrada")
    st.dataframe(df, use_container_width=True)

    def calcular_velocidad(Q, D):
        area = math.pi * (D / 2) ** 2
        return Q / area if area else 0

    def calcular_perdida_hf(Q, L, D, C):
        return 10.67 * L * (Q ** 1.85) / ((C ** 1.85) * (D ** 4.87))

    def sugerir_diametro(Q, velocidad_objetivo=1.0):
        area = Q / velocidad_objetivo
        D = math.sqrt((4 * area) / math.pi)
        return D

    st.subheader("📈 Resultados por Tramo")

    resultados = []
    for _, row in df.iterrows():
        tramo = row["Tramo"]
        L = row["Longitud (m)"]
        Q = row["Caudal (m3/s)"]
        D = row["Diámetro (m)"]
        C = row["C"]
        nodo_ini = row["Nodo Inicial"]
        nodo_fin = row["Nodo Final"]

        v = calcular_velocidad(Q, D)
        hf = calcular_perdida_hf(Q, L, D, C)
        D_economico = sugerir_diametro(Q)

        resultados.append({
            "Tramo": tramo,
            "Nodo Inicial": nodo_ini,
            "Nodo Final": nodo_fin,
            "Velocidad (m/s)": round(v, 3),
            "hf (m)": round(hf, 3),
            "Diámetro económico (m)": round(D_economico, 3),
            "Color": "🔴" if v < 0.9 or v > 1.1 else "🟢"
        })

    resultados_df = pd.DataFrame(resultados)
    st.dataframe(resultados_df, use_container_width=True)

    st.subheader("🔍 Visualización de la Red")
    G = nx.DiGraph()
    for _, row in resultados_df.iterrows():
        G.add_edge(row["Nodo Inicial"], row["Nodo Final"],
                   label=f'{row["Velocidad (m/s)"]} m/s',
                   color='red' if row["Color"] == "🔴" else 'green')

    pos = nx.spring_layout(G, seed=42)
    edge_labels = nx.get_edge_attributes(G, "label")
    edge_colors = [G[u][v]["color"] for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color=edge_colors, width=2, ax=ax)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
    st.pyplot(fig)
