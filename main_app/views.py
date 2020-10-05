import json
from datetime import datetime

from diff_match_patch import diff_match_patch
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import *
from .execute_code import *


# Create your views here.
def home_view(request):
    if request.method == "POST":
        pass
    else:
        context = {"data": "", "language": "python"}
        if request.session.get("session_id", False):
            ob = File.objects.filter(session_id=request.session["session_id"]).first()
            request.session["last_changed"] = str(ob.last_changed)
            context["data"] = ob.file_current
            context["language"] = ob.language
            print("Old session found: ", request.session['session_id'], " File ID: ", ob.id)
        else:
            s = Session.objects.create()
            f = File.objects.create(session_id=s)
            request.session["session_id"] = s.id
            request.session["file_id"] = f.id
            request.session["last_changed"] = str(f.last_changed)
            print("New session created: ", s.id)

        return render(request, "home.html", context)


# Send changes to server
def sync_with_db(request):
    local_content = request.POST.get("data")
    # print(local_content)
    ob = File.objects.filter(id=request.session["file_id"]).first()
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
        print("in 1")
        # time = datetime.now(pytz.timezone("Asia/Kolkata"))
        print("TIME: ", time)
        File.objects.filter(id=request.session['file_id']).update(file_backup=server_content, file_current=results[0],
                                                                  last_changed=time)
        request.session["last_changed"] = str(time)
        return HttpResponse(json.dumps({"content": results[0]}), content_type="application/json")

    else:
        print("in 2")
        File.objects.filter(id=request.session['file_id']).update(file_backup=server_content,
                                                                  file_current=local_content, last_changed=time)
        request.session["last_changed"] = str(time)

        return HttpResponse(json.dumps({"content": local_content}), content_type="application/json")


# Refresh from server
def get_from_db(request):
    local_last_change = request.session["last_changed"].replace('"', "")
    ob = File.objects.filter(session_id=request.session["session_id"]).first()
    print("OB", request.session["session_id"])
    server_last_change = str(ob.last_changed)

    print(local_last_change, server_last_change)
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
    request.session.flush()
    return redirect("/")


def same_session(request, num: int):
    request.session["session_id"] = num
    request.session["file_id"] = num
    ob = File.objects.filter(session_id=request.session["session_id"]).first()

    request.session["last_changed"] = str(ob.last_changed)
    return redirect("/")


def change_language(request):
    lang = request.POST.get("language")
    File.objects.filter(id=request.session["file_id"]).update(language=lang)

    return redirect("/")


def execute_code_fun(request):
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
