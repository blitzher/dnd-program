let $ = (e) => document.getElementById(e);

let world = undefined;
var path = [];

async function load_world() {
  world = await ee("get_world");
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
