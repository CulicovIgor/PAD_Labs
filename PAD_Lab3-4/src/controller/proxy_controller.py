import urllib.parse as urlp
import requests
import cherrypy
import random
import json


class Proxy(object):
    def __init__(self):
        self.cache_valid = False
        data = json.load(open('config/nodes_config.json'))
        self.list_of_addresses = []
        for address in data['nodes']:
            self.list_of_addresses.append(address['address'])
        print(self.list_of_addresses)

    def handle_get(self):
        requested_url = urlp.urlparse(cherrypy.url())
        print("url")
        print(requested_url)
        url = "http://" + \
              self.list_of_addresses[
                  random.randint(
                      0, len(self.list_of_addresses) - 1)] + requested_url.path
        print(url)
        resp = requests.get(url, cherrypy.request.params, headers=cherrypy.request.headers)
        cherrypy.response.headers['Content-Type'] = resp.headers['Content-Type']
        return resp

    def handle_put(self):
        requested_url = urlp.urlparse(cherrypy.url())
        print("url")
        print(requested_url)
        url = "http://" + \
              self.list_of_addresses[
                  random.randint(
                      0, len(self.list_of_addresses) - 1)] + requested_url.path
        resp = requests.get(url, cherrypy.request.params, headers=cherrypy.request.headers)
        return resp

    def handle_patch(self):
        requested_url = urlp.urlparse(cherrypy.url())
        print("url")
        print(requested_url)
        url = "http://" + \
              self.list_of_addresses[
                  random.randint(
                      0, len(self.list_of_addresses) - 1)] + ""
        resp = requests.get(url, cherrypy.request.params)
        return resp

    def handle_post(self):
        requested_url = urlp.urlparse(cherrypy.url())
        print("url")
        print(requested_url)
        url = "http://" + \
              self.list_of_addresses[
                  random.randint(
                      0, len(self.list_of_addresses) - 1)] + requested_url
        resp = requests.post(url, cherrypy.request.body.read().decode(), headers=cherrypy.request.headers)
        return resp

    @cherrypy.expose
    def default(self, *args, **kwargs):
        print("params")
        print(cherrypy.request.params)
        print("headers")
        print(cherrypy.request.headers)
        if cherrypy.request.method == "PATCH":
            return self.handle_patch()
        if cherrypy.request.method == "PUT":
            return self.handle_put()
        if cherrypy.request.method == "GET":
            return self.handle_get()
        if cherrypy.request.method == "POST":
            return self.handle_post()
        return "Hello body!"

    @cherrypy.expose
    def index(self, *args, **kwargs):
        print("headers")
        print(cherrypy.request.headers)
        return "It doesn't work!"

    @cherrypy.expose
    def api(self, *args, **kwargs):
        return "Well done"
