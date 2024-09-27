SELECT 
    Produto,
    Regiao_cliente,
    Canal_venda,
    SUM(Quantidade) AS total_vendas
FROM 
    "NOME_TABELA_SILVER_VENDAS"
GROUP BY 
    Produto, Regiao_cliente, Canal_venda
ORDER BY 
    total_vendas DESC;