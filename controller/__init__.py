import controller.recruiter as rec
import controller.commander as com
import controller.leader as lea
from flask import Flask


class Recruiter:
    @staticmethod
    def set_model(model):
        rec.recruiter = model

    @staticmethod
    def generate_server(url_prefix):
        server = Flask(__name__)
        server.register_blueprint(rec.server, url_prefix=url_prefix)
        return server


class Commander:
    @staticmethod
    def set_model(model):
        com.commander = model

    @staticmethod
    def generate_server(url_prefix):
        server = Flask(__name__)
        server.register_blueprint(com.server, url_prefix=url_prefix)
        return server


class Leader:
    @staticmethod
    def set_model(model):
        lea.leader = model

    @staticmethod
    def generate_server(url_prefix):
        server = Flask(__name__)
        server.register_blueprint(lea.server, url_prefix=url_prefix)
        return server
