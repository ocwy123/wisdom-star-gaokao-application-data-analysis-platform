from pyspark.sql import functions as F
from pyspark.sql.types import *

def clean_admission_data(df):
    # 假设原始数据字段：school_id, major_id, province, year, min_score, min_rank ...
    # 进行数据类型转换、缺失值处理、省份名称统一等
    cleaned = df.select(
        F.col('school_id').cast(IntegerType()),
        F.col('major_id').cast(IntegerType()),
        F.when(F.col('province').isin(['北京', '北京市']), '北京市')
         .otherwise(F.col('province')).alias('province'),
        F.col('year').cast(IntegerType()),
        F.col('min_score').cast(IntegerType()),
        F.col('min_rank').cast(IntegerType()),
        F.current_timestamp().alias('created_at')
    ).dropDuplicates(['school_id', 'major_id', 'province', 'year'])
    return cleaned