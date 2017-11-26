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

    @cherrypy.expose
    def default(self, *args, **kwargs):
        print("params")
        print(cherrypy.request.params)
        print("headers")
        print(cherrypy.request.headers)
        if cherrypy.request.method == "POST":
            requested_url = urlp.urlparse(cherrypy.url())
            print(requested_url)
            url = "http://" + \
                  self.list_of_addresses[
                      random.randint(
                          0, len(self.list_of_addresses) - 1)] + "/api"
            resp = requests.post(url, cherrypy.request.body.read().decode())
            return resp
        return "Hello nigga!"

    @cherrypy.expose
    def index(self, *args, **kwargs):
        return "It doesn't work!"

    @cherrypy.expose
    def api(self, *args, **kwargs):
        return "Well done"
