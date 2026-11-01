// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

package com.yusufgunay.kertik

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.RectF
import android.os.Build
import android.os.Bundle
import android.os.SystemClock
import android.util.TypedValue
import android.view.View
import android.widget.RemoteViews
import androidx.core.content.ContextCompat

/**
 * Ana ekrandaki Kontrol Widget'ı (4×2 ve dinamik boyutlar).
 *
 * Canlı sanat tuvali (Ebru / Kum Bahçesi) ve C-Kertik kalası / kum bahçesi
 * vitriniyle uygulamanın yaşayan bir parçasıdır.
 */
class KontrolWidget : AppWidgetProvider() {

    override fun onUpdate(ctx: Context, yon: AppWidgetManager, idler: IntArray) {
        for (id in idler) ciz(ctx, yon, id)
    }

    override fun onAppWidgetOptionsChanged(
        ctx: Context, yon: AppWidgetManager, id: Int, yeni: Bundle?
    ) {
        ciz(ctx, yon, id)
    }

    private fun ciz(ctx: Context, yon: AppWidgetManager, id: Int) {
        val d = WidgetDurum.oku(ctx)
        val gece = (ctx.resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) ==
                Configuration.UI_MODE_NIGHT_YES

        val r = RemoteViews(ctx.packageName, R.layout.widget_kontrol)
        val p = paletAl(ctx, gece)

        // 1. Durum Başlığı — 15 dilli kaynaklardan; büyük harf görünümü (ÇALIŞIYOR /
        // MOLADA / KERTİK) her dilde aynı kalsın diye tasarım kararı olarak korunuyor.
        val (etiket, etiketRenk) = when (d.durum) {
            WidgetDurum.CALISIYOR ->
                (if (d.mod == "pomodoro") ctx.getString(R.string.widget_pomodoro) else ctx.getString(R.string.widget_calisiyor))
                    .uppercase() to p.vurgu
            WidgetDurum.MOLADA -> ctx.getString(R.string.widget_molada).uppercase() to p.serin
            else -> ctx.getString(R.string.app_name).uppercase() to p.soluk
        }
        r.setTextViewText(R.id.wDurum, etiket)
        r.setTextColor(R.id.wDurum, etiketRenk)

        // 2. Sayaç / Süre
        if (d.seansVar) {
            r.setViewVisibility(R.id.wSayac, View.VISIBLE)
            r.setViewVisibility(R.id.wDurgun, View.GONE)
            val temel = SystemClock.elapsedRealtime() - (System.currentTimeMillis() - d.temelMs)
            r.setChronometer(R.id.wSayac, temel, null, true)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                r.setChronometerCountDown(R.id.wSayac, d.geriSayim)
            }
            r.setTextColor(
                R.id.wSayac,
                if (d.durum == WidgetDurum.MOLADA) p.serin else p.murekkep
            )
        } else {
            r.setViewVisibility(R.id.wSayac, View.GONE)
            r.setViewVisibility(R.id.wDurgun, View.VISIBLE)
            r.setTextViewText(R.id.wDurgun, sureKisa(d.bugunNetMs))
            r.setTextColor(R.id.wDurgun, p.murekkep)
        }

        // 3. Alt Bilgi
        r.setTextViewText(R.id.wAlt, altSatir(ctx, d))
        r.setTextColor(R.id.wAlt, p.soluk)

        // 4. Düğmeler
        val birincilYazi: String
        val birincilEylem: String
        when (d.durum) {
            WidgetDurum.CALISIYOR -> {
                birincilYazi = ctx.getString(R.string.bildirim_mola)
                birincilEylem = "break"
            }
            WidgetDurum.MOLADA -> {
                birincilYazi = ctx.getString(R.string.bildirim_devam)
                birincilEylem = "resume"
            }
            else -> {
                birincilYazi = ctx.getString(R.string.widget_baslat)
                birincilEylem = "start"
            }
        }
        r.setTextViewText(R.id.wBir, birincilYazi)
        r.setTextColor(R.id.wBir, if (d.durum == WidgetDurum.MOLADA) Color.WHITE else p.kagit)
        r.setOnClickPendingIntent(R.id.wBir, eylem(ctx, birincilEylem))

        if (d.seansVar) {
            r.setViewVisibility(R.id.wIki, View.VISIBLE)
            r.setTextViewText(R.id.wIki, ctx.getString(R.string.bildirim_bitir))
            r.setTextColor(R.id.wIki, p.soluk)
            r.setOnClickPendingIntent(R.id.wIki, eylem(ctx, "end"))
        } else {
            r.setViewVisibility(R.id.wIki, View.GONE)
        }

        // Gövdeye dokunulduğunda uygulamayı aç
        r.setOnClickPendingIntent(R.id.wKok, eylem(ctx, null))

        // 5-6. Canlı Arka Plan Tuvali + Sağ Vitrin.
        // Binder işlem sınırı (~1 MB) aşılmasın diye vitrin ayrı bir RemoteViews
        // bitmap'i olarak DEĞİL, tuval bitmap'inin üstüne gömülü olarak gönderiliyor
        // (bkz. WidgetCizer.ENCOK_BAYT — artık bayt bütçesiyle hesaplanıyor, hem de
        // tek bitmap göndererek Binder'a giden toplam veri daha da azaltılıyor).
        val boy = boyutDp(yon, id)
        val wPx = dp(ctx, boy.first.toFloat()).toInt()
        val hPx = dp(ctx, boy.second.toFloat()).toInt()

        val seansDk = (d.netMs / 60000).toInt()
        val bugunDk = (d.bugunNetMs / 60000).toInt()
        val gun = WidgetCizer.gunAnahtari()
        val bugunTas = d.duvar.firstOrNull { it.oncekiGun == 0 }?.tas ?: 0

        // Sanat moda bağlı, seansın var olup olmamasına değil: pomodoro kum bahçesi,
        // kronometre ebru. Boştayken mod değiştirmek iki dili karıştırıyordu.
        val tuvalBm = if (d.mod == "pomodoro") {
            WidgetCizer.kumBahcesiTuvali(wPx, hPx, gun, bugunTas, gece, p)
        } else {
            WidgetCizer.ebruTuvali(
                wPx, hPx,
                WidgetCizer.hash32(d.baslangic.ifEmpty { "live" }),
                if (d.seansVar) seansDk else bugunDk,
                d.durum == WidgetDurum.MOLADA,
                p
            )
        }

        val vitrinW = dp(ctx, 72f).toInt()
        val vitrinH = dp(ctx, (boy.second - 20).coerceIn(50, 160).toFloat()).toInt()

        // Vitrin YALNIZ gerçek veriyle çizilir. Çalışılmamışken çentik veya taş
        // göstermek uygulamanın kendi ilkesine (dürüst süre kaydı) aykırı; veri
        // yoksa vitrin hiç görünmez.
        val vitrinBm = if (d.mod == "pomodoro") {
            if (bugunTas > 0) WidgetCizer.kumBahcesiTuvali(vitrinW, vitrinH, gun, bugunTas, gece, p) else null
        } else {
            val veri = d.cubuk ?: if (bugunDk > 0) {
                WidgetDurum.Cubuk("w-day", bugunDk, emptyList(), 0)
            } else null
            if (veri != null) {
                WidgetCizer.cizCKertik(veri, p, vitrinW, vitrinH, if (d.seansVar) 0f else 0.50f)
            } else null
        }

        if (tuvalBm != null) {
            if (vitrinBm != null) {
                birlestirVitrin(tuvalBm, vitrinBm, ctx, wPx, hPx)
            }
            r.setImageViewBitmap(R.id.wTuval, tuvalBm)
            r.setViewVisibility(R.id.wTuval, View.VISIBLE)
            r.setViewVisibility(R.id.wVitrin, View.GONE)
        } else if (vitrinBm != null) {
            // Tuval çizilemediyse (ör. bellek darlığı) en azından vitrini eski
            // yoldan, kendi görünümünde göster.
            r.setViewVisibility(R.id.wTuval, View.GONE)
            r.setImageViewBitmap(R.id.wVitrin, vitrinBm)
            r.setViewVisibility(R.id.wVitrin, View.VISIBLE)
        } else {
            r.setViewVisibility(R.id.wTuval, View.GONE)
            r.setViewVisibility(R.id.wVitrin, View.GONE)
        }

        r.setInt(
            R.id.wKok, "setBackgroundResource",
            if (gece) R.drawable.widget_arka_gece else R.drawable.widget_arka
        )

        yon.updateAppWidget(id, r)
    }

    /** Vitrini tuval bitmap'inin sağ kenarına gömer — wVitrinAlani'nin XML'deki
     * konumuyla aynı oranda (74dp genişlik, 12dp sağ boşluk, 10dp üst/alt).
     * Tuval kucult() ile küçültülmüş olabilir; hedef dikdörtgen tuvalin KENDİ
     * piksel boyutuna göre orantılanır, bu yüzden her zaman doğru yere düşer. */
    private fun birlestirVitrin(tuval: android.graphics.Bitmap, vitrin: android.graphics.Bitmap, ctx: Context, istenenW: Int, istenenH: Int) {
        try {
            val c = Canvas(tuval)
            val olcekX = tuval.width / istenenW.toFloat()
            val olcekY = tuval.height / istenenH.toFloat()
            val marjSag = dp(ctx, 12f)
            val vitrinAlaniW = dp(ctx, 74f)
            val dX1 = (istenenW - marjSag) * olcekX
            val dX0 = dX1 - vitrinAlaniW * olcekX
            val dY0 = dp(ctx, 10f) * olcekY
            val dY1 = tuval.height - dY0
            if (dX1 > dX0 && dY1 > dY0) {
                val boya = Paint(Paint.ANTI_ALIAS_FLAG)
                c.drawBitmap(vitrin, null, RectF(dX0, dY0, dX1, dY1), boya)
            }
        } catch (e: Exception) {
            // Birleştirme başarısız olsa da tuval kendi başına gösterilebilir durumda kalır.
        }
    }

    private fun altSatir(ctx: Context, d: WidgetDurum): String = when {
        d.durum == WidgetDurum.MOLADA -> ctx.getString(R.string.widget_mola_alt)
        d.durum == WidgetDurum.CALISIYOR && d.mod == "pomodoro" && d.hedefDk > 0 ->
            ctx.getString(R.string.widget_ilerleme, d.netMs / 60000, d.hedefDk)
        d.durum == WidgetDurum.CALISIYOR && d.not.isNotBlank() -> d.not
        d.durum == WidgetDurum.CALISIYOR && d.baslangic.isNotBlank() ->
            ctx.getString(R.string.widget_basladin, d.baslangic)
        d.durum == WidgetDurum.CALISIYOR -> ctx.getString(R.string.widget_centik, d.netMs / 60000)
        d.bugunNetMs > 0 -> ctx.getString(R.string.widget_bugun_dk, d.bugunNetMs / 60000)
        else -> ctx.getString(R.string.widget_bos)
    }

    private fun sureKisa(ms: Long): String {
        val dk = ms / 60000
        val s = dk / 60
        val d = dk % 60
        return if (s > 0) "${s}s %02d".format(d) else "%02d:00".format(d)
    }

    private fun paletAl(ctx: Context, gece: Boolean): WidgetCizer.Palet {
        fun c(gunduzId: Int, geceId: Int): Int {
            return ContextCompat.getColor(ctx, if (gece) geceId else gunduzId)
        }
        return WidgetCizer.Palet(
            kagit = c(R.color.w_kagit, R.color.w_kagit_gece),
            murekkep = c(R.color.w_murekkep, R.color.w_murekkep_gece),
            soluk = c(R.color.w_soluk, R.color.w_soluk_gece),
            cizgi = c(R.color.w_cizgi, R.color.w_cizgi_gece),
            vurgu = c(R.color.w_vurgu, R.color.w_vurgu_gece),
            serin = c(R.color.w_serin, R.color.w_serin_gece),
            kopru = c(R.color.w_kopru, R.color.w_kopru_gece),
            mola1 = c(R.color.w_mola1, R.color.w_mola1_gece),
            mola2 = c(R.color.w_mola2, R.color.w_mola2_gece),
            tas = c(R.color.w_tas, R.color.w_tas_gece),
            tasIsik = c(R.color.w_tas_isik, R.color.w_tas_isik_gece)
        )
    }

    private fun eylem(ctx: Context, komut: String?): PendingIntent {
        val niyet = Intent(ctx, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
            if (komut != null) putExtra(MainActivity.EXTRA_EYLEM, komut)
        }
        val bayrak = PendingIntent.FLAG_UPDATE_CURRENT or
                (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        val istekKodu = komut?.hashCode() ?: 0
        return PendingIntent.getActivity(ctx, istekKodu, niyet, bayrak)
    }

    private fun dp(ctx: Context, v: Float): Float =
        TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, ctx.resources.displayMetrics)

    private fun boyutDp(yon: AppWidgetManager, id: Int): Pair<Int, Int> {
        val sec = yon.getAppWidgetOptions(id) ?: return 250 to 110
        val w = sec.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH, 250)
        val h = sec.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT, 110)
        return w to h
    }
}
