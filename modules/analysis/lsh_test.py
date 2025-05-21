import io
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select

from modules.info_db.info_db_module import get_info_db_by_info_db_no
from modules.info_column.info_column_module import get_info_columns_by_info_db_no_origin_table
from modules.common.s3_client import get_s3_client, bucket_name
from resources.config.s3_config import S3_Config


def upload_to_s3(file_content, file_name):
    s3 = get_s3_client()
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
    return f"https://{bucket_name}.s3.{S3_Config.region_name}.amazonaws.com/{file_name}"


def perform_cohort_analysis(df):
    df['users_last_login'] = pd.to_datetime(df['users_last_login'])
    df['cohort_month'] = df['users_last_login'].dt.to_period('M')
    df['login_month'] = df['users_last_login'].dt.to_period('M')

    cohort_data = df.groupby(['cohort_month', 'login_month'])['users_user_id'].nunique().unstack(0).fillna(0)

    return cohort_data


def test_full_pipeline(info_db_no, origin_table, file_name="cohort_analysis.csv"):
    info_db = get_info_db_by_info_db_no(info_db_no).to_dict()
    engine = create_engine(
        f"mysql+pymysql://{info_db['user']}:{info_db['password']}@{info_db['host']}:{info_db['port']}/{info_db['name']}"
    )

    info_columns = get_info_columns_by_info_db_no_origin_table(info_db_no, origin_table)
    mapped_columns = {col.origin_column: col.analysis_column for col in info_columns}

    metadata = MetaData()
    external_table = Table(origin_table, metadata, autoload_with=engine)

    with engine.connect() as conn:
        query = select(external_table)
        result = conn.execute(query).mappings().all()
        mapped_result = [
            {mapped_columns.get(k, k): v for k, v in row.items()}
            for row in result
        ]

    df = pd.DataFrame(mapped_result)

    cohort_table = perform_cohort_analysis(df)

    csv_buffer = io.StringIO()
    cohort_table.to_csv(csv_buffer)

    s3_url = upload_to_s3(csv_buffer.getvalue(), file_name)

    print(f"S3 업로드 완료: {s3_url}")
    return s3_url