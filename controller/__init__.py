from flask import Flask


class RecruiterServer:
    @staticmethod
    def set_model(model):
        import controller.recruiter as rec
        rec.recruiter = model

    @staticmethod
    def generate_server(url_prefix):
        import controller.recruiter as rec
        server = Flask(__name__)
        server.register_blueprint(rec.server, url_prefix=url_prefix)
        return server


class CommanderServer:
    @staticmethod
    def set_model(model):
        import controller.commander as com
        com.commander = model

    @staticmethod
    def generate_server(url_prefix):
        import controller.commander as com
        server = Flask(__name__)
        server.register_blueprint(com.server, url_prefix=url_prefix)
        return server


class LeaderServer:
    @staticmethod
    def set_model(model):
        import controller.leader as lea
        lea.leader = model

    @staticmethod
    def generate_server(url_prefix):
        import controller.leader as lea
        server = Flask(__name__)
        server.register_blueprint(lea.server, url_prefix=url_prefix)
        return server
