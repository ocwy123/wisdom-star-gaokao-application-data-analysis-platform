from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
<<<<<<< HEAD

db = SQLAlchemy()
cors = CORS()
=======
from flask_caching import Cache

db = SQLAlchemy()
cors = CORS()
cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862
