from flask import Flask

# 이건 테스트 용입니다. 나중에 삭제해주세요.
from modules.analysis.lsh_test_service import lsh_test_bp
# from resources.config.internal_db_config import Config
from resources.config.internal_local_db_config import Config
from models import db
from routes.dash_board_routes import dashboard_bp
from routes.info_db_routes import info_db_bp
from routes.info_column_routes import info_column_bp
from routes.analysis_routes import analysis_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# 블루프린트 등록
app.register_blueprint(info_db_bp, url_prefix='/python-api/info_db')
app.register_blueprint(info_column_bp, url_prefix='/python-api/info_column')
app.register_blueprint(analysis_bp, url_prefix='/python-api/analysis')

app.register_blueprint(dashboard_bp, url_prefix='/python-api/dashboard')

app.register_blueprint(lsh_test_bp)

if __name__ == '__main__':
    app.run(debug=True)