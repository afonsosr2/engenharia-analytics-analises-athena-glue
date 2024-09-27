SELECT 
    v.produto,
    rs.Avaliacao,
    SUM(v.Quantidade) AS total_vendas
FROM 
    "NOME_TABELA_SILVER_REDES_SOCIAIS" rs
JOIN 
    "NOME_TABELA_SILVER_VENDAS" v ON rs.Nome_produto = v.Produto
GROUP BY 
    v.produto, rs.Avaliacao
ORDER BY 
    rs.Avaliacao DESC;