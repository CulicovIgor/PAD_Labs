import urllib.parse as urlp
import requests
import cherrypy
import random
import json


class Proxy(object):
    def __init__(self):
        self.cache = {}
        data = json.load(open('config/nodes_config.json'))
        self.list_of_addresses = []
        for address in data['nodes']:
            self.list_of_addresses.append(address['address'])
        print(self.list_of_addresses)

    def handle_get(self, params, headers):
        # TODO implementing cache
        requested_url = urlp.urlparse(cherrypy.url())
        path = str(requested_url.path)
        params_str = str(params)
        if requested_url.path in self.cache:
            if params_str in self.cache[path]:
                if headers["Content-Type"] in self.cache[path][params_str]:
                    print("Cache response")
                    cherrypy.response.headers["Content-Type"] = headers["Content-Type"]
                    return self.cache[path][params_str][headers["Content-Type"]]
        rand = random.randint(0, len(self.list_of_addresses) - 1)
        print("random: " + str(rand))
        url = "http://" + self.list_of_addresses[rand] + requested_url.path
        # TODO delete this
        url = "http://192.168.1.25:8080/api"
        resp = requests.get(url, params=params, headers=headers)
        if resp.headers["Content-Type"] == headers["Content-Type"]:
            print("Adding to cache")
            print(resp.content)
            self.cache[path] = {
                str(params): {
                    headers["Content-Type"]: resp.content.decode()
                }
            }
            print("Cache")
            print(self.cache)
        for key, value in resp.headers.items():
            cherrypy.response.headers[key] = value
        return resp

    def handle_post(self, params, headers):
        requested_url = urlp.urlparse(cherrypy.url())
        self.cache.clear()
        rand = random.randint(0, len(self.list_of_addresses) - 1)
        print("random: " + str(rand))
        url = "http://" + self.list_of_addresses[rand] + requested_url.path
        # TODO delete this
        url = "http://192.168.1.25:8080/api"
        resp = requests.post(url, cherrypy.request.body.read().decode(), headers=headers, params=params)
        for key, value in resp.headers.items():
            cherrypy.response.headers[key] = value
        return resp

    @cherrypy.expose
    def default(self, *args, **kwargs):
        # headers and query params
        params = cherrypy.request.params
        headers = cherrypy.request.headers

        if cherrypy.request.method == "GET":
            return self.handle_get(params, headers)
        if cherrypy.request.method == "POST":
            return self.handle_post(params, headers)

        # if cherrypy.request.method == "PATCH":
        #     return self.handle_patch()
        # if cherrypy.request.method == "PUT":
        #     return self.handle_put()
        return "This method is not implemented"

    @cherrypy.expose
    def index(self, *args, **kwargs):
        print("headers")
        print(cherrypy.request.headers)
        return "It doesn't work!"

    @cherrypy.expose
    def api(self, *args, **kwargs):
        print("HEADERS2")
        print(cherrypy.request.headers)
        print("PARAMS2")
        print(cherrypy.request.params)
        cherrypy.response.headers = cherrypy.request.headers
        if cherrypy.request.method == "POST":
            cherrypy.response.headers['Content-Type'] = "application/json"
            dictionary = {"name": "DachKib", "s_s": "dead"}
            return json.dumps(dictionary).encode()
        return "Well done"

        # def handle_put(self):
        #     requested_url = urlp.urlparse(cherrypy.url())
        #     print("url")
        #     print(requested_url)
        #     url = "http://" + \
        #           self.list_of_addresses[
        #               random.randint(
        #                   0, len(self.list_of_addresses) - 1)] + requested_url.path
        #     resp = requests.get(url, cherrypy.request.params, headers=cherrypy.request.headers)
        #     return resp
        #
        # def handle_patch(self):
        #     requested_url = urlp.urlparse(cherrypy.url())
        #     print("url")
        #     print(requested_url)
        #     url = "http://" + \
        #           self.list_of_addresses[
        #               random.randint(
        #                   0, len(self.list_of_addresses) - 1)] + ""
        #     resp = requests.get(url, cherrypy.request.params)
        #     return resp
