let gridDensity;
const pixelsInMeter=100;
let sf; // scaleFactor
let mx, my; // mouse coords;

let anchors = [];
let anchor_size;
let px = 0; // pan X
let py = 0; // pan Y

let tx, ty; //tag position

let animation_radius;
let connection_established = true;

var socket;


function setup() {
  createCanvas(windowWidth, windowHeight);

  gridDensity = pixelsInMeter;
  sf = 1;
  animation_radius = 0;
  anchors = [['0x1234', 0.0, 0,0],
             ['0x5678', 10.0, 10.0],
             ['0x9012', 0.0, 10.0],
             ['0x3456', 10.0, 0.0],
             ['0x7890', -10.0, -10.0]]
  anchor_size = pixelsInMeter / 2;

  tx = 0;
  ty = 0;

  socket = io.connect('http://127.0.0.1:3000');
  socket.on('position', updateTag);

}

function updateTag(data) {
  //console.log(data);
  tx = data.x * pixelsInMeter;
  ty = data.y * pixelsInMeter;
}

function drawCoordinateSystem() {
  stroke(255, 0, 0, 32);
  let gd = gridDensity * sf
  // vertical lines
  for (let i = px; i > -windowWidth; i = i - gd) {
    line(i, 0, i, windowHeight);
  }
  for (let i = px; i < windowWidth; i = i + gd) {
    line(i, 0, i, windowHeight);
  }
  // horizontal lines
  for (let i = py; i > -windowHeight; i = i - gd) {
    line(0, i, windowWidth, i);
  }
  for (let i = py; i < windowHeight; i = i + gd) {
    line(0, i, windowWidth, i);
  }
}

function return2Zero() {
  sf = 1;
  px = 0;
  py = 0;
}

/* Emiting example
function mouseDragged() {
  console.log('Sending:', mx, my);
  let data = {
    x: mx,
    y: my
  }
  socket.emit('mouse', data);
}
*/

function drawTag(posX, posY) {
  animation_radius += 2;
  if (animation_radius > 100) {
    animation_radius = 0;
  }

  push();
  fill(255, 0, 0, 220);
  ellipse(posX * sf + px, posY * sf + py, 50 * sf, 50 * sf);
  if (connection_established) {
    fill(255, 0, 0, 64);
    ellipse(posX * sf + px, posY  *sf + py, animation_radius * sf, animation_radius * sf);
  }
  pop();
}

function drawRuler() {
  push();
  stroke(0)
  line(windowWidth - 200, windowHeight - 50, windowWidth - 100, windowHeight - 50);
  line(windowWidth - 200, windowHeight - 40, windowWidth - 200, windowHeight - 60);
  line(windowWidth - 100, windowHeight - 40, windowWidth - 100, windowHeight - 60);
  textSize(30);
  text('1m', windowWidth - 170, windowHeight - 55);  
  pop();

}

function drawTriangle(cx, cy, a) {
  x1 = int(cx - a / 2) ;
  x2 = int(cx);
  x3 = int(cx + a / 2);

  y1 = int(cy + (1.73 * a) / 6);
  y2 = int(cy - (1.73 * a) / 4);
  y3 = y1

  triangle(x1, y1, x2, y2, x3, y3)
}

function drawAnchors() {
  let a = anchor_size * sf;
  stroke(0);
  fill(0)
  anchors.forEach(element => {
    x = (element[1] * pixelsInMeter * sf + px) ;
    y = (element[2] * pixelsInMeter * sf + py);
    drawTriangle(x , y, a);
    push();
    stroke(0)
    textSize(20);
    text(element[0], element[1] * 100 * sf + 30 + px, element[2] * 100 * sf + py);  
    pop();
  })
}


function draw() {
  mx = mouseX;
  my = mouseY;

  background(255);
  drawAnchors();
  drawCoordinateSystem();
  drawRuler();

  if (connection_established) {
    drawTag(tx, ty);
  }

  if (mouseIsPressed) {
    px -= pmouseX - mouseX;
    py -= pmouseY - mouseY;
  }

}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}


window.addEventListener("wheel", function (e) {
  if (e.deltaY > 0)
    sf *= 1.05;
  else
    sf *= 0.95;
});