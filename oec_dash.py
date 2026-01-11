from sqlalchemy import create_engine,text
from pathlib import Path
import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st

#Apontando para base de dados no mesmo diretório do script executado
DB_PATH = Path(__file__).resolve().parent / "complexidade_economica"
engine = create_engine(f"sqlite:///{DB_PATH}")

#queries como string
query_importadores = text("""
SELECT  importer_name,
		UPPER(importer_id) AS codigo_pais,
		SUM(value) AS Total
FROM trade_i_oec_a_sitc2
WHERE exporter_name = 'Brazil'
GROUP BY exporter_name, importer_name
ORDER BY Total DESC
""")

query_exportadores = text("""
SELECT  exporter_name,
		UPPER(exporter_id) AS codigo_pais,
		SUM(value) AS Total
FROM trade_i_oec_a_sitc2
WHERE importer_name = 'Brazil'
GROUP BY exporter_name, importer_name
ORDER BY Total DESC
""")

query_saldo_balanca = text("""
--Questão: qual a razão entre exportações e importações entre o Brasil e os outros países do mundo?
WITH BrasilExportacoes AS (SELECT importer_name AS parceiro, SUM(value) AS total_exportacoes, UPPER(importer_id) AS codigo_parceiro
					 FROM trade_i_oec_a_sitc2
					 WHERE exporter_name = 'Brazil'
					 GROUP BY importer_name),
BrasilImportacoes AS (SELECT exporter_name AS parceiro, SUM(value) AS total_importacoes
					 FROM trade_i_oec_a_sitc2
					 WHERE importer_name = 'Brazil'
					 GROUP BY exporter_name)
SELECT be.parceiro AS Parceiro,
	   be.codigo_parceiro AS codigo_pais,
	   ROUND((be.total_exportacoes)*1.0/(bi.total_importacoes),3) AS Razao_comercial
FROM BrasilExportacoes AS be
JOIN BrasilImportacoes AS bi ON be.parceiro = bi.parceiro
ORDER BY Razao_comercial 
""")

with engine.connect() as conn:
    df = pd.read_sql_query(query_saldo_balanca, conn)
    df_importadores = pd.read_sql_query(query_importadores, conn)
    df_exportadores = pd.read_sql_query(query_exportadores, conn)
    
df['log_razao'] = np.log10(df['Razao_comercial'])
df_importadores['log_imp'] = np.log10(df_importadores['Total'])
df_exportadores['log_exp'] = np.log10(df_exportadores['Total'])

print(df_exportadores)

fig = px.choropleth(
    df,
    locations='codigo_pais',
    locationmode='ISO-3',
    color='Razao_comercial',
    labels={'Razao_comercial': "<b>log(exportações / importações)</b>"},
    hover_name='Parceiro',
    color_continuous_scale='Viridis',
    range_color=(0.1,3),
    title='Parceiros comerciais do Brasil',
    projection='natural earth'
)

fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    },
    title_x=0,title_y=0.99,
    margin=dict(t=80),
    width=700,
    height=420
)

fig_imp = px.choropleth(
    df_importadores,
    locations='codigo_pais',
    locationmode='ISO-3',
    color='log_imp',
    labels={'log_imp': "<b>Exportações de produtos brasileiros (US$)</b>"},
    hover_name='importer_name',
    color_continuous_scale='Viridis',
    range_color=(9,11),
    title='Maiores importadores de produtos brasileiros',
    projection='natural earth'
)

fig_imp.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    },
    title_x=0,title_y=0.99,
    margin=dict(t=80),
    width=700,
    height=420
)

fig_exp = px.choropleth(
    df_exportadores,
    locations='codigo_pais',
    locationmode='ISO-3',
    color='log_exp',
    labels={'log_exp': "<b>Exportadores de produtos para o Brasil(US$)</b>"},
    hover_name='exporter_name',
    color_continuous_scale='Viridis',
    range_color=(6,11),
    title='Maiores exportadores para o Brasil',
    projection='natural earth'
)

fig_exp.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    },
    title_x=0,title_y=0.99,
    margin=dict(t=80),
    width=700,
    height=420
)

#Sessão de dashboard
## Título da página,layout
st.set_page_config(page_title="Dash teste",layout="wide")

#Título do seu dashboard
st.write("""
# Painel de complexidade econômica e trocas comerciais do Brasil
Navegue pelas seções do painel abaixo
""")

st.sidebar.title("Menu")

col1,col2 = st.columns(2)
con1=col1.container(key="container_azul_1")
con2=col2.container(key="container_azul_2")

def load_css():
    return """
  <style>
    /* Target the inner container created by Streamlit */
    .st-key-container_azul_1 > div,
    .st-key-container_azul_2 > div,
    .st-key-container_azul_3 > div {
        background-color: rgba(100, 100, 200, 0.3);
        border-radius: 10px;
        padding: 20px;
        min-height: 500px;
    }
    </style>
    """

st.markdown(load_css(), unsafe_allow_html=True)


with con1:
    st.plotly_chart(fig_imp)
    st.plotly_chart(fig)

with con2:
    st.plotly_chart(fig_exp)
    st.write("**Seção 4**")