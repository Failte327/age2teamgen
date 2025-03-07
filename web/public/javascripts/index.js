const mapUrl = "/map";

window.onload = async function getPlayers() {
  const response = await fetch("/get_players");
  response.json().then((players) => {
    for (var player in players) {
      var form = document.createElement("form");
      form.id = `${player}AddToList`;
      form.action = `javascript:addPlayerToList(${player})`;
      var button = document.createElement("button");
      button.classList = ["button", "btn"];
      button.innerHTML = `${player}`;
      button.id = player;
      button.type = "submit";
      document.querySelector("#add-player-container").appendChild(form);
      document.querySelector(`#${player}AddToList`).appendChild(button);
    }
  });
};

function addPlayerToList(name) {
  var form = document.createElement("form");
  form.id = `${name.id}Form`;
  form.action = `javascript:removePlayerFromList(${name.id})`;
  var player = document.createElement("button");
  player.innerHTML = name.id;
  player.id = name.id;
  player.style = "background-color:green";
  player.type = "submit";
  document.querySelector(`#${name.id}`).remove();
  document.querySelector("#current-players").appendChild(form);
  document.querySelector(`#${name.id}Form`).appendChild(player);
}

function removePlayerFromList(name) {
  var player = document.createElement("button");
  player.classList = ["button", "btn"];
  player.innerHTML = name.id;
  player.id = name.id;
  player.type = "submit";
  document.querySelector(`#${name.id}`).remove();
  document.querySelector(`#${name.id}AddToList`).appendChild(player);
}

function getMap() {
  fetch(mapUrl)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      response.text().then((text) => {
        if (document.querySelector(`#chosenMap`) !== null) {
          document.querySelector(`#chosenMap`).remove();
        }
        var el = document.createElement("div");
        el.innerHTML = text;
        el.id = "chosenMap";
        document.querySelector("#maps").appendChild(el);
        return text;
      });
    })
    .then((data) => {
      console.log(data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

const statsUrl = "/stats";

function getStats(user) {
  fetch(`${statsUrl}?user=${user[0].innerHTML}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      response.text().then((text) => {
        if (document.querySelector(`#innerStats`) !== null) {
          document.querySelector(`#innerStats`).remove();
        }
        var el = document.createElement("div");
        el.innerHTML = text;
        el.id = "innerStats";
        document.querySelector("#stats").appendChild(el);
        return text;
      });
    })
    .then((data) => {
      console.log(data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

async function getTeams() {
  var playerList = [];
  var loader = document.createElement("div");
  var listElement = document.querySelector("#current-players").childNodes;
  listElement.forEach((i) => {
    if (i[0]) {
      playerList.push(i[0]["id"]);
    }
  })
  loader.classList = "loader";
  loader.id = "loader";
  if (document.querySelector("#loader")) {
    document.querySelector("#loader").remove();
  }
  document.querySelector("#teams").appendChild(loader);
  const response = await fetch("/generate_teams", {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(playerList),
  });
  response.json().then((data) => {
    if (document.querySelector("#loader")) {
      document.querySelector("#loader").remove()
    }
    var ele = document.createElement("div");
    ele.innerHTML = data;
    document.querySelector("#teams").appendChild(ele);
  })
}