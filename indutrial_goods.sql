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
	   ROUND(i.indust_export*1.0/t.total_export,3) AS "Particip. commodities",
	   ROUND(mi."Median (2021 prices)",2) AS "Mediana da renda"
FROM Industrial AS i
JOIN TodasExportacoes AS t ON i.exporter_name = t.exporter_name
JOIN MedianIncome AS mi ON i.exporter_name = mi.Entity
GROUP BY 1
ORDER BY 2 DESC