
const C = require(process.argv[2]);
const pubs = { mu: 0.012150584270571545,
  C: {L1:3.1883411054012485, L2:3.1721604503998044, L3:3.0121471493422489, L4:2.9879970524275450, L5:2.9879970524275450} };
const mine = { mu: C.MU_EARTH_MOON };
// instrument check at the published mu (isolates Omega definition + root solve from the mu choice)
const lpP = C.lagrangePoints(pubs.mu);
const lpM = C.lagrangePoints(mine.mu);
let maxRelP = 0, maxRelM = 0;
for (const k of ["L1","L2","L3","L4","L5"]) {
  const relP = Math.abs(lpP.points[k].C - pubs.C[k]) / Math.abs(pubs.C[k]);
  const relM = Math.abs(lpM.points[k].C - pubs.C[k]) / Math.abs(pubs.C[k]);
  if (relP > maxRelP) maxRelP = relP;
  if (relM > maxRelM) maxRelM = relM;
  console.log(k, "mine@pubmu="+lpP.points[k].C.toFixed(13), "published="+pubs.C[k], "rel@pubmu="+relP.toExponential(2), "rel@my mu="+relM.toExponential(2));
}
console.log("MAX rel @ published mu (instrument agreement):", maxRelP.toExponential(3));
console.log("MAX rel @ my mu (mu-induced shift):", maxRelM.toExponential(3));
console.log("residual of gradOmega at published mu:", lpP.maxResidual.toExponential(3));
