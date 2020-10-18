function language_changed() {

    var lang = $("#language").val();

    editor.session.setMode("ace/mode/" + lang);

    $.ajax({
        type: "POST",
        url: "/change_language/",
        dataType: "json",
        data: {"language": lang},
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