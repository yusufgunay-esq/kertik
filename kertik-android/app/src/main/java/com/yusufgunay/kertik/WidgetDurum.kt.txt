// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

package com.yusufgunay.kertik

import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import org.json.JSONArray
import org.json.JSONObject

/**
 * Widget'ın gördüğü durum.
 *
 * WebView'deki verinin tek yönlü hafif bir JSON aynasıdır.
 */
data class WidgetDurum(
    val durum: String = BOS,            // "bos" | "calisiyor" | "molada"
    val temelMs: Long = 0L,             // kronometrenin dayandığı an (duvar saati)
    val geriSayim: Boolean = false,     // pomodoro hedefi dolmadıysa geri sayar
    val netMs: Long = 0L,               // seansın o anki net çalışması
    val not: String = "",
    val bugunNetMs: Long = 0L,
    val baslangic: String = "",         // "19:37"
    val mod: String = "stopwatch",      // "stopwatch" | "pomodoro"
    val hedefDk: Int = 0,
    val cubuk: Cubuk? = null,
    val duvar: List<Gun> = emptyList(),
    val guncellendi: Long = 0L
) {
    /** Bir seansın çubuğu veya taş verisi. */
    data class Cubuk(
        val id: String,
        val dk: Int,
        val molalar: List<IntArray>,
        val sayilmayan: Int
    )

    /** Duvardaki bir gün. [oncekiGun] 0 = bugün.
     *
     * Duvar tek moda aittir (web tarafı yürürlükteki modun günlerini yollar).
     * Kronometre gününün ölçüsü [dk], pomodoro gününün ölçüsü [tas] sayısıdır;
     * ikisi aynı günde dolu olmaz. */
    data class Gun(
        val oncekiGun: Int,
        val dk: Int,
        val tas: Int,
        val molalar: List<IntArray>
    )

    val seansVar: Boolean get() = durum != BOS

    companion object {
        const val BOS = "bos"
        const val CALISIYOR = "calisiyor"
        const val MOLADA = "molada"

        private const val DOSYA = "kertik_widget"
        private const val ANAHTAR = "durum"

        fun oku(ctx: Context): WidgetDurum {
            val ham = ctx.getSharedPreferences(DOSYA, Context.MODE_PRIVATE)
                .getString(ANAHTAR, null) ?: return WidgetDurum()
            return coz(ham)
        }

        /** Web tarafından gelen JSON'u sakla. Bozuksa eskisi olduğu gibi kalır. */
        fun yaz(ctx: Context, ham: String): Boolean {
            return try {
                coz(ham)                       // önce ayrıştırılabildiğini doğrula
                ctx.getSharedPreferences(DOSYA, Context.MODE_PRIVATE)
                    .edit().putString(ANAHTAR, ham).apply()
                true
            } catch (e: Exception) {
                false
            }
        }

        private fun coz(ham: String): WidgetDurum {
            val o = JSONObject(ham)
            return WidgetDurum(
                durum = o.optString("durum", BOS),
                temelMs = o.optLong("temel", 0L),
                geriSayim = o.optBoolean("geri", false),
                netMs = o.optLong("net", 0L),
                not = o.optString("not", ""),
                bugunNetMs = o.optLong("bugunNet", 0L),
                baslangic = o.optString("bas", ""),
                mod = o.optString("mod", "stopwatch"),
                hedefDk = o.optInt("hedef", 0),
                cubuk = o.optJSONObject("cubuk")?.let { c ->
                    Cubuk(
                        id = c.optString("id", "x"),
                        dk = c.optInt("dk", 0),
                        molalar = araliklar(c.optJSONArray("m")),
                        sayilmayan = c.optInt("s", 0)
                    )
                },
                duvar = o.optJSONArray("duvar")?.let { d ->
                    (0 until d.length()).mapNotNull { i ->
                        val g = d.optJSONObject(i) ?: return@mapNotNull null
                        Gun(
                            oncekiGun = g.optInt("g", i),
                            dk = g.optInt("dk", 0),
                            tas = g.optInt("n", 0),
                            molalar = araliklar(g.optJSONArray("m"))
                        )
                    }
                } ?: emptyList(),
                guncellendi = o.optLong("t", 0L)
            )
        }

        private fun araliklar(a: JSONArray?): List<IntArray> {
            if (a == null) return emptyList()
            val out = ArrayList<IntArray>(a.length())
            for (i in 0 until a.length()) {
                val p = a.optJSONArray(i) ?: continue
                if (p.length() < 2) continue
                out.add(intArrayOf(p.optInt(0), p.optInt(1)))
            }
            return out
        }

        /**
         * Hem KontrolWidget hem DuvarWidget için güncelleme yayını gönderir.
         */
        fun yenile(ctx: Context) {
            val yon = AppWidgetManager.getInstance(ctx) ?: return
            for (sinif in listOf(KontrolWidget::class.java, DuvarWidget::class.java)) {
                val idler = try {
                    yon.getAppWidgetIds(ComponentName(ctx, sinif))
                } catch (e: Exception) {
                    continue
                }
                if (idler == null || idler.isEmpty()) continue
                val niyet = Intent(ctx, sinif).apply {
                    action = AppWidgetManager.ACTION_APPWIDGET_UPDATE
                    putExtra(AppWidgetManager.EXTRA_APPWIDGET_IDS, idler)
                }
                ctx.sendBroadcast(niyet)
            }
        }
    }
}
