from constants import logging, request, json, app,db
from main import Main

logging.basicConfig(level=logging.INFO, filename='/home/AbilityForAlice2/mysite/app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


@app.route('/', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {}
    }

    one = Main(response, request.json, db)
    one.start()
    response = one.get_response()
    return json.dumps(response)
