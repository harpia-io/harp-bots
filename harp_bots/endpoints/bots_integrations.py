from microservice_template_core.tools.flask_restplus import api
from flask_restx import Resource
import traceback
from microservice_template_core.tools.logger import get_logger
from harp_bots.models.bots_integrations import Bots, BotsSchema
from flask import request
from werkzeug.exceptions import BadRequest
from microservice_template_core.decorators.auth_decorator import token_required
import uuid

logger = get_logger()
ns = api.namespace('api/v1/bots', description='Harp All Bots endpoints')
bots = BotsSchema()


@ns.route('')
class CreateBot(Resource):
    @staticmethod
    @api.response(200, 'Bot has been created')
    @api.response(400, 'Bot already exist')
    @api.response(500, 'Unexpected error on backend side')
    # @token_required()
    def put():
        """
        Create New Bot directly via API
        Use this method to create New Bot directly via API
        * Send a JSON object
        ```
            {
                "bot_name": "Voice",
                "status": "pending",
                "config": {
                    "TWILIO_ACCOUNT_SID": "****",
                    "TWILIO_AUTH_TOKEN": "*****",
                    "TWILIO_PHONE_NUMBER": "+14158739892"
                }
            }
        ```
        """
        try:
            data = bots.load(request.get_json())
            new_obj = Bots.create_bot(data)
            result = bots.dump(new_obj.dict())
        except ValueError as val_exc:
            logger.warning(
                msg=str(val_exc),
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"General exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500

        return result, 200


@ns.route('/<bot_name>')
class UpdateBot(Resource):
    @staticmethod
    @api.response(200, 'Bot has been update')
    @api.response(400, 'Bot already exist')
    @api.response(500, 'Unexpected error on backend side')
    # @token_required()
    def post(bot_name):
        """
        Update existing Bot
        Use this method to update existing Bot directly via API
        * Send a JSON object
        ```
            {
                "bot_name": "Grafana integration 1",
                "status": "pending", # Possible options: active (green), pending (grey), error (red)
                "config": {
                    "key": 1
                }
            }
        ```
        """
        if not bot_name:
            return {'msg': 'bot_name should be specified'}, 404
        obj = Bots.obj_exist(bot_name=bot_name)
        if not obj:
            return {'msg': f'Bot with specified id - {bot_name} is not exist'}, 404
        try:
            data = bots.load(request.get_json())
            obj.update_obj(data, bot_name=bot_name)
            result = bots.dump(obj.dict())
        except ValueError as val_exc:
            logger.warning(
                msg=f"Bot updating exception \nException: {str(val_exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except BadRequest as bad_request:
            logger.warning(
                msg=f"Bot updating exception \nException: {str(bad_request)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': str(bad_request)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"Bot updating exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500
        return result, 200

    @staticmethod
    # @token_required()
    def get(bot_name):
        """
            Return Bot object with specified id
        """
        if not bot_name:
            return {'msg': 'bot_name should be specified'}, 404
        obj = Bots.obj_exist(bot_name=bot_name)
        if not obj:
            return {'msg': f'object with bot_name - {bot_name} is not found'}, 404
        result = bots.dump(obj.dict())
        return result, 200

    @staticmethod
    # @token_required()
    def delete(bot_name):
        """
            Delete Bot object with specified name
        """
        if not bot_name:
            return {'msg': 'bot_name should be specified'}, 404
        obj = Bots.obj_exist(bot_name=bot_name)
        try:
            if obj:
                obj.delete_obj()
                logger.info(
                    msg=f"Bot deletion. Name: {bot_name}",
                    extra={})
            else:
                return {'msg': f'Object with specified bot_name - {bot_name} is not found'}, 404
        except Exception as exc:
            logger.critical(
                msg=f"Bot deletion exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': f'Deletion of Bot with name: {bot_name} failed. '
                           f'Exception: {str(exc)}'}, 500
        return {'msg': f"Bot with name: {bot_name} successfully deleted"}, 200


@ns.route('/all')
class AllBots(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    # @token_required()
    def get():
        """
        Return All exist Bots
        """
        new_obj = Bots.get_all_bots()

        result = {'bots': new_obj}

        return result, 200


@ns.route('/status/<bot_status>')
class AllBots(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    def get(bot_status):
        """
            Return Bot object with specified id
        """
        if not bot_status:
            return {'msg': 'bot_status should be specified'}, 404
        new_obj = Bots.obj_exist(bot_status=bot_status)
        if not new_obj:
            return {'msg': f'object with bot_status - {bot_status} is not found'}, 404

        result = {'bots': new_obj}

        return result, 200
