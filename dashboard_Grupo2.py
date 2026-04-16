import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

 
# CONFIGURACIÓN INICIAL
 
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

sns.set_theme(style="whitegrid")

 
# CARGA DE DATOS
 
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df['Date'] = pd.to_datetime(df['Date'])

    # Mapear sucursales (UNA SOLA VEZ)
    branch_map = {
        'A': 'A - Yangon',
        'B': 'B - Mandalay',
        'C': 'C - Naypyitaw'
    }
    df['Branch_full'] = df['Branch'].map(branch_map)

    return df

df = load_data()

 
# SIDEBAR (FILTROS)
 
st.sidebar.title(" Dashboard Department Store")
st.sidebar.markdown("### 🔍 Filtros de exploración")

branch = st.sidebar.multiselect(
    "Selecciona sucursal",
    sorted(df['Branch'].unique()),
    default=df['Branch'].unique()
)

product = st.sidebar.multiselect(
    "Selecciona línea de producto",
    sorted(df['Product line'].unique()),
    default=df['Product line'].unique()
)

customer = st.sidebar.multiselect(
    "Selecciona tipo de cliente",
    sorted(df['Customer type'].unique()),
    default=df['Customer type'].unique()
)

# Filtro de fecha (PRO)
date_range = st.sidebar.date_input(
    "Rango de fechas",
    [df['Date'].min(), df['Date'].max()]
)

 
# FILTRADO
 
df_filtered = df[
    (df['Branch'].isin(branch)) &
    (df['Product line'].isin(product)) &
    (df['Customer type'].isin(customer)) &
    (df['Date'].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

 
# TÍTULO
#
st.title(" Dashboard de Ventas - Supermarket Sales")
st.markdown("Explora el comportamiento de las ventas, productos y clientes mediante visualizaciones interactivas.")


# MÉTRICAS

col1, col2, col3 = st.columns(3)

col1.metric("💰 Ventas Totales", f"${df_filtered['Total'].sum():,.0f}")
col2.metric("📦 Transacciones", f"{len(df_filtered):,}")
col3.metric("⭐ Rating Promedio", f"{df_filtered['Rating'].mean():.2f}")


# ANÁLISIS TEMPORAL

st.markdown("## 📈 Análisis Temporal")

df_time = df_filtered.groupby('Date')['Total'].sum().reset_index()

fig1, ax1 = plt.subplots(figsize=(12,5))

sns.lineplot(
    data=df_time,
    x='Date',
    y='Total',
    marker='o',
    color="#279B0A",
    linewidth=2.5,
    ax=ax1
)

ax1.fill_between(
    df_time['Date'],
    df_time['Total'],
    color="#1F88D3",
    alpha=0.3
)

ax1.set_title("Evolución de las ventas totales en el tiempo", fontsize=14, weight='bold')
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Ventas totales")

plt.setp(ax1.get_xticklabels(), rotation=45)
sns.despine()

fig1.tight_layout()
st.pyplot(fig1)


# ANÁLISIS DE PRODUCTOS

st.markdown("## 📦 Análisis de Productos")

colA, colB = st.columns(2)


with colA:
    df_prod = df_filtered.groupby('Product line')['Total'].sum().reset_index()
    df_prod = df_prod.sort_values(by='Total', ascending=False)

    fig2, ax2 = plt.subplots(figsize=(8,5))
    palette = sns.color_palette("crest", len(df_prod))

    sns.barplot(
        data=df_prod,
        x='Total',
        y='Product line',
        hue='Product line',
        palette=palette,
        legend=False,
        ax=ax2
    )

    ax2.set_title("Ventas por línea de producto", fontsize=13, weight='bold')
    ax2.set_xlabel("Ventas")
    ax2.set_ylabel("")

    for i, value in enumerate(df_prod['Total']):
        ax2.text(value, i, f' {value:.0f}', va='center')

    sns.despine()
    fig2.tight_layout()
    st.pyplot(fig2)


with colB:
    df_group = df_filtered.groupby('Product line')['Total'].sum()
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(df_group)))

    fig6, ax6 = plt.subplots()

    wedges, texts, autotexts = ax6.pie(
        df_group,
        labels=df_group.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        wedgeprops={'edgecolor': 'white'}
    )

    centre_circle = plt.Circle((0,0), 0.40, fc='white')
    ax6.add_artist(centre_circle)

    ax6.set_title("Participación de ventas", fontsize=13, weight='bold')
    ax6.set_aspect('equal')

    st.pyplot(fig6)

 
# 🏬 ANÁLISIS POR SUCURSAL
 
st.markdown("##  Análisis por Sucursal")

 
df_grouped = df_filtered.groupby(['Branch_full', 'Product line'])['Total'].sum().reset_index()

order = df_filtered.groupby('Branch')['Total'].sum().sort_values(ascending=False).index
branch_map = {'A': 'A - Yangon', 'B': 'B - Mandalay', 'C': 'C - Naypyitaw'}
order = [branch_map[o] for o in order]

fig3, ax3 = plt.subplots(figsize=(12,6))

sns.barplot(
    data=df_grouped,
    x='Branch_full',
    y='Total',
    hue='Product line',
    order=order,
    palette='viridis',
    ax=ax3
)

for container in ax3.containers:
    ax3.bar_label(container, fmt='%.0f', padding=2)

ax3.set_title("Rendimiento por sucursal y producto")
ax3.legend(bbox_to_anchor=(1.02, 1), loc='upper left')

fig3.tight_layout()
st.pyplot(fig3)

 
fig4, ax4 = plt.subplots(figsize=(10,5))

sns.countplot(
    data=df_filtered,
    x='Payment',
    hue='Branch_full',
    palette='viridis',
    ax=ax4
)

ax4.set_title("Preferencias de pago por sucursal")
ax4.legend(bbox_to_anchor=(1.02, 1), loc='upper left')

sns.despine()
fig4.tight_layout()
st.pyplot(fig4)


# 👥 ANÁLISIS DE CLIENTES

st.markdown("## 👥 Análisis de Clientes")

fig5, ax5 = plt.subplots(figsize=(8,5))

palette = {
    'Normal': '#4C72B0',
    'Member': '#55A868'
}

sns.boxplot(
    data=df_filtered,
    x='Customer type',
    y='Total',
    order=['Normal', 'Member'],
    hue='Customer type',
    palette=palette,
    legend=False,
    ax=ax5
)

ax5.set_title("Distribución de ventas por tipo de cliente")

sns.despine()
fig5.tight_layout()

st.pyplot(fig5)

# REFLEXIÓN

st.markdown("##  Reflexión sobre interactividad")

st.markdown("""
El dashboard incorpora filtros interactivos por sucursal, línea de producto, tipo de cliente y rango de fechas.

Estos elementos permiten segmentar dinámicamente la información, facilitando la comparación entre distintas dimensiones del negocio y la identificación de patrones específicos.

El uso de filtros múltiples permite analizar combinaciones de variables, mientras que el control temporal permite observar la evolución de los datos en distintos periodos.

En conjunto, estas herramientas transforman el dashboard en un sistema exploratorio, mejorando significativamente la comprensión de los datos frente a visualizaciones estáticas.
""") 
