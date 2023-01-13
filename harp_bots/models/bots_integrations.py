import traceback
from microservice_template_core import db
import datetime
import ujson as json
from microservice_template_core.tools.logger import get_logger
from marshmallow import Schema, fields

logger = get_logger()


class Bots(db.Model):
    __tablename__ = 'bot_integrations'

    bot_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bot_name = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    status = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    config = db.Column(db.Text(4294000000), default='{}')
    create_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)
    last_update_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)

    def __repr__(self):
        return f"{self.bot_id}_{self.bot_name}"

    def dict(self):
        return {
            'bot_id': self.bot_id,
            'bot_name': self.bot_name,
            'config': json.loads(self.config),
            'status': self.status,
            'create_ts': self.create_ts,
            'last_update_ts': self.last_update_ts
        }

    @classmethod
    def create_bot(cls, data):
        exist_bot_name = cls.query.filter_by(bot_name=data['bot_name']).one_or_none()
        if exist_bot_name:
            raise ValueError(f"Bot Name: {data['bot_name']} already exist")
        new_obj = Bots(
            bot_name=data['bot_name'],
            status=data['status'],
            config=json.dumps(data['config']),
        )
        new_obj = new_obj.save()
        return new_obj

    @classmethod
    def obj_exist(cls, bot_name=None, bot_status=None):
        if bot_name:
            return cls.query.filter_by(bot_name=bot_name).one_or_none()

        if bot_status:
            get_all_bots = cls.query.filter_by(status=bot_status).all()
            all_bots = [single_event.bot_name for single_event in get_all_bots]
            return all_bots

    def update_obj(self, data, bot_name):
        if 'config' in data:
            data['config'] = json.dumps(data['config'])

        self.query.filter_by(bot_name=bot_name).update(data)

        db.session.commit()

    def bots_info_dict(self):
        return {
            'bot_id': self.bot_id,
            'bot_name': self.bot_name,
            'config': json.loads(self.config),
            'status': self.status
        }

    @classmethod
    def get_all_bots(cls):
        get_all_bots = cls.query.filter_by().all()
        all_bots = [single_event.bots_info_dict() for single_event in get_all_bots]

        return all_bots

    def save(self):
        try:
            db.session.add(self)
            db.session.flush()
            db.session.commit()

            return self
        except Exception as exc:
            logger.critical(
                msg=f"Can't commit changes to DB \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            db.session.rollback()

    def delete_obj(self):
        db.session.delete(self)
        db.session.commit()


class BotsSchema(Schema):
    bot_id = fields.Int(dump_only=True)
    bot_name = fields.Str(required=True)
    status = fields.Str(required=True)
    config = fields.Dict(required=True)
    create_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
    last_update_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)