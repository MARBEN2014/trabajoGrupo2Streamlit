import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# CONFIGURACIÓN INICIAL
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# CARGA DE DATOS
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# SIDEBAR (FILTROS)
st.sidebar.header("Dashboard Supermarket Sales")

st.sidebar.subheader("Filtros")

branch = st.sidebar.multiselect(
    "Sucursal",
    df['Branch'].unique(),
    default=df['Branch'].unique()
)

product = st.sidebar.multiselect(
    "Línea de producto",
    df['Product line'].unique(),
    default=df['Product line'].unique()
)

customer = st.sidebar.multiselect(
    "Tipo de cliente",
    df['Customer type'].unique(),
    default=df['Customer type'].unique()
)

payment = st.sidebar.multiselect(
    "Medio de pago",
    df['Payment'].unique(),
    default=df['Payment'].unique()
)

# FILTRADO
df_filtered = df[
    (df['Branch'].isin(branch)) &
    (df['Product line'].isin(product)) &
    (df['Customer type'].isin(customer)) &
    (df['Payment'].isin(payment))
]

# MÉTRICAS
st.markdown("## 📊 Métricas Generales")

col1, col2, col3 = st.columns(3)

col1.metric("Ventas Totales", f"${df_filtered['Total'].sum():,.0f}")
col2.metric("Cantidad Promedio", f"{df_filtered['Quantity'].mean():.2f}")
col3.metric("Rating Promedio", f"{df_filtered['Rating'].mean():.2f}")

# ======================================================
# GRÁFICO 1: SERIES TEMPORALES
# ======================================================
st.markdown("### 📈 Evolución de ventas en el tiempo")

df_time = df_filtered.groupby('Date')['Total'].sum().reset_index()

fig1, ax1 = plt.subplots(figsize=(10,4))
sns.lineplot(data=df_time, x='Date', y='Total', ax=ax1)
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Ventas")
fig1.autofmt_xdate()
st.pyplot(fig1)

# ======================================================
# GRÁFICO 2: BARPLOT PRODUCTOS
# ======================================================
st.markdown("### 📊 Ventas por línea de producto")

df_prod = df_filtered.groupby('Product line')['Total'].sum().reset_index()

fig2, ax2 = plt.subplots(figsize=(10,4))
sns.barplot(data=df_prod, x='Product line', y='Total', palette='viridis', ax=ax2)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=30)
st.pyplot(fig2)

# ======================================================
# GRÁFICO 3: SCATTER
# ======================================================
st.markdown("### 🔍 Relación Precio vs Ventas")

fig3, ax3 = plt.subplots(figsize=(10,4))
sns.scatterplot(
    data=df_filtered,
    x='Unit price',
    y='Total',
    hue='Product line',
    palette='viridis',
    alpha=0.6,
    ax=ax3
)
ax3.legend(bbox_to_anchor=(1.05, 1))
st.pyplot(fig3)

# ======================================================
# GRÁFICO 4: HISTOGRAMA
# ======================================================
st.markdown("### 📉 Distribución de ventas")

fig4, ax4 = plt.subplots(figsize=(10,4))
sns.histplot(df_filtered['Total'], kde=True, color='steelblue', ax=ax4)
st.pyplot(fig4)

# ======================================================
# GRÁFICO 5: DONUT (TU MEJOR GRÁFICO)
# ======================================================
st.markdown("### 🥧 Participación de ventas por línea de producto")

df_group = df_filtered.groupby('Product line')['Total'].sum()

colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(df_group)))

fig5, ax5 = plt.subplots()

wedges, texts, autotexts = ax5.pie(
    df_group,
    labels=df_group.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    wedgeprops={'edgecolor': 'white'}
)

centre_circle = plt.Circle((0,0), 0.55, fc='white')
ax5.add_artist(centre_circle)

ax5.set_aspect('equal')
st.pyplot(fig5)

# ======================================================
# REFLEXIÓN (IMPORTANTE PARA LA NOTA)
# ======================================================
st.markdown("## 🧠 Reflexión sobre interactividad")

st.markdown("""
Se incorporaron filtros interactivos en el panel lateral (sucursal, línea de producto, tipo de cliente y medio de pago), permitiendo al usuario explorar los datos de forma dinámica.

Estos filtros mejoran la visualización porque:

- Permiten analizar subconjuntos específicos del dataset.
- Facilitan la comparación entre categorías.
- Hacen el dashboard más flexible e intuitivo.
- Transforman gráficos estáticos en herramientas exploratorias.

Esto aporta valor al análisis al permitir una exploración más profunda y personalizada de los datos.
""")