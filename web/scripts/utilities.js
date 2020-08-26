let $ = (e) => document.getElementById(e);

let world = undefined;
let locks = undefined;
let keys = undefined;
let settings = undefined;
var path = [];
var unlocked = new Set([])

async function load_world() {
  world = await ee("get_world");
  locks = await ee("get_locks");
}

function load_from_url() {
  // read text from URL location
  var request = new XMLHttpRequest();
  request.open("GET", "http://www.puzzlers.org/pub/wordlists/pocket.txt", true);
  request.send(null);
  request.onreadystatechange = function () {
    if (request.readyState === 4 && request.status === 200) {
      var type = request.getResponseHeader("Content-Type");
      if (type.indexOf("text") !== 1) {
        return request.responseText;
      }
    }
  };
}

function set_header(name) {
  $("head_space").textContent = name;
}

async function ee(f, ...args) {
  // wrapper for getting python functions from eel
  // making the function calls a bit prettier
  return await eel[f](...args)();
}

function add_to_ul(ul, name, callback) {
  var para = document.createElement("p");
  var node = document.createTextNode(name);
  var li = document.createElement("li");
  para.appendChild(node);
  li.appendChild(para);

  if (ul === PATH_UL) {
    li.className = "path";
  } else {
    li.className = "menu";
  }

  if (callback != undefined) {
    li.onclick = callback;
  }

  ul.appendChild(li);
}

function clear_all() {
  // clear menu
  Object.values(MENU_UL.children).forEach((child) => {
    MENU_UL.removeChild(child);
  });

  // clear path
  Object.values(PATH_UL.children).forEach((child) => {
    PATH_UL.removeChild(child);
  });

  // clear and hide display box
  DISPLAY.textContent = "";
  DSP_BOX.style.display = "none";
}

function follow_path(obj, ...path) {
  for (let index = 0; index < path.length; index++) {
    const item = path[index];
    obj = obj[item];
  }

  return obj;
}

async function load_key_file() {
  const FIELD = $("uploadField");

  file = $("keyFile").files[0];

  try {
    obj = JSON.parse(await file.text());
  } catch (SyntaxError) {
    $("uploadResponseField").textContent = "Invalid 'keys' file!";
    return
  }

  keys = obj.keys;
  settings = obj.settings;

  keys.forEach(key => {
    doors = locks[key]
    doors.forEach(door => {
      unlocked.add(door)
    });
  });

  // clear all objects in the field
  Object.values(FIELD.children).forEach((child) => {
    FIELD.removeChild(child);
  });

  update_menu();
  FIELD.textContent = "Success!";

  display_seconds = 3
  setTimeout(() => {
    FIELD.style.display = "none";
    $('display-box').style.marginBottom = "0cm"
  }, display_seconds * 1000);
}

function is_unlocked(option) {
  let door
  if (path.length > 0) {
    door = path.join("/") + `/${option}`
  } else {
    door = option
  }
  return (unlocked.has(door))
}