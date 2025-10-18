const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const wsUrl = `${protocol}${window.location.host}/ws`;

let ws;
let reconnectInterval = 3000;
const heart = document.getElementById("heart");
const status = document.getElementById("status");

function connect() {
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    status.innerText = "💓 Connected";
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "heartbeat") {
      pulse();
      const bpm = (60 / data.interval).toFixed(0);
      status.innerText = `💓 ${bpm} bpm — ${data.active_clients} connected`;
    } else if (data.type === "flatline") {
      flatline();
      status.innerText = "— flatline —";
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
  setTimeout(() => {
    heart.style.transform = "scale(1)";
    heart.style.opacity = "0.8";
  }, 150);
}

function flatline() {
  heart.style.opacity = "0.2";
}

connect();
