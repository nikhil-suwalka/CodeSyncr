import json
import random
from datetime import datetime, timedelta

from diff_match_patch import diff_match_patch
from django.contrib.auth import authenticate
from django.contrib.auth import logout
import django.contrib.auth

from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from online_users.models import OnlineUserActivity

from .execute_code import *
from .models import *


def main(request):
    if request.user.is_authenticated:
        # if request.session.get("email", False):
        # userob = User.objects.filter(email=request.session.get("email")).first()
        userob = request.user
        print("User:", userob.email, userob.first_name)
        ob = Session.objects.filter(users=userob)
        links = [[i.id, i.project_name] for i in ob]
        return render(request, "home.html", {"links": links})
    else:
        return redirect("/login")


def login(request):
    if request.session.get("email", False):
        return redirect("/")

    if request.method == "POST":

        email = request.POST.get("email")
        pwd = request.POST.get("pwd")
        if request.POST.get("login"):
            # ob = User.objects.filter(email=email, password=pwd).first()
            ob = authenticate(username=email, password=pwd)
            if ob is not None:
                django.contrib.auth.login(request, ob)
                request.session['email'] = email
                request.session['name'] = ob.first_name
                # user = authenticate(username=email, password=pwd)

            else:
                print("WRONG PASSWORD")
                return render(request, "login.html", context={"error": "Invalid credentials"})

        else:
            name = request.POST.get("name")
            if User.objects.filter(email=email).count() > 0:
                return render(request, "login.html", context={"error": "Email already exists"})
            # User.objects.create(name=name, password=pwd, email=email)
            user = User.objects.create_user(username=email, email=email, password=pwd, first_name=name)
            request.session['email'] = email
            request.session['name'] = name
            django.contrib.auth.login(request, user)

            authenticate(username=email, password=pwd)

        return redirect("/")
    else:
        return render(request, "login.html", context={"error": ""})


def create_link(request):
    if request.method == "POST":
        raise Http404
    else:
        sid = getUniqueCode()
        s = Session.objects.create(id=sid)
        f = File.objects.create(session_id=s)
        request.session[sid] = {'file_id': f.id}
        # s.users.add(User.objects.filter(email=request.session.get('email')).first())
        s.users.add(request.user)
        return redirect("/" + str(sid))
        # return render(request, "workarea.html", context)


def home_view(request, session_id):
    if request.method == "POST":
        raise Http404
    else:
        if request.session.get("email", False):
            context = {}
            session = Session.objects.filter(id=session_id)

            if (session.count() == 0):
                raise Http404
            # user_ob = User.objects.filter(email=request.session.get("email")).first()
            user_ob = request.user
            session_ob = session.first()
            if user_ob not in session_ob.users.all():
                session_ob.users.add(user_ob)

            fileob = File.objects.filter(session_id=session_id).first()
            request.session[session_id] = {'file_id': fileob.id}

            context["data"] = fileob.file_current
            context["version"] = fileob.version
            context["language"] = fileob.language
            context["current_user"] = user_ob.first_name
            context["collabs"] = get_all_collaborators(session_id, user_ob.first_name)
            context["project_name"] = session_ob.project_name
            return render(request, "workarea.html", context)
        else:
            return redirect("/")


def get_all_collaborators(session_id: str, current_user: str) -> list:
    collaborators = []
    users = Session.objects.filter(id=session_id).first().users.all()
    online_users = get_online_users()

    for user in users:
        if user.first_name != current_user:
            collaborators.append([user.first_name, user.id in online_users])
    return collaborators


# Send changes to server
def sync_with_db(request, session_link):
    if request.method == "GET":
        raise Http404

    data = request.POST.get("data")
    version = int(request.POST.get("version"))
    copy = request.POST.get("copy")
    dmp = diff_match_patch()
    patches = dmp.patch_make(copy, data)
    diff = dmp.patch_toText(patches)
    session_ob = Session.objects.filter(id=session_link).first()
    fileob = File.objects.filter(session_id=session_ob).first()

    if Diff.objects.filter(file_id=fileob, version=version).count() > 0:
        version += 1

    # TODO: Improve
    if fileob.version < version:
        Diff.objects.create(data=diff, version=version, file_id=fileob)

        patches = dmp.patch_fromText(diff)
        new_text, _ = dmp.patch_apply(patches, fileob.file_current)
        File.objects.filter(session_id=session_ob).update(file_current=new_text, file_backup=new_text, version=version)

    else:
        diff_obs = Diff.objects.filter(file_id=fileob, version__gte=version).order_by('version')
        for diff_ob in diff_obs:
            patches = dmp.patch_fromText(diff_ob.data)
            data, _ = dmp.patch_apply(patches, data)
            version = diff_ob.version
        version += 1
        File.objects.filter(session_id=session_ob).update(file_current=data, file_backup=data, version=version)
        Diff.objects.create(file_id=fileob, data=diff, version=version)
        new_text = data

    return HttpResponse(json.dumps({"version": version, "latest_data": new_text}), content_type="application/json")


# Refresh from server
def get_from_db(request, session_link):
    if request.method == "GET":
        raise Http404

    data = request.POST.get("data")
    version = int(request.POST.get("version"))
    dmp = diff_match_patch()
    session_ob = Session.objects.filter(id=session_link).first()
    fileob = File.objects.filter(session_id=session_ob).first()
    diff_obs = Diff.objects.filter(file_id=fileob, version__gt=version).order_by('version')

    if diff_obs.count() > 0:
        for diff_ob in diff_obs:
            patches = dmp.patch_fromText(diff_ob.data)
            data, _ = dmp.patch_apply(patches, data)
            version = diff_ob.version

        return HttpResponse(json.dumps({"change": "true", "version": version, "latest_data": data}),
                            content_type="application/json")

    return HttpResponse(json.dumps({"change": "false"}),
                        content_type="application/json")


def clear_session(request):
    # if request.method == "GET":
    #     raise Http404
    logout(request)
    request.session.flush()
    return redirect("/")


def change_language(request, session_link):
    if request.method == "POST":
        # session_link = request.get_full_path().split("/")[1]
        lang = request.POST.get("language")
        File.objects.filter(id=request.session[session_link]["file_id"]).update(language=lang)

        return HttpResponse()
    else:
        raise Http404


def change_project_name(request, session_link):
    if request.method == "POST":
        new_name = request.POST.get("new_name")
        Session.objects.filter(id=session_link).update(project_name=new_name)
        return HttpResponse()
    else:
        raise Http404


def execute_code_fun(request):
    if request.method == "POST":

        lang = request.POST.get("language")
        source = request.POST.get("source")

        output = ""
        if lang == "python":
            output = run_python(source)
        elif lang == "c_cpp":
            output = run_cpp(source)
        elif lang == "java":
            output = run_java(source)

        output = output.replace('\\n', "<br>")
        # output = "<br />".join(output.split("\n"))
        # print("OUTPUT: ", output)
        return HttpResponse(json.dumps({"output": output}), content_type="application/json")
    else:
        raise Http404


def delete_user_from_project(request, session_link):
    if request.method == "POST":
        user_ob = request.user
        session = Session.objects.filter(id=session_link)
        session_ob = session.first()
        if user_ob in session_ob.users.all():
            session_ob.users.remove(user_ob)
        return HttpResponse(json.dumps({"msg": "Done"}))

    else:
        raise Http404


def getUniqueCode():
    s = ""
    for i in range(12):
        s = s + chr(random.randint(97, 122))

    s = s[:4] + "-" + s[4:8] + "-" + s[8:]

    if Session.objects.filter(id=s).count() > 0:
        return getUniqueCode()
    return s


def get_online_users():
    ids = [user.id for user in OnlineUserActivity.get_user_activities(timedelta(minutes=2))]
    return (ids)
