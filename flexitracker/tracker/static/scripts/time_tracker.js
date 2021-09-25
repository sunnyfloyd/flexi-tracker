document.addEventListener("DOMContentLoaded", onMount);

function onMount() {
    let timerControl = document.querySelector("#timer-control");
    if (timerControl !== null) {
        timerControl.addEventListener("click", setUpTimer);
    }
    showTime();
    let timerLink = document.querySelector("#timer-link");
    timerLink.addEventListener("click", setUpMiniTimer);
}

async function setUpMiniTimer() {
    let runningTimerPk = this.dataset.runningTimer === "None" ? null : this.dataset.runningTimer;
    let action = "stop";

    response = await fetch(`https://${window.location.host}/issue/${runningTimerPk}/time_tracker/`, {
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
    let timerControl = document.querySelector("#timer-control");
    
    timerItem.classList.toggle("timer-hidden");

    if (timerControl !== null) {
        workEffort.innerHTML = data.work_effort_actual;
        timerControl.innerHTML = "Start Timer";
        timerControl.dataset.runningTimer = "None";
        timerControl.classList.toggle("btn-info");
        timerControl.classList.toggle("btn-warning");
    }
}

async function setUpTimer() {
    let issuePk = this.dataset.pk;
    let runningTimerPk = this.dataset.runningTimer === "None" ? null : this.dataset.runningTimer;
    let action;
    let timerLink = document.querySelector("#timer-link");

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
            timerLink.dataset.runningTimer = issuePk;
            showTime();
        } else if (action === "stop") {
            this.innerHTML = "Start Timer";
            this.dataset.runningTimer = "None";
            timerLink.dataset.runningTimer = "None";
        }
    }
}

async function showTime(timerItem, currentWorkEffort) {
    if (!timerItem) {
        timerItem = document.querySelector("#timer-item");
    }
    if (!Object.values(timerItem.classList).includes("timer-hidden")) {
        if (currentWorkEffort === undefined) {
            let response = await fetch(`https://${window.location.host}/user_timer_effort/`, {
                method: "GET"
            });
            currentWorkEffort = await response.json();
            currentWorkEffort = parseInt(currentWorkEffort.work_effort);
        }

        let timerWidget = document.querySelector("#timer-widget");
        var time = convertHMS(currentWorkEffort);
        timerWidget.innerText = time;
        timerWidget.textContent = time;

        setTimeout(showTime, 1000, timerItem, currentWorkEffort + 1);
    }
}

function convertHMS(sec) {
    let hours = Math.floor(sec / 3600);
    let minutes = Math.floor((sec - (hours * 3600)) / 60);
    let seconds = sec - (hours * 3600) - (minutes * 60);
    if (hours < 10) {
        hours = "0" + hours;
    }
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (seconds < 10) {
        seconds = "0" + seconds;
    }
    return hours + ':' + minutes + ':' + seconds; // Return is HH : MM : SS
}

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