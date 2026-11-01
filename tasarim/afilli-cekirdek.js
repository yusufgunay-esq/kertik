/* ============================================================
   AKIŞ — "afilli" sürüm
   ------------------------------------------------------------
   Sanat DEĞİŞMİYOR. Uygulamadaki akış-çizgisi ebrusu aynı ebru.
   Üç şey ekleniyor, üçü de kullanıcının kendi notlarından:

   1) FIRÇA BASINCI  (24-sanat-dili.md §2.3 ve §Fırça basıncı tablosu)
      Şerit sabit kalınlıkta bir vektör çizgisi değil. Kalınlık şerit
      boyunca değişiyor: uçlar ince, gövde dolgun, üstüne şeridin kendi
      gürültüsünden gelen düzensizlik. "Doku eklenen katman değil,
      çizginin kendi davranışından çıkmalı" kuralının karşılığı.

   2) KADEMELİ SIKLAŞMA  (statikleşmenin çözümü)
      Eski kod tek bir alan hesaplıyor ve `dolum` dakikada bitiriyordu;
      sonrası donuk. Katman denemesi ise her katmana YENİ tohum verdiği
      için birbirini kesen bağımsız alanlar üretti → moiré.
      Burada tohum ve açı alanı HİÇ DEĞİŞMİYOR. Sadece şerit aralığı
      (dsep) kademe kademe daralıyor. Yeni şeritler eskilerin ARASINA,
      onlara paralel yerleşiyor — kesişme yok, dolayısıyla moiré yok.
      Görsel sonuç: desen bozulmuyor, ipekleşiyor.

   3) MOLA = SİLİKLEŞME  (20-sanat-geri-bildirim.md madde 3, kullanıcı notu)
      Molada zıt renk yok. Aynı mürekkep, zayıflamış: daha soluk, daha
      ince, yıkamasız. Çiğ renk çakışması yerine nefes.
   ============================================================ */

function h2i(i,j,s){let n=Math.imul(i|0,374761393)^Math.imul(j|0,668265263)^Math.imul(s|0,362437);
  n=Math.imul(n^(n>>>13),1274126177);return((n^(n>>>16))>>>0)/4294967296}
function vnoise(x,y,s){const i=Math.floor(x),j=Math.floor(y),fx=x-i,fy=y-j;
  const u=fx*fx*(3-2*fx),v=fy*fy*(3-2*fy);
  const a=h2i(i,j,s),b=h2i(i+1,j,s),c=h2i(i,j+1,s),d=h2i(i+1,j+1,s);
  return(a*(1-u)+b*u)*(1-v)+(c*(1-u)+d*u)*v}
function fbm(x,y,s){return vnoise(x,y,s)*.6+vnoise(x*2.1,y*2.1,s+7)*.27+vnoise(x*4.3,y*4.3,s+19)*.13}
function hash32(t){let h=2166136261;for(let i=0;i<t.length;i++){h^=t.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
function rng32(a){a=a>>>0;return()=>{a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);
  t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

function hexHsl(x){const m=/^#([0-9a-f]{6})$/i.exec(x||"");if(!m)return null;
  const n=parseInt(m[1],16),r=(n>>16)/255,g=(n>>8&255)/255,b=(n&255)/255;
  const mx=Math.max(r,g,b),mn=Math.min(r,g,b),l=(mx+mn)/2,d=mx-mn;
  if(!d)return[0,0,l];
  const s=l>.5?d/(2-mx-mn):d/(mx+mn);
  let h=mx===r?(g-b)/d+(g<b?6:0):mx===g?(b-r)/d+2:(r-g)/d+4;
  return[h*60,s,l]}

/* ---------- alan: uygulamadaki `ebru` yönünün açı alanı, birebir ---------- */
function aciAlani(seed, W, f){
  return (x,y)=> (fbm(x/(W/f[0]), y/(W/f[0]), seed)*2-1)*Math.PI*1.9
               + (fbm(x/(W/f[1]), y/(W/f[1]), seed+3)-.5)*1.1
               + (f[2] ? (fbm(x/(W/f[2]), y/(W/f[2]), seed+11)-.5)*.5 : 0);
}

/* Bir kademe hesaplar. `eskiler` önceki kademelerin şeritleri — yeni şeritler
   onlara değmeden aralarına yerleşsin diye ızgaraya işaretleniyor. */
function kademeHesapla(seed, W, H, A, dsep, dene, eskiler, tohumEk){
  const R=rng32(seed+tohumEk);
  const STEP=2.0, MAXL=A.maxl;
  const gw=Math.ceil(W/dsep)+2, gh=Math.ceil(H/dsep)+2;
  const dolu=new Uint8Array(gw*gh);
  const aci=aciAlani(seed,W,A.af);
  const isaretle=(x,y)=>{const gi=(x/dsep|0)+1,gj=(y/dsep|0)+1;
    if(gi>=0&&gj>=0&&gi<gw&&gj<gh) dolu[gj*gw+gi]=1};
  const bosMu=(x,y)=>{
    const gi=(x/dsep|0)+1, gj=(y/dsep|0)+1;
    if(gi<0||gj<0||gi>=gw||gj>=gh) return false;
    for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++){
      const q=(gj+b)*gw+(gi+a); if(q>=0&&q<dolu.length&&dolu[q]) return false;
    }
    return true;
  };
  /* önceki kademeler yerini korusun */
  for(const p of eskiler) for(let k=0;k<p.length;k+=2) isaretle(p[k],p[k+1]);

  const seritler=[];
  for(let i=0;i<dene;i++){
    const x0=R()*W, y0=R()*H;
    if(!bosMu(x0,y0)) continue;
    const pts=[];
    for(const yon of [1,-1]){
      let x=x0,y=y0; const par=[];
      for(let k=0;k<MAXL/STEP;k++){
        const a=aci(x,y);
        x+=Math.cos(a)*STEP*yon; y+=Math.sin(a)*STEP*yon;
        if(x<-14||y<-14||x>W+14||y>H+14) break;
        if(k>2&&!bosMu(x,y)) break;
        par.push(x,y);
      }
      if(yon===1) pts.push(...par);
      else{const rev=[];for(let k=par.length-2;k>=0;k-=2)rev.push(par[k],par[k+1]);pts.unshift(...rev)}
    }
    if(pts.length<12) continue;
    for(let k=0;k<pts.length;k+=2) isaretle(pts[k],pts[k+1]);
    seritler.push(Float32Array.from(pts));
  }
  return seritler;
}

/* şeridin "ağırlık sırası" — uygulamadaki akisSira ile aynı fikir */
function agirlikSirasi(seritler, W, seed){
  const n=seritler.length, w=new Float32Array(n), idx=[];
  for(let i=0;i<n;i++){
    const p=seritler[i], k=(p.length>>2)<<1;
    w[i]=fbm(p[k]/W*1.7, p[k+1]/W*1.7, seed+91); idx.push(i);
  }
  idx.sort((a,b)=>w[a]-w[b]);
  const s=new Float32Array(n);
  for(let r=0;r<n;r++) s[idx[r]]= n>1 ? r/(n-1) : 0;
  return s;
}

/* ---------- kademeler ----------
   bitis[n] = ILK * KAT^n  → 80, 240, 720, 2160, 6480 dk.
   Her kademe bir öncekinin arasına giriyor; aralık her seferinde /BOL.
   67 saatte 5. kademenin ortasındayız: hiçbir an donmuyor.            */
function kademeler(K){
  const L=[]; let bas=0;
  for(let n=0;n<K.kademeSayi;n++){
    const bitis=K.ilkDolum*Math.pow(K.katOran,n);
    L.push({n, bas, bitis, dsep:K.dsep0/Math.pow(K.bol,n),
            dene:Math.round(K.dene0*Math.pow(K.bol,n*1.35)),
            incelme:Math.pow(K.incelmeOran,n)});
    bas=bitis;
  }
  return L;
}

/* Verilen dakikada hangi kademelerin ne kadarı çizilmiş olmalı */
function doluluk(kd, dk){
  if(dk<=kd.bas) return 0;
  if(dk>=kd.bitis) return 1;
  return (dk-kd.bas)/(kd.bitis-kd.bas);
}

/* ---------- fırça basıncı ----------
   Şerit, kalınlığı boyunca değişen parçalara bölünüp çiziliyor.
   Uçlar ince (künt değil, sivri), gövde dolgun, üstüne şeridin kendi
   gürültüsünden gelen düzensizlik. */
function firca(g, p, tabanKalinlik, tohum, parca){
  const n=p.length>>1;
  if(n<3){ return }
  const adim=Math.max(2, Math.ceil(n/parca));
  for(let a=0;a<n-1;a+=adim){
    const b=Math.min(n-1, a+adim);
    const s=(a+b)/2/(n-1);                       // 0..1 şerit boyunca
    // uçlarda incelme (sin eğrisi), ortada dolgunluk
    const uc=Math.pow(Math.sin(Math.PI*Math.min(1,Math.max(0,s))), .42);
    // basınç dalgalanması — el titremesi, hep aynı yerde değil
    const bas=1+(fbm(s*4.1+tohum*.013, tohum*.07, tohum|0)-.5)*.85;
    const w=tabanKalinlik*(.26+.74*uc)*bas;
    if(w<=.02) continue;
    g.lineWidth=w;
    g.beginPath(); g.moveTo(p[a*2],p[a*2+1]);
    for(let k=a+1;k<=b;k++) g.lineTo(p[k*2],p[k*2+1]);
    g.stroke();
  }
}

if(typeof module!=="undefined") module.exports={kademeHesapla,agirlikSirasi,kademeler,doluluk,firca,hash32,hexHsl,fbm};
