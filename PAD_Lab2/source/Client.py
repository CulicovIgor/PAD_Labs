import socket
import json
import jsonschema
from lxml import etree
from io import StringIO

TCP_IP = '127.0.0.1'
TCP_PORT = 9099
BUFFER_SIZE = 2048
df = input('Choose data format(xml/json): ')
filter_str = input('Choose data format(xml/json): ')
MESSAGE = "{" \
          ' "type":"' + df + '",' \
                             ' "filter":"' + filter_str + '"' \
                                                          '}'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE.encode())
data = s.recv(BUFFER_SIZE)
#print(data)
if df == "json":
    with open('schema_json.json', 'r') as schema_file:
        schema_to_check = schema_file.read()

    schema = json.loads(schema_to_check)
    jsonschema.validate(data.decode(), schema)
    try:
        with open('schema_json.json', 'r') as schema_file:
            schema_to_check = schema_file.read()

        schema = json.loads(schema_to_check)
        jsonschema.validate(data.decode(), schema)
        print("Json valid")
    except ValueError:
        print("Json is not valid")
else:
    if df == "xml":
        with open('schema_xml.xml', 'r') as schema_file:
            schema_to_check = schema_file.read()
        schema_root = etree.parse(StringIO(schema_to_check))
        schema = etree.XMLSchema(schema_root)
        xmlparser = etree.XMLParser(schema=schema)
        etree.fromstring(data, xmlparser)
        try:
            print("XML valid")
        except etree.XMLSchemaError:
            print("XML not valid")

print(data.decode())
s.close()
