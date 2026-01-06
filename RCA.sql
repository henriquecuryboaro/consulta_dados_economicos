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
ORDER BY 2 DESC
