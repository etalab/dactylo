# -*- coding: utf-8 -*-


# Dactylo -- A datasets activity streams logger
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 Etalab
# http://github.com/etalab/dactylo
#
# This file is part of Dactylo.
#
# Dactylo is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Dactylo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Controllers for websockets"""


import json

import webob
import ws4py.server.wsgiutils
import ws4py.websocket

from .. import contexts, model, urls, wsgihelpers


#class WebSocketEmitter(ws4py.websocket.WebSocket):
#    def closed(self, code, reason = None):
#        try:
#            model.websocket_clients.remove(self)
#        except ValueError:
#            # Client is missing from list.
#            pass

#    def opened(self):
#        model.websocket_clients.append(self)

#websocket_emitter_app = ws4py.server.wsgiutils.WebSocketWSGIApplication(handler_cls = WebSocketEmitter)


class WebSocketMetricsEmitter(ws4py.websocket.WebSocket):
    def closed(self, code, reason = None):
        try:
            model.websocket_metrics_clients.remove(self)
        except ValueError:
            # Client is missing from list.
            pass

    def opened(self):
        model.websocket_metrics_clients.append(self)

        message = unicode(json.dumps(model.metrics, encoding = 'utf-8', ensure_ascii = False, indent = 2))
        self.send(message)

websocket_metrics_emitter_app = ws4py.server.wsgiutils.WebSocketWSGIApplication(handler_cls = WebSocketMetricsEmitter)


#def api1_listen(environ, start_response):
#    req = webob.Request(environ)
##    ctx = contexts.Ctx(req)
##    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

#    assert req.method == 'GET'
##    params = req.GET
##    inputs = dict(
##        first_key = params.get('first_key'),
##        keys = params.get('keys'),
##        limit = params.get('limit'),
##        values = params.get('values'),
##        )

#    return websocket_emitter_app(environ, start_response)


def api1_metrics(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)
#    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'GET'

    try:
        return websocket_metrics_emitter_app(environ, start_response)
    except ws4py.server.wsgiutils.HandshakeError as error:
        return wsgihelpers.bad_request(ctx, explanation = ctx._(u'WebSocket Handshake Error: {0}').format(error))


def route_api1_class(environ, start_response):
    router = urls.make_router(
#        ('GET', '^/?$', api1_listen),
        ('GET', '^/metrics/?$', api1_metrics),
        )
    return router(environ, start_response)
