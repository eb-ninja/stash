import collections
import datetime
import logging
import json
import uuid

import pilo


logger = logging.getLogger(__name__)


MIME = collections.namedtuple('MIME', [
    'accept_type', 'source', 'content_type', 'encode',
])


JSONSource = pilo.source.JsonSource


class JSONEncoder(json.JSONEncoder):

    def __init__(self, indent=4, sort_keys=True, errors='strict'):
        super(JSONEncoder, self).__init__(indent=indent, sort_keys=sort_keys)
        self.errors = errors

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return self._datetime(o)
        if isinstance(o, datetime.date):
            return self._date(o)
        if isinstance(o, datetime.time):
            return self._time(o)
        if isinstance(o, uuid.UUID):
            return self._uuid(o)
        if self.errors == 'strict':
            raise TypeError(repr(o) + ' is not JSON serializable')
        if self.errors == 'warn':
            logger.warning(repr(o) + ' is not JSON serializable')

    def _datetime(self, o):
        return o.isoformat()

    def _date(self, o):
        return '{:04d}-{:02d}-{:02d}'.format(o.year, o.month, o.day)

    def _time(self, o):
        return o.strftime('%H:%M:%S')

    def _uuid(self, o):
        return str(o.hex)


json = MIME(
    accept_type='application/json',
    source=JSONSource,
    content_type='application/json',
    encode=JSONEncoder().encode,
)
