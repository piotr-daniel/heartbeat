const ws = new WebSocket(`ws://${window.location.host}/ws`);
const heart = document.getElementById("heart");
const status = document.getElementById("status");
const people = document.getElementById("people");

let beatInterval = 1000;

ws.onopen = () => {
    status.innerText = "💓 Connected. Waiting for heartbeat...";
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "heartbeat") {
        beatInterval = data.interval * 1000;
        pulse();
        status.innerText = `💓 beating at ${(1000 / beatInterval * 60).toFixed(0)} bpm`;
        people.innerText = `Supported by ${data.active_clients} people`;
    } else if (data.type === "flatline") {
        flatline();
    }
};

function pulse() {
    heart.style.transform = "scale(1.3)";
    heart.style.opacity = "1";
    setTimeout(() => {
        heart.style.transform = "scale(1)";
        heart.style.opacity = "0.8";
    }, 150);
}

function flatline() {
    heart.style.opacity = "0.2";
    status.innerText = "— flatline —";
}
