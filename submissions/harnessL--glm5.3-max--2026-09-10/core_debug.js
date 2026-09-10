const MU = 0.0121505856096241;              // m_moon/(m_earth+m_moon)
const DU_KM = 384400;                       // 1 DU in km
const TU_DAYS = 27.321661 / (2*Math.PI);    // 1 TU in days
const V_KMS = (DU_KM/TU_DAYS)/86400;        // 1 DU/TU in km/s
const VERSION = "v1";

function allFinite(a){ for(let i=0;i<a.length;i++) if(!isFinite(a[i])) return false; return true; }
function fmt(v,d=4){ return (v>=0?"+":"")+v.toFixed(d); }
function fmtE(v){ if(v===0) return "0"; const e=v.toExponential(2); return e; }
function clamp(v,a,b){ return Math.min(b,Math.max(a,v)); }

/* ---------- 2. 动力学模型 ---------- */
function omega(x,y){                        // 有效势 Ω
  const r1=Math.hypot(x+MU,y), r2=Math.hypot(x-1+MU,y);
  return 0.5*(x*x+y*y) + (1-MU)/r1 + MU/r2;
}
function omegaGrad(x,y){                    // ∂Ω/∂x, ∂Ω/∂y
  const dx1=x+MU, dy1=y, dx2=x-1+MU, dy2=y;
  const r1=Math.sqrt(dx1*dx1+dy1*dy1), r2=Math.sqrt(dx2*dx2+dy2*dy2);
  const c1=(1-MU)/(r1*r1*r1), c2=MU/(r2*r2*r2);
  return {x: x - c1*dx1 - c2*dx2, y: y - c1*dy1 - c2*dy2};
}
function deriv(s,out){                      // s=[x,y,vx,vy] → out=ds/dt
  const x=s[0],y=s[1],vx=s[2],vy=s[3];
  const dx1=x+MU, dy1=y, dx2=x-1+MU, dy2=y;
  const r1s=dx1*dx1+dy1*dy1, r2s=dx2*dx2+dy2*dy2;
  const r1=Math.sqrt(r1s), r2=Math.sqrt(r2s);
  const c1=(1-MU)/(r1s*r1), c2=MU/(r2s*r2);
  out[0]=vx; out[1]=vy;
  out[2]=2*vy + x - c1*dx1 - c2*dx2;
  out[3]=-2*vx + y - c1*dy1 - c2*dy2;
}
function derivJac(s,J){                     // ∂(deriv)/∂s 解析雅可比, 4x4 row-major
  const x=s[0],y=s[1];
  const dx1=x+MU, dy1=y, dx2=x-1+MU, dy2=y;
  const r1s=dx1*dx1+dy1*dy1, r2s=dx2*dx2+dy2*dy2;
  const r1=Math.sqrt(r1s), r2=Math.sqrt(r2s);
  const t1=(1-MU)/(r1s*r1*r1), t2=MU/(r2s*r2*r2);          // 1/r^3 系数
  const u1=3*(1-MU)/(r1s*r1s*r1), u2=3*MU/(r2s*r2s*r2);    // 3/r^5 系数
  J[0]=0; J[1]=0; J[2]=1; J[3]=0;
  J[4]=0; J[5]=0; J[6]=0; J[7]=1;
  J[8]= 1 - t1 + u1*dx1*dx1 - t2 + u2*dx2*dx2;   // ∂ax/∂x
  J[9]= u1*dx1*dy1 + u2*dx2*dy2;                 // ∂ax/∂y
  J[10]=0; J[11]=2;
  J[12]= u1*dx1*dy1 + u2*dx2*dy2;                // ∂ay/∂x
  J[13]= 1 - t1 + u1*dy1*dy1 - t2 + u2*dy2*dy2; // ∂ay/∂y
  J[14]=-2; J[15]=0;
}
function jacobiC(s){ return 2*omega(s[0],s[1]) - (s[2]*s[2]+s[3]*s[3]); }
function accelNorm(x,y,vx,vy){
  const g=omegaGrad(x,y);
  return Math.hypot(2*vy+g.x, -2*vx+g.y);
}
function isAllowed(x,y,C){ return 2*omega(x,y) >= C; }

/* ---------- 3. 拉格朗日点 ---------- */
function solveCollinear(x0){
  let x=x0;
  for(let i=0;i<80;i++){
    const sa=x+MU, sb=x-1+MU;
    const f = x - (1-MU)*sa/Math.pow(Math.abs(sa),3) - MU*sb/Math.pow(Math.abs(sb),3);
    const fp = 1 + 2*(1-MU)/Math.pow(Math.abs(sa),3) + 2*MU/Math.pow(Math.abs(sb),3);
    const d=f/fp; x-=d;
    if(Math.abs(d)<1e-15) break;
  }
  return x;
}
const cbrtMu=Math.pow(MU/3,1/3);
const LPTS=[
  {name:"L1", x:solveCollinear(1-MU-cbrtMu), y:0},
  {name:"L2", x:solveCollinear(1-MU+cbrtMu), y:0},
  {name:"L3", x:solveCollinear(-1-5*MU/12),  y:0},
  {name:"L4", x:0.5-MU, y: Math.sqrt(3)/2},
  {name:"L5", x:0.5-MU, y:-Math.sqrt(3)/2},
];
const CV = { L1:2*omega(LPTS[0].x,0), L2:2*omega(LPTS[1].x,0), L3:2*omega(LPTS[2].x,0),
             L4:2*omega(LPTS[3].x,LPTS[3].y), L5:CV_L5() };
function CV_L5(){ return 2*omega(0.5-MU,-Math.sqrt(3)/2); }

/* ---------- 4. 积分器 ---------- */
const _k1=new Float64Array(4),_k2=new Float64Array(4),_k3=new Float64Array(4),_k4=new Float64Array(4),_tmp=new Float64Array(4);

function stHalt(st,msg){ st.halted=true; st.haltMsg=msg; }
function checkAccel(st){                     // 奇异防护
  deriv(st.s,_tmp);
  if(Math.abs(_tmp[2])>1e12||Math.abs(_tmp[3])>1e12){ stHalt(st,"加速度过大（接近主星奇点）— 已停止"); return false; }
  return true;
}
function trackR(st){
  const r1=Math.hypot(st.s[0]+MU,st.s[1]), r2=Math.hypot(st.s[0]-1+MU,st.s[1]);
  if(r1<st.minR1)st.minR1=r1; if(r1>st.maxR1)st.maxR1=r1;
  if(r2<st.minR2)st.minR2=r2; if(r2>st.maxR2)st.maxR2=r2;
}
function postStep(st,h){
  st.steps++; if(h!=null){ st.hLast=h; if(h<st.minH)st.minH=h; }
  if(!allFinite(st.s)){ stHalt(st,"检测到非有限状态 (NaN/Inf) — 仿真已停止"); return false; }
  trackR(st); return true;
}

/* RK4 定步长 */
function stepRK4(st){
  if(!checkAccel(st)) return {failed:true};
  const s=st.s, h=st.dt;
  deriv(s,_k1);
  for(let i=0;i<4;i++)_tmp[i]=s[i]+0.5*h*_k1[i]; deriv(_tmp,_k2);
  for(let i=0;i<4;i++)_tmp[i]=s[i]+0.5*h*_k2[i]; deriv(_tmp,_k3);
  for(let i=0;i<4;i++)_tmp[i]=s[i]+h*_k3[i];     deriv(_tmp,_k4);
  for(let i=0;i<4;i++) s[i]+= (h/6)*(_k1[i]+2*_k2[i]+2*_k3[i]+_k4[i]);
  st.evals+=4; st.t+=h;
  return postStep(st,h)?{h}: {failed:true};
}

/* 隐式中点（辛, 二阶）: 牛顿迭代解 z = y + h f((y+z)/2) */
const _Jf=new Float64Array(16);
function solveLin4(M,rhs){                    // 高斯消元(部分主元), M 4x4 row-major, 原地
  const a=Float64Array.from(M), b=Float64Array.from(rhs);
  for(let col=0;col<4;col++){
    let piv=col, mx=Math.abs(a[col*4+col]);
    for(let r=col+1;r<4;r++){ const v=Math.abs(a[r*4+col]); if(v>mx){mx=v;piv=r;} }
    if(mx<1e-300) return null;
    if(piv!==col){ for(let c2=0;c2<4;c2++){const t=a[col*4+c2];a[col*4+c2]=a[piv*4+c2];a[piv*4+c2]=t;} const t=b[col];b[col]=b[piv];b[piv]=t; }
    for(let r=col+1;r<4;r++){
      const f=a[r*4+col]/a[col*4+col];
      if(f===0)continue;
      for(let c2=col;c2<4;c2++)a[r*4+c2]-=f*a[col*4+c2];
      b[r]-=f*b[col];
    }
  }
  const x=new Float64Array(4);
  for(let r=3;r>=0;r--){ let v=b[r]; for(let c2=r+1;c2<4;c2++)v-=a[r*4+c2]*x[c2]; x[r]=v/a[r*4+r]; }
  return x;
}
function stepIMP(st){
  const y=st.s.slice(), h=st.dt, n=4;
  let z=y.slice();
  const mid=new Float64Array(4), f=new Float64Array(4), rhs=new Float64Array(4), M=new Float64Array(16);
  let it=0, conv=false;
  for(it=0;it<14;it++){
    for(let i=0;i<n;i++)mid[i]=0.5*(y[i]+z[i]);
    if(!allFinite(mid)){ stHalt(st,"隐式中点：中点状态非有限"); return {failed:true}; }
    deriv(mid,f); derivJac(mid,_Jf);
    for(let i=0;i<n;i++){
      rhs[i]=z[i]-y[i]-h*f[i];
      for(let j=0;j<n;j++)M[i*4+j]=-0.5*h*_Jf[i*4+j];
      M[i*4+i]+=1;
    }
    const dz=solveLin4(M,rhs);
    if(!dz){ stHalt(st,"隐式中点：线性求解失败"); return {failed:true}; }
    let dm=0;
    for(let i=0;i<n;i++){ z[i]+=dz[i]; if(Math.abs(dz[i])>dm)dm=Math.abs(dz[i]); }
    st.evals+=2;
    console.log('  imp it='+it+' dm='+dm.toExponential(3)+' z='+z.map(v=>v.toFixed(6)).join(',')); if(dm<1e-13){ conv=true; break; }
  }
  if(!conv){ stHalt(st,"隐式中点：牛顿迭代未收敛（减小 dt）"); return {failed:true}; }
  st.s=z; st.t+=h;
  return postStep(st,h)?{h}: {failed:true};
}

/* GBS: Gragg 修正中点 + Neville 外推, 自适应 */
const GBS_SEQ=[2,4,6,8,12,16,24,32,48,64];
const GBS={KMAX:8,HMIN:1e-9,HMAX:2.0,ATOL:1e-14};
function mmid(y0,h,nsub){
  const n=4, hst=h/nsub;
  let a=y0.slice(), b=new Float64Array(4), t;
  deriv(a,_tmp);
  for(let i=0;i<n;i++)b[i]=y0[i]+hst*_tmp[i];
  for(let i=1;i<nsub;i++){
    deriv(b,_tmp);
    t=new Float64Array(4);
    for(let c=0;c<n;c++)t[c]=y0[c]+2*hst*_tmp[c];
    a=b; b=t;
  }
  deriv(b,_tmp);
  const out=new Float64Array(4);
  for(let c=0;c<n;c++)out[c]=0.5*(a[c]+b[c]+hst*_tmp[c]);
  return out;
}
function gbsErrNorm(dy,y,tol){
  let e=0;
  for(let c=0;c<4;c++){
    const sc=GBS.ATOL+tol*Math.abs(y[c]);
    const v=Math.abs(dy[c])/sc;
    if(v>e)e=v;
  }
  return e;
}
function gbsTryStep(y,h,tol){
  const rows=[], xs=[];
  let evals=0, prevErr=Infinity, lastK=1;
  for(let k=0;k<GBS.KMAX;k++){
    const nsub=GBS_SEQ[k];
    const yk=mmid(y,h,nsub); evals+=nsub+2;
    xs.push((h/nsub)*(h/nsub));
    const row=new Array(k+1);
    row[0]=yk;
    for(let j=1;j<=k;j++){
      const A=rows[k-1][j-1], B=row[j-1];
      const xa=xs[k-j], xb=xs[k];
      const w=(0-xa)/(xb-xa);
      const v=new Float64Array(4);
      for(let c=0;c<4;c++)v[c]=A[c]+w*(B[c]-A[c]);
      row[j]=v;
    }
    rows.push(row);
    const yex=row[k];
    let dyv;
    if(k>0){ dyv=new Float64Array(4); for(let c=0;c<4;c++)dyv[c]=yex[c]-row[k-1][c]; }
    else dyv=yex;
    const err=gbsErrNorm(dyv,yex,tol); console.log('  k='+k+' nsub='+GBS_SEQ[k]+' err='+err.toExponential(3));
    lastK=k;
    if(err<1) return {ok:true,ynew:yex,err,k,evals};
    if(k>=2 && err>prevErr*1.3) break;       // 外推不再改善
    prevErr=err;
  }
  return {ok:false,err:prevErr,k:lastK,evals};
}
function stepGBS(st){
  let h=clamp(st.gbsH||0.05, GBS.HMIN, GBS.HMAX);
  for(let a=0;a<50;a++){
    const r=gbsTryStep(st.s,h,st.tol);
    st.evals+=r.evals;
    if(r.ok){
      st.s=r.ynew; st.t+=h;
      const grow=Math.min(4,Math.max(1,0.9*Math.pow(1/r.err,1/(2*r.k+4))));
      st.gbsH=clamp(h*grow,GBS.HMIN,GBS.HMAX);
      return postStep(st,h)?{h,err:r.err,k:r.k}:{failed:true};
    }
    const k=Math.max(1,r.k);
    h*=clamp(0.9*Math.pow(1/r.err,1/(2*k+2)),0.2,0.9);
    if(h<GBS.HMIN){ stHalt(st,"GBS 步长下溢（容差过严或轨迹奇异）"); return {failed:true}; }
  }
  stHalt(st,"GBS 步长控制重试超限"); return {failed:true};
}

