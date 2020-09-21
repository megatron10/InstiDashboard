# gevent.monkey should be done as early as possible
from app import create_app  # this imports app
from logging.handlers import RotatingFileHandler
from gevent import pywsgi
import logging
import os
from gevent import monkey
monkey.patch_all()


# create a file handler to store weblogs
os.makedirs("tmp", exist_ok=True)
handler = RotatingFileHandler(
    "tmp/tmp.log", maxBytes=1000000000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s {%(pathname)s:%(lineno)d} - %(message)s"
)
handler.setFormatter(formatter)

app = create_app()
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

# run the application
server = pywsgi.WSGIServer(("localhost", 36227), app)
app.logger.info("Serving at %s", "http://localhost:36227")
server.serve_forever()
