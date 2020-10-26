
link = window.location.href.split("/");
session_link = link[link.length - 2]
function language_changed() {

    var lang = $("#language").val();

    editor.session.setMode("ace/mode/" + lang);

    $.ajax({
        type: "POST",
        url: "/change_language/" + session_link + "/",
        dataType: "json",
        data: {"language": lang},
        headers: {"X-CSRFToken": cookies["csrftoken"]},

        success:
            function (data) {

            }
    });
}

function project_name_change(){
    var new_name = $("#project_name").text();
    $.ajax({
        type: "POST",
        url: "/change_project_name/" + session_link + "/",
        dataType: "json",
        data: {"new_name": new_name},
        headers: {"X-CSRFToken": cookies["csrftoken"]},

        success:
            function (data) {

            }
    });
}

function execute_code() {

    var source = editor.getValue();
    var lang = $("#language").val();


    $.ajax({
        type: "POST",
        url: "/execute_code/",
        dataType: "json",
        data: {"language": lang, "source": source},
        headers: {"X-CSRFToken": cookies["csrftoken"]},

        success:
            function (data) {
                $("#codeoutput").html(data.output);
            }
    });
}