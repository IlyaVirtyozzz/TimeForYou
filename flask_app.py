from constants import logging, request, json, app, db
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
    if request.json['request']["command"] != "ping":
        logging.info(
            str(response['session']["user_id"][:5]) + " : " + str(
                request.json['request']["command"]) + "|{}|".
            format("new" if request.json['session']['new'] else "old") +
            str(response['response']['text']))

    return json.dumps(response)
