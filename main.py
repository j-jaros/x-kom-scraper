import flask

from scraper import scraper

app = flask.Flask(__name__, template_folder='./templates', static_folder='./static')


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/sprawdz-podzespoly")
def check_components():
    return flask.render_template("check.html")


@app.route("/api/v1/check_components", methods=['POST'])
def api_check_components():
    data = flask.request.get_json()
    url = data['url']
    response = scraper(url)
    return flask.jsonify({'code': 'ok', 'title': response[0], 'response': response[1], 'unrecognized': response[2]})


app.run(host="0.0.0.0", port=1024)
