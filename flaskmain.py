from flask import Flask, request, abort
import git
import os
import hmac
import hashlib
import json
# from .. import youtube_handler

SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__)


def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


@app.route('/')
def index():
    return '<h1>Hello World</h1>'


@app.route('/GSTV', methods=['POST'])
def gstv_webhook():
    data = request.get_json()
    with open('GSTV_dump.json', 'a') as f:
        json.dump(data, f)
    with open('GSTV_dumps.json', 'a') as f:
        f.write(json.dump(data))
    youtube_handler(request)


@app.route('/Dobryak', methods=['POST'])
def dobryak_webhook():
    data = request.get_json()
    with open('Dobryak_dump.json', 'a') as f:
        json.dump(data, f)
    with open('Dobryak_dumps.json', 'a') as f:
        f.write(json.dump(data))
    youtube_handler(request)


@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method != 'POST':
        return 'OK'
    else:
        abort_code = 418
        if 'X-Github-Event' not in request.headers:
            abort(abort_code)
        if 'X-Github-Delivery' not in request.headers:
            abort(abort_code)
        if 'X-Hub-Signature' not in request.headers:
            abort(abort_code)
        if not request.is_json:
            abort(abort_code)
        if 'User-Agent' not in request.headers:
            abort(abort_code)
        ua = request.headers.get('User-Agent')
        if not ua.startswith('GitHub-Hookshot/'):
            abort(abort_code)
        event = request.headers.get('X-GitHub-Event')
        if event == "ping":
            return json.dumps({'msg': 'Hi!'})
        if event != "push":
            return json.dumps({'msg': "Wrong event type"})
        x_hub_signature = request.headers.get('X-Hub-Signature')
        if not is_valid_signature(x_hub_signature, request.data, SECRET_KEY):
            print('Deploy signature failed: {sig}'.format(sig=x_hub_signature))
            abort(abort_code)
        payload = request.get_json()
        if payload is None:
            print('Deploy payload is empty: {payload}'.format(
                payload=payload))
            abort(abort_code)
        if payload['ref'] != 'refs/heads/master':
            return json.dumps({'msg': 'Not master; ignoring'})
        repo = git.Repo('/home/UltraXionUA/GN')
        origin = repo.remotes.origin
        pull_info = origin.pull()
        if len(pull_info) == 0:
            return json.dumps({'msg': "Didn't pull any information from remote!"})
        if pull_info[0].flags > 128:
            return json.dumps({'msg': "Didn't pull any information from remote!"})
        commit_hash = pull_info[0].commit.hexsha
        build_commit = f'build_commit = "{commit_hash}"'
        print(f'{build_commit}')
        return 'Updated PythonAnywhere server to commit {commit}'.format(commit=commit_hash)


def main():
    app.run()


if __name__ == '__main__':
    main()



