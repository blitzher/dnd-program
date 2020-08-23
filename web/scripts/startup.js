// start
let current_menu;
function update_menu() {
  clear_all();

  current_menu = follow_path(world, ...path);

  // update the menu itself
  for (let index = 0; index < Object.keys(current_menu).length; index++) {
    const element = Object.keys(current_menu)[index];

    let callback;
    switch (typeof current_menu[element]) {
      case typeof {}:
        callback = () => {
          path.push(element);
          update_menu();
        };
        break;

      case typeof []:
        callback = () => {
          path = current_menu[element];
          update_menu();
        };
        break;

      case typeof "":
        callback = () => {
          DSP_BOX.style.display = "block";
          DISPLAY.textContent = current_menu[element];
        };
        break;

      default:
        break;
    }

    add_to_ul(MENU_UL, element, callback);
  }

  // update the path
  add_to_ul(PATH_UL, "Alterace", () => {
    path = [];
    update_menu();
  });
  for (let index = 0; index < path.length; index++) {
    const element = path[index];

    let callback = () => {
      path = path.slice(0, index + 1);
      update_menu();
    };

    add_to_ul(PATH_UL, element, callback);
  }
}

async function main() {
  add_to_ul(PATH_UL, "Alterace");

  add_to_ul(MENU_UL, "Loading...");
  await load_world();

  update_menu();
}

main();
