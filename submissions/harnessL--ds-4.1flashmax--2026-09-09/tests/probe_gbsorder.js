
const C = require(process.argv[2]);
const mu = C.MU_EARTH_MOON;
const ic = C.presets(mu)[0].state;
for (const H0 of [0.8, 0.4, 0.2]) {
  const y1 = C.stepGBSFix(ic, H0, mu, 4);
  const y2 = C.stepGBSFix(ic, H0/2, mu, 4);
  const y3 = C.stepGBSFix(ic, H0/4, mu, 4);
  const e1 = C.errState(y1,y2), e2 = C.errState(y2,y3);
  console.log("H0="+H0, "e1="+e1.toExponential(2), "e2="+e2.toExponential(2), "self-order="+(Math.log(e1/e2)/Math.LN2).toFixed(2));
}
