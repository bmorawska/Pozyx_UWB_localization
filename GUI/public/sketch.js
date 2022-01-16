/* Units and sizes definition */
const pixelsInMeter = 100;
const gridDensity = pixelsInMeter;
const anchor_size = pixelsInMeter / 2;

/* Variables */
let sf;           // scaleFactor
let mx, my;       // mouse coords;
let px, py;       // pan X
let tx, ty;       // tag position
let anchors = []; // place for anchors positions and ids

/* Error estimation */
const errorSamplesNumber = 10;  // number of samples taking into account in radius estimation
const lastValuesX = [];         // values to estimate tag error radius in X
const lastValuesY = [];         // values to estimate tag error radius in Y
let lastAnimationRadius;
let animationRadius;
const animationAlpha = 0.6;

/* Websocket communication */
let connection_established = true;
let socket;


function setup() {
  createCanvas(windowWidth, windowHeight);

  // Variables initialization
  sf = 1;
  animationRadius = [0.0, 0.0];
  lastAnimationRadius = animationRadius;
  anchors = [
    ['0x6744',0.0, 0.0],
    ['0x674c',4.0, 0.0],
    ['0x672a',8.0, 0.0],
    ['0x675b',12.0,0.0],
    ['0x6e45',12.0,4.0],
    ['0x6743',8.0, 4.0],
    ['0x6757',4.0, 4.0],
    ['0x6e04',0.0, 4.0]
  ];


  tx = 0;
  ty = 0;
  px = 0;
  py = 0;

  iter_last_values = 0;

  // Websocket connection
  socket = io.connect('http://10.128.114.173:3000');
  socket.on('position', updateTag);
  socket.on('anchors', updateAnchors);
}

/**
 * The function load anchors positions and ids.
 * @param {*} data : data received from websocket.
 */
function updateAnchors(data) {
  anchors = data;
}

/**
 * The function updates tag position and scale it to GUI units. 
 * It is called as a callback, when websocket of topic 'position' is received.
 * @param {*} data : data received from websocket.
 */
function updateTag(data) {
  tx = data.x * pixelsInMeter;
  ty = data.y * pixelsInMeter;
}

/**
 * Calculate mean value of array.
 * @param {*} arr: input array
 * @returns mean value
 */
function mean(arr) {
  let sum = 0;
  for (let i = 0; i < arr.length; i++) {
    sum += arr[i];
  }
  return sum / arr.length;
}

/**
 * Estimates error in x and y as maximal difference between values in last errorSamplesNumber measurements.
 */
function estimateError() {
  lastValuesX.push(tx);
  lastValuesY.push(ty);
  if (lastValuesX.length <= 1) {
    return [0.0, 0.0];
  }
  else if (lastValuesX.length > 10) {
    lastValuesX.shift();
    lastValuesY.shift();
  }

  const meanX = mean(lastValuesX);
  const meanY = mean(lastValuesY);
  const maxDiffX = new Array(errorSamplesNumber).fill(0);
  const maxDiffY = new Array(errorSamplesNumber).fill(0);

  for (let i = 0; i < lastValuesX.length; i++)
  {
    maxDiffX[i] = Math.abs(lastValuesX[i] - meanX);
    maxDiffY[i] = Math.abs(lastValuesY[i] - meanY);
  }

  maxx = Math.max(...maxDiffX) * animationAlpha + lastAnimationRadius[0] * (1 - animationAlpha);
  maxy = Math.max(...maxDiffY) * animationAlpha + lastAnimationRadius[0] * (1 - animationAlpha);

  animationRadius = [maxx, maxy];
  lastAnimationRadius = animationRadius;
}

/**
 * Draws coordinate system in fit scale.
 */
function drawCoordinateSystem() {
  stroke(255, 0, 0, 32); // light red
  let gd = gridDensity * sf // scale

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

/**
 * Draws the tag and its error on a map.
 * @param {*} posX: x coordinate of tag 
 * @param {*} posY: y coordinate of tag
 */
function drawTag(posX, posY) {
  push();
  fill(255, 0, 0, 220);
  const radius = 50 * sf;
  ellipse(posX * sf + px, posY * sf + py, radius, radius);
  if (connection_established) {
    fill(255, 0, 0, 64);
    ellipse(posX * sf + px, posY * sf + py, radius + animationRadius[0] * sf, radius + animationRadius[1] * sf);
  }
  pop();
}

/**
 * Draws scale ruler onto a map.
 */
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

/**
 * Draws the shape of anchor (triangle).
 * @param {*} cx: x coordinate of anchor - center of triangle
 * @param {*} cy: y coordinate of anchor - center of triangle
 * @param {*} a:  side size of triangle
 */
function drawTriangle(cx, cy, a) {
  x1 = int(cx - a / 2);
  x2 = int(cx);
  x3 = int(cx + a / 2);

  y1 = int(cy + (1.73 * a) / 6);
  y2 = int(cy - (1.73 * a) / 4);
  y3 = y1

  triangle(x1, y1, x2, y2, x3, y3)
}

/**
 * Iterates through anchors and draws them on the map in fit scale.
 */
function drawAnchors() {
  let a = anchor_size * sf;
  stroke(0);
  fill(0)
  anchors.forEach(element => {
    x = (element[1] * pixelsInMeter * sf + px);
    y = (element[2] * pixelsInMeter * sf + py);
    drawTriangle(x, y, a);
    push();
    stroke(0)
    textSize(20);
    text(element[0], element[1] * 100 * sf + 30 + px, element[2] * 100 * sf + py);
    pop();
  })
}

/**
 * Loop function.
 */
function draw() {
  mx = mouseX;
  my = mouseY;

  background(255);
  drawAnchors();
  drawCoordinateSystem();
  drawRuler();
  estimateError();

  if (connection_established) {
    drawTag(tx, ty);
  }

  if (mouseIsPressed) {
    px -= pmouseX - mouseX;
    py -= pmouseY - mouseY;
  }

}

/**
 * Adjusts window size.
 */
function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

/**
 * When mouse wheel scrolled, the function changes scale.
 */
window.addEventListener("wheel", function (e) {
  if (e.deltaY > 0)
    sf *= 1.05;
  else
    sf *= 0.95;
});