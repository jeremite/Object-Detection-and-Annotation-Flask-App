
const image = document.getElementById('image');
const canvas = document.getElementById('canvas');
const dropContainer = document.getElementById('container');
const warning = document.getElementById('warning');
const fileInput = document.getElementById('fileUploader');
var filename = "";
var ctx = canvas.getContext('2d');

// for drawing rectangle
var rect = {};
var drag = false;
var guides = false;
var imageObj = null;
var if_has = false;
var cur_rects = []


// for guides
var $canvas=$("#canvas");
var canvasOffset=$canvas.offset();
var offsetX=canvasOffset.left;
var offsetY=canvasOffset.top;

// url for ajax
const URL = "/api"
const URL_SAVE ="/save"
// const URL = "http://192.168.163.132:5000/api/"

/*
function GetUrlPara()
　　{
	var protocol = window.location.protocol.toString();
	// var host =  window.location.host.toString();
	var host =  document.domain.toString();
        var port = window.location.port.toString();
	var url = protocol + '//' + host + ":5000/api/";
	return url;
　　}


const URL = GetUrlPara()
// alert(URL);
*/

function preventDefaults(e) {
  e.preventDefault()
  e.stopPropagation()
};


function windowResized() {
  let windowW = window.innerWidth;
  if (windowW < 480 && windowW >= 200) {
    dropContainer.style.display = 'block';
  } else if (windowW < 200) {
    dropContainer.style.display = 'none';
  } else {
    dropContainer.style.display = 'block';
  }
}

['dragenter', 'dragover'].forEach(eventName => {
  dropContainer.addEventListener(eventName, e => dropContainer.classList.add('highlight'), false)
});

['dragleave', 'drop'].forEach(eventName => {
  dropContainer.addEventListener(eventName, e => dropContainer.classList.remove('highlight'), false)
});

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropContainer.addEventListener(eventName, preventDefaults, false)
});

dropContainer.addEventListener('drop', gotImage, false)

// send image to server, then receive the result, draw it to canvas.
function communicate(img_base64_url) {
  $.ajax({
    url: URL,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({"image": img_base64_url}),
    dataType: "json"
  }).done(function(response_data) {
      console.log("send back successfullly")
      drawResult(response_data.results);
  });
}

// handle image files uploaded by user, send it to server, then draw the result.
function parseFiles(files) {
  const file = files[0];
  filename = file.name;
  console.log("file name is:"+filename);
  const imageType = /image.*/;
  if (file.type.match(imageType)) {
    warning.innerHTML = '';
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      image.src = reader.result;
      // send the img to server
      communicate(reader.result);

    }
  } else {
    setup();
    warning.innerHTML = 'Please drop an image file.';
  }

}

// call back function of drag files.
function gotImage(e) {
  const dt = e.dataTransfer;
  const files = dt.files;
  if (files.length > 1) {
    console.error('upload only one file');
  }
  parseFiles(files);
}

// callback function of input files.
function handleFiles() {
  parseFiles(fileInput.files);
}

// callback fuction of button.
function clickUploader() {
  fileInput.click();
  // set the drag and guids event to false
  drag=false;
  guides = false;
  canvas.removeEventListener('mousemove', mouseMove, false);
  canvas.removeEventListener('mousedown', mouseDown, false);
  canvas.removeEventListener('mouseup', mouseUp, false);
  canvas.removeEventListener('keydown', keyDown,false);
}

// draw results on image.
function drawResult(results) {

    canvas.width = image.width;
    canvas.height = image.height;
    ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0);
    for(bboxInfo of results) {
      bbox = bboxInfo['bbox'];
      class_name = bboxInfo['name'];
      score = bboxInfo['conf'];

      ctx.beginPath();
      ctx.lineWidth="2";

      ctx.strokeStyle="red";
      ctx.fillStyle="red";

      ctx.rect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]);
      ctx.stroke();

      ctx.font="20px Arial";

      let content = class_name + " " + parseFloat(score).toFixed(2);
      ctx.fillText(content, bbox[0], bbox[1] < 20 ? bbox[1] + 30 : bbox[1]-5);
  }

}

function draw(){
  console.log("clear canvas and rects");
  cur_rects = [];
  ctx.clearRect(0, 0, canvas.width,canvas.height);
  ctx.drawImage(image, 0, 0);

  canvas.addEventListener('keydown', keyDown,false);
  canvas.addEventListener('mousemove', mouseMove, false);
  canvas.addEventListener('mousedown', mouseDown, false);
  canvas.addEventListener('mouseup', mouseUp, false);


}
function keyDown(e){
  console.log("keydown")
  if (e.key == 'w') {
    console.log("key is w")
    guides=true;
  }

}
function mouseDown(e) {
    rect.startX = e.pageX - this.offsetLeft;
    rect.startY = e.pageY - this.offsetTop;
    drag = true;
}

function mouseUp() {
  drag = false;
  guides = false;
  cur_rects.push([rect.startX, rect.startY, rect.w, rect.h])
}

function mouseMove(e) {
    console.log("guides is "+guides)
    if(guides){
        const x =e.pageX - this.offsetLeft;
        const y = e.pageY - this.offsetTop;
        const { height, width } = canvas;
        ctx.clearRect(0, 0, width, height);
        ctx.drawImage(image, 0, 0);
        for (r of cur_rects){
          ctx.strokeRect(r[0],r[1],r[2],r[3]);
        }
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.closePath();
        ctx.strokeStyle = 'red';
        ctx.stroke();
    }
    if (drag) {
        ctx.drawImage(image, 0, 0);
        for (r of cur_rects){
          ctx.strokeRect(r[0],r[1],r[2],r[3]);
        }
        console.log("draw img");
        rect.w = (e.pageX - this.offsetLeft) - rect.startX;
        rect.h = (e.pageY - this.offsetTop) - rect.startY;
        ctx.strokeStyle = 'red';
        ctx.strokeRect(rect.startX, rect.startY, rect.w, rect.h);
        ctx.fillStyle = "rgb(255,0,0,0.5)"//"blue";
        ctx.fillRect(rect.startX, rect.startY, rect.w, rect.h);

    }
}


// mouse pointer guides
/*
$("#canvas").mousemove(function(e){handleMouseMove(e);});


function handleMouseMove(e){
    e.preventDefault();
    e.stopPropagation();

    mouseX=parseInt(e.clientX-offsetX);
    mouseY=parseInt(e.clientY-offsetY);
    let ctx=canvas.getContext("2d");

    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.beginPath();
    ctx.moveTo(mouseX,mouseY-canvas.height);
    ctx.lineTo(mouseX,mouseY+canvas.height);
    ctx.moveTo(mouseX-canvas.width,mouseY);
    ctx.lineTo(mouseX+canvas.width,mouseY);
    ctx.stroke();
}
*/

function save() {
  $.ajax({
    url: URL_SAVE,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({"coordinates": cur_rects,"width":image.width, "height":image.height,"filename": filename}),
    dataType: "json",
    success: function(data){
         console.log("save success");
         console.log("return are:"+JSON.parse(data['num_f']))
         document.getElementById("number").innerHTML=JSON.parse(data['num_f']);
        //$( ".sortable" ).sortable( "refresh" );
       },
    error: function(err) {
           console.log("lose");
       }
});
}
// 初始化函数
async function setup() {
  // Make a detection with the default image
  // detectImage();
  console.log("init");
  //var canvasTmp = document.createElement("canvas");
  //canvasTmp.width = image.width;
  //canvasTmp.height = image.height;
  //var ctx = canvasTmp.getContext("2d");
  let c = document.getElementById("canvas")
  let x = c.getContext('2d');
  let img = new Image();
  img.onload = function() {
      c.width = img.width;
      c.height = img.height;
      x.clearRect(0, 0, c.width, c.height);
      x.drawImage(img, 0, 0);
    };
  img.src = '/static/images/demo_res.png';


  //ctx.drawImage(image, 0, 0);
  //var dataURL = canvasTmp.toDataURL("image/png");
  //communicate(dataURL)
}
$(document).ready(function($){
setup();
});
