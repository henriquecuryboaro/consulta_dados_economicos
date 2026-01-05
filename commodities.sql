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