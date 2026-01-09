from sqlalchemy import create_engine,text
from pathlib import Path
import pandas as pd

#Apontando para base de dados no mesmo diretório do script executado
DB_PATH = Path(__file__).resolve().parent / "complexidade_economica"
engine = create_engine(f"sqlite:///{DB_PATH}")

#queries como string
query_RCA = text("""
WITH CountryProduct AS (SELECT exporter_name, 
			  SUM(value) AS cnt_prod_export
			  FROM trade_i_oec_a_sitc2
			  WHERE sitc2_code = 107423 --Rotary pumps
			  GROUP BY exporter_name, sitc2_code),
CountryExport AS (SELECT exporter_name, 
			  SUM(value) AS total_country_export
			  FROM trade_i_oec_a_sitc2
			  GROUP BY exporter_name),
MedianIncome AS (SELECT * FROM daily_median_income WHERE "Year" = 2018)
SELECT cp.exporter_name AS País,
	   ROUND((((cp.cnt_prod_export)*1.0/(ce.total_country_export))/
	   ((SELECT SUM(value) FROM trade_i_oec_a_sitc2 WHERE sitc2_code = 311121 GROUP BY sitc2_code)*1.0/(SELECT SUM(value) FROM trade_i_oec_a_sitc2))),3)  AS RCA,
	   ROUND(mi."Median (2021 prices)",2) AS "Mediana da renda"
FROM CountryProduct AS cp
JOIN CountryExport AS ce ON cp.exporter_name = ce.exporter_name
JOIN MedianIncome AS mi ON cp.exporter_name = mi.Entity
GROUP BY 1
ORDER BY 2 DESC;
""")

query_saldo_balanca = text("""
--Questão: qual a razão entre exportações e importações entre o Brasil e os outros países do mundo?
WITH BrasilExportacoes AS (SELECT importer_name AS parceiro, SUM(value) AS total_exportacoes
					 FROM trade_i_oec_a_sitc2
					 WHERE exporter_name = 'Brazil'
					 GROUP BY importer_name),
BrasilImportacoes AS (SELECT exporter_name AS parceiro, SUM(value) AS total_importacoes
					 FROM trade_i_oec_a_sitc2
					 WHERE importer_name = 'Brazil'
					 GROUP BY exporter_name)
SELECT be.parceiro AS Parceiro, 
	   ROUND((be.total_exportacoes)*1.0/(bi.total_importacoes),3) AS Razao_comercial
FROM BrasilExportacoes AS be
JOIN BrasilImportacoes AS bi ON be.parceiro = bi.parceiro
ORDER BY Razao_comercial;
""")

query_commodities = text("""
--Questão: existe correlação entre a razão de commodities na pauta de exportações de um país e a renda deste país?
WITH Commoditties AS (SELECT exporter_name, 
			  SUM(value) AS commod_export
			  FROM trade_i_oec_a_sitc2
			  WHERE sitc2_code LIKE '7%' OR sitc2_code LIKE '8%'
			  GROUP BY exporter_name),
TodasExportacoes AS (SELECT exporter_name, 
			  SUM(value) AS total_export
			  FROM trade_i_oec_a_sitc2
			  GROUP BY exporter_name),
MedianIncome AS (SELECT * FROM daily_median_income WHERE "Year" = 2018)
SELECT c.exporter_name AS País,
	   ROUND(c.commod_export*1.0/t.total_export,3) AS "Particip. commodities",
	   ROUND(mi."Median (2021 prices)",2) AS "Mediana da renda"
FROM Commoditties AS c
JOIN TodasExportacoes AS t ON c.exporter_name = t.exporter_name
JOIN MedianIncome AS mi ON c.exporter_name = mi.Entity
GROUP BY 1
ORDER BY 2 DESC
""")

query_industrial = text("""
--Questão: existe correlação entre a razão de bens industrializados na pauta de exportações de um país e a renda deste país?
WITH Industrial AS (SELECT exporter_name, 
			  SUM(value) AS indust_export
			  FROM trade_i_oec_a_sitc2
			  WHERE sitc2_code LIKE '1%' OR sitc2_code LIKE '2%' OR sitc2_code LIKE '4%'
			  GROUP BY exporter_name),
TodasExportacoes AS (SELECT exporter_name, 
			  SUM(value) AS total_export
			  FROM trade_i_oec_a_sitc2
			  GROUP BY exporter_name),
MedianIncome AS (SELECT * FROM daily_median_income WHERE "Year" = 2018)
SELECT i.exporter_name AS País,
	   ROUND(i.indust_export*1.0/t.total_export,3) AS "Particip. industrial",
	   ROUND(mi."Median (2021 prices)",2) AS "Mediana da renda"
FROM Industrial AS i
JOIN TodasExportacoes AS t ON i.exporter_name = t.exporter_name
JOIN MedianIncome AS mi ON i.exporter_name = mi.Entity
GROUP BY 1
ORDER BY 2 DESC
""")

with engine.connect() as conn:
    df = pd.read_sql_query(query_commodities, conn)
print(df)