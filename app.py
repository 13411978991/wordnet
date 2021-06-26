from flask import Flask
from get_wordcloud_adjnet.get import blueprint

app = Flask(__name__)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(debug=True)