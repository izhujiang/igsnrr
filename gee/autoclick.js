function runTaskList() {
  var tasklist = document
    .getElementById("task-pane")
    .shadowRoot.querySelectorAll(
      "div.task.legacy.type-EXPORT_IMAGE.awaiting-user-config"
    );
  for (var i = 0; i < tasklist.length; i++)
    tasklist[i].getElementsByClassName("run-button")[0].click();
}

function confirmAll() {
  var diags = document.getElementsByTagName("ee-image-config-dialog");
  // console.log(diags.length);
  for (var i = 0; i < diags.length; i++) {
    run =
      diags[i].shadowRoot.children[0].shadowRoot.querySelector(".ok-button");
    run.click();
  }
}
runTaskList();
setTimeout(() => {
  confirmAll();
}, 60000);
