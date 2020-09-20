let timer, timeoutVal = 1000; // time it takes to wait for user to stop typing in ms

// const status = document.getElementById('status');
const typer = document.getElementById('code_area');
var stop_receiving = false;
typer.addEventListener('keypress', handleKeyPress);
typer.addEventListener('keyup', handleKeyUp);


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
    window.clearTimeout(timer); // prevent errant multiple timeouts from being generated
    timer = window.setTimeout(() => {
        console.log("Stopped typing")
        console.log(cookies)
        $.ajax({
            type: "POST",
            url: "/update/",
            dataType: "json",
            data: {"data": typer.value},
            headers: {"X-CSRFToken": cookies["csrftoken"]},

            success:
                function (data) {

                    typer.value = data.content;
                }
        });

        stop_receiving = false;

        // status.innerHTML = 'All done typing! Do stuff like save content to DB, send WebSocket message to server, etc.';
    }, timeoutVal);
}


setInterval(function () {

    if (!stop_receiving) {
        // console.log("timeout2")
        $.ajax({
            type: "POST",
            url: "/refresh/",
            dataType: "json",
            data: {"data": typer.value},
            headers: {"X-CSRFToken": cookies["csrftoken"]},
            success:
                function (data) {
                    if (data.change === "true")
                        typer.value = data.content;
                }
        });
    }
}, 1000)