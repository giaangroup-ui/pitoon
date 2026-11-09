/** Simple damped spring: x'' = -k*(x-target) - c*x' */
export class Spring {
  constructor(x=0,k=180,c=14){this.x=x;this.v=0;this.k=k;this.c=c;this.target=x}
  set(t){this.target=t} snap(t){this.x=this.target=t;this.v=0}
  step(dt){const a=-this.k*(this.x-this.target)-this.c*this.v; this.v+=a*dt; this.x+=this.v*dt; return this.x}
}
export function springsFrom(els){return els.map(e=>new Spring(+e.dataset.y||0))}
