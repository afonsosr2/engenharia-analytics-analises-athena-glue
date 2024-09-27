SELECT 
    Produto,
    SUM(Quantidade_vendida) AS total_vendida,
    (SUM(Quantidade_em_estoque) - SUM(Quantidade_vendida)) AS estoque_restante
FROM 
    "NOME_TABELA_SILVER_ESTOQUES"
GROUP BY 
    Produto
ORDER BY 
    estoque_restante ASC;