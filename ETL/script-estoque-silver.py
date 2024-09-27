import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Gerando um DynamicFrame a partir de uma tabela no Data Catalog
estoques_zoop_dyf = glueContext.create_dynamic_frame.from_catalog(database='NOME_DATABASE', table_name='NOME_TABELA_BRONZE')

# Convertendo o DynamicFrame em um DataFrame Spark
estoques_zoop_df = estoques_zoop_dyf.toDF()

## Tratando os textos da coluna produto
# Importando a função sql do Pyspark regexp_replace para troca de expressões
from pyspark.sql.functions import regexp_replace

# Trocando "_" por " " entre os nomes dos produtos
estoques_zoop_df = estoques_zoop_df.withColumn("Produto", regexp_replace("Produto", "_", " "))

### Ajustando datas

# Importando funções sql do Spark para passar nomes das colunas e formatar data  
from pyspark.sql.functions import col, to_date

# Transformar a coluna Data realmente em uma data válida
estoques_zoop_df = estoques_zoop_df.withColumn("Data", to_date(col("Data"), "yyyy/MM/dd"))

### Convertendo o DataFrame Spark em DynamicFrame e mapeando os tipos dos dados

# Importando a função que gera um DynamicFrame
from awsglue.dynamicframe import DynamicFrame

# Converter o DataFrame Spark em DynamicFrame
estoques_zoop_dyf = DynamicFrame.fromDF(estoques_zoop_df, glueContext, "glue_etl")

# Mapeando as colunas do DynamicFrame
estoques_zoop_dyf_mapeado = estoques_zoop_dyf.apply_mapping(
    mappings=[
        ("ID_estoque", "long", "id_estoque", "long"),
        ("ID_produto", "long", "id_produto", "long"),
        ("Produto", "string", "produto", "string"),
        ("Categoria_produto", "string", "categoria_produto", "string"),
        ("Data", "date", "data", "date"),
        ("Horario", "string", "horario", "timestamp"),
        ("Quantidade_em_estoque", "long", "quantidade_em_estoque", "int"),
        ("Quantidade_novos_produtos", "long", "quantidade_novos_produtos", "int"),
        ("Quantidade_vendida", "long", "quantidade_vendida", "int")
    ]
)

# Configurando o glueContext sink para escrever nova tabela
s3output = glueContext.getSink(
  path="s3://NOME_BUCKET/silver/NOME_TABELA_SEPARADA/",
  connection_type="s3",
  updateBehavior="UPDATE_IN_DATABASE",
  partitionKeys=[],
  compression="snappy",
  enableUpdateCatalog=True,
  transformation_ctx="s3output",
)

# Escreendo a tabela no Glue Data Catalog
s3output.setCatalogInfo(
  catalogDatabase="NOME_DATABASE", catalogTableName="NOME_TABELA_SILVER"
)
s3output.setFormat("glueparquet")
s3output.writeFrame(estoques_zoop_dyf_mapeado)

job.commit()