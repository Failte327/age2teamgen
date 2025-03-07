var express = require('express');
var router = express.Router();
var maps = ["Acclivity", "Acropolis", "African Clearing", "Aftermath", "Alpine Lakes", "Amazon Tunnel", "Arabia", "Archipelago", "Arena", "Atacama", "Baltic", "Black Forest", "Bog Islands", "Bogland", "Budapest", "Cenotes", "City of Lakes", "Coastal", "Coastal Forest", "Continental", "Crater", "Crater Lake", "Crossroads", "Enclosed", "Eruption", "Fortress", "Four Lakes", "Frigid Lake", "Ghost Lake", "Gold Rush", "Golden Pit", "Golden Swamp", "Greenland", "Haboob", "Hamburger", "Hideout", "Highland", "Hill Fort", "Islands", "Kawasan", "Kilimanjaro", "Land Madness", "Land Nomad", "Lombardia", "Lowland", "Mangrove Jungle", "Marketplace", "Meadow", "Mediterranean", "MegaRandom", "Michi", "Migration", "Mongolia", "Morass", "Mountain Pass", "Mountain Range", "Mountain Ridge", "Nile Delta", "Nomad", "Northern Isles", "Oasis", "Pacific", "Islands", "Ravines", "Ring Fortress", "Rivers", "Runestones", "Sacred Springs", "Salt Marsh", "Sandbank", "Scandinavia", "Seize The Mountain", "Serengeti", "Shoals", "Socotra", "Steppe", "Team Islands", "Team Moats", "Valley", "Volcanic Island", "Wade", "Water", "Nomad", "Wolf Hill", "Yucatan"]
// helper function to determine if team size is odd or even
function isWholeNumber(num) {
  return Number.isInteger(num) && num >= 0;
}
// ratings determined by an average of rating estimates collected from 2 of the players in the group
var playersToRatings = { "sjhalbleib": 1200, "reklewt": 1120, "smhalbleib": 1030, "nomrom": 1325, "djhalbleib": 1060, "scotthalb": 990, "charletttehalbleib": 950, "iceyman8": 925, "country_slicker": 890, "kolob_eagle25": 955, "quintonius": 1150, "meghalb": 850, "brando": 710, "stealy5": 1175, "azorr": 900, "acbishop": 900, "chad": 1250, "computer": 850};
/* players mapped to their aoe2insights.com ids, for now this method of determining teams is deprecated
var playersToIds  = {"sjhalbleib": 4289859, "reklewt": 5375940, "smhalbleib": 6877853, "nomrom": 2804382, "djhalbleib": 6867836, "scotthalb": 6867861, "charletttehalbleib": 10061690, "iceyman8": 8230988, "country_slicker": 10785824, "kolob_eagle25": 6888316, "quintonius": 2182022, "meghalb": 7451904, "brando": 7436245, "brandonnelson68": 7436245, "stealy5": 6901071, "azorr": 10455474, "acbishop": 4527003, "chad": 1198985, "iceyman8": 8230988}
*/

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'AoE2 Team Generator' });
});

router.get('/map', function(req, res, next) {
  var rand = Math.floor(Math.random() * maps.length);
  res.send(maps[rand])
})

router.get('/get_players', function(req, res, next) {
  res.send(playersToRatings);
})

router.post('/generate_teams', function(req, res, next) {
  var data = req.body;
  var playerList = [];
  var currentPlayers = {};
  for (var i in data) {
    playerList.push(data[i]);
  };
  for (var player in playerList) {
    var name = playerList[player];
    currentPlayers[name] = playersToRatings[name];
  }
  var teamSize = (Object.keys(currentPlayers).length) / 2;
  if (!isWholeNumber(teamSize)) {
    res.send({"error": "Team size is uneven, please add a computer for matching purposes."})
  } else {
    var teamsSet = false;
    var playerNames = Object.keys(currentPlayers);
    var loops = 0;
    while (!teamsSet) {
      var team1 = [];
      var team2 = [];
      while (team1.length < teamSize) {
        var randomNum = Math.floor(Math.random() * playerNames.length);
        var choice = playerNames[randomNum];
        if (!team1.includes(choice)) {
          team1.push(choice);
        }
      }
      while (team2.length < teamSize) {
        var randomNum = Math.floor(Math.random() * playerNames.length);
        var choice = playerNames[randomNum];
        if (!team1.includes(choice) && !team2.includes(choice)) {
          team2.push(choice);
        }
      }
      var team1Score = 0;
      var team2Score = 0;
      for (var i in team1) {
        team1Score = team1Score + currentPlayers[team1[i]];
      }
      for (var i in team2) {
        team2Score = team2Score + currentPlayers[team2[i]];
      }
      if (team1Score > team2Score) {
        var deficit = team1Score - team2Score;
        if (deficit < 300) {
          teamsSet = true;
        }
      } else {
        var deficit = team2Score - team1Score;
        if (deficit < 300) {
          teamsSet = true;
        }
      }
      loops++
      if (loops > 100) {
        teamsSet = true;
      }
    }
    res.send({"team 1": team1, "team 2": team2})
  }
})

module.exports = router;
