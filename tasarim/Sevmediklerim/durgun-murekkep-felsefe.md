# Durgun Mürekkep — algoritmik sanat felsefesi

> Kertik'in arka plan sanatı için üretken estetik. `24-sanat-dili.md`'nin
> (wabi-sabi anayasası) altında çalışır, onu ihlal edemez.
> Uygulaması: `tasarim/durgun-murekkep.html`

---

## Kavramsal tohum: ebru

Bu algoritmanın içine gömülü olan şey **ebru**dur — ve bu hiçbir yerde
yazmayacak, hiçbir ekranda söylenmeyecek.

Ebrunun tek bir kuralı vardır ve o kural bu uygulamanın da tek kuralıdır:
**tekne bir kere kaldırılır.** Su üstündeki desen kâğıda alındığı anda iş biter.
Geri alınamaz, düzeltilemez, "biraz daha iyisini deneyelim" denemez. Ebru
ustasının elindeki tek malzeme, o anın kendisidir.

Kertik'in de tek iddiası budur: *dürüst kayıt.* Geçmiş bir seans düzeltilemez,
güzelleştirilemez. Desen, o gün ne olduysa odur.

Bilen hisseder. Bilmeyen sadece güzel bir şey görür. İkisi de yeterlidir.

---

## Felsefe

**Zaman bir çizgi değildir; çökmüş bir sıvıdır.**

Geleneksel zaman görselleştirmesi soldan sağa akar: eksen, ölçek, işaret. Bu
dil dürüsttür ama ölüdür — çünkü zamanı *ölçtüğünü* iddia eder. Oysa yaşanan
zaman ölçülmez; koyulaşır, incelir, bazı yerlerde durur, bazı yerlerde
girdaba girer. Durgun Mürekkep bu deneyimi bir alan olarak kurar: her piksel
bir **ana** karşılık gelir, ama o anlar düz bir sırada dizilmez — akışkan bir
alana bükülerek dağılırlar. Zaman koordinatı görüntünün kendisine gömülüdür.

**Görünen şey hareketin kendisi değil, hareketin durmuş hâlidir.**

Bu algoritma asla animasyon yapmaz. Tek bir kare hesaplanır ve orada kalır —
çünkü sürekli devinen bir arka plan dikkat ister, ve dikkat isteyen bir
odaklanma uygulaması kendi sözünü bozar. Ama hareketsizlik cansızlık değildir:
alan adım adım *büküldüğü* için, duran görüntü hâlâ akmış olmanın izini taşır.
Deniz durgunken bile dalganın nereden geldiğini gösterir. Bu ayrım — hareketsiz
ama hareket etmiş görünmek — algoritmanın en zor ve en çok emek isteyen
yanıdır; alan bükümü katsayılarının her biri, ölü bir doku ile nefes alan bir
yüzey arasındaki eşikte defalarca ayarlanmıştır.

**Bükülme, tekrarın panzehiridir.**

Tek katmanlı gürültü duvar kâğıdı üretir: her yeri her yerine benzer, bakılacak
bir yer yoktur. Alan kendi üstüne katlandığında — gürültünün çıktısı yeniden
gürültüye koordinat olarak verildiğinde — tekrar kırılır. İkinci katlanmada
damarlar oluşur, üçüncüde kılcallar. Ortaya çıkan yapı ne rastgeledir ne
düzenlidir: **kaçınılmaz** görünür. Ustalığın ölçütü budur; alanın nerede
duracağına, kaç kere katlanacağına, hangi ölçekte kılcallanacağına dair her
karar, yüzlerce denemeden süzülmüş bir yargıdır.

**Değer aralığı, doygunluktan önce gelir.**

Bir görüntüyü derin yapan şey rengi değil, en koyu ile en açık arasındaki
mesafedir. Renk dar tutulur — tek bir aile, birkaç derece kayan bir ton
— ama değer sonuna kadar açılır: neredeyse siyahtan parlak vurguya. Yanardönerlik
buradan doğar, doygunluktan değil. Bu, ustanın en çok direnmesi gereken
noktadır: renk eklemek kolaydır, değer inşa etmek zordur.

**Kılcal, kütleden daha çok emek ister.**

Ebruyu ebru yapan, büyük renk kütleleri değil, aralarındaki saç teli
inceliğindeki sınırlardır. Alanın eş-değer eğrileri üzerinde beliren bu
kılcallar, algoritmanın en pahalı ve en belirleyici katmanıdır. Onlarsız
görüntü bir lekedir; onlarla birlikte bir yüzeydir. Kalınlıkları, sıklıkları
ve nerede kaybolacakları, ancak konunun derinine inmiş birinin verebileceği
kararlardır.

**Boşluk, deseni tamamlayan malzemedir.**

Alan asla kâğıdın tamamını doldurmaz. Mürekkebin ulaşmadığı yer eksiklik
değil, kompozisyonun yarısıdır. Ve bu boşluk keyfî değildir: seansın kendisi
tarafından belirlenir. Kısa bir çalışma az mürekkep bırakır ve bu bir kusur
değil, dürüst bir kayıttır.

**Sakinlik, çalkantı kadar bilgidir.**

Alanın her noktası bir ana karşılık geldiğine göre, o anda ne olduğu o noktanın
dokusunu belirler: çalışılan dakikalar çalkantılı ve kılcallı, molalar durgun
ve pürüzsüz. Böylece seansın ritmi ölçülerek değil **bakılarak** okunur.
Uzun bir mola, alanın ortasında geniş ve sakin bir su olarak durur. Kimse
"bu bir moladır" demez; göz zaten bilir.

---

## Algoritmik ifade

**Zaman alanı.** Tek bir bükülmüş gürültü alanı `m(x,y) ∈ [0,1]` kurulur ve
bu alan seansın zaman ekseni olarak yorumlanır. `m` küçükse o piksel seansın
başına, büyükse sonuna aittir. Alan bükülmüş olduğu için zaman düz akmaz;
kıvrılır, kollara ayrılır, kendi üstüne kapanır.

**Ortaya çıkış.** Görüntü `m ≤ ilerleme` olan yerlerde vardır. Seans ilerledikçe
mürekkep organik olarak yayılır — daire değil, gerçek bir yayılma. Sınır sert
değil, ıslak bir kenarla yumuşar.

**Doku ayrımı.** Her pikselin `m` değeri seans olaylarıyla karşılaştırılır: o an
çalışma ise yerel çalkantı ve kılcal yoğunluğu yükselir; mola ise alan
düzleşir, doygunluk düşer, kılcallar seyrelir.

**Renk.** Dar bir ton ailesi içinde, `m` ve alanın yerel eğimi kullanılarak
birkaç derecelik kayma. Değer aralığı sonuna kadar açık. Vurgu rengi yalnızca
kılcallarda ve çok az.

**Tohum.** Seansın kimliği alanın tohumudur. Aynı seans her açılışta aynı deseni
verir; başka seans başka desen. Tesadüf yok, tekrar yok.

**Maliyet.** Alan seans başına bir kez, düşük çözünürlüklü bir tampona hesaplanır
ve yumuşatılarak büyütülür. Kare döngüsü yok, parçacık yok, `requestAnimationFrame`
yok. Hesap bittiğinde işlemci tamamen serbest kalır.
