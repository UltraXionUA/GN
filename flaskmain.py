from flask import Flask, request
import git


app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello World Bitch!!!<h1>'


@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/UltraXionUA/GN')
        repo.commit()
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400


def main():
    app.run()


if __name__ == '__main__':
    main()
