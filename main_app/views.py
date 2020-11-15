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
        print("create_link called by POST")
    else:
        sid = getUniqueCode()
        s = Session.objects.create(id=sid)
        f = File.objects.create(session_id=s)
        request.session[sid] = {'file_id': f.id, 'last_changed': str(f.last_changed)}
        # s.users.add(User.objects.filter(email=request.session.get('email')).first())
        s.users.add(request.user)
        print("New session created: ", sid)
        return redirect("/" + str(sid))
        # return render(request, "workarea.html", context)


def home_view(request, session_id):
    if request.method == "POST":
        print("home_view called by POST")
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
            print(get_all_collaborators(session_id, user_ob.first_name))

            fileob = File.objects.filter(session_id=session_id).first()
            request.session[session_id] = {'file_id': fileob.id, 'last_changed': str(fileob.last_changed)}

            context["data"] = fileob.file_current
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

    # session_link = request.get_full_path().split("/")[1]

    local_content = request.POST.get("data")
    # print(local_content)
    ob = File.objects.filter(id=request.session[session_link]['file_id']).first()
    server_content = ob.file_current
    backup_content = ob.file_backup

    # Another method
    # diff_text = ""
    # for line in difflib.unified_diff(server_content.split('\n'), local_content.split('\n')):
    #     diff_text += line + "\n"
    #
    # # for diff in whatthepatch.parse_patch(diff_text):
    # #     print(diff)
    #
    # diff = [x for x in whatthepatch.parse_patch(diff_text)]
    # diff = diff[0]
    # print(diff)
    # tzu = whatthepatch.apply_diff(diff, server_content)
    # print(tzu)

    # Merge
    dmp = diff_match_patch()
    diff = dmp.diff_main(server_content, local_content, True)

    if len(diff) > 2:
        dmp.diff_cleanupSemantic(diff)
    patch_list = dmp.patch_make(server_content, local_content, diff)
    patch_text = dmp.patch_toText(patch_list)
    patches = dmp.patch_fromText(patch_text)
    results = dmp.patch_apply(patches, server_content)

    # print(local_content, "\t", server_content)
    print(results)
    time = datetime.now()
    if (results[1][0]):
        # time = datetime.now(pytz.timezone("Asia/Kolkata"))
        File.objects.filter(id=request.session[session_link]['file_id']).update(file_backup=server_content,
                                                                                file_current=results[0],
                                                                                last_changed=time)
        request.session[session_link]["last_changed"] = str(time)
        return HttpResponse(json.dumps({"content": results[0]}), content_type="application/json")

    else:
        File.objects.filter(id=request.session[session_link]['file_id']).update(file_backup=server_content,
                                                                                file_current=local_content,
                                                                                last_changed=time)
        request.session[session_link]["last_changed"] = str(time)

        return HttpResponse(json.dumps({"content": local_content}), content_type="application/json")


# Refresh from server
def get_from_db(request, session_link):
    if request.method == "GET":
        raise Http404
    # session_link = request.get_full_path().split("/")[1]
    local_last_change = request.session[session_link]["last_changed"].replace('"', "")
    ob = File.objects.filter(id=request.session[session_link]['file_id']).first()
    server_last_change = str(ob.last_changed)

    # print(local_last_change, server_last_change)
    if server_last_change != local_last_change:
        # print("Changed")
        #
        # # Merge
        # local_content = request.POST.get("data")
        server_content = ob.file_current
        # backup_content = ob.file_backup
        #
        # dmp = diff_match_patch()
        # dmp.Diff_Timeout = 5
        # # print("------------")
        # # print(local_content, server_content)
        # diff = dmp.diff_main(backup_content, server_content, True)
        # print("DIFF: ", dmp.Diff_Timeout)
        # if len(diff) > 2:
        #     dmp.diff_cleanupSemantic(diff)
        # patch_list = dmp.patch_make(backup_content, server_content, diff)
        # patch_text = dmp.patch_toText(patch_list)
        # patches = dmp.patch_fromText(patch_text)
        # results = dmp.patch_apply(patches, local_content)
        #
        # request.session["last_changed"] = server_last_change
        # print("xyz")
        # print(request.session["last_changed"], server_last_change)
        #
        # print(results)
        # if (len(results) > 0 and len(results[1]) > 0 and results[1][0]):
        #     return HttpResponse(json.dumps({"change": "true", "content": results[0]}),
        #                         content_type="application/json")
        # else:
        #     return HttpResponse(json.dumps({"change": "true", "content": server_content}),
        #                         content_type="application/json")

        return HttpResponse(json.dumps({"change": "true", "content": server_content}),
                            content_type="application/json")

    else:
        # print("Not Changed")

        return HttpResponse(json.dumps({"change": "false"}), content_type="application/json")


def clear_session(request):
    # if request.method == "GET":
    #     raise Http404
    logout(request)
    request.session.flush()
    return redirect("/")


# TODO: Remove
# def same_session(request, num: int):
#     request.session["session_id"] = num
#     request.session["file_id"] = num
#     ob = File.objects.filter(session_id=request.session["session_id"]).first()
#
#     request.session["last_changed"] = str(ob.last_changed)
#     return redirect("/")


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
