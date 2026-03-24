# 计算近5年录取位次趋势，生成宽表供机器学习使用
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("TrendAnalysis").enableHiveSupport().getOrCreate()

# 读取Hive表
df = spark.table("gkzy_hive.ods_admission_record")

windowSpec = Window.partitionBy("school_id", "major_id").orderBy("year")
trend_df = df.withColumn("prev_rank", F.lag("min_rank", 1).over(windowSpec)) \
             .withColumn("rank_change", F.col("min_rank") - F.col("prev_rank")) \
             .groupBy("school_id", "major_id") \
             .agg(F.avg("rank_change").alias("avg_rank_change"),
                  F.stddev("min_rank").alias("rank_stddev"))

# 结果存入MySQL或Hive
trend_df.write.format("jdbc").options(...).save()