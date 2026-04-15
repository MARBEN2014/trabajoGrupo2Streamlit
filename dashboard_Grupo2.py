import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==============================
# CONFIGURACIÓN
# ==============================
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
sns.set_theme(style="whitegrid")

# ==============================
# CARGA DE DATOS
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    branch_map = {
        'A': 'A - Yangon',
        'B': 'B - Mandalay',
        'C': 'C - Naypyitaw'
    }
    df['Branch_full'] = df['Branch'].map(branch_map)

    return df

df = load_data()

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("📊 Dashboard Supermarket Sales")

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

date_range = st.sidebar.date_input(
    "Rango de fechas",
    [df['Date'].min(), df['Date'].max()]
)

# ==============================
# FILTRO
# ==============================
df_filtered = df[
    (df['Branch'].isin(branch)) &
    (df['Product line'].isin(product)) &
    (df['Customer type'].isin(customer)) &
    (df['Date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# ==============================
# TÍTULO
# ==============================
st.title("📊 Dashboard de Ventas")

# ==============================
# MÉTRICAS
# ==============================
col1, col2, col3 = st.columns(3)

col1.metric("💰 Ventas Totales", f"${df_filtered['Total'].sum():,.0f}")
col2.metric("📦 Transacciones", f"{len(df_filtered):,}")
col3.metric("⭐ Rating", f"{df_filtered['Rating'].mean():.2f}")

# =========================================================
# 📈 1. ANÁLISIS TEMPORAL (SOLO)
# =========================================================
st.markdown("## 📈 Evolución de ventas")

df_time = df_filtered.groupby('Date')['Total'].sum().reset_index()

fig1, ax1 = plt.subplots(figsize=(12,5))

sns.lineplot(
    data=df_time,
    x='Date',
    y='Total',
    marker='o',
    color="#1F77B4",
    linewidth=2.5,
    ax=ax1
)

ax1.fill_between(
    df_time['Date'],
    df_time['Total'],
    color="#1F77B4",
    alpha=0.2
)

ax1.set_title("Ventas en el tiempo", weight='bold')
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Ventas")

plt.setp(ax1.get_xticklabels(), rotation=45)
sns.despine()

fig1.tight_layout()
st.pyplot(fig1)

# =========================================================
# 📊 2. GRID 2x2 GRÁFICOS
# =========================================================
st.markdown("## 📊 Análisis General")

colA, colB = st.columns(2)

# ------------------------------
# BARPLOT PRODUCTOS
# ------------------------------
with colA:
    df_prod = df_filtered.groupby('Product line')['Total'].sum().reset_index()
    df_prod = df_prod.sort_values('Total', ascending=False)

    fig2, ax2 = plt.subplots(figsize=(7,4))
    palette = sns.color_palette("crest", len(df_prod))

    sns.barplot(
        data=df_prod,
        x='Total',
        y='Product line',
        palette=palette,
        ax=ax2
    )

    for i, v in enumerate(df_prod['Total']):
        ax2.text(v, i, f'{v:.0f}', va='center')

    ax2.set_title("Ventas por producto")
    ax2.set_xlabel("")
    ax2.set_ylabel("")
    sns.despine()

    st.pyplot(fig2)

# ------------------------------
# DONUT CORREGIDO
# ------------------------------
with colB:
    df_group = df_filtered.groupby('Product line')['Total'].sum()

    fig3, ax3 = plt.subplots()

    colors = sns.color_palette("viridis", len(df_group))

    wedges, texts, autotexts = ax3.pie(
        df_group,
        labels=df_group.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        textprops={'fontsize': 9}
    )

    centre_circle = plt.Circle((0,0),0.40,fc='white')
    ax3.add_artist(centre_circle)

    ax3.set_title("Participación de ventas")
    ax3.axis('equal')

    st.pyplot(fig3)

# =========================================================
# 🏬 3. SUCURSALES + PAGOS (2x2)
# =========================================================
st.markdown("## 🏬 Sucursales y Clientes")

colC, colD = st.columns(2)

# ------------------------------
# SUCURSALES
# ------------------------------
with colC:
    df_branch = df_filtered.groupby('Branch_full')['Total'].sum().reset_index()

    fig4, ax4 = plt.subplots(figsize=(7,4))

    sns.barplot(
        data=df_branch,
        x='Branch_full',
        y='Total',
        palette='viridis',
        ax=ax4
    )

    for i, v in enumerate(df_branch['Total']):
        ax4.text(i, v, f'{v:.0f}', ha='center')

    ax4.set_title("Ventas por sucursal")
    sns.despine()

    st.pyplot(fig4)

# ------------------------------
# PAGOS
# ------------------------------
with colD:
    fig5, ax5 = plt.subplots(figsize=(7,4))

    sns.countplot(
        data=df_filtered,
        x='Payment',
        hue='Branch_full',
        palette='viridis',
        ax=ax5
    )

    ax5.set_title("Métodos de pago")
    ax5.legend(bbox_to_anchor=(1.02,1), loc='upper left')

    sns.despine()

    st.pyplot(fig5)

# =========================================================
# 👥 4. BOXPLOT FINAL
# =========================================================
st.markdown("## 👥 Distribución de clientes")

fig6, ax6 = plt.subplots(figsize=(8,4))

sns.boxplot(
    data=df_filtered,
    x='Customer type',
    y='Total',
    hue='Customer type',
    palette={'Normal':'#4C72B0','Member':'#55A868'},
    legend=False,
    ax=ax6
)

ax6.set_title("Ventas por tipo de cliente")

sns.despine()
fig6.tight_layout()

st.pyplot(fig6)
