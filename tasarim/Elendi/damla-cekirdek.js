/* ============================================================
   EBRU ÇEKİRDEĞİ — gerçek ebru fiziğiyle, alan koruyan dönüşümler
   ------------------------------------------------------------
   Ekranda "çizgi" biriktirmiyoruz. Teknede TEK bir kompozisyon var;
   her yeni damla o kompozisyonun TAMAMINI dışa doğru iter. Bu yüzden
   hiçbir zaman statikleşmez — 4020. dakikada da resim her an değişiyor.

   Matematik (Jaffer, "Marbling Deformation Mathematics"):
     damla:  P' = C + (P-C) * sqrt(1 + r^2/|P-C|^2)      (alan korur)
     tarak:  P' = P + u * M * lam^(d/z)                   (alan korur)
   ============================================================ */

function h2i(i,j,s){let n=Math.imul(i|0,374761393)^Math.imul(j|0,668265263)^Math.imul(s|0,362437);
  n=Math.imul(n^(n>>>13),1274126177);return((n^(n>>>16))>>>0)/4294967296}
function vn(x,y,s){const i=Math.floor(x),j=Math.floor(y),fx=x-i,fy=y-j;
  const u=fx*fx*(3-2*fx),v=fy*fy*(3-2*fy);
  const a=h2i(i,j,s),b=h2i(i+1,j,s),c=h2i(i,j+1,s),d=h2i(i+1,j+1,s);
  return(a*(1-u)+b*u)*(1-v)+(c*(1-u)+d*u)*v}
function fbm(x,y,s){return vn(x,y,s)*.6+vn(x*2.1,y*2.1,s+7)*.27+vn(x*4.3,y*4.3,s+19)*.13}
function hashStr(t){let h=2166136261;for(let i=0;i<t.length;i++){h^=t.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
function rng(a){a=a>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);
  t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

/* ---------- şekil: kendini yeniden örnekleyen çokgen ---------- */
class Sekil{
  constructor(cx,cy,r,tohum,N){
    this.x=[]; this.y=[];
    for(let i=0;i<N;i++){
      const a=i/N*Math.PI*2;
      const w=1+(fbm(Math.cos(a)*1.7+3.1, Math.sin(a)*1.7+5.9, tohum)-.5)*.12;
      this.x.push(cx+Math.cos(a)*r*w); this.y.push(cy+Math.sin(a)*r*w);
    }
    this.canli=true;
  }
  /* dönüşümden sonra uzayan kenarlara nokta ekle, kısalanları at.
     Dönüşümler pürüzsüz ve küçük adımlarla uygulandığı için mevcut
     koordinatta ara nokta eklemek görsel olarak yeterli. */
  yenidenOrnekle(maxKenar, minKenar, tavan){
    const X=this.x, Y=this.y, n=X.length;
    if(n<3){ this.canli=false; return }
    const nx=[], ny=[];
    const bol = n<tavan;
    for(let i=0;i<n;i++){
      const j=(i+1)%n;
      const dx=X[j]-X[i], dy=Y[j]-Y[i];
      const d=Math.sqrt(dx*dx+dy*dy);
      if(d<minKenar && nx.length>3 && i!==n-1) continue;   // fazlalığı at
      nx.push(X[i]); ny.push(Y[i]);
      if(bol && d>maxKenar){
        const k=Math.min(4,Math.ceil(d/maxKenar)-1);
        for(let t=1;t<=k;t++){ nx.push(X[i]+dx*t/(k+1)); ny.push(Y[i]+dy*t/(k+1)) }
      }
    }
    this.x=nx; this.y=ny;
    if(nx.length<3) this.canli=false;
  }
  kutu(){
    let a=1e9,b=1e9,c=-1e9,d=-1e9;
    for(let i=0;i<this.x.length;i++){
      if(this.x[i]<a)a=this.x[i]; if(this.x[i]>c)c=this.x[i];
      if(this.y[i]<b)b=this.y[i]; if(this.y[i]>d)d=this.y[i];
    }
    return[a,b,c,d];
  }
}

function damlaUygula(S, cx, cy, r){
  const r2=r*r, X=S.x, Y=S.y;
  for(let i=0;i<X.length;i++){
    const dx=X[i]-cx, dy=Y[i]-cy;
    const d2=dx*dx+dy*dy;
    if(d2<1e-6){ X[i]=cx+r; Y[i]=cy; continue }
    const k=Math.sqrt(1+r2/d2);
    X[i]=cx+dx*k; Y[i]=cy+dy*k;
  }
}
function tarakUygula(S, ax, ay, ux, uy, M, s, z, lam){
  const nx=-uy, ny=ux, X=S.x, Y=S.y;
  for(let i=0;i<X.length;i++){
    let q=(X[i]-ax)*nx+(Y[i]-ay)*ny;
    q=((q%s)+s)%s;
    const d=Math.abs(q-s/2);
    const f=Math.pow(lam, d/z);
    X[i]+=ux*M*f; Y[i]+=uy*M*f;
  }
}

/* ---------- düşük tutarsızlıklı (R2) saçılım: her ön-ek eşit dağılır ---------- */
const R2G=1.32471795724474602596, A1=1/R2G, A2=1/(R2G*R2G);
function r2(i){ return [ (0.5+A1*(i+1))%1, (0.5+A2*(i+1))%1 ] }

/* ============================================================ */
function cizelge(se, dk, K){
  const s0=hashStr(se.id), R=rng(s0);
  const ops=[];
  const molada=m=>{ for(const b of (se.molalar||[])) if(m>=b[0]&&m<b[1]) return true; return false };
  // damla zamanlaması: t(k)=A*k^US — başta sık (ekran çabuk canlanır),
  // sonra seyrekleşir (67 saatte bile tekne doymaz). Ağaç halkası mantığı.
  const dmZaman = k => K.A*Math.pow(k, K.US);
  let i=0;
  for(;;){
    const t=dmZaman(i);
    if(t>dk) break;
    const [u,v]=r2(i+ (s0%97));
    let cx=K.kenar + u*(K.W-2*K.kenar) + (fbm(i*.41,1.7,s0+11)-.5)*K.sapma;
    let cy=K.kenar + v*(K.H-2*K.kenar) + (fbm(i*.41,9.3,s0+23)-.5)*K.sapma;
    // gerçek ebruda damlaların bir kısmı ÖNCEKİ damlanın üstüne düşer →
    // iç içe halkalar. Ebruyu "konfeti"den ayıran şey bu.
    if(i>2 && h2i(i,7,s0+61) < K.icIce){
      const j=i-1-Math.floor(h2i(i,9,s0+71)*Math.min(i,5));
      const o2=ops[j];
      if(o2){ cx=o2.cx+(h2i(i,13,s0+83)-.5)*K.yaricap*.7;
              cy=o2.cy+(h2i(i,17,s0+91)-.5)*K.yaricap*.7 }
    }
    ops.push({tip:"damla", t, i, cx, cy, r:K.yaricap*(0.82+R()*0.36),
      mola:molada(t), sure:Math.max(1,dmZaman(i+1)-t)});
    i++;
    if(i>K.tavanDamla) break;
  }
  if(K.tarakAralik>0){
    for(let t=K.tarakAralik; t<=dk; t+=K.tarakAralik){
      const n=Math.round(t/K.tarakAralik);
      const a=(n%2? Math.PI/2 : 0) + (fbm(n*.71,3.3,s0+5)-.5)*.55;
      ops.push({tip:"tarak", t,
        ax:K.W/2+(fbm(n*.9,1.1,s0+31)-.5)*90, ay:K.H/2+(fbm(n*.9,7.7,s0+37)-.5)*160,
        ux:Math.cos(a), uy:Math.sin(a),
        M:K.tarakGuc*(n%2?1:-1), s:K.tarakAralikPx, z:K.tarakZ, lam:K.tarakLam});
    }
  }
  ops.sort((a,b)=> a.t-b.t || (a.tip==="damla"?-1:1));
  return ops;
}

function kompozisyon(se, dk, K){
  const ops=cizelge(se, dk, K);
  const s0=hashStr(se.id);
  const sekiller=[];
  const pay=K.pay||120;   // kadrajın dışında bu kadar payda kalanlar hâlâ yaşıyor
  for(let k=0;k<ops.length;k++){
    const o=ops[k];
    if(o.tip==="damla"){
      const buyume=Math.min(1, (dk-o.t)/o.sure);
      const r=o.r*Math.sqrt(Math.max(1e-4,buyume));
      if(r<0.35) continue;
      for(const S of sekiller){
        if(!S.canli) continue;
        damlaUygula(S,o.cx,o.cy,r);
        S.yenidenOrnekle(K.maxKenar,K.minKenar,K.tavan);
        const b=S.kutu();
        if(b[2]<-pay||b[0]>K.W+pay||b[3]<-pay||b[1]>K.H+pay) S.canli=false;
      }
      const S=new Sekil(o.cx,o.cy,r,s0+o.i*13,K.nokta);
      S.mola=o.mola; S.i=o.i; S.t=o.t;
      sekiller.push(S);
    } else {
      for(const S of sekiller){
        if(!S.canli) continue;
        tarakUygula(S,o.ax,o.ay,o.ux,o.uy,o.M,o.s,o.z,o.lam);
        S.yenidenOrnekle(K.maxKenar,K.minKenar,K.tavan);
      }
    }
  }
  return sekiller.filter(S=>S.canli);
}

if(typeof module!=="undefined") module.exports={kompozisyon,cizelge,fbm,hashStr,rng};
