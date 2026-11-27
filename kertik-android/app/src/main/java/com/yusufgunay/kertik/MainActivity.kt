// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

package com.yusufgunay.kertik

import android.Manifest
import android.app.AutomaticZenRule
import android.app.NotificationManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.provider.Settings
import android.service.notification.Condition
import android.service.notification.ZenPolicy
import android.view.ViewGroup
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.webkit.WebViewAssetLoader
import com.google.android.gms.auth.api.identity.AuthorizationRequest
import com.google.android.gms.auth.api.identity.Identity
import com.google.android.gms.common.api.ApiException
import com.google.android.gms.common.api.Scope

/**
 * Kertik'in native kabuğu.
 *
 * Uygulamanın tamamı hâlâ tek bir `assets/index.html`. Bu sınıfın işi üç şey:
 *  1. O sayfayı `https://appassets.androidplatform.net/` kaynağından servis etmek
 *     (gerçek bir https kaynağı — Drive senkronunun CORS'u buna bağlı).
 *  2. Sayfadan gelen çağrılarla bildirim çubuğundaki canlı sayacı yönetmek.
 *  3. Bildirimdeki Mola/Devam/Bitir tuşlarını sayfaya geri iletmek.
 *
 * Zamanın tek doğruluk kaynağı hâlâ sayfadaki olay damgaları. Burada hiçbir süre
 * tutulmuyor, sayılmıyor, saklanmıyor — bildirim sadece bir gösterge.
 */
class MainActivity : ComponentActivity() {

    private lateinit var web: WebView
    private lateinit var bildirim: Bildirim
    private lateinit var kasa: Kasa
    private var sayfaHazir = false
    private var bekleyenEylem: String? = null

    override fun onCreate(state: Bundle?) {
        installSplashScreen()
        super.onCreate(state)
        aktifOrnek = this
        bildirim = Bildirim(this)

        // Yetim kalmış DND durumunu temizle (önceki oturum olağandışı sonlandıysa cihaz sessizde kalmasın)
        val prefs = getSharedPreferences(PREFS_ADI, Context.MODE_PRIVATE)
        run {
            val nm = getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
            if (nm != null && nm.isNotificationPolicyAccessGranted) {
                if (prefs.getBoolean(KEY_ZEN_AKTIF, false)) {
                    val kuralId = prefs.getString(KEY_ZEN_KURAL_ID, null)
                    if (kuralId != null) {
                        try {
                            nm.setAutomaticZenRuleState(kuralId, Condition(ZEN_KOSUL_URI, "", Condition.STATE_FALSE))
                        } catch (e: Exception) {}
                    }
                    prefs.edit().remove(KEY_ZEN_AKTIF).apply()
                }
                if (prefs.contains(KEY_DND_ORIJINAL)) {
                    val orijinal = prefs.getInt(KEY_DND_ORIJINAL, NotificationManager.INTERRUPTION_FILTER_ALL)
                    try { nm.setInterruptionFilter(orijinal) } catch (e: Exception) {}
                    prefs.edit().remove(KEY_DND_ORIJINAL).apply()
                }
            }
        }

        val yukleyici = WebViewAssetLoader.Builder()
            .addPathHandler("/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        web = WebView(this)
        web.layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT
        )
        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            mediaPlaybackRequiresUserGesture = false
            textZoom = 100                     // sistem yazı boyutu düzeni bozmasın
            cacheMode = android.webkit.WebSettings.LOAD_DEFAULT
        }
        web.isVerticalScrollBarEnabled = false
        web.overScrollMode = WebView.OVER_SCROLL_NEVER
        web.isHapticFeedbackEnabled = true
        if (BuildConfig.DEBUG) WebView.setWebContentsDebuggingEnabled(true)

        web.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView, request: WebResourceRequest
            ): WebResourceResponse? = yukleyici.shouldInterceptRequest(request.url)

            override fun shouldOverrideUrlLoading(
                view: WebView, request: WebResourceRequest
            ): Boolean {
                val u: Uri = request.url
                if (u.host == "appassets.androidplatform.net") return false
                // dış bağlantılar (ör. google.com/device) sistem tarayıcısında açılsın
                return try {
                    startActivity(Intent(Intent.ACTION_VIEW, u))
                    true
                } catch (e: Exception) {
                    true
                }
            }

            override fun onPageFinished(view: WebView, url: String) {
                sayfaHazir = true
                bekleyenEylem?.let { eylem -> bekleyenEylem = null; eylemGonder(eylem) }
            }
        }

        web.addJavascriptInterface(Kopru(), "KertikNative")

        /* Kertik Tam — tek seferlik uygulama içi ürün. Sayfa kilidi kendisi
           yönetiyor; buradaki köprü yalnız mağazayla konuşuyor (bkz. Kasa.kt). */
        kasa = Kasa(this, web)
        web.addJavascriptInterface(kasa.Kopru(), "KertikKasa")

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (web.canGoBack()) {
                    web.goBack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                    isEnabled = true
                }
            }
        })

        setContentView(web)
        web.loadUrl("https://appassets.androidplatform.net/index.html")

        eylemOku(intent)
        kasa.basla()
    }

    /* Satın alma başka bir cihazda yapılmış ya da iade edilmiş olabilir; öne
       her gelişte mağazaya sorulur. Sayfa sonucu kendisi bekliyor. */
    override fun onResume() {
        super.onResume()
        onPlanda = true
        if (::kasa.isInitialized) kasa.tazele()
    }

    /* Mola haberi yalnız uygulama öndeyken susar; öndeyse sayfa aynı anı kendisi karşılıyor. */
    override fun onPause() {
        onPlanda = false
        super.onPause()
    }

    override fun onNewIntent(yeni: Intent) {
        super.onNewIntent(yeni)
        intent = yeni
        eylemOku(yeni)
    }

    private fun eylemOku(gelen: Intent?) {
        val eylem = gelen?.getStringExtra(EXTRA_EYLEM) ?: return
        val sessiz = gelen.getBooleanExtra(EXTRA_SESSIZ, false)
        gelen.removeExtra(EXTRA_EYLEM)
        gelen.removeExtra(EXTRA_SESSIZ)
        if (sayfaHazir) eylemGonder(eylem) else bekleyenEylem = eylem
        if (sessiz) {
            moveTaskToBack(true)
        }
    }

    fun eylemGonder(eylem: String) {
        val guvenli = eylem.filter { it.isLetter() }        // sadece break/resume/end
        web.evaluateJavascript(
            "window.kertikNativeEylem && window.kertikNativeEylem('$guvenli')",
            null
        )
    }

    fun dndIzniVar(): Boolean {
        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return false
        return nm.isNotificationPolicyAccessGranted
    }

    fun dndIzniIste() {
        runOnUiThread {
            try {
                val intent = Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                startActivity(intent)
            } catch (e: Exception) {}
        }
    }

    // Kertik'in kendi odak modu. Kullanıcının kendi Rahatsız Etmeyin tanımına
    // dokunmaz; sistemin Modlar ekranında "Kertik" adıyla ayrı durur.
    //
    // Politika: mesaj ve bildirim sesi yok. Geçenler yalnızca alarmlar,
    // yıldızlı kişilerden aramalar ve aynı kişinin tekrar araması (acil durum).
    // Medya sesi açık kalır, çalışırken müzik dinleyen susturulmaz.
    //
    // Kural her seansta güncellenir; eski sürümün gevşek kuralı cihazda
    // kaldıysa ilk seansta düzelir. Kural kurulamazsa (bazı OEM kabukları)
    // cihazın normal Rahatsız Etmeyin moduna düşülür.
    private fun odakPolitikasi(): ZenPolicy? {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return null
        return ZenPolicy.Builder()
            .allowAlarms(true)
            .allowMedia(true)
            .allowSystem(false)
            .allowReminders(false)
            .allowEvents(false)
            .allowCalls(ZenPolicy.PEOPLE_TYPE_STARRED)
            .allowRepeatCallers(true)
            .allowMessages(ZenPolicy.PEOPLE_TYPE_NONE)
            .apply {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    allowConversations(ZenPolicy.CONVERSATION_SENDERS_NONE)
                }
            }
            .build()
    }

    private fun odakKuraliKur(): AutomaticZenRule {
        val politika = odakPolitikasi()
        if (Build.VERSION.SDK_INT >= 35) {
            return AutomaticZenRule.Builder("Kertik", ZEN_KOSUL_URI)
                .setType(AutomaticZenRule.TYPE_OTHER)
                .setConfigurationActivity(ComponentName(this, MainActivity::class.java))
                .setInterruptionFilter(NotificationManager.INTERRUPTION_FILTER_PRIORITY)
                .setIconResId(R.drawable.ic_odak_modu)
                .setTriggerDescription(getString(R.string.odak_modu_tetik))
                .setManualInvocationAllowed(false)
                .apply { if (politika != null) setZenPolicy(politika) }
                .build()
        }
        @Suppress("DEPRECATION")
        val kural = AutomaticZenRule(
            "Kertik",
            ComponentName(this, MainActivity::class.java),
            ZEN_KOSUL_URI,
            NotificationManager.INTERRUPTION_FILTER_PRIORITY,
            true
        )
        if (politika != null) kural.zenPolicy = politika
        return kural
    }

    private fun zenKuralIdGetir(nm: NotificationManager): String? {
        val prefs = getSharedPreferences(PREFS_ADI, Context.MODE_PRIVATE)
        val mevcut = prefs.getString(KEY_ZEN_KURAL_ID, null)
        if (mevcut != null) {
            val duruyor = try { nm.getAutomaticZenRule(mevcut) != null } catch (e: Exception) { false }
            if (duruyor) {
                if (prefs.getInt(KEY_ZEN_SURUM, 0) < ZEN_SURUM) {
                    try {
                        nm.updateAutomaticZenRule(mevcut, odakKuraliKur())
                        prefs.edit().putInt(KEY_ZEN_SURUM, ZEN_SURUM).apply()
                    } catch (e: Exception) {}
                }
                return mevcut
            }
        }

        return try {
            val yeniId = nm.addAutomaticZenRule(odakKuraliKur())
            prefs.edit().putString(KEY_ZEN_KURAL_ID, yeniId).putInt(KEY_ZEN_SURUM, ZEN_SURUM).apply()
            yeniId
        } catch (e: Exception) {
            null
        }
    }

    fun dndBaslat(): Boolean {
        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return false
        if (!nm.isNotificationPolicyAccessGranted) return false
        val prefs = getSharedPreferences(PREFS_ADI, Context.MODE_PRIVATE)

        val kuralId = zenKuralIdGetir(nm)
        if (kuralId != null) {
            val basarili = try {
                nm.setAutomaticZenRuleState(kuralId, Condition(ZEN_KOSUL_URI, "", Condition.STATE_TRUE))
                true
            } catch (e: Exception) {
                false
            }
            if (basarili) {
                prefs.edit().putBoolean(KEY_ZEN_AKTIF, true).apply()
                return true
            }
        }

        // Yedek yol: kural mekanizması bu cihazda çalışmadıysa eski küresel anahtar
        if (!prefs.contains(KEY_DND_ORIJINAL)) {
            val suanki = nm.currentInterruptionFilter
            prefs.edit().putInt(KEY_DND_ORIJINAL, suanki).apply()
        }
        return try {
            nm.setInterruptionFilter(NotificationManager.INTERRUPTION_FILTER_PRIORITY)
            true
        } catch (e: Exception) {
            false
        }
    }

    fun dndBitir() {
        val nm = getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return
        val prefs = getSharedPreferences(PREFS_ADI, Context.MODE_PRIVATE)

        val kuralId = prefs.getString(KEY_ZEN_KURAL_ID, null)
        if (kuralId != null && nm.isNotificationPolicyAccessGranted) {
            try {
                nm.setAutomaticZenRuleState(kuralId, Condition(ZEN_KOSUL_URI, "", Condition.STATE_FALSE))
            } catch (e: Exception) {}
        }
        prefs.edit().remove(KEY_ZEN_AKTIF).apply()

        // Yedek yoldan geldiyse eski filtreyi geri koy
        if (prefs.contains(KEY_DND_ORIJINAL)) {
            val orijinal = prefs.getInt(KEY_DND_ORIJINAL, NotificationManager.INTERRUPTION_FILTER_ALL)
            if (nm.isNotificationPolicyAccessGranted) {
                try { nm.setInterruptionFilter(orijinal) } catch (e: Exception) {}
            }
            prefs.edit().remove(KEY_DND_ORIJINAL).apply()
        }
    }

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
        val nightMode = newConfig.uiMode and android.content.res.Configuration.UI_MODE_NIGHT_MASK
        val koyu = nightMode == android.content.res.Configuration.UI_MODE_NIGHT_YES
        web.evaluateJavascript("window.sistemTemaDegisti && window.sistemTemaDegisti($koyu)", null)
    }

    override fun onDestroy() {
        if (aktifOrnek == this) aktifOrnek = null
        // Seans açıkken uygulama kapatılsa bile bildirim kalsın; süre damgalardan
        // hesaplandığı için doğru kalmaya devam eder.
        if (::kasa.isInitialized) kasa.kapat()
        web.removeJavascriptInterface("KertikNative")
        web.removeJavascriptInterface("KertikKasa")
        (web.parent as? ViewGroup)?.removeView(web)
        web.destroy()
        super.onDestroy()
    }

    /** Sayfadan çağrılan yüzey. Buradaki hiçbir metot veri yazmaz. */
    inner class Kopru {
        @JavascriptInterface
        fun sistemKoyuMu(): Boolean {
            val nightMode = resources.configuration.uiMode and android.content.res.Configuration.UI_MODE_NIGHT_MASK
            return nightMode == android.content.res.Configuration.UI_MODE_NIGHT_YES
        }

        @JavascriptInterface
        fun temaDegisti(koyu: Boolean) {
            runOnUiThread {
                try {
                    val renk = if (koyu) 0xFF131417.toInt() else 0xFFF5F1E6.toInt()
                    window.statusBarColor = renk
                    window.navigationBarColor = renk
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        val controller = window.insetsController
                        if (controller != null) {
                            val mask = android.view.WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS or
                                    android.view.WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS
                            if (koyu) {
                                controller.setSystemBarsAppearance(0, mask)
                            } else {
                                controller.setSystemBarsAppearance(mask, mask)
                            }
                        }
                    } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        @Suppress("DEPRECATION")
                        var flags = window.decorView.systemUiVisibility
                        flags = if (koyu) {
                            flags and android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR.inv() and
                                    android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR.inv()
                        } else {
                            flags or android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR or
                                    android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
                        }
                        @Suppress("DEPRECATION")
                        window.decorView.systemUiVisibility = flags
                    }
                } catch (e: Exception) {}
            }
        }

        @JavascriptInterface
        fun dndIzniVar(): Boolean = this@MainActivity.dndIzniVar()

        @JavascriptInterface
        fun dndIzniIste() = this@MainActivity.dndIzniIste()

        @JavascriptInterface
        fun dndBaslat(): Boolean = this@MainActivity.dndBaslat()

        @JavascriptInterface
        fun dndBitir() = this@MainActivity.dndBitir()

        @JavascriptInterface
        fun goster(baslik: String, alt: String, temelMs: String, geriSayim: Boolean, molada: Boolean) {
            val temel = temelMs.toLongOrNull() ?: return
            runOnUiThread { bildirim.goster(baslik, alt, temel, geriSayim, molada) }
        }

        @JavascriptInterface
        fun gizle() = runOnUiThread { bildirim.gizle() }

        /** Mola başlarken sayfa en çok iki an verir; bkz. [MolaHaberi]. */
        @JavascriptInterface
        fun molaHaberiKur(json: String) = MolaHaberi.kur(applicationContext, json)

        @JavascriptInterface
        fun molaHaberiIptal() = MolaHaberi.iptal(applicationContext)

        /**
         * Ana ekran widget'larının gördüğü durumu tazele.
         *
         * Widget ayrı bir süreçte çizilir ve WebView'in `localStorage`'ına
         * erişemez; bu yüzden web tarafı durumu her değiştiğinde küçük bir
         * JSON bırakıyor. Ayna **tek yönlü ve türev**: burada hiçbir şey
         * sayılmıyor, hesaplanmıyor. Bozulursa uygulamanın verisi etkilenmez.
         *
         * Widget hiç eklenmemişse [WidgetDurum.yenile] sessizce hiçbir şey
         * yapmaz, dolayısıyla bu çağrının maliyeti yok denecek kadar azdır.
         */
        @JavascriptInterface
        fun widgetDurum(json: String) {
            val ctx = applicationContext
            if (!WidgetDurum.yaz(ctx, json)) return
            runOnUiThread { WidgetDurum.yenile(ctx) }
        }

        @JavascriptInterface
        fun bildirimIzniVar(): Boolean = bildirim.izinVar()

        @JavascriptInterface
        fun bildirimIzniIste() {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return
            if (bildirim.izinVar()) return
            runOnUiThread {
                requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), IZIN_KODU)
            }
        }

        @JavascriptInterface
        fun ekraniAcikTut(acik: Boolean) = runOnUiThread {
            if (acik) window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            else window.clearFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        }

        private fun fireEffect(v: android.os.Vibrator, fx: android.os.VibrationEffect) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    try {
                        v.vibrate(
                            fx,
                            android.os.VibrationAttributes.Builder()
                                .setUsage(android.os.VibrationAttributes.USAGE_HARDWARE_FEEDBACK)
                                .build()
                        )
                        return
                    } catch (t: Throwable) {}
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    try {
                        v.vibrate(
                            fx,
                            android.media.AudioAttributes.Builder()
                                .setUsage(android.media.AudioAttributes.USAGE_ASSISTANCE_SONIFICATION)
                                .setContentType(android.media.AudioAttributes.CONTENT_TYPE_SONIFICATION)
                                .build()
                        )
                        return
                    } catch (t: Throwable) {}
                }
                v.vibrate(fx)
            } catch (e: Exception) {}
        }

        @JavascriptInterface
        fun titret(ms: Long) {
            titretHassas(ms, 190)
        }

        @JavascriptInterface
        fun titretHassas(ms: Long, genlik: Int) {
            runOnUiThread {
                try {
                    val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        (getSystemService(android.content.Context.VIBRATOR_MANAGER_SERVICE) as? android.os.VibratorManager)?.defaultVibrator
                    } else {
                        @Suppress("DEPRECATION")
                        getSystemService(android.content.Context.VIBRATOR_SERVICE) as? android.os.Vibrator
                    } ?: return@runOnUiThread

                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        val amp = genlik.coerceIn(1, 255)
                        val fx = if (vibrator.hasAmplitudeControl()) {
                            android.os.VibrationEffect.createOneShot(ms, amp)
                        } else {
                            android.os.VibrationEffect.createOneShot(ms, android.os.VibrationEffect.DEFAULT_AMPLITUDE)
                        }
                        fireEffect(vibrator, fx)
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator.vibrate(ms)
                    }
                } catch (e: Exception) {}
            }
        }

        @JavascriptInterface
        fun titretOnTanimli(efekt: String) {
            runOnUiThread {
                try {
                    val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        (getSystemService(android.content.Context.VIBRATOR_MANAGER_SERVICE) as? android.os.VibratorManager)?.defaultVibrator
                    } else {
                        @Suppress("DEPRECATION")
                        getSystemService(android.content.Context.VIBRATOR_SERVICE) as? android.os.Vibrator
                    } ?: return@runOnUiThread

                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        val effectId = when (efekt.lowercase().trim()) {
                            "click", "baslat", "kertik" -> android.os.VibrationEffect.EFFECT_CLICK
                            "heavy", "heavy_click", "tas" -> android.os.VibrationEffect.EFFECT_HEAVY_CLICK
                            "tick", "donum", "mandal" -> android.os.VibrationEffect.EFFECT_TICK
                            "double_click" -> android.os.VibrationEffect.EFFECT_DOUBLE_CLICK
                            else -> android.os.VibrationEffect.EFFECT_CLICK
                        }
                        val fx = android.os.VibrationEffect.createPredefined(effectId)
                        fireEffect(vibrator, fx)
                    } else {
                        titretHassas(12, 190)
                    }
                } catch (e: Exception) {}
            }
        }

        @JavascriptInterface
        fun titretPattern(patternStr: String) {
            runOnUiThread {
                try {
                    val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        (getSystemService(android.content.Context.VIBRATOR_MANAGER_SERVICE) as? android.os.VibratorManager)?.defaultVibrator
                    } else {
                        @Suppress("DEPRECATION")
                        getSystemService(android.content.Context.VIBRATOR_SERVICE) as? android.os.Vibrator
                    } ?: return@runOnUiThread

                    val parts = patternStr.split(",").mapNotNull { it.trim().toLongOrNull() }.toLongArray()
                    if (parts.isEmpty()) return@runOnUiThread
                    if (parts.size == 1) {
                        titretHassas(parts[0], 190)
                    } else {
                        val timings = LongArray(parts.size + 1)
                        timings[0] = 0
                        for (i in parts.indices) timings[i + 1] = parts[i]
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            val fx = android.os.VibrationEffect.createWaveform(timings, -1)
                            fireEffect(vibrator, fx)
                        } else {
                            @Suppress("DEPRECATION")
                            vibrator.vibrate(timings, -1)
                        }
                    }
                } catch (e: Exception) {}
            }
        }

        /**
         * Genlik zarflı doku. `titretPattern`'in aksine BURADA ZARF KAYBOLMAZ:
         * süreler ve genlikler birlikte gider, böylece 24-sanat-dili.md §6.5'teki
         * "sönümlenen darbe" gerçekten sönümlenir. Genlik denetimi olmayan eski
         * cihazlarda otomatik olarak düz desene düşer — titreşim yine olur,
         * sadece dokusu düzleşir.
         *
         * @param sureler   "22,26,12" — ms. Çift indisler vuruş, tek indisler sessizlik.
         * @param genlikler "190,0,95" — 1-255. Boş bırakılabilir.
         * @param komp      Android 12+ kompozisyon primitifi adı; desteklenmiyorsa yok sayılır.
         */
        @JavascriptInterface
        fun titretDoku(sureler: String, genlikler: String, komp: String) {
            runOnUiThread {
                try {
                    val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        (getSystemService(android.content.Context.VIBRATOR_MANAGER_SERVICE) as? android.os.VibratorManager)?.defaultVibrator
                    } else {
                        @Suppress("DEPRECATION")
                        getSystemService(android.content.Context.VIBRATOR_SERVICE) as? android.os.Vibrator
                    } ?: return@runOnUiThread

                    val t = sureler.split(",").mapNotNull { it.trim().toLongOrNull() }.toLongArray()
                    if (t.isEmpty()) return@runOnUiThread
                    val a = genlikler.split(",").mapNotNull { it.trim().toIntOrNull() }
                        .map { it.coerceIn(0, 255) }.toIntArray()

                    /* En iyi his: donanım primitifleri (Android 12+, destekleyen cihaz). */
                    if (komp.isNotBlank()) {
                        val efekt = kompozisyon(vibrator, komp)
                        if (efekt != null) {
                            fireEffect(vibrator, efekt)
                            return@runOnUiThread
                        }
                    }

                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O &&
                        a.size == t.size && vibrator.hasAmplitudeControl()) {
                        val fx = android.os.VibrationEffect.createWaveform(t, a, -1)
                        fireEffect(vibrator, fx)
                        return@runOnUiThread
                    }

                    /* Genliksiz yol: createWaveform(timings, -1) KAPALI durumdan başlar,
                       bu yüzden başa 0 eklenir. */
                    val timings = LongArray(t.size + 1)
                    timings[0] = 0
                    for (i in t.indices) timings[i + 1] = t[i]
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        val fx = android.os.VibrationEffect.createWaveform(timings, -1)
                        fireEffect(vibrator, fx)
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator.vibrate(timings, -1)
                    }
                } catch (e: Exception) {}
            }
        }

        /**
         * "Taşın kuma oturması" — pomodoro bitişinin dokusu. Telefon elde değil,
         * cepte ya da masada olduğu için tek istisna: bu doku bir yüzey değil,
         * bir haberdir. Yine de alarm değil: net bir darbe ve iki zayıflayan yankı.
         * Cihaz primitifi desteklemiyorsa null döner, çağıran taraf zarflı
         * waveform'a düşer — his biraz kabalaşır, davranış aynı kalır.
         */
        private fun kompozisyon(v: android.os.Vibrator, ad: String): android.os.VibrationEffect? {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.R) return null
            return try {
                val CLICK = android.os.VibrationEffect.Composition.PRIMITIVE_CLICK
                val TICK  = android.os.VibrationEffect.Composition.PRIMITIVE_TICK
                val LOW   = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S)
                    android.os.VibrationEffect.Composition.PRIMITIVE_LOW_TICK else TICK
                val THUD  = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S)
                    android.os.VibrationEffect.Composition.PRIMITIVE_THUD else CLICK

                when (ad) {
                    "tas_oturma" -> {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                            v.areAllPrimitivesSupported(THUD, LOW)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(THUD, 1.0f, 0)
                                .addPrimitive(LOW, 0.6f, 45)
                                .addPrimitive(LOW, 0.3f, 50)
                                .compose()
                        } else null
                    }
                    "sec" -> {
                        if (v.areAllPrimitivesSupported(CLICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(CLICK, 0.70f)
                                .compose()
                        } else if (v.areAllPrimitivesSupported(TICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(TICK, 0.75f)
                                .compose()
                        } else null
                    }
                    "baslat" -> {
                        if (v.areAllPrimitivesSupported(CLICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(CLICK, 0.90f)
                                .compose()
                        } else null
                    }
                    "kertik" -> {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                            v.areAllPrimitivesSupported(THUD)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(THUD, 0.85f)
                                .compose()
                        } else if (v.areAllPrimitivesSupported(CLICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(CLICK, 0.95f)
                                .compose()
                        } else null
                    }
                    "mola" -> {
                        if (v.areAllPrimitivesSupported(LOW)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(LOW, 0.60f)
                                .compose()
                        } else if (v.areAllPrimitivesSupported(TICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(TICK, 0.60f)
                                .compose()
                        } else null
                    }
                    "devam" -> {
                        if (v.areAllPrimitivesSupported(CLICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(CLICK, 0.75f)
                                .compose()
                        } else null
                    }
                    "bitir" -> {
                        if (v.areAllPrimitivesSupported(CLICK, TICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(CLICK, 0.85f, 0)
                                .addPrimitive(TICK, 0.60f, 40)
                                .compose()
                        } else if (v.areAllPrimitivesSupported(CLICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(CLICK, 0.85f)
                                .compose()
                        } else null
                    }
                    "not" -> {
                        if (v.areAllPrimitivesSupported(TICK)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(TICK, 0.80f)
                                .compose()
                        } else null
                    }
                    "donum" -> {
                        if (v.areAllPrimitivesSupported(LOW)) {
                            android.os.VibrationEffect.startComposition()
                                .addPrimitive(LOW, 0.50f)
                                .compose()
                        } else null
                    }
                    else -> null
                }
            } catch (e: Exception) { null }
        }

        /**
         * Google Drive (appdata) yetkisi. Gömülü bir istemci sırrı YOK — kimlik
         * paket adı + imza sertifikasının SHA-1'i üzerinden Google Cloud Console'da
         * eşleşiyor (bkz. 17-google-senkron.md). `interaktif=false` arka plan
         * eşitlemesi içindir: kullanıcıya hiçbir ekran göstermeden, önceden
         * verilmiş izin varsa sessizce tazeler; yoksa sessizce başarısız olur.
         * `interaktif=true` yalnız kullanıcı "bağlan"a bastığında kullanılır ve
         * gerekiyorsa Google'ın kendi hesap seçici ekranını açar.
         */
        @JavascriptInterface
        fun googleYetkiIste(interaktif: Boolean) {
            val istek = AuthorizationRequest.builder()
                .setRequestedScopes(listOf(Scope("https://www.googleapis.com/auth/drive.appdata")))
                .build()
            Identity.getAuthorizationClient(this@MainActivity)
                .authorize(istek)
                .addOnSuccessListener { sonuc ->
                    if (sonuc.hasResolution()) {
                        if (!interaktif) { yetkiSonucGonder(null, "izin_gerekli"); return@addOnSuccessListener }
                        try {
                            startIntentSenderForResult(
                                sonuc.pendingIntent!!.intentSender, YETKI_KODU, null, 0, 0, 0
                            )
                        } catch (e: Exception) {
                            yetkiSonucGonder(null, "baslatilamadi")
                        }
                    } else {
                        yetkiSonucGonder(sonuc.accessToken, null)
                    }
                }
                .addOnFailureListener { e -> yetkiSonucGonder(null, e.message ?: "hata") }
        }

        @JavascriptInterface
        fun surum(): String = BuildConfig.VERSION_NAME

        /**
         * Seansın resmini cihaza yazar. Sayfa PNG'yi base64 olarak veriyor;
         * burada tutulan, saklanan, hesaplanan hiçbir şey yok — gelen bayt
         * doğrudan diske gidiyor.
         *
         * Android 10 ve üstünde MediaStore'a yazılıyor: izin istemiyor,
         * dosya Resimler/Kertik altında galeride görünüyor. Daha eski
         * sürümlerde galeriye yazmak WRITE_EXTERNAL_STORAGE izni ister —
         * tek bir resim için o izni istemek orantısız, o yüzden orada
         * paylaşma ekranı açılıyor ve kullanıcı nereye kaydedeceğini seçiyor.
         *
         * Dönüş: "galeri" | "paylas" | "hata" — sayfa buna göre ne yazacağını bilir.
         */
        @JavascriptInterface
        fun resimKaydet(b64: String, ad: String): String = try {
            val bayt = android.util.Base64.decode(b64, android.util.Base64.DEFAULT)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) galeriyeYaz(bayt, ad)
            else { runOnUiThread { resmiPaylas(bayt, ad) }; "paylas" }
        } catch (e: Exception) { "hata" }

        /**
         * Seansın kartını/resmini doğrudan sistem paylaşım sayfasıyla (Instagram, WhatsApp, vb.) paylaşır.
         */
        @JavascriptInterface
        fun resimPaylas(b64: String, ad: String): String = try {
            val bayt = android.util.Base64.decode(b64, android.util.Base64.DEFAULT)
            runOnUiThread { resmiPaylas(bayt, ad) }
            "paylas"
        } catch (e: Exception) { "hata" }

        /**
         * JSON yedek dosyasını cihaza kaydeder veya paylaşır.
         * Android 10+: MediaStore.Downloads ile doğrudan İndirilenler klasörüne yazar.
         * Android 9 ve altı ya da hata durumunda: Paylaşım intent'i ile kullanıcıya sunar.
         *
         * Dönüş: "indirildi" | "paylas" | "hata" — sayfa buna göre buton metnini günceller.
         */
        @JavascriptInterface
        fun yedekKaydet(json: String, ad: String): String = try {
            val bayt = json.toByteArray(Charsets.UTF_8)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) indirilenlereYaz(bayt, ad)
            else { runOnUiThread { yedegiPaylas(bayt, ad) }; "paylas" }
        } catch (e: Exception) { "hata" }
    }

    /** Android 10+: izinsiz, doğrudan galeriye. */
    @androidx.annotation.RequiresApi(Build.VERSION_CODES.Q)
    private fun galeriyeYaz(bayt: ByteArray, ad: String): String {
        val alanlar = android.content.ContentValues()
        alanlar.put(MediaStore.Images.Media.DISPLAY_NAME, ad)
        alanlar.put(MediaStore.Images.Media.MIME_TYPE, "image/png")
        alanlar.put(MediaStore.Images.Media.RELATIVE_PATH, android.os.Environment.DIRECTORY_PICTURES + "/Kertik")
        alanlar.put(MediaStore.Images.Media.IS_PENDING, 1)

        val cozucu = contentResolver
        val hedef = cozucu.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, alanlar)
        if (hedef == null) return "hata"

        try {
            val akis = cozucu.openOutputStream(hedef)
            if (akis == null) throw java.io.IOException("akış açılamadı")
            akis.use { it.write(bayt) }
        } catch (e: Exception) {
            // Yarım kalan kaydı bırakma: IS_PENDING'de takılı dosya galeriyi kirletir.
            try { cozucu.delete(hedef, null, null) } catch (_: Exception) {}
            return "hata"
        }

        val bitti = android.content.ContentValues()
        bitti.put(MediaStore.Images.Media.IS_PENDING, 0)
        cozucu.update(hedef, bitti, null, null)
        return "galeri"
    }

    /** Android 9 ve altı: izin istemek yerine paylaşma ekranı. */
    private fun resmiPaylas(bayt: ByteArray, ad: String) {
        try {
            val dizin = java.io.File(cacheDir, "resim").apply { mkdirs() }
            dizin.listFiles()?.forEach { it.delete() }      // önceki denemeler birikmesin
            val dosya = java.io.File(dizin, ad)
            dosya.writeBytes(bayt)
            val u = androidx.core.content.FileProvider.getUriForFile(
                this, "$packageName.dosya", dosya
            )
            val niyet = Intent(Intent.ACTION_SEND).apply {
                type = "image/png"
                putExtra(Intent.EXTRA_STREAM, u)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(niyet, getString(R.string.resmi_kaydet)))
        } catch (e: Exception) { /* sessiz: sayfa zaten "paylas" duydu */ }
    }

    /** Android 10+: izinsiz, doğrudan İndirilenler klasörüne. */
    @androidx.annotation.RequiresApi(Build.VERSION_CODES.Q)
    private fun indirilenlereYaz(bayt: ByteArray, ad: String): String {
        val alanlar = android.content.ContentValues()
        alanlar.put(MediaStore.Downloads.DISPLAY_NAME, ad)
        alanlar.put(MediaStore.Downloads.MIME_TYPE, "application/json")
        alanlar.put(MediaStore.Downloads.RELATIVE_PATH, android.os.Environment.DIRECTORY_DOWNLOADS + "/Kertik")
        alanlar.put(MediaStore.Downloads.IS_PENDING, 1)

        val cozucu = contentResolver
        val hedef = cozucu.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, alanlar)
        if (hedef == null) return "hata"

        try {
            val akis = cozucu.openOutputStream(hedef)
            if (akis == null) throw java.io.IOException("akış açılamadı")
            akis.use { it.write(bayt) }
        } catch (e: Exception) {
            // Yarım kalan kaydı bırakma
            try { cozucu.delete(hedef, null, null) } catch (_: Exception) {}
            return "hata"
        }

        val bitti = android.content.ContentValues()
        bitti.put(MediaStore.Downloads.IS_PENDING, 0)
        cozucu.update(hedef, bitti, null, null)
        return "indirildi"
    }

    /** Android 9 ve altı ya da doğrudan paylaşım: FileProvider üzerinden paylaşma ekranı. */
    private fun yedegiPaylas(bayt: ByteArray, ad: String) {
        try {
            val dizin = java.io.File(cacheDir, "yedek").apply { mkdirs() }
            dizin.listFiles()?.forEach { it.delete() }      // önceki denemeler birikmesin
            val dosya = java.io.File(dizin, ad)
            dosya.writeBytes(bayt)
            val u = androidx.core.content.FileProvider.getUriForFile(
                this, "$packageName.dosya", dosya
            )
            val niyet = Intent(Intent.ACTION_SEND).apply {
                type = "application/json"
                putExtra(Intent.EXTRA_STREAM, u)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(niyet, getString(R.string.yedegi_kaydet)))
        } catch (e: Exception) { /* sessiz: sayfa zaten "paylas" duydu */ }
    }

    /** `googleYetkiIste`nin sonucunu sayfaya iletir. Hiçbir süre/veri burada tutulmaz. */
    private fun yetkiSonucGonder(token: String?, hata: String?) {
        val t = token?.let { "\"" + it.replace("\"", "\\\"") + "\"" } ?: "null"
        val h = hata?.let { "\"" + it.replace("\"", "\\\"") + "\"" } ?: "null"
        runOnUiThread {
            web.evaluateJavascript("window.kertikYetkiSonuc && window.kertikYetkiSonuc($t, $h)", null)
        }
    }

    override fun onActivityResult(kod: Int, sonucKodu: Int, veri: Intent?) {
        super.onActivityResult(kod, sonucKodu, veri)
        if (kod != YETKI_KODU) return
        try {
            val sonuc = Identity.getAuthorizationClient(this).getAuthorizationResultFromIntent(veri)
            yetkiSonucGonder(sonuc.accessToken, null)
        } catch (e: ApiException) {
            yetkiSonucGonder(null, "reddedildi")
        } catch (e: Exception) {
            yetkiSonucGonder(null, "reddedildi")
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == IZIN_KODU && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            web.evaluateJavascript("window.nativeBildir && window.nativeBildir(true)", null)
        }
    }

    companion object {
        var aktifOrnek: MainActivity? = null
        /** Etkinlik şu an ekranda mı (onResume ile onPause arası). */
        @Volatile var onPlanda = false
        const val EXTRA_EYLEM = "kertik_eylem"
        const val EXTRA_SESSIZ = "kertik_sessiz"
        const val EYLEM_BROADCAST = "com.yusufgunay.kertik.EYLEM"
        private const val IZIN_KODU = 91
        private const val YETKI_KODU = 92
        private const val PREFS_ADI = "kertik_ayarlar"
        private const val KEY_DND_ORIJINAL = "dnd_orijinal_filtre"
        private const val KEY_ZEN_KURAL_ID = "zen_kural_id"
        private const val KEY_ZEN_AKTIF = "zen_aktif"
        private const val KEY_ZEN_SURUM = "zen_kural_surum"
        private const val ZEN_SURUM = 3
        private val ZEN_KOSUL_URI: Uri = Uri.parse("condition://com.yusufgunay.kertik/seans")
    }
}
