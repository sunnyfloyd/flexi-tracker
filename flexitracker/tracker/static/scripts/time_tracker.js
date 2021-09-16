document.addEventListener("DOMContentLoaded", onMount);

function onMount() {
    let timer = document.querySelector("#timer-control");
    timer.addEventListener("click", setUpTimer);

    let timerItem = document.querySelector("#timer-item");
    if (!Object.values(timerItem.classList).includes("timer-hidden")) {
        console.log("timer not hidden!");
        showTime();
    }
}

async function setUpTimer() {
    let issuePk = this.dataset.pk;
    let runningTimerPk = this.dataset.runningTimer === "None" ? null : this.dataset.runningTimer;
    let action;

    if (runningTimerPk === issuePk) {
        action = "stop";
    } else if (runningTimerPk === null) {
        action = "start";
    }

    if (action === "start" || action === "stop") {
        response = await fetch("time_tracker/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRF()
            },
            body: JSON.stringify({
                action: action
            })
        });
        let data = await response.json();

        let workEffort = document.querySelector("#work-effort");
        let timerItem = document.querySelector("#timer-item");

        workEffort.innerHTML = data.work_effort_actual;

        timerItem.classList.toggle("timer-hidden");
        this.classList.toggle("btn-info");
        this.classList.toggle("btn-warning");
        if (action === "start") {
            this.innerHTML = "Stop Timer";
            this.dataset.runningTimer = issuePk;
            showTime();
        } else if (action === "stop") {
            this.innerHTML = "Start Timer";
            this.dataset.runningTimer = "None";
        }
    }
}

// async function getUserWorkEffort() {
//     currentWorkEffort = await fetch(`http://${window.location.host}/user_timer_effort/`, {
//         method: "GET"
//     });

//     return currentWorkEffort;
// }

async function showTime(currentWorkEffort) {
    if (currentWorkEffort === undefined) {
        let response = await fetch(`http://${window.location.host}/user_timer_effort/`, {
            method: "GET"
        });
        var currentWorkEffort = await response.json();
        currentWorkEffort = parseInt(currentWorkEffort.work_effort);
    }

    console.log(currentWorkEffort);

    let timerWidget = document.querySelector("#timer-widget");
    var time = currentWorkEffort;
    timerWidget.innerText = time;
    timerWidget.textContent = time;

    setTimeout(showTime, 1000, time + 1);
}

// async function showTime() {
//     currentWorkEffort = await fetch(`http://${window.location.host}/user_timer_effort/`, {
//         method: "GET"
//     });

//     var date = new Date();
//     var h = date.getHours(); // 0 - 23
//     var m = date.getMinutes(); // 0 - 59
//     var s = date.getSeconds(); // 0 - 59

//     h = (h < 10) ? "0" + h : h;
//     m = (m < 10) ? "0" + m : m;
//     s = (s < 10) ? "0" + s : s;

//     var time = h + ":" + m + ":" + s;
//     document.getElementById("MyClockDisplay").innerText = time;
//     document.getElementById("MyClockDisplay").textContent = time;

//     setTimeout(showTime, 1000);
// }

function getCSRF() {
    cookieName = "csrftoken"
    let csrfToken = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, cookieName.length + 1) === (cookieName + "=")) {
                csrfToken = decodeURIComponent(cookie.substring(cookieName.length + 1));
                break;
            }
        }
    }
    return csrfToken;
}