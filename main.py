from flask import Flask
import simulation as simulation

app = Flask(__name__)

@app.route("/")
def index():
    text = simulation.main()
    # text = "Hello World!"
    return text

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)