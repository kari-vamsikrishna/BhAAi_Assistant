function sendCommand() {
    const input = document.getElementById("command").value;
    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ command: input })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("response").innerText = "🧠 GIRI: " + data.response;
    })
    .catch(err => {
        console.error("Error:", err);
    });
}
