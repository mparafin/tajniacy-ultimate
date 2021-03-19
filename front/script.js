console.log("huhuhuuu!");
var myHeading = document.querySelector("h1");
myHeading.textContent = "Huhuhuhuuu!";
document.querySelector("h1").onclick = function () {
    alert("Yeah, baby!");
}

socket = new WebSocket('ws://127.0.0.1:8888');

function send_message(node) {
    socket.send(node.textContent);
}

socket.onmessage = function(s) {
    console.log("Message from server! : " + s.data);
    let newp = document.createElement("p");
    newp.textContent = s.data;
    newp.onclick = function () {
        send_message(newp);
    }
    document.querySelector("body").appendChild(newp);
}
