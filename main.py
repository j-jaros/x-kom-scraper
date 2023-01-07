from scraper import scraper
import flask
import waitress

app = flask.Flask(__name__, template_folder="./templates", static_folder="./static")

@app.errorhandler(500)
def error500(e):
    return "internal_server_error", 500

@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/check_parts", methods=["POST"])
def check_parts():
    keys = list(flask.request.get_json().keys())
    if keys != ['url']:
        return 'invalid_keys'
    return scraper(flask.request.json['url'], 0)

app.run("127.0.0.1", 1024)
