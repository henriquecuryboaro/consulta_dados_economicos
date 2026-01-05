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
ORDER BY Razao_comercial 
