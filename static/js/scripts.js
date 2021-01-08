//========================================================================
// Drag and drop image handling
//========================================================================

var fileDrag = document.getElementById("file-drag");
var fileSelect = document.getElementById("file-upload");
var inputLink = document.getElementById("basic-url");

// Add event listeners
fileDrag.addEventListener("dragover", fileDragHover, false);
fileDrag.addEventListener("dragleave", fileDragHover, false);
fileDrag.addEventListener("drop", fileSelectHandler, false);
fileSelect.addEventListener("change", fileSelectHandler, false);


function fileDragHover(e) {
  // prevent default behaviour
  e.preventDefault();
  e.stopPropagation();
  fileDrag.style.border = "none";
  fileDrag.className = e.type === "dragover" ? "upload-box dragover" : "upload-box";
}

function fileSelectHandler(e) {
  // handle file selecting
  var files = e.target.files || e.dataTransfer.files;
  fileDragHover(e);
  fileDrag.style.borderStyle = "none";
  for (var i = 0, f; (f = files[i]); i++) {
    previewFile(f);
  }
  inputLink.disabled = true;
}

//========================================================================
// Web page elements for functions to use
//========================================================================

var imagePreview = document.getElementById("image-preview");
var imageBox = document.getElementById("image-box");
var uploadCaption = document.getElementById("upload-caption");
var loader = document.getElementById("loader");


var textBox = document.getElementById("text-box");


var typeImage = 0; // type:  0-previewFile, 1-previewURL, 2-previewBase64

inputLink.oninput = function () {
  var val = inputLink.value;
  if (checkURL(val) == true) {
    previewURL(val);
    typeImage = 1;

  }
  else if (val.length == 0) {
    fileDrag.style.border = "0.1rem dashed #007bff";
    hide(imagePreview);
    show(uploadCaption);
  }
  else {
    typeImage = 2;
    previewBase64(val);
  }
}

function checkURL(url) {
  return (url.match(/\.(jpeg|jpg|gif|png)$/) != null);
}

/**
 * Convert an image 
 * to a base64 url
 * @param  {String}   url         
 * @param  {Function} callback    
 * @param  {String}   [outputFormat=image/png]           
 */
function convertImgToBase64(url, callback, outputFormat) {
  var canvas = document.createElement('CANVAS');
  var ctx = canvas.getContext('2d');
  var img = new Image;
  img.crossOrigin = 'Anonymous';
  img.onload = function () {
    canvas.height = img.height;
    canvas.width = img.width;
    ctx.drawImage(img, 0, 0);
    var dataURL = canvas.toDataURL(outputFormat || 'image/jpeg');
    callback.call(this, dataURL);
    // Clean up
    canvas = null;
  };
}


// function toDataURL(url, callback) {
//   var xhr = new XMLHttpRequest();
//   xhr.open('get', url);
//   xhr.responseType = 'blob';
//   xhr.onload = function () {
//     var fr = new FileReader();

//     fr.onload = function () {
//       callback(this.result);
//     };

//     fr.readAsDataURL(xhr.response); // async call
//   };

//   xhr.send();
// }

//========================================================================
// Main button events
//========================================================================

function submitImage() {

  var myListText = document.getElementById('resultCeleb');
  var btnSubmit = document.getElementById('btn-submit');
  btnSubmit.disabled = true;
  // var btnClean = document.getElementById('btn-clean');
  // btnClean.disabled = true;
  // console.log(typeImage)
  switch (typeImage) {
    case 0:
      if (!imagePreview.src || !imagePreview.src.startsWith("data")) {
        window.alert("Please select an image before submit.");
        return;
      }
      predictImage(imagePreview.src);
      break;
    case 1:
      convertImgToBase64(imagePreview.src, function (base64Img) {
        console.log(base64Img);
        previewBase64(base64Img);
      });
      predictImage(imagePreview.src)
      break;
    case 2:
      predictImage(inputLink.value)
      break;
  }

  typeImage = 0;
  loader.classList.remove("hidden");

  // call the predict function of the backend

}



function clearImage() {
  var myListText = document.getElementById('resultCeleb');

  if (document.body.contains(document.getElementById('image-box'))) {
    var myobj = document.getElementById("image-box");
    while (myobj.firstChild) {
      myobj.removeChild(myobj.lastChild);
    }
  }

  fileDrag.style.border = "0.1rem dashed #007bff";

  inputLink.disabled = false;
  inputLink.value = "";

  var btnSubmit = document.getElementById('btn-submit');
  btnSubmit.disabled = false;

  // reset selected files
  fileSelect.value = "";

  // remove image sources and hide them
  imagePreview.src = "";

  hide(imagePreview);
  hide(loader);
  hide(textBox);

  show(uploadCaption);
}

function previewURL(link) {
  displayImage(link, "image-preview");
  show(imagePreview);
  hide(uploadCaption);
  fileDrag.style.border = "none";
}

function previewBase64(str) {
  fileDrag.style.border = "none";
  displayImage(str, "image-preview");
  show(imagePreview);
  hide(uploadCaption);
}

function previewFile(file) {
  // show the preview of the image
  // console.log(file.name);

  fileDrag.style.border = "none";
  var fileName = encodeURI(file.name);

  var reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onloadend = () => {
    displayImage(reader.result, "image-preview");

    show(imagePreview);
    hide(uploadCaption);
  };
}

//========================================================================
// Helper functions
//========================================================================

function predictImage(image) {

  console.log(JSON.stringify(image));
  fetch("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ "base64": image })

  })
    .then(resp => {
      if (resp.ok)
        resp.json().then(data => {
          // var btnClean = document.getElementById('btn-clean');
          // btnClean.disabled = false;
          console.log(data.length);
          if (data.length > 0) {
            CreateFaceResult(data);
            hide(loader);
            textBox.classList.remove("hidden");
          } else {
            window.alert("Hinh anh hien tai ko co nguoi noi tieng");
            hide(loader);
          }

        });
    })
    .catch(err => {
      console.log("An error occured", err.message);
      window.alert("Oops! Something went wrong.");
    });
}

function displayImage(image, id) {
  // display image on given id <img> element
  let display = document.getElementById(id);
  console.log.apply(image);
  display.src = image;
  show(display);
}

function displayResult(data) {
  // display the result
  imageDisplay.classList.remove("loading");
  hide(loader);
}

function hide(el) {
  // hide an element
  el.classList.add("hidden");
}

function show(el) {
  // show an element
  el.classList.remove("hidden");
}

function CreateFaceResult(listData) {
  for (i = 0; i < listData.length; i++) {
    console.log("vo", listData[i].bboxes)
    var div = document.createElement("DIV");
    div.setAttribute('id', 'result');
    var x = document.createElement("IMG");
    x.src = listData[i].base64;
    var canvas = document.createElement("CANVAS");
    canvas.setAttribute('id', 'face')
    var ctx = canvas.getContext("2d");
    var w = listData[i].bboxes[2] - listData[i].bboxes[0];
    var h = listData[i].bboxes[3] - listData[i].bboxes[1];
    if (w > 300 || h > 150) {
      canvas.width = w;
      canvas.height = h;
    }
    ctx.drawImage(imagePreview, listData[i].bboxes[0], listData[i].bboxes[1], w, h, 2, 2, w, h);

    div.appendChild(canvas);
    div.appendChild(x);
    var para = document.createElement("P")
    para.setAttribute('text-align', ':center')
    para.innerText = listData[i].labels;
    div.appendChild(para);
    imageBox.appendChild(div);
  }
}
