from microservice_template_core import Core
from microservice_template_core.settings import ServiceConfig, FlaskConfig, DbConfig
from harp_bots.endpoints.bots_integrations import ns as bots_integrations
from harp_bots.endpoints.health import ns as health


def main():
    ServiceConfig.configuration['namespaces'] = [bots_integrations, health]
    FlaskConfig.FLASK_DEBUG = False
    DbConfig.USE_DB = True
    app = Core()
    app.run()


if __name__ == '__main__':
    main()

