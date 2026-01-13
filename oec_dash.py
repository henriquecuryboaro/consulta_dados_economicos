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

query_pauta = text("""
SELECT  product_name AS Produto,
		sitc2_code,
		ROUND((SUM(value)*1.0/(SELECT SUM(value) FROM trade_i_oec_a_sitc2 WHERE exporter_name = 'Brazil' GROUP BY exporter_name)),5) AS Participacao_produto
FROM trade_i_oec_a_sitc2
WHERE exporter_name = 'Brazil'
GROUP BY product_name
HAVING Participacao_produto > 0.001
ORDER BY Participacao_produto DESC
""")

query_paises_destino = text("""
SELECT DISTINCT importer_name
FROM trade_i_oec_a_sitc2
WHERE exporter_name = 'Brazil'
GROUP BY importer_name, exporter_name
""")                 

with engine.connect() as conn:
    df, df_importadores = pd.read_sql_query(query_saldo_balanca, conn), pd.read_sql_query(query_importadores, conn)
    df_exportadores, df_pauta, df_destino = pd.read_sql_query(query_exportadores, conn), pd.read_sql_query(query_pauta, conn), pd.read_sql_query(query_paises_destino, conn)
    
df['log_razao'] = np.log10(df['Razao_comercial'])
df_importadores['log_imp'] = np.log10(df_importadores['Total'])
df_exportadores['log_exp'] = np.log10(df_exportadores['Total'])

fig = px.choropleth(
    df,
    locations='codigo_pais',
    locationmode='ISO-3',
    color='Razao_comercial',
    labels={'Razao_comercial': "<b></b>"},
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
    title_x=0,title_y=0.9,
	title=dict(text="Relação entre exportações e importações por país<br><sup>Valor exibido: log(exportações/importações)\n</sup>",
	    font=dict(size=28)),
    margin=dict(t=80),
    width=770,
    height=462
)

fig_imp = px.choropleth(
    df_importadores,
    locations='codigo_pais',
    locationmode='ISO-3',
    color='log_imp',
    labels={'log_imp': "<b></b>"},
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
    title_x=0,title_y=0.9,
		title=dict(text="Maiores importadores de produtos brasileiros<br><sup>Valor exibido: log(exportações)\n</sup>",
	    font=dict(size=28)),
    margin=dict(t=80),
    width=770,
    height=462
)

fig_exp = px.choropleth(
    df_exportadores,
    locations='codigo_pais',
    locationmode='ISO-3',
    color='log_exp',
    labels={'log_exp': "<b></b>"},
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
    title_x=0,title_y=0.9,
		title=dict(text="Maiores exportadores para o Brasil<br><sup>Valor exibido: log(importaçẽs)\n</sup>",
	    font=dict(size=28)),
    margin=dict(t=80),
    width=770,
    height=462
)

fig_tree_pauta = px.treemap(df_pauta, path = ['Produto'], values= 'Participacao_produto', title='Principais produtos exportados pelo Brasil')
fig_tree_pauta.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    },
    title_x=0,title_y=0.9,
		title=dict(text="Principais produtos exportados pelo Brasil<br><sup>Participação do produto na pauta de exportações do Brasil\n</sup>",
	    font=dict(size=28)),
    margin=dict(t=80),
    width=630,
    height=472.5
)

def load_css():
	return """
<style>
	/* Target the inner container created by Streamlit */
	.st-key-container_azul_1 > div,
	.st-key-container_azul_2 > div,
	.st-key-container_azul_3 > div {
		background-color: rgba(173, 216, 230, 0.3);
		border-radius: 10px;
		padding: 20px;
		min-height: 500px;
	}
	</style>
	"""


## Título da página,layout
st.set_page_config(page_title="Dash teste",layout="wide")

def main():
	#Título do dashboard a ser impresso no corpo do documento
	st.write("""
	# Painel de complexidade econômica e trocas comerciais do Brasil
	""")
	st.sidebar.title("Menu de navegação")
	page = st.sidebar.selectbox('Escolha a página',['Visão geral', 'Comparativos'])

	if page == 'Visão geral':
		#Divisão da área do painel em blocos ('containers')
		col1,col2 = st.columns(2)
		con1=col1.container(key="container_azul_1")
		con2=col2.container(key="container_azul_2")

		st.markdown(load_css(), unsafe_allow_html=True)

		#Atribuição de objetos às áreas definidas por 'containers'
		with con1:
			st.plotly_chart(fig_imp)
			st.plotly_chart(fig)

		with con2:
			st.plotly_chart(fig_exp)
			st.plotly_chart(fig_tree_pauta)
	if page == 'Comparativos':
		pais_alvo = st.selectbox('Escolha o país para visualizar dados', df_destino['importer_name'])
		
        #Divisão da área do painel em blocos ('containers')
		col1,col2 = st.columns(2)
		con1=col1.container(key="container_azul_1")
		con2=col2.container(key="container_azul_2")

		st.markdown(load_css(), unsafe_allow_html=True)
		
        		#Atribuição de objetos às áreas definidas por 'containers'
		with con1:
			st.write('**Seção 1**')

		with con2:
			st.write('**Seção 2**')

				
if __name__ == "__main__":
    main()