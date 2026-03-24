import yaml
from pyspark.sql import SparkSession
from etl.clean.enrollment_clean import clean_admission_data
from etl.transform.heat_calc import calculate_heat
from etl.loader.hive_loader import load_to_hive
from etl.loader.mysql_loader import load_to_mysql
import logging

# 加载配置
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 初始化Spark
spark = SparkSession.builder \
    .appName(config['spark']['app_name']) \
    .master(config['spark']['master']) \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.executor.memory", config['spark']['executor_memory']) \
    .enableHiveSupport() \
    .getOrCreate()

# 配置日志（记录到MySQL）
def log_etl_status(job_name, status, message=''):
    # 将日志写入MySQL的 sys_etl_log 表
    pass

try:
    # 1. 读取原始数据
    raw_df = spark.read.json(config['etl']['input_path'] + '/*.jl')
    
    # 2. 清洗录取数据
    clean_admission_df = clean_admission_data(raw_df)
    
    # 3. 计算热度指标
    heat_df = calculate_heat(clean_admission_df)
    
    # 4. 加载到Hive（ODS层）
    load_to_hive(clean_admission_df, 'ods_admission_record', config)
    
    # 5. 加载到MySQL（业务库）
    load_to_mysql(heat_df, 'ana_school_heat', config)
    
    log_etl_status('full_etl', 'SUCCESS')
except Exception as e:
    log_etl_status('full_etl', 'FAILED', str(e))
    raise