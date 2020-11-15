let timer, timeoutVal = 1000; // time it takes to wait for user to stop typing in ms

// const status = document.getElementById('status');
var typer = ace.edit("codearea");

var aceDiv = document.getElementById("codearea");
var stop_receiving = false;
aceDiv.addEventListener('keypress', handleKeyPress);
aceDiv.addEventListener('keyup', handleKeyUp);

link = window.location.href.split("/");
session_link = link[link.length - 2]
cookies = document.cookie.split(';').reduce((cookies, cookie) => {
    const [name, value] = cookie.split('=').map(c => c.trim());
    cookies[name] = value;
    return cookies;
}, {});

// when user is pressing down on keys, clear the timeout
function handleKeyPress(e) {
    stop_receiving = true;
    window.clearTimeout(timer);
    // status.innerHTML = 'Typing...';
}

// when the user has stopped pressing on keys, set the timeout
// if the user presses on keys before the timeout is reached, then this timeout is canceled
function handleKeyUp(e) {
    var dict = JSON.parse(localStorage.getItem(session_link));

    window.clearTimeout(timer); // prevent errant multiple timeouts from being generated
    timer = window.setTimeout(() => {
        console.log("Stopped typing")
        console.log(cookies)
        $.ajax({
            type: "POST",
            url: "/update/" + session_link + "/",
            dataType: "json",
            data: {
                "data": typer.getSession().getValue(),
                "version": parseInt(dict.version) + 1,
                "copy": dict.copy
            },
            headers: {"X-CSRFToken": cookies["csrftoken"]},

            success:
                function (data) {
                    cursor = editor.selection.getCursor();

                    var local_storage_dict = {};
                    local_storage_dict["copy"] = data.latest_data;
                    local_storage_dict["version"] = data.version;
                    localStorage.setItem(session_link, JSON.stringify(local_storage_dict));
                    typer.setValue(data.latest_data, 1);
                    typer.moveCursorTo(cursor.row, cursor.column);

                }
        });

        stop_receiving = false;

        // status.innerHTML = 'All done typing! Do stuff like save content to DB, send WebSocket message to server, etc.';
    }, timeoutVal);
}


setInterval(function () {

    var dict = JSON.parse(localStorage.getItem(session_link));

    if (!stop_receiving) {
        // console.log("timeout2")
        $.ajax({
            type: "POST",
            url: "/refresh/" + session_link + "/",
            dataType: "json",
            data: {
                "data": typer.getSession().getValue(),
                "version": parseInt(dict.version)
            },
            headers: {"X-CSRFToken": cookies["csrftoken"]},
            success:
                function (data) {
                    if (data.change === "true" && !stop_receiving) {
                        typer.setValue(data.latest_data, 1);
                        var local_storage_dict = {};
                        local_storage_dict["copy"] = data.latest_data;
                        local_storage_dict["version"] = data.version;
                        localStorage.setItem(session_link, JSON.stringify(local_storage_dict));

                    }
                }
        });
    }
}, 1000)