from django.shortcuts import render, redirect
from django.contrib import messages
from pprint import pprint
from django.forms.models import model_to_dict

from models import *

LOGIN_TARGET = "trading/"

# Create your views here.
def index(response):
    if "user" in response.session:
        return redirect("/"+LOGIN_TARGET)
    messagelist = messages.get_messages(response).__iter__()
    try:
        header = messagelist.next()
    except StopIteration:
        header = ""
    rest = []
    for message in messagelist:
        rest.append(message)
    return render(response, "users/index.html", {"header":header, "rest":rest})

def register(response):
    user, errors = User.objects.register(response.POST)
    if user is not None:
        messages.success(response, "Successfully registered!")
        response.session["user"] = {"id":user.id, "name":user.username}
        return redirect("/"+LOGIN_TARGET)
    else:
        messages.error(response, "There were errors with your registration:")
        for error in errors:
            messages.error(response, error)
        return redirect("/")

def login(response):
    result = User.objects.tryLogin(response.POST["username"], response.POST["password"])
    if (type(result) is User):
        messages.success(response, "Successfully logged in!")
        response.session["user"] = {"id":result.id, "name":result.username}
        return redirect("/"+LOGIN_TARGET)
    else:
        messages.error(response, result)
        return redirect("/")

def logout(response):
    del response.session["user"]
    return redirect("/")
