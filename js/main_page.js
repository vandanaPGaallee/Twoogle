var response = null;
var obj = {}
obj["topic"] = ""
obj["city"] = ""
obj["lang"] = ""
obj["query"] = ""
var topic = {"Infrastructure":"infra"}
var map = {"Infrastructure":"infra", "Paris":"France", "English": "en", "French":"fr", "Hindi":"hi","Spanish":"es", "Thai":"th"}
var city = {"Paris":"france"}
var url = 'https://55324216.ngrok.io/getDefaultResults'

function AddTweets(screen_name, name, summary, tweet_link) {
    var node = document.createElement("DIV")
    node.id = "tweet"
    var head = document.createElement("H6");
    head.id = "tweet_heading"
    head.appendChild(document.createTextNode(name));
    var link = document.createElement('a');
    link.id = "tweet_link"
    link.setAttribute('href', "https://twitter.com/user/status/" + tweet_link);
    link.appendChild(document.createTextNode("https://twitter.com/user/status/" + tweet_link));
    var text = document.createElement("p");
    text.id = "tweet_text"
    text.appendChild(document.createTextNode(summary));
    node.appendChild(head)
    node.appendChild(link)
    node.appendChild(text)
    document.getElementById("tweets").appendChild(node);
}


function AddTrends(tag, count) {
    var node = document.createElement("DIV")
    node.id = "trend"
    var head = document.createElement("H6");
    head.id = "trend_heading"
    head.appendChild(document.createTextNode(tag));
    var text = document.createElement("p");
    text.id = "trend_count"
    text.appendChild(document.createTextNode(count));
    node.appendChild(head)
    node.appendChild(text)
    // document.getElementById("trends").appendChild(node);
    return node
}

  window.onload = function(){
    if(Boolean(window.location.search)){
      var data = window.location.search.substring(1);
      data = data.split("&").filter(x => x.split("=")[0] === "query")[0]
      if(Boolean(data)){
        data = data.split("=");
        document.getElementById("search_panel").value = decodeURIComponent(data[1]);
        document.getElementById("tweets").innerHTML = ""
        obj["query"] = decodeURIComponent(data[1]);
        getJSON()
        // write code here to make api call to fetch tweets from api
      }
    }
  }
  
  fetch("https://55324216.ngrok.io/trending").then(x => x.json()).then(y => {
    document.getElementById("trends").innerHTML = '<h3><b>Trending for You</b></h3>' + y.map(data => {
      return `<div id="trend"><div id="trend_head"> #${data.label}</div><div id="trend_count">${data.value} Tweets</div></div>`
    }).join("");
  })
  
  // fetch("https://f749e1b9.ngrok.io/trending").then(x => x.json()).then(y => {
  //   document.getElementById("trends").innerHTML = y.map(y=>data, function(data) {
  //       var node = document.createElement("DIV")
  //       node.id = "trend"
  //       var head = document.createElement("H6");
  //       head.id = "trend_heading"
  //       head.appendChild(document.createTextNode(data.label));
  //       var text = document.createElement("p");
  //       text.id = "trend_count"
  //       text.appendChild(document.createTextNode(data.val));
  //       node.appendChild(head)
  //       node.appendChild(text)
  //       // document.getElementById("trends").appendChild(node);
  //       return node
  //   }).join("");
  // })
  
  function openDashboard(){
    var query = document.getElementById("search_panel").value;
    console.log(query)
    window.location.replace("dashboard.html?query="+query);
  }
function clearFilters() {
  obj["topic"] = ""
  obj["city"] = ""
  obj["lang"] = ""
  $('select').prop('selectedIndex', 0);
}

function SearchResults(id, param) {
  console.log(document.getElementById(id).value)
  document.getElementById("tweets").innerHTML = ""
  obj[param] = document.getElementById(id).value;
  clearFilters()
  getJSON()
}


function ApplyFilter(id, param) {
  console.log("param triggered")
  document.getElementById("tweets").innerHTML = ""
  var sel = document.getElementById(id);
  var value = sel.options[sel.selectedIndex].text;
  if(value in map) {
    obj[param] = map[value]
  } else {
    obj[param] = value
  }
  console.log(obj)
  getJSON()
}

function RetrieveTweets(docs) {
    var x,i;
    for (i in docs){
        x = docs[i]
        console.log(x)
        AddTweets(x.screen_name != null ? x.screen_name : "", x.name != null ? x.name : "", x.summary, x.link != null ? x.link : "");
    }
}

var getJSON = function() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-type','application/json; charset=utf-8');
    // xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
    // sxhr.setRequestHeader('Access-Control-Allow-Methods', '*');
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        console.log("called : ");
        var jsonResponse = xhr.response;
        // console.log(jsonResponse);
        RetrieveTweets(jsonResponse);
      } else {
         console.log("failed");
      }
    };
    xhr.send(JSON.stringify(obj));
};