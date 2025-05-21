from flask import Blueprint, request, jsonify
from modules.analysis.lsh_test import test_full_pipeline

lsh_test_bp = Blueprint("cohort", __name__, url_prefix="/python-api/cohort")

@lsh_test_bp.route("/analyze", methods=["POST"])
def analyze_cohort():
    data = request.get_json()
    info_db_no = data.get("info_db_no")
    origin_table = data.get("origin_table")
    file_name = data.get("file_name", "cohort_analysis.csv")

    try:
        url = test_full_pipeline(info_db_no, origin_table, file_name)
        return jsonify({"success": True, "s3_url": url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
