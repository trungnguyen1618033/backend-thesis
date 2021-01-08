
var list = document.getElementById("list");
var img = document.getElementById("image_celeb");
var btn = document.getElementById("listCeleb");
function show(el) {
  // show an element
  el.classList.remove("hidden");
}
function hide(el) {
  // hide an element
  el.classList.add("hidden");
}

function submitCeleb() {
  listCeleb();
}

function listCeleb() {
  fetch("/index", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
  })
    .then(resp => {
      if (resp.ok)
        resp.json().then(data => {
          hide(img);
          show(list);
          btn.disabled = true;
          $('#example').DataTable({
            data: data.celeb,
            "columns": [
              { "data": "stt" },
              { "data": "ten" },
              {
                "data": "link",
                "render": function (data, type, row, meta) {
                  return '<a href="' + data + '">Link</a>';
                }
              }
            ]
          });
        });
    })
    .catch(err => {
      console.log("An error occured", err.message);
      window.alert("Oops! Something went wrong.");
    });
}
