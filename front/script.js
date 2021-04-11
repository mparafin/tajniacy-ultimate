// ------ GLOBALS ------
const SOCKET = new WebSocket('ws://'+ location.host + ':8888');
const TEAM_NAMES = ["red", "blue", "spec"];
const TILE_COLORS = {
	"RED":"lightcoral",
	"BLUE":"lightskyblue",
	"SPEC":"wheat",
	"KILLER":"black"
};
const ENTRY_REGEXP = /[^A-Za-z0-9\-\sąćęłńóśżź]/i;
TEAM = "spec";
TURN = "spec";
PHASE = "capt";

// ------ BUTTONS ------

function init_namechanger() {
	document.getElementById("namechanger").onclick = function () {
		let nick = document.getElementById("nick").value;
		SOCKET.send(JSON.stringify({"type":"nick", "nick":nick}));
	}
}

function init_teamchanger(team) {
	document.getElementById("join"+team).onclick = function () {
		SOCKET.send(JSON.stringify({"type":"teamchange", "team":team}));
	}
}

function init_captbutton(team) {
	document.getElementById("capt"+team).onclick = function () {
		SOCKET.send(JSON.stringify({"type":"capt", "team":team}));
	}
}

function init_teambuttons() {
	TEAM_NAMES.forEach(team => {
		init_teamchanger(team);
		if (team !== "spec") {
			init_captbutton(team);
		}
	});
}

function init_entrybutton() {
	document.getElementById("entrybutton").onclick = function () {
		let entry = document.getElementById("entry").value;
		let entrynumber = document.getElementById("entrynumber").value;
		if (ENTRY_REGEXP.test(entry)) {
			console.log("Incorrect entry string!");
			return;
		}
		SOCKET.send(JSON.stringify({"type":"entry", "entry":entry, "entrynumber":entrynumber}));
	}
}

function init_reset_buttons() {
	document.getElementById("resetgame").onclick = function () {
		SOCKET.send(JSON.stringify({"type":"resetgame"}));
	}
	document.getElementById("resetsecret").onclick = function () {
		SOCKET.send(JSON.stringify({"type":"resetsecret"}));
	}
}

function init_pass_button() {
	document.getElementById("pass").onclick = function () {
		SOCKET.send(JSON.stringify({"type":"pass"}))
	}
}

function init_wordsmenu_buttons() {
	document.getElementById("showwordsmenu").onclick = function () {
		document.getElementById("wordssidebar").style.width = "20%";
	}
	document.getElementById("closewordsmenu").onclick = function () {
		document.getElementById("wordssidebar").style.width = "0";
	}
}

function send_selected_files() {
	files = [];
	let w = document.getElementById("wordsmenu");
	w.childNodes.forEach(div => {
		let checkbox = div.childNodes[0];
		let filename = div.childNodes[1];
		if (checkbox.checked) {
			files.push(filename.textContent);
		}
	})
	SOCKET.send(JSON.stringify({"type":"file_choice", "files":files}));
}

// -------- HELPER FUNCTIONS -------

function be_captain() {
	document.getElementById("captred").style.visibility = "hidden";
	document.getElementById("captblue").style.visibility = "hidden";
	document.getElementById("captain_stuff").style.display = "flex";
	document.getElementById("captain_stuff").style.visibility =
			(TEAM === TURN && PHASE === "capt") ? "visible" : "hidden";
}

function be_deckhand() {
	document.getElementById("captred").style.visibility = "visible";
	document.getElementById("captblue").style.visibility = "visible";
	document.getElementById("captain_stuff").style.display = "none";
	for(let i=0; i < matrix.rows.length; i++) {
		const row = matrix.rows[i];
		for(let j=0; j < row.cells.length; j++) {
			const cell = row.cells[j];
			cell.style.backgroundColor = "white";
		}
	}

}

// -------- PROTOCOL HANDLERS -------

function player_list_handler(message) {
	TEAM_NAMES.forEach(team => {
		elementName = team + "team";
		let t = document.getElementById(elementName);
		while(t.firstChild) {
			t.removeChild(t.lastChild);
		}
		if (message["player"].team.toLowerCase() === team) {
			// update player team
			TEAM = team;

			// determine "pass" button visibility
			document.getElementById("pass").style.visibility = 
					(TEAM === TURN && PHASE === "team") ? "visible" : "hidden";
		
			// create first entry in team list for player
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
		// create an entry for every other player
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
		document.getElementById(key).style.backgroundColor = TILE_COLORS[data[key]];
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
			cell.style.backgroundColor = "white";
			cell.style.color = "black";
		}
	}

	uncovered_handler(message);
}

function entry_handler(message) {
	TURN = message["turn"].toLowerCase();
	switch (message["turn"]) {
		case "RED":
			document.querySelector("body").style.backgroundColor = "rgba(255, 0, 0, 0.1)";
			break;
		case "BLUE":
			document.querySelector("body").style.backgroundColor = "rgba(0, 0, 255, 0.1)";
			break;
		default:
			console.log("Interesting, turn of team " + message["team"]);
			break;
	} 

	if (message["entry"] === "") {
		// captain thinking phase
		PHASE = "capt";
		document.getElementById("entrydiv").style.display = "none";
		document.getElementById("captain_stuff").style.visibility =
			TEAM === TURN ? "visible" : "hidden";
		document.getElementById("pass").style.visibility = "hidden";
	} else {
		// team thinking phase
		PHASE = "team";
		document.getElementById("entrydiv").style.display = "flex";
		document.getElementById("entrytextdisplay").textContent = message["entry"].toUpperCase();
		document.getElementById("entrynumberdisplay").textContent = message["number"];
		document.getElementById("pass").style.visibility =
			TEAM === TURN ? "visible" : "hidden";
		document.getElementById("captain_stuff").style.visibility = "hidden";
	}
}

function secret_handler(message) {
	data = message["secret"];
	colors = {
		"RED":"rgba(255,0,0,0.2)",
		"BLUE":"rgba(100,149,237,0.2)",
		"SPEC":"rgba(245,222,179,0.2)",
		"KILLER":"rgba(0,0,0,0.3)"
	}
	for(let i=0; i < matrix.rows.length; i++) {
		const row = matrix.rows[i];
		for(let j=0; j < row.cells.length; j++) {
			const cell = row.cells[j];
			cell.style.backgroundColor = colors[data[i][j]];
		}
	}
}

function file_list_handler(message) {
	let w = document.getElementById("wordsmenu");
	while(w.firstChild) {
		w.removeChild(t.lastChild);
	}
	message["files"].forEach(file => {
		let div = document.createElement("div");
		div.id = "file_" + file;
		div.style.display = "flex";
		div.style.flexDirection = "row";
		div.style.alignContent = "center";
		let checkbox = document.createElement("input");
		checkbox.type = "checkbox";
		checkbox.style.margin = "0.2em";
		div.appendChild(checkbox);
		let p = document.createElement("p");
		p.textContent = file;
		p.style.margin = "0.2em";
		div.appendChild(p);
		w.appendChild(div);
	})
	let sendbutt = document.createElement("button");
	sendbutt.textContent = "Uaktualnij";
	sendbutt.onclick = send_selected_files;
	document.getElementById("wordssidebar").append(sendbutt);
}

function file_choice_handler(message) {
	let file_choice = new Set(message["files"]);
	let file_list = document.getElementById("wordsmenu");
	file_list.childNodes.forEach(div => {
		div.childNodes[0].checked = file_choice.has(div.childNodes[1].textContent);
	})
}

function alert_handler(message) {
	alert(message["message"]); //lol
}

function echo_handler(message) {
	console.log("Echo from server:\n");
	console.log(JSON.stringify(message["data"]));
}

var handlers = {
	"player_list": player_list_handler,
	"matrix": matrix_handler,
	"uncovered": uncovered_handler,
	"entry": entry_handler,
	"secret": secret_handler,
	"file_list": file_list_handler,
	"file_choice": file_choice_handler,
	"alert": alert_handler,
	"echo": echo_handler,
}

// ------------------ START -----------------

init_namechanger();
init_teambuttons();
init_entrybutton();
init_reset_buttons();
init_wordsmenu_buttons();
init_pass_button();

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
		td.style.backgroundColor = "white";
		td.textContent = "";
		td.onclick = function () {
			SOCKET.send(JSON.stringify({"type":"click", "id":td.id}));
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

SOCKET.onmessage = function(s) {
	// console.log("Message from server! : " + s.data);
	try {
		message = JSON.parse(s.data);	
	} catch (error) {
		console.log("Unparseable data: " + s.data);
	}

	handlers[message["type"]](message);
	

}
