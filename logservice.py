#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import ujson as json
from elasticsearch import Elasticsearch
from tornado.options import define, options
from time import strftime

define("port", default=8888, help="run on the given port", type=int)
define("es_server", default="127.0.0.1", help="run on the given port", type=str)

tornado.options.parse_command_line()

es = Elasticsearch([
    {'host': options.es_server}
])


class BaseHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')
        self.set_header('Server', 'reformo/rlog')
        self.set_status(200, 'OK')


class LogPostHandler(BaseHandler):

    def post(self):
        app_identifier = tornado.escape.url_unescape(self.get_argument('identifier', default='__nan__', strip=True))
        log_type = tornado.escape.url_unescape(self.get_argument('type', default='warning', strip=True))
        description = tornado.escape.url_unescape(self.get_argument('description', default='', strip=True))
        source_user_id = tornado.escape.url_unescape(self.get_argument('user_id', default='', strip=True))
        source_date = tornado.escape.url_unescape(self.get_argument('date', default='', strip=True))
        source_data_json = tornado.escape.url_unescape(self.get_argument('data', default='', strip=True))
        source_data_obj = json.loads(source_data_json)
        source_data = {app_identifier: source_data_obj}
        log_date = strftime("%Y-%m-%d %H:%M:%S")
        doc = {'identifier': app_identifier, 'log_date': log_date, 'log_type': log_type, 'description': description,
               'source_user_id': source_user_id, 'source_log_date': source_date, 'source_data': source_data,
               'status': 0, 'history': [{'version': 1, 'history_date': log_date, 'history_data': None}]}
        res = es.index(index="logservice", doc_type='logs', body=doc)
        self.set_status(201, 'Created')
        response = {"status": 201, "data": res}
        output = json.dumps(response, sort_keys=True, indent=4)
        self.write(output)


class LogHandler(BaseHandler):

    def get(self, slug):
        try:
            res = es.get(index="logservice", doc_type='logs', id=slug)
            doc = res['_source']
            doc['_id'] = res['_id']
            self.set_status(200, 'OK')
            response = {"status": 200, "data": doc}
        except:
            self.set_status(404, 'Not Found')
            response = {"status": 404, "error": "Not found"}
        output = json.dumps(response, sort_keys=True, indent=4)
        self.write(output)

    def put(self, slug):
        res = None
        try:
            res = es.get(index="logservice", doc_type='logs', id=slug)
            data = res['_source'];
            history_date = strftime("%Y-%m-%d %H:%M:%S")
            status = tornado.escape.url_unescape(self.get_argument('status', default=0, strip=True))
            history_data_json = tornado.escape.url_unescape(self.get_argument('history_data', default=0, strip=True))
            history_data_obj = json.loads(history_data_json)
            history_data = data['history']
            history_length = len(history_data)
            new_version = history_data[history_length-1]['version']+1
            history_data_new = {'history_data': history_data_obj, 'history_date': history_date, 'version': new_version}
            history_data.append(history_data_new)
            body = {"doc": {"status": status, 'history': history_data}}
            res = es.update(index="logservice", doc_type='logs', id=slug,  body=body)
            self.set_status(200, 'OK')
            response = {"status": 200, "data": res}
        except:
            self.set_status(404, 'Not Found')
            response = {"status": 404, "error": res}
        output = json.dumps(response, sort_keys=True, indent=4)
        self.write(output)

    def delete(self, slug):
        try:
            res = es.delete(index="logservice", doc_type='logs', id=slug)
            doc = res
            doc['_id'] = res['_id']
            self.set_status(200, 'OK')
            response = {"status": 200, "data": doc}
        except:
            self.set_status(404, 'Not Found')
            response = {"status": 404, "error": "Not found"}
        output = json.dumps(response, sort_keys=True, indent=4)
        self.write(output)


class MainHandler(BaseHandler):

    def get(self):
        self.set_status(200, 'OK')
        data = {"status": 200, "message": "OK"}
        output = json.dumps(data, sort_keys=True, indent=4)
        self.write(output)


def main():
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/log", LogPostHandler),
        (r"/log/([^/]+)", LogHandler)
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
