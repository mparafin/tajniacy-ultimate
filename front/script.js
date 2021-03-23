socket = new WebSocket('ws://127.0.0.1:8888');
teamNames = ["red", "blue", "spec"]

document.getElementById("namechanger").onclick = function () {
	let nick = document.getElementById("nick").value;
	socket.send(JSON.stringify({"type":"nick", "nick":nick}));
}

teamNames.forEach(team => {
	document.getElementById("join"+team).onclick = function () {
		socket.send(JSON.stringify({"type":"teamchange", "team":team}));
	}
})

matrix = document.getElementById("matrix");
matrix.setAttribute('border', '1');
for (let i = 0; i < 5; i++) {
	let tr = document.createElement("tr");
	for (let j = 0; j < 5; j++) {
		let td = document.createElement("td");
		td.id = i + " " + j;
		td.style.textAlign = 'center';
		td.style.verticalAlign = 'middle';
		td.textContent = "I am cell " + td.id;
		td.onclick = function () {
			socket.send(JSON.stringify({"type":"click", "id":td.id}));
		}
		tr.appendChild(td);
	}
	matrix.appendChild(tr);
}

socket.onmessage = function(s) {
	message = JSON.parse(s.data)
	switch(message["type"]) {
		case "nick":
			console.log("Changed player nickname to: " + message["nick"]);
			break;
		case "player_list":
			teamNames.forEach(team => {
				elementName = team + "team";
				let t = document.getElementById(elementName);
				if(t != null) {
					while(t.firstChild) {
						t.removeChild(t.lastChild);
					}
				}
				if (message["player"].team.toLowerCase() === team) {
					p = document.createElement("div");
					p.textContent = message["player"].nick;
					p.style.color = "rgb(0, 100, 10)";
					t.appendChild(p);
				}
				message[team].forEach(player => {
					p = document.createElement("div");
					p.textContent = player;
					t.appendChild(p);
				})
			});
	}

	console.log("Message from server! : " + s.data);
}
