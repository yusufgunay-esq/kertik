/* ============================================================
   KUM BAHÇESİ ÇEKİRDEĞİ (karesansui)
   ------------------------------------------------------------
   Damar denemesinin sorunu şuydu: boşlukta yüzen bağımsız
   şekiller → konfeti. Kompozisyon yok, sadece nesne var.

   Burada tam tersi: ekranın TAMAMI baştan doludur — taranmış kum.
   Zaman geçtikçe eklenen şey nesne değil, BOZULMA. Bir taş
   düştüğünde kum çizgileri onun etrafından dolanmak zorunda kalır.
   Düzenin içindeki tek tek kusurlar (fukinsei), düzenin kendisi
   sayesinde okunur.

   Aynı alan koruyan dönüşüm, farklı taban:
     taş:  P' = C + (P-C)·√(1 + r²/|P-C|²)
   Taban paralel çizgi olunca sonuç ebru değil, tırmık izi oluyor.
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
const R2G=1.32471795724474602596, A1=1/R2G, A2=1/(R2G*R2G);
function r2(i){ return [ (0.5+A1*(i+1))%1, (0.5+A2*(i+1))%1 ] }

/* ---------- taşların zamanlaması ---------- */
/* t(k)=A·k^US → başta sık, sonra seyrek. 67 saatte ~35 taş: bir bahçe
   dolusu, ama kalabalık değil. Taşlar arası sürede AKTİF taş büyümeye
   devam eder → kum her an yeniden dizilir, ekran hiç donmaz. */
function taslar(se, dk, K){
  const s0=hashStr(se.id), R=rng(s0), L=[];
  const molada=m=>{ for(const b of (se.molalar||[])) if(m>=b[0]&&m<b[1]) return true; return false };
  const zaman=k=>K.A*Math.pow(k,K.US);
  for(let i=0;;i++){
    const t=zaman(i); if(t>dk||i>K.tavan) break;
    const [u,v]=r2(i+(s0%89));
    let cx=K.kenar+u*(K.W-2*K.kenar)+(fbm(i*.43,1.7,s0+11)-.5)*K.sapma;
    let cy=K.ust +v*(K.H-K.ust-K.alt)+(fbm(i*.43,9.3,s0+23)-.5)*K.sapma;
    // saatin çevresi temiz kalsın: bu diske düşen taş dışa itilir.
    // Sonuç kompozisyon olarak da doğru — saat açık kumda durur,
    // taşlar aşağıda toplanır (karesansui'de de boşluk taş kadar önemlidir).
    // taş kadrajın içinde kalsın — yarım kesilmiş taş kaza gibi duruyor
    const rTah=K.tas*1.5;
    cx=Math.min(K.W-rTah, Math.max(rTah, cx));
    cy=Math.min(K.H-rTah, Math.max(rTah, cy));
    // kadranın çevresi boş kalsın. Yatayda yer yok (ekran dar), o yüzden
    // çakışan taş DİKEY olarak dışarı taşınır: saat açık kumda durur,
    // taşlar altta ve üstte toplanır. Boşluk taş kadar kompozisyon.
    if(K.bosR>0){
      const ry=K.bosR*K.bosOran, dx=cx-K.bosX;
      const kalan=1-(dx*dx)/(K.bosR*K.bosR);
      if(kalan>0){
        const yari=ry*Math.sqrt(kalan)+rTah*.55;
        if(Math.abs(cy-K.bosY)<yari) cy = K.bosY + (cy<K.bosY?-1:1)*yari;
      }
    }
    cy=Math.min(K.H-rTah, Math.max(rTah, cy));
    L.push({
      i, t, sure:Math.max(1,zaman(i+1)-t), cx, cy,
      r0:K.tas*(0.72+R()*0.62),
      don:R()*Math.PI, mola:molada(t),
      tohum:s0+i*29
    });
  }
  return L;
}

/* ---------- kum: ekranı baştan sona kaplayan tırmık izleri ---------- */
function kumCizgileri(se, K){
  const s0=hashStr(se.id);
  const L=[], adim=K.adim;
  const n=Math.ceil((K.H+2*K.tasma)/K.aralik)+1;
  for(let j=0;j<n;j++){
    const y0=-K.tasma+j*K.aralik;
    const P={x:[],y:[]};
    for(let x=-K.tasma; x<=K.W+K.tasma; x+=adim){
      // tırmık el işi: çizgi tam düz değil, çok hafif dalgalı (fukinsei)
      const w=(fbm(x/210, y0/210, s0+3)-.5)*K.dalga
            + (fbm(x/54,  y0/54,  s0+9)-.5)*K.dalga*.35;
      P.x.push(x); P.y.push(y0+w);
    }
    L.push(P);
  }
  return L;
}

function itUygula(P, cx, cy, r){
  const r2v=r*r, X=P.x, Y=P.y;
  for(let i=0;i<X.length;i++){
    const dx=X[i]-cx, dy=Y[i]-cy;
    const d2=dx*dx+dy*dy;
    if(d2<1e-6){ X[i]=cx+r; Y[i]=cy; continue }
    const k=Math.sqrt(1+r2v/d2);
    X[i]=cx+dx*k; Y[i]=cy+dy*k;
  }
}
/* uzayan kenarlara nokta ekle — taşın çevresindeki halka köşeli olmasın */
function yenidenOrnekle(P, maxKenar, tavan){
  const X=P.x, Y=P.y, n=X.length;
  if(n>tavan) return;
  const nx=[], ny=[];
  for(let i=0;i<n-1;i++){
    const dx=X[i+1]-X[i], dy=Y[i+1]-Y[i];
    const d=Math.sqrt(dx*dx+dy*dy);
    nx.push(X[i]); ny.push(Y[i]);
    if(d>maxKenar){
      const k=Math.min(5,Math.ceil(d/maxKenar)-1);
      for(let t=1;t<=k;t++){ nx.push(X[i]+dx*t/(k+1)); ny.push(Y[i]+dy*t/(k+1)) }
    }
  }
  nx.push(X[n-1]); ny.push(Y[n-1]);
  P.x=nx; P.y=ny;
}

/* taşın kendi silueti — daire değil, yontulmamış taş */
function tasSilueti(t, r){
  const N=26, X=[], Y=[];
  for(let i=0;i<N;i++){
    const a=i/N*Math.PI*2+t.don;
    const w=1+(fbm(Math.cos(a)*2.2+1.3, Math.sin(a)*2.2+7.1, t.tohum)-.5)*.46;
    X.push(t.cx+Math.cos(a)*r*w*1.06); Y.push(t.cy+Math.sin(a)*r*w*.86);
  }
  return {x:X,y:Y};
}

function bahce(se, dk, K){
  const T=taslar(se,dk,K);
  const kum=kumCizgileri(se,K);
  const cizilecek=[];
  for(const t of T){
    const buyume=Math.min(1,(dk-t.t)/t.sure);
    const r=t.r0*Math.sqrt(Math.max(1e-4,buyume));
    if(r<0.4) continue;
    for(const P of kum){ itUygula(P,t.cx,t.cy,r); yenidenOrnekle(P,K.maxKenar,K.noktaTavan); }
    cizilecek.push({t, r, sil:tasSilueti(t,r)});
  }
  return {kum, taslar:cizilecek};
}

if(typeof module!=="undefined") module.exports={bahce,taslar,kumCizgileri,fbm,hashStr,rng};
