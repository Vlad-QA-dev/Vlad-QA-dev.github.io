// «Матрица» из нулей и единиц
const c   = document.getElementById('matrix');
const ctx = c.getContext('2d');

let w = c.width  = window.innerWidth;
let h = c.height = window.innerHeight;

const cols = Math.floor(w / 20) + 1;
const ypos = Array(cols).fill(0);

function draw() {
  ctx.fillStyle = 'rgba(0,0,0,0.05)';
  ctx.fillRect(0, 0, w, h);

  ctx.fillStyle = '#0F0';
  ctx.font = '16px monospace';

  ypos.forEach((y, i) => {
    const bit = Math.random() < 0.5 ? '0' : '1';
    const x   = i * 20;
    ctx.fillText(bit, x, y);
    ypos[i] = (y > h && Math.random() > 0.975) ? 0 : y + 20;
  });
}

setInterval(draw, 60);

window.addEventListener('resize', () => {
  w = c.width  = window.innerWidth;
  h = c.height = window.innerHeight;
});