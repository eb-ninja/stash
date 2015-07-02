import logging
import sys

import coid
import flask
from flask.ext import hype
import pilo
from pilo.fields import Datetime, Dict, Integer, List, String, SubForm
from werkzeug.exceptions import BadRequest

from stash import models
from . import mimes

logger = logging.getLogger(__name__)


class RequestMIMEMixin(object):

    def accept_match(self, *mime_types):
        mime_type = self.accept_mimetypes.best_match(
            mime_types, default=mime_types[0]
        )
        if not mime_type:
            raise BadRequest(
                'No matching accept mime-type'
            )

    def accept_encoder(self):
        self.accept_match(mimes.json.accept_type)
        return mimes.json.accept_type, mimes.json.encode

    def content_source(self):
        if self.mimetype == mimes.json.content_type:
            charset = self.mimetype_params.get('charset') or None
            return mimes.json.source(
                text=self.get_data(), encoding=charset
            )
        raise BadRequest(
            'Unsupported content mime-type "{}"'.format(self.mimetype)
        )


class Request(RequestMIMEMixin, flask.Request):
    pass


RequestForm = hype.RequestForm

request = flask.request

Response = flask.Response


class Application(flask.Flask):

    request_class = Request

    debug = True

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__('stash.api', *args, **kwargs)
        self.url_map.redirect_defaults = False
        self.register_error_handler(Exception, self.on_error)

    def on_error(self, ex):
        exc_info = sys.exc_info()
        try:
            encode_type, encode = mimes.json.content_type, mimes.json.encode
        except BadRequest:
            flask.app.reraise(*exc_info)
        try:
            error = Error.cast(ex)
        except (ValueError, LookupError):
            flask.app.reraise(*exc_info)
        if error.status_code >= 500:
            logger.exception(exc_info[0], exc_info=exc_info)
        return Response(
            status=error.status_code,
            response=encode(error),
            content_type=encode_type,
        )


app = Application()


class Resource(hype.Resource):

    registry = hype.Registry(app)


class ZKBinding(hype.Binding):

    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        super(ZKBinding, self).__init__(*args, **kwargs)

    def get(self, guid):
        return self.cls.get(guid)


class Error(pilo.Form):

    registry = {}

    @classmethod
    def cast(cls, ex):
        if type(ex) not in cls.registry:
            raise LookupError('None registered for {0}'.format(type(ex)))
        return cls.registry[type(ex)](ex)

    type = pilo.fields.String()

    status_code = pilo.fields.Integer()

    description = pilo.fields.String()


class Link(hype.Link):

    def _url_map(self):
        return app.url_map


class Item(Resource):

    id = hype.Id(codec=coid.Id(encoding='base58'))
    href = Link('item.show', item='id')
    reservations = Link('reservation.index', item='id')

    metadata = Dict(String(), String())
    tags = List(String())
    capacity = Integer()
    available = Integer()
    committed = Integer()

    class Create(RequestForm):

        capacity = Integer()
        metadata = Dict(String(), String())
        tags = List(String())

    @classmethod
    def create(cls, source):
        form = cls.Create(source)
        obj = models.Item.create(
            capacity=form.capacity,
            metadata=form.metadata,
            tags=form.tags,
        )
        return cls(obj)

    @classmethod
    def index(cls):
        objs = models.Item.index()
        return map(cls, objs)


Item.bind(
    ZKBinding(models.Item),
)


class Reservation(Resource):

    id = hype.Id(codec=coid.Id(encoding='base58'))
    href = Link('reservation.show', item='id')
    item_link = Link('item.show', item='id')

    quantity = Integer()
    status = String(default='pending')
    expires_at = Datetime(format='iso8601')

    class Create(RequestForm):

        quantity = Integer(default=1)

    @classmethod
    def create(cls, source):
        form = cls.Create(source)
        obj = models.Reservation.create(form.quantity)
        return cls(obj)

    @classmethod
    def index(cls):
        objs = models.Item.index()
        return map(cls, objs)


Reservation.bind(
    ZKBinding(models.Reservation),
)


@app.route('/items', methods=['GET'], endpoint='item.index')
def item_index():
    items = Item.index()
    return Response(
        status=200,
        response=mimes.json.encode(items),
        content_type=mimes.json.content_type
    )


@app.route('/items', methods=['POST'], endpoint='item.create')
def item_create():
    item = Item.create(request.content_source())
    return Response(
        status=201,
        response=mimes.json.encode(item),
        content_type=mimes.json.content_type
    )


@app.route('/items/<Item:item>', methods=['GET'], endpoint='item.show')
def item_show(item):
    return Response(
        status=200,
        response=mimes.json.encode(item),
        content_type=mimes.json.content_type
    )


def item_delete(item):
    pass


@app.route('/items/<Item:item>/reservations', methods=['GET'], endpoint='reservation.index')
@app.route('/reservations/', methods=['GET'], endpoint='reservation.index', defaults={'item': None})
def reservation_index():
    reservations = Reservation.index()
    return Response(
        status=200,
        response=mimes.json.encode(reservations),
        content_type=mimes.json.content_type
    )


@app.route('/reservations/<Reservation:reservation>', methods=['GET'], endpoint='reservation.show')
def reservation_show(reservation):
    return Response(
        status=200,
        response=mimes.json.encode(reservation),
        content_type=mimes.json.content_type
    )


@app.route('/items/<Item:item>/reservations', methods=['POST'], endpoint='reservation.create')
def reservation_create(item):
    pass


@app.route('/items/<Item:item>/reservations/<Reservation:reservation>', methods=['PUT'], endpoint='reservation.update')
@app.route('/reservations/<Reservation:reservation>', methods=['PUT'], endpoint='reservation.update', defaults={'item': None})
def reservation_update(item, reservation):
    return Response(status=200)


@app.route('/items/<Item:item>/reservations/<Reservation:reservation>', methods=['DELETE'], endpoint='reservation.delete')
@app.route('/reservations/<Reservation:reservation>', methods=['DELETE'], endpoint='reservation.delete', defaults={'item': None})
def reservation_delete(item, reservation):
    return Response(status=200)
