// ------ GLOBALS ------
socket = new WebSocket('ws://'+ location.host + ':8888');
teamNames = ["red", "blue", "spec"]
tileColors = {
	"RED":"lightcoral",
	"BLUE":"lightskyblue",
	"SPEC":"wheat",
	"KILLER":"black"
}

// ------ BUTTONS ------

function init_namechanger() {
	let nick = document.getElementById("nick").value;
	document.getElementById("namechanger").onclick = function () {
		socket.send(JSON.stringify({"type":"nick", "nick":nick}));
	}
}

function init_teamchanger(team) {
	document.getElementById("join"+team).onclick = function () {
		socket.send(JSON.stringify({"type":"teamchange", "team":team}));
	}
}

function init_captbutton(team) {
	document.getElementById("capt"+team).onclick = function () {
		socket.send(JSON.stringify({"type":"capt", "team":team}));
	}
}

function init_entrybutton() {
	document.getElementById("entrybutton").onclick = function () {
		let entry = document.getElementById("entry").value;
		let entrynumber = document.getElementById("entrynumber").value;
		socket.send(JSON.stringify({"type":"entry", "entry":entry, "entrynumber":entrynumber}));
	}
}

// -------- HELPER FUNCTIONS -------

function be_captain() {
	document.getElementById("captred").style.visibility = "hidden";
	document.getElementById("captblue").style.visibility = "hidden";
	document.getElementById("captain_stuff").style.visibility = "visible";
}

function be_deckhand() {
	document.getElementById("captred").style.visibility = "visible";
	document.getElementById("captblue").style.visibility = "visible";
	document.getElementById("captain_stuff").style.visibility = "hidden";
}

// -------- PROTOCOL HANDLERS -------

function player_list_handler(message) {
	teamNames.forEach(team => {
		elementName = team + "team";
		let t = document.getElementById(elementName);
		while(t.firstChild) {
			t.removeChild(t.lastChild);
		}
		if (message["player"].team.toLowerCase() === team) {
			p = document.createElement("div");
			p.textContent = message["player"].nick;
			p.style.color = "rgb(0, 100, 10)";
			p.style.padding = "0px 0.5em";
			if (message["player"].capt) {
				p.style.fontWeight = "bold";
				be_captain();
			} else {
				be_deckhand();
			}
			t.appendChild(p);
		}
		message[team].forEach(player => {
			p = document.createElement("div");
			p.textContent = player["nick"];
			p.style.padding = "0px 0.5em";
			if (player.capt) {
				p.style.fontWeight = "bold";
				t.insertBefore(p, t.firstChild);
			} else{
				t.appendChild(p);
			}
		})
	});
}

function uncovered_handler(message) {
	data = message["uncovered"];
	Object.keys(data).forEach(key => {
		document.getElementById(key).style.backgroundColor = tileColors[data[key]];
		if (data[key] === "KILLER") {
			document.getElementById(key).style.color = "white";
		}
		});
}

function matrix_handler(message) {
	data = message["matrix"]
	for (let i = 0; i < matrix.rows.length; i++) {
		const row = matrix.rows[i];
		for (let j = 0; j < row.cells.length; j++) {
			const cell = row.cells[j];
			cell.textContent = data[i][j];
		}
	}

	uncovered_handler(message);
}

function echo_handler(message) {
	console.log("Echo from server:\n");
	console.log(JSON.stringify(message["data"]));
}

handlers = {
	"player_list": player_list_handler,
	"matrix": matrix_handler,
	"uncovered": uncovered_handler,
	"echo": echo_handler,
}

// ------------------ START -----------------

init_namechanger();
init_entrybutton();

teamNames.forEach(team => {
	init_teamchanger(team);
	if (team !== "spec") {
		init_captbutton(team);
	}
});

matrix = document.getElementById("matrix");
matrix.setAttribute('border', '1');
for (let i = 0; i < 5; i++) {
	let tr = document.createElement("tr");
	for (let j = 0; j < 5; j++) {
		let td = document.createElement("td");
		td.id = i + " " + j;
		td.style.textAlign = 'center';
		td.style.verticalAlign = 'middle';
		td.style.borderRadius = '1em';
		td.textContent = "";
		td.onclick = function () {
			socket.send(JSON.stringify({"type":"click", "id":td.id}));
		}
		tr.appendChild(td);
	}
	matrix.appendChild(tr);
}

select = document.getElementById("entrynumber");
for (let i = 0; i < 10; i++) {
	let opt = document.createElement("option");
	opt.value = i;
	opt.text = i;
	select.appendChild(opt);
}

socket.onmessage = function(s) {
	// console.log("Message from server! : " + s.data);
	try {
		message = JSON.parse(s.data);	
	} catch (error) {
		console.log("Unparseable data: " + s.data);
	}

	handlers[message["type"]](message);
	

}
