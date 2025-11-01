const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const wsUrl = `${protocol}${window.location.host}/ws`;

let ws;
let reconnectInterval = 3000;
const heart = document.getElementById("heart");
const status = document.getElementById("status");
const info = document.getElementById("info");
const title = document.getElementById("title");
const max_clients = document.getElementById("max_clients");
const total_visits = document.getElementById("total_visits");
const number_of_births = document.getElementById("number_of_births");
const heart_life = document.getElementById("heart_life");
const beats = document.getElementById("beats");
const observers = document.getElementById("observers");

function connect() {
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    status.innerText = "";
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "heartbeat") {
      pulse();
      const bpm = (60 / data.interval).toFixed(0);
      beats.innerText = `💓 ${bpm} bpm`;
      observers.innerText = `${data.active_clients}`;
      max_clients.innerText = `${data.max_clients}`;
      total_visits.innerText = `${data.total_visits}`;
      number_of_births.innerText = `${data.number_of_births}`;
      heart_life.innerText = `${data.heart_life}`;
    } else if (data.type === "flatline") {
      flatline();
      status.innerText = "——— The heart is no longer beating ———";
    }
  };

  ws.onclose = () => {
    flatline();
    status.innerText = "⚠️ Disconnected — retrying...";
    setTimeout(connect, reconnectInterval);
  };

  ws.onerror = () => {
    ws.close();
  };
}

function pulse() {
  heart.style.transform = "scale(1.3)";
  heart.style.opacity = "1";
  title.style.color = "#ff004c";
  setTimeout(() => {
    heart.style.transform = "scale(1)";
    heart.style.opacity = "0.8";
  }, 200);
}

function flatline() {
  heart.style.opacity = "0.2";
  title.style.color = "#888";
}

heart.addEventListener('click', () => {
  fetch("/update-stat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "heart_life", value: 60 }),
    })
  .then(res => res.json())
  .then(console.log);
});

connect();
