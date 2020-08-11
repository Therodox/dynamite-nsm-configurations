import sys
import json
import base64
from urllib.request import Request
from urllib.request import urlopen

object_types = [
    'config',
    'dashboard',
    'search',
    'visualization',
    'index-pattern'
]
encoded_bytes = '{}:{}'.format('elastic', sys.argv[3]).encode('utf-8')
base64string = base64.b64encode(encoded_bytes).decode('utf-8')
for object_type in object_types:
    data = {
        'type': object_type,
        'includeReferencesDeep': True
    }

    url_request = Request(
                        url='http://{}:{}/api/saved_objects/_export'.format(
                            sys.argv[1], sys.argv[2]
                        ),
                        data=json.dumps(data).encode('utf-8'),
                        headers={'Content-Type': 'application/json', 'kbn-xsrf': True}
                    )
    url_request.add_header("Authorization", "Basic %s" % base64string)
    response = urlopen(url_request)
    print(response.read().decode('utf-8'))
