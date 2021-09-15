document.addEventListener("DOMContentLoaded", onMount)

function onMount() {
    let timer = document.querySelector("#timer-control");
    timer.addEventListener("click", toggleTimer);
}

function toggleTimer() {
    let issuePk = this.dataset.pk;
    let runningTimerPk = this.dataset.runningTimer === "None" ? null : this.dataset.runningTimer;
    let action;

    if (runningTimerPk === issuePk) {
        action = "stop";
    } else if (runningTimerPk === null) {
        action = "start";
    }

    if (action === "start" || action === "stop") {
        fetch("time_tracker/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRF()
                },
                body: JSON.stringify({
                    action: action
                })
            })
            .then(response => {
                this.classList.toggle("btn-info");
                this.classList.toggle("btn-warning");
                if (action === "start") {
                    this.innerHTML = "Stop Timer";
                    this.dataset.runningTimer = issuePk;
                } else if (action === "stop") {
                    this.innerHTML = "Start Timer";
                    this.dataset.runningTimer = "None";
                }
            });
    }
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