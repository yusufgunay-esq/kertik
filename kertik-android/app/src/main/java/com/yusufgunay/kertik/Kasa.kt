package com.yusufgunay.kertik

import android.app.Activity
import android.content.Context
import android.webkit.JavascriptInterface
import android.webkit.WebView
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import org.json.JSONObject

/**
 * Kertik Tam — tek seferlik uygulama içi ürün.
 *
 * Uygulama mağazada ücretsiz. Kurulumdan sonra on dört gün her şey açık;
 * süre dolunca uygulama KİLİTLENMEZ, düşer. Çekirdek — sayaç, seans, görevler,
 * dürüst kayıt, geçmiş, yedek, bulut, tema, diller — hiçbir zaman kilitlenmez.
 * Kullanıcının kendi kaydı asla rehin alınmaz (bkz. Fiyat.md, 16-para-kazanma.md).
 *
 * Bu sınıf yalnız bir kapıdır: hiçbir şey saymaz, hiçbir kullanıcı verisine
 * dokunmaz. Tuttuğu tek şey mağazadan gelen yanıtın gölgesi (sahiplik ve
 * biçimlenmiş fiyat), o da uçak modunda açılışta ekranın doğru görünmesi için.
 * Doğruluğun kaynağı her zaman mağazadır: bağlantı kurulduğu anda gölge tazelenir.
 *
 * Sayfa tarafındaki karşılığı `index.html` içindeki "Kertik Tam" bölümüdür.
 * Köprü yoksa sayfa kilidi kendiliğinden açık sayar: bir arıza kullanıcının
 * aleyhine sonuçlanmaz.
 */
class Kasa(private val etkinlik: Activity, private val web: WebView) : PurchasesUpdatedListener {

    companion object {
        /** Play Console'daki ürün kimliği. */
        const val URUN = "kertik_tam"

        private const val PREFS = "kertik_kasa"
        private const val A_SAHIP = "sahip"
        private const val A_FIYAT = "fiyat"
    }

    private val prefs = etkinlik.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    @Volatile private var urun: ProductDetails? = null
    @Volatile private var hazir = false

    private val istemci: BillingClient = BillingClient.newBuilder(etkinlik)
        .setListener(this)
        .enablePendingPurchases(
            PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()
        )
        /* Bağlantı düşerse kütüphane kendi kurar; elle yeniden bağlanma kodu yok. */
        .enableAutoServiceReconnection()
        .build()

    // ------------------------------------------------------------------ yaşam

    fun basla() {
        if (istemci.isReady) { tazele(); return }
        istemci.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(sonuc: BillingResult) {
                hazir = sonuc.responseCode == BillingClient.BillingResponseCode.OK
                if (hazir) tazele() else sayfayaBildir(null)
            }
            override fun onBillingServiceDisconnected() { hazir = false }
        })
    }

    /**
     * Ürünü ve sahipliği yeniden okur. Her `onResume`'da çağrılır: satın alma
     * başka bir cihazda yapılmış ya da iade edilmiş olabilir.
     */
    fun tazele() {
        if (!istemci.isReady) { basla(); return }
        urunuOku()
        sahipligiOku(false)
    }

    fun kapat() {
        try { istemci.endConnection() } catch (e: Exception) {}
    }

    // ----------------------------------------------------------------- gölge

    private fun sahipMi(): Boolean = prefs.getBoolean(A_SAHIP, false)

    private fun fiyat(): String = prefs.getString(A_FIYAT, "").orEmpty()

    private fun sahipYaz(deger: Boolean) {
        if (prefs.getBoolean(A_SAHIP, false) == deger) return
        prefs.edit().putBoolean(A_SAHIP, deger).apply()
    }

    // ---------------------------------------------------------------- mağaza

    /**
     * Tek seferlik ürünün teklifi.
     *
     * Play iki ayrı alan sunuyor ve hangisinin dolu geleceği ürünün Console'da
     * nasıl kurulduğuna bağlı: çoklu satın alma seçeneği tanımlanmış ürünlerde
     * LİSTE dolu gelir, tek seçenekli sade bir üründe liste NULL döner ve teklif
     * tekil alanda durur. `kertik_tam` sade bir ürün, yani bugün çalışan yol
     * ikincisi; ileride seçenek eklenirse ilki devreye giriyor.
     *
     * Bu ayrım gözden kaçarsa fiyat hiç okunamaz ve satın alma düğmesi rakamsız
     * kalır.
     */
    @Suppress("DEPRECATION")
    private fun teklif(d: ProductDetails): ProductDetails.OneTimePurchaseOfferDetails? =
        d.oneTimePurchaseOfferDetailsList?.firstOrNull() ?: d.oneTimePurchaseOfferDetails

    private fun urunuOku() {
        val istek = QueryProductDetailsParams.newBuilder()
            .setProductList(
                listOf(
                    QueryProductDetailsParams.Product.newBuilder()
                        .setProductId(URUN)
                        .setProductType(BillingClient.ProductType.INAPP)
                        .build()
                )
            )
            .build()

        istemci.queryProductDetailsAsync(istek) { sonuc, paket ->
            if (sonuc.responseCode == BillingClient.BillingResponseCode.OK) {
                val d = paket.productDetailsList.orEmpty().firstOrNull()
                urun = d
                /* Fiyatı biz biçimlendirmiyoruz: para birimi, ayraç ve sıra
                   ülkeye göre değişiyor, mağaza hazır veriyor. */
                val f = d?.let { teklif(it) }?.formattedPrice
                if (!f.isNullOrBlank()) prefs.edit().putString(A_FIYAT, f).apply()
            }
            sayfayaBildir(null)
        }
    }

    /**
     * @param geriYukleme kullanıcı "daha önce aldım" dediyse true. Yalnız o
     *   durumda sonuç bulunamadığında sayfaya bir not düşülür; arka plandaki
     *   sessiz tazelemeler hiçbir şey yazmaz.
     */
    private fun sahipligiOku(geriYukleme: Boolean) {
        val istek = QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.INAPP)
            .build()

        istemci.queryPurchasesAsync(istek) { sonuc, liste ->
            if (sonuc.responseCode == BillingClient.BillingResponseCode.OK) {
                var bulundu = false
                for (a in liste.orEmpty()) {
                    if (!a.products.contains(URUN)) continue
                    if (a.purchaseState != Purchase.PurchaseState.PURCHASED) continue
                    bulundu = true
                    onayla(a)
                }
                /* Yanıt OK ise liste yetkilidir: iade edilmiş bir satın alma
                   burada görünmez ve sahiplik geri alınır. Yanıt OK DEĞİLSE
                   (çevrimdışı, mağaza yok) gölgeye dokunulmaz. */
                sahipYaz(bulundu)
                sayfayaBildir(if (geriYukleme && !bulundu) "yok" else null)
            } else {
                sayfayaBildir(if (geriYukleme) "olmadi" else null)
            }
        }
    }

    private fun onayla(a: Purchase) {
        if (a.isAcknowledged) return
        val p = AcknowledgePurchaseParams.newBuilder()
            .setPurchaseToken(a.purchaseToken)
            .build()
        istemci.acknowledgePurchase(p) { }
    }

    private fun satinAlmaAkisi() {
        val d = urun
        if (!istemci.isReady || d == null) { basla(); sayfayaBildir("olmadi"); return }

        val secenek = BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(d)
        /* Çoklu seçenekli üründe belirteç zorunlu, sade üründe gereksiz. Varsa
           veriliyor, yoksa hiç konmuyor; ikisi de Play'in kabul ettiği biçim. */
        val belirtec = teklif(d)?.offerToken
        if (!belirtec.isNullOrBlank()) secenek.setOfferToken(belirtec)

        val akis = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(listOf(secenek.build()))
            .build()

        etkinlik.runOnUiThread {
            try { istemci.launchBillingFlow(etkinlik, akis) }
            catch (e: Exception) { sayfayaBildir("olmadi") }
        }
    }

    override fun onPurchasesUpdated(sonuc: BillingResult, liste: MutableList<Purchase>?) {
        when (sonuc.responseCode) {
            BillingClient.BillingResponseCode.OK -> {
                var bulundu = false
                liste?.forEach { a ->
                    if (a.products.contains(URUN) &&
                        a.purchaseState == Purchase.PurchaseState.PURCHASED
                    ) {
                        bulundu = true
                        onayla(a)
                    }
                }
                if (bulundu) sahipYaz(true)
                sayfayaBildir(null)
            }
            /* Kullanıcı zaten sahip: mağazaya sorup gölgeyi düzelt. */
            BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED -> sahipligiOku(false)
            BillingClient.BillingResponseCode.USER_CANCELED -> sayfayaBildir("iptal")
            else -> sayfayaBildir("olmadi")
        }
    }

    // ----------------------------------------------------------------- sayfa

    /**
     * Sayfaya durumu bildirir. Not alanı yalnız kullanıcının başlattığı bir
     * işlemin sonucunu anlatır: "iptal", "olmadi", "yok". Boşsa sessiz tazeleme.
     */
    private fun sayfayaBildir(not: String?) {
        val js = "window.kertikKasaDurum && window.kertikKasaDurum(" +
                sahipMi() + "," +
                JSONObject.quote(fiyat()) + "," +
                JSONObject.quote(not.orEmpty()) + ")"
        etkinlik.runOnUiThread {
            try { web.evaluateJavascript(js, null) } catch (e: Exception) {}
        }
    }

    /** Sayfadan görünen yüzey. Buradaki hiçbir metot veri yazmaz. */
    inner class Kopru {
        @JavascriptInterface
        fun durum(): String = JSONObject()
            .put("sahip", sahipMi())
            .put("fiyat", fiyat())
            .put("hazir", istemci.isReady)
            .toString()

        @JavascriptInterface
        fun satinAl() = satinAlmaAkisi()

        @JavascriptInterface
        fun geriYukle() {
            if (!istemci.isReady) { basla(); sayfayaBildir("olmadi"); return }
            sahipligiOku(true)
        }
    }
}
