from django.shortcuts import render
import git


def index(request):
    return render(request, 'MainApp/index.html')


def webhook(request):
    if request.method == 'POST':
        repo = git.Repo('https://github.com/UltraXionUA/GN')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400