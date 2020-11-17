
link = window.location.href.split("/");
session_link = link[link.length - 2]
function language_changed(lang) {


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
    if(new_name.length === 0) {
        $("#project_name").text("Untitled Project");
        new_name = "Untitled Project";
    }
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
    var lang = $("#language").html();


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