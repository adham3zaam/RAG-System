from flask import Flask, render_template

from routes.rag_routes import rag_routes


app = Flask(__name__)


app.register_blueprint(rag_routes)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/health")
def health():

    return {
        "status": "healthy"
    }


if __name__ == "__main__":

    app.run(debug=True)