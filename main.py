import flask

# from scraper import scraper

app = flask.Flask(__name__, template_folder='./templates', static_folder='./static')


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/sprawdz-podzespoly")
def check_components():
    return flask.render_template_string("<h1>to jest strona z sprawdzeniem podzespolow</h1>")


app.run()
