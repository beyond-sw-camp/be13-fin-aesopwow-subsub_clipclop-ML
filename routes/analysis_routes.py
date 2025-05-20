from flask import Blueprint, jsonify, Response, request
from botocore.exceptions import NoCredentialsError, ClientError

from modules.analysis.analysis_module import module_get_s3_file

from modules.info_db.info_db_module import get_info_db_by_info_db_no
from modules.analysis.ml_test import test_convert_data

analysis_bp = Blueprint('python-api/analysis', __name__)

# 원본
# @analysis_bp.route('', methods=['GET'])
# def get_s3_file():
#     file_name = request.args.get('file_name', type=str)
#     # file_name = "local_file.txt"
#     bucket_name = "python-aesop"

#     try:
#         s3_object = module_get_s3_file(bucket_name, file_name)
#         return Response(
#             s3_object['Body'].read(),
#             mimetype=s3_object['ContentType'],
#             headers={"Content-Disposition": f"attachment;filename={file_name}"}
#         )
#     except ClientError as e:
#         return jsonify({'error': str(e)}), 404
#     except NoCredentialsError:
#         return jsonify({'error': 'AWS credentials not found.'}), 403

# 개선 코드
# @analysis_bp.route('', methods=['GET'])
# def get_s3_file_from_s3():
#     import csv
#     import io

#     info_db_no = request.args.get('infoDbNo', type=str)

#     # 1️⃣ infoDbNo → 실제 파일명 매핑
#     INFO_DB_FILE_MAP = {
#         "1": "mock_dashboard.csv"
#         # 다른 파일들도 필요 시 추가 가능
#     }

#     file_name = INFO_DB_FILE_MAP.get(info_db_no)
#     if not file_name:
#         return jsonify({'error': f'No file mapped for infoDbNo={info_db_no}'}), 404

#     bucket_name = "python-aesop"

#     try:
#         # 2️⃣ S3에서 객체 가져오기 (Binary Stream)
#         s3_object = module_get_s3_file(bucket_name, file_name)
#         file_content = s3_object['Body'].read().decode('utf-8')

#         # 3️⃣ CSV 파싱
#         csvfile = io.StringIO(file_content)
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             return jsonify({
#                 "labels": row["labels"].split("|"),
#                 "values": list(map(int, row["values"].split("|"))),
#                 "total": int(row["total"]),
#                 "active": int(row["active"]),
#                 "new": int(row["new"]),
#                 "churn": int(row["churn"]),
#                 "dormant": int(row["dormant"])
#             })

#     except ClientError as e:
#         return jsonify({'error': str(e)}), 404
#     except NoCredentialsError:
#         return jsonify({'error': 'AWS credentials not found.'}), 403

# 테스트
@analysis_bp.route('', methods=['GET'])
def get_s3_file():
    import os
    import csv

    info_db_no = request.args.get('infoDbNo', type=str)

    # ✅ 1. 번호에 따라 파일명을 매핑
    INFO_DB_FILE_MAP = {
        "1": "mock_dashboard.csv"
    }

    filename = INFO_DB_FILE_MAP.get(info_db_no)
    if not filename:
        return jsonify({'error': f'No file mapped for infoDbNo={info_db_no}'}), 404

    # ✅ 2. 상대 경로로 파일 찾기
    mock_csv_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'data', filename)

    try:
        with open(mock_csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                return jsonify({
                    "labels": row["labels"].split("|"),
                    "values": list(map(int, row["values"].split("|"))),
                    "total": int(row["total"]),
                    "active": int(row["active"]),
                    "new": int(row["new"]),
                    "churn": int(row["churn"]),
                    "dormant": int(row["dormant"])
                })
    except FileNotFoundError:
        return jsonify({'error': f'File not found: {filename}'}), 404

@analysis_bp.route('', methods=['POST'])
def upload_s3_file():
    info_db_no = request.args.get('info_db_no', type=int)
    analysis_no = request.args.get('analysis_no', type=int)

    info_db = get_info_db_by_info_db_no(info_db_no)

    # upload_file_to_s3("local_file.txt", "python-aesop", "external/local_file.txt")
    file_path = "/Users/songhyeonjun/Desktop/prj_fin/be13-fin-aesopwow-subsub_clipclop-ML/routes/test.csv"
    object_name = None

    if object_name is None:
        object_name = file_path.split("/")[-1]

    try:
        upload_s3_file(file_path, object_name)
        print(f"✅ '{file_path}' has been uploaded.'")
    except FileNotFoundError:
        return jsonify({'error': 'The file was not found.'}), 403
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not available.'}), 403

    return jsonify({"message": "File uploaded successfully!"})

@analysis_bp.route('/test', methods=['GET'])
def test_convert():
    info_db_no = request.args.get('info_db_no', type=int)
    origin_table = request.args.get('origin_table', type=str)

    mapped_row = test_convert_data(info_db_no, origin_table)
    if mapped_row:
        return jsonify(mapped_row)
    else:
        return jsonify({"error": "Mapped row not found"}), 404