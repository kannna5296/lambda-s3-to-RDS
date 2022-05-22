import sys
import logging
import rds_config
import s3_config
import pymysql
import boto3
import io
import csv
import datetime
#log settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#rds settings
rds_host  = rds_config.db_host
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

#rds connection get(from https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/services-rds-tutorial.html)
try:
    conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

#s3 setting
s3 = boto3.resource('s3')
bucket_name = s3_config.bucket_name
object_key_name = s3_config.object_key_name
src_file_encoding=s3_config.src_file_encoding

#Lambda Handler
def handler(event, context):
    """
    S3取得
    """
    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(object_key_name)
    response = obj.get()    
    body = response['Body'].read().decode(src_file_encoding)

    st = io.StringIO()
    st.write(body)
    st.seek(0)

    csv_f =csv.reader(st)

    """
    S3データをクラスに置き換え
    """
    taskDatas=[] #空List
    rowNumber = -1 #Csv行数カウント（もうちょいうまいロジックあるやろ...）
    for row in csv_f: #rowはList
        rowNumber += 1
        if(rowNumber == 0):
            continue #最初の行はスキップ
        #クラス化
        taskDatas.append(TaskCsvModel(row[0], row[1]))
    #csv行数確認
    logger.info(rowNumber)


    """
    This function fetches content from MySQL RDS instance
    """
    item_count = 0

    dt_now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    with conn.cursor() as cur:
        #TODO taskテーブルとの整合性は後(task_idは仮)
        #TODO TaskCsvModel.nameを元にはユーザの存在確認(user_idは仮)
        #TODO BULK_INSERT
        #TODO トランザクション周り
        for taskData in taskDatas:
            sql = 'insert into task_detail (task_id, user_id, content, created_at) values (1, 1, "' + taskData.content + '","'+ dt_now + '")'
            cur.execute(sql)
        conn.commit()
    conn.commit()

    return "Added %d items from RDS MySQL table" %(item_count)

#csvデータクラス
class TaskCsvModel:
    def __init__(self, name, content):
        self.name = name
        self.content = content