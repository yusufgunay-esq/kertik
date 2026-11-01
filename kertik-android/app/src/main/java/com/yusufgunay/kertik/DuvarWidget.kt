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
import android.os.Build
import android.os.Bundle
import android.util.TypedValue
import android.view.View
import android.widget.RemoteViews
import androidx.core.content.ContextCompat

/**
 * Son 30 günün emeğini gösteren Duvar Widget'ı.
 *
 * 30 gün boyunca C · Kertik kalasları ve kum bahçesi taşları galerisini
 * kademeli patina solmasıyla sergiler.
 */
class DuvarWidget : AppWidgetProvider() {

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

        val r = RemoteViews(ctx.packageName, R.layout.widget_duvar)
        val p = paletAl(ctx, gece)

        // 1. Başlık ve Özet
        r.setTextViewText(R.id.wDuvarBaslik, ctx.getString(R.string.app_name).uppercase() + " · " + ctx.getString(R.string.widget_duvar_baslik).uppercase())
        r.setTextColor(R.id.wDuvarBaslik, p.soluk)

        val calisilanGun = d.duvar.count { it.dk > 0 || it.tas > 0 }
        val ozet = ctx.getString(R.string.widget_otuz_gun) + (
            if (calisilanGun > 0) " · " + ctx.getString(R.string.widget_gunde_seans, calisilanGun) else ""
        )
        r.setTextViewText(R.id.wDuvarOzet, ozet)
        r.setTextColor(R.id.wDuvarOzet, p.soluk)

        r.setTextViewText(R.id.wDuvarSol, ctx.getString(R.string.widget_gun_once, 30))
        r.setTextColor(R.id.wDuvarSol, p.soluk)
        r.setTextViewText(R.id.wDuvarSag, ctx.getString(R.string.widget_bugun))
        r.setTextColor(R.id.wDuvarSag, p.soluk)

        // 2. Tıklama
        r.setOnClickPendingIntent(R.id.wDuvarKok, ac(ctx))

        // 3. Duvar Çizimi (30 Günlük Galeri)
        val boy = boyutDp(yon, id)
        val wPx = dp(ctx, boy.first.toFloat()).toInt()
        val hPx = dp(ctx, (boy.second - 44).coerceIn(40, 300).toFloat()).toInt()

        val bm = WidgetCizer.duvarGalerisi(d.duvar, d.mod, p, wPx, hPx)
        if (bm != null) {
            r.setImageViewBitmap(R.id.wDuvarCanvas, bm)
            r.setViewVisibility(R.id.wDuvarCanvas, View.VISIBLE)
        } else {
            r.setViewVisibility(R.id.wDuvarCanvas, View.GONE)
        }

        r.setInt(
            R.id.wDuvarKok, "setBackgroundResource",
            if (gece) R.drawable.widget_arka_gece else R.drawable.widget_arka
        )

        yon.updateAppWidget(id, r)
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

    private fun ac(ctx: Context): PendingIntent {
        val niyet = Intent(ctx, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        val bayrak = PendingIntent.FLAG_UPDATE_CURRENT or
                (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        return PendingIntent.getActivity(ctx, 42, niyet, bayrak)
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
