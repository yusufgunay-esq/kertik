// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

package com.yusufgunay.kertik

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RadialGradient
import android.graphics.Shader
import java.util.Calendar
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.floor
import kotlin.math.hypot
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * Android Widget'ları için yüksek kaliteli sanat çizim motoru.
 *
 * Web tarafındaki (index.html) FBM/gürültü, canlı Ebru tuvali, C-Kertik kalas
 * ve kum bahçesi algoritmalarını Android Canvas üzerinde icra eder.
 */
object WidgetCizer {

    /** RemoteViews'a giden bitmap Binder işlem sınırının (~1 MB) altında kalsın diye
     *  BAYT cinsinden bütçelenir — piksel sayısı değil. ARGB_8888'de piksel başına 4
     *  bayt gider; 450.000 bayt ≈ 440 KB, tek bitmap için güvenli bir pay bırakır. */
    private const val ENCOK_BAYT = 450_000L

    /* ---- Deterministik Hash & RNG (index.html ile birebir aynı) ---- */
    fun hash32(s: String): Int {
        var h = -2128831035 // 2166136261L in Int
        for (c in s) {
            h = h xor c.code
            h *= 16777619
        }
        return h
    }

    /** Web tarafındaki dayKey(ts) ile aynı biçimde "YYYY-MM-DD" üretir (yerel takvim).
     * [oncekiGun] gün öncesini ister; 0 = bugün. Widget'ın kum bahçesi tohumu bununla
     * kurulur, böylece aynı gün için widget her yenilendiğinde AYNI bahçe çıkar. */
    fun gunAnahtari(oncekiGun: Int = 0): String {
        val takvim = Calendar.getInstance()
        if (oncekiGun != 0) takvim.add(Calendar.DAY_OF_YEAR, -oncekiGun)
        val y = takvim.get(Calendar.YEAR)
        val m = takvim.get(Calendar.MONTH) + 1
        val d = takvim.get(Calendar.DAY_OF_MONTH)
        return "%04d-%02d-%02d".format(y, m, d)
    }

    class Rng(tohum: Int) {
        private var a = tohum
        fun next(): Double {
            a += 0x6D2B79F5
            var t = (a xor (a ushr 15)) * (1 or a)
            t = (t + ((t xor (t ushr 7)) * (61 or t))) xor t
            return ((t xor (t ushr 14)).toLong() and 0xFFFFFFFFL).toDouble() / 4294967296.0
        }
    }

    /* ---- Gürültü ve FBM Matematik Motoru ---- */
    private fun h2i(i: Int, j: Int, s: Int): Double {
        var n = (i * 374761393) xor (j * 668265263) xor (s * 362437)
        n = (n xor (n ushr 13)) * 1274126177
        return ((n xor (n ushr 16)).toLong() and 0xFFFFFFFFL).toDouble() / 4294967296.0
    }

    private fun vnoise(x: Double, y: Double, s: Int): Double {
        val i = floor(x).toInt()
        val j = floor(y).toInt()
        val fx = x - i
        val fy = y - j
        val u = fx * fx * (3.0 - 2.0 * fx)
        val v = fy * fy * (3.0 - 2.0 * fy)
        val a = h2i(i, j, s)
        val b = h2i(i + 1, j, s)
        val c = h2i(i, j + 1, s)
        val d = h2i(i + 1, j + 1, s)
        return (a * (1.0 - u) + b * u) * (1.0 - v) + (c * (1.0 - u) + d * u) * v
    }

    private fun fbm(x: Double, y: Double, s: Int): Double {
        return vnoise(x, y, s) * 0.60 +
                vnoise(x * 2.1, y * 2.1, s + 7) * 0.27 +
                vnoise(x * 4.3, y * 4.3, s + 19) * 0.13
    }

    private fun alfa(renk: Int, a: Float): Int {
        val op = (a.coerceIn(0f, 1f) * 255).toInt()
        return Color.argb(op, Color.red(renk), Color.green(renk), Color.blue(renk))
    }

    private fun hyp(a: Float, b: Float): Float = hypot(a.toDouble(), b.toDouble()).toFloat()

    /** Piksel sayısı değil BAYT bütçesine göre küçültme oranı. */
    private fun kucult(w: Int, h: Int): Float {
        val bayt = w.toLong() * h.toLong() * 4L
        if (bayt <= ENCOK_BAYT) return 1f
        return sqrt(ENCOK_BAYT.toDouble() / bayt.toDouble()).toFloat()
    }

    class Palet(
        val kagit: Int,
        val murekkep: Int,
        val soluk: Int,
        val cizgi: Int,
        val vurgu: Int,
        val serin: Int,
        val kopru: Int,
        val mola1: Int,
        val mola2: Int,
        val tas: Int,
        val tasIsik: Int
    )

    // ============================================================
    // 1. CANLI EBRU / AKIŞ ALANI TUVALİ (Kronometre Arka Planı)
    // ============================================================
    fun ebruTuvali(
        genislikPx: Int,
        yukseklikPx: Int,
        seed: Int,
        dakika: Int,
        isBreak: Boolean,
        p: Palet
    ): Bitmap? {
        var w = genislikPx.coerceAtLeast(32)
        var h = yukseklikPx.coerceAtLeast(32)
        val olcek = kucult(w, h)
        w = (w * olcek).toInt().coerceAtLeast(32)
        h = (h * olcek).toInt().coerceAtLeast(32)

        val bm = try {
            Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        } catch (e: OutOfMemoryError) {
            return null
        }
        val c = Canvas(bm)
        val r = Rng(seed)

        // 1. Yıkama Gradyanı
        val anaRenk = if (isBreak) p.serin else p.vurgu
        val boya = Paint(Paint.ANTI_ALIAS_FLAG)
        boya.shader = LinearGradient(
            0f, 0f, w.toFloat(), h.toFloat(),
            intArrayOf(
                alfa(anaRenk, 0.22f),
                alfa(p.kopru, 0.10f),
                alfa(anaRenk, 0.18f)
            ),
            null,
            Shader.TileMode.CLAMP
        )
        c.drawRect(0f, 0f, w.toFloat(), h.toFloat(), boya)
        boya.shader = null

        // 2. Akış Çizgileri
        val density = min(75, max(24, (dakika * 0.65f).toInt()))
        val path = Path()
        val boyaSerit = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            style = Paint.Style.STROKE
            strokeCap = Paint.Cap.ROUND
        }

        fun aci(x: Double, y: Double): Double {
            return (fbm(x / (w / 2.4), y / (w / 2.4), seed) * 2.0 - 1.0) * Math.PI * 1.85 +
                    (fbm(x / (w / 5.5), y / (w / 5.5), seed + 3) - 0.5) * 1.15
        }

        for (i in 0 until density) {
            var x = r.next() * w
            var y = r.next() * h
            val isMajor = (i % 5 == 0)
            val isFeather = (i % 3 == 1)

            path.reset()
            path.moveTo(x.toFloat(), y.toFloat())

            val len = (if (isMajor) 150.0 else 85.0) + r.next() * 50.0
            val step = 2.5
            val maxSteps = (len / step).toInt()

            for (s in 0 until maxSteps) {
                val a = aci(x, y)
                x += cos(a) * step
                y += sin(a) * step
                if (x < -15 || y < -15 || x > w + 15 || y > h + 15) break
                path.lineTo(x.toFloat(), y.toFloat())
            }

            when {
                isMajor -> {
                    boyaSerit.color = alfa(anaRenk, 0.60f)
                    boyaSerit.strokeWidth = 2.4f
                }
                isFeather -> {
                    boyaSerit.color = alfa(anaRenk, 0.35f)
                    boyaSerit.strokeWidth = 1.1f
                }
                else -> {
                    boyaSerit.color = alfa(if (isBreak) anaRenk else p.murekkep, 0.16f)
                    boyaSerit.strokeWidth = 0.85f
                }
            }
            c.drawPath(path, boyaSerit)
        }

        return bm
    }

    // ============================================================
    // 2. KUM BAHÇESİ (Pomodoro Arka Planı) — GERÇEK BAHÇE
    // ============================================================
    // index.html'deki KUMMOD/KUM bölümünün Android Canvas'a taşınmış hâli:
    // günün tohumundan gelen bahçe biçimi (ada/ust/alt/sol/sag/capraz), taşların
    // "en iyi aday" yerleşimi, tırmık izlerinin yürüyen-kareler (marching squares)
    // konturu ve taşa yakınlıkla değişen çizgi rengi. Kademeli sıklaşma (rüzgar/
    // difüzyon aşınması) widget'a taşınmadı: bu, hangi molanın ne kadar sürdüğü
    // gibi bilgi widget'ın aldığı JSON'da yok (yalnız günün TAŞ SAYISI var) — widget
    // günün bahçesini her zaman "kademe 0" bandıyla, tam kurulmuş hâliyle gösterir.
    // Aynı sebeple her taş varsayılan bir hedefle (25 dk) çiziliyor: bireysel
    // pomodoro sürelerine widget'ın erişimi yok.

    private const val KUM_BANT = 6.2f
    private const val KUM_ARA_MIN = 30f
    private const val KUM_ARA_MAX = 58f
    private const val KUM_ST = 3.2f
    private const val KUM_VARSAYILAN_HEDEF_DK = 25f

    private const val B_ADA = 0
    private const val B_UST = 1
    private const val B_ALT = 2
    private const val B_SOL = 3
    private const val B_SAG = 4
    private const val B_CAPRAZ = 5

    private class KumBicimi(
        val tur: Int, val eg: Double, val aci: Double, val gurultu: Double, val araKat: Double
    )

    private class KumTas(
        val x: Float, val y: Float, val r: Float, val a: Float, val e: Float, val tohum: Int
    )

    private class KumAlan(val gw: Int, val gh: Int, val st: Float, val g: FloatArray, val maxF: Float)

    private fun kumBicimUret(tohum: Int): KumBicimi {
        val r = Rng(tohum + 17)
        val z = r.next()
        val tur = when {
            z < .12 -> B_ADA
            z < .36 -> B_UST
            z < .58 -> B_ALT
            z < .74 -> B_SOL
            z < .88 -> B_SAG
            else -> B_CAPRAZ
        }
        return KumBicimi(
            tur = tur,
            eg = (r.next() - .5) * .52,
            aci = r.next() * Math.PI * 2,
            gurultu = .70 + r.next() * .55,
            araKat = .88 + r.next() * .30
        )
    }

    private fun kumCepheMesafe(x: Double, y: Double, w: Double, h: Double, b: KumBicimi): Double {
        return when (b.tur) {
            B_ADA -> 1e7
            B_UST -> (y - h * .045) + b.eg * (x - w * .5)
            B_ALT -> (h * .955 - y) + b.eg * (x - w * .5)
            B_SOL -> (x - w * .055) + b.eg * (y - h * .5) * .6
            B_SAG -> (w * .945 - x) + b.eg * (y - h * .5) * .6
            else -> {
                val ca = cos(b.aci); val sa = sin(b.aci)
                ((x - w * .5) * ca + (y - h * .5) * sa) + max(w, h) * .58
            }
        }
    }

    private fun kumSmin(a: Double, b: Double, k: Double): Double {
        val h = (0.5 + 0.5 * (b - a) / k).coerceIn(0.0, 1.0)
        return b * (1 - h) + a * h - k * h * (1 - h)
    }

    /** Taşların "en iyi aday" (Mitchell) yerleşimi. Bireysel pomodoro hedef
     * süreleri widget'a ulaşmadığı için hepsi aynı varsayılan boyuttan türer;
     * yalnız dönüş/basıklık ve dış hat gürültüsü taştan taşa değişir. */
    private fun kumTasUret(tohum: Int, n: Int, w: Float, h: Float): List<KumTas> {
        if (n <= 0) return emptyList()
        val r = Rng(tohum + 31)
        val olcek = if (n <= 5) 1f else Math.pow(5.0 / n, 0.26).toFloat()
        val rad = max(
            w * .022f,
            w * (.030f + sqrt(KUM_VARSAYILAN_HEDEF_DK / 60f) * .038f) * olcek
        )
        val out = ArrayList<KumTas>(n)
        for (i in 0 until n) {
            var bx = w * .5f
            var by = h * .4f
            var iyi = -1e9f
            for (d in 0 until 44) {
                val x = w * (.11f + r.next().toFloat() * .78f)
                val y = h * (.085f + r.next().toFloat() * .60f)
                var m = min(
                    min(x - rad * 1.4f, w - x - rad * 1.4f),
                    min(y - rad * 1.4f, h * .70f - y - rad * 1.4f)
                )
                m = min(m, hyp(x - w * .5f, (y - h * .42f) * .74f) - rad - w * .30f)
                for (t in out) m = min(m, hyp(t.x - x, t.y - y) - (t.r + rad) - w * .10f)
                if (m > iyi) { iyi = m; bx = x; by = y }
                if (iyi > w * .055f) break
            }
            val a = r.next().toFloat() * (Math.PI * 2).toFloat()
            val e = .74f + r.next().toFloat() * .40f
            val tohumTas = (r.next() * 1e6).toInt()
            out.add(KumTas(bx, by, rad, a, e, tohumTas))
        }
        return out
    }

    private fun kumAlanKur(w: Float, h: Float, tohum: Int, b: KumBicimi, taslar: List<KumTas>, ara: Float): KumAlan {
        val st = KUM_ST
        val yum = (ara * 1.25).coerceAtLeast(1.0)
        val gw = (w / st).toInt() + 2
        val gh = (h / st).toInt() + 2
        val g = FloatArray(gw * gh)
        var mx = 1f
        for (j in 0 until gh) {
            val y = (j * st).toDouble()
            for (i in 0 until gw) {
                val x = (i * st).toDouble()
                var f = kumCepheMesafe(x, y, w.toDouble(), h.toDouble(), b) +
                        (fbm(x / (w * .80), y / (w * 1.6), tohum + 3) - .5) * ara * b.gurultu
                for (t in taslar) {
                    val dx = (x - t.x) * cos(t.a.toDouble()) + (y - t.y) * sin(t.a.toDouble())
                    val dy = (-(x - t.x) * sin(t.a.toDouble()) + (y - t.y) * cos(t.a.toDouble())) / t.e
                    f = kumSmin(f, hypot(dx, dy) - t.r, yum)
                }
                val ff = f.toFloat()
                g[j * gw + i] = ff
                if (ff > mx) mx = ff
            }
        }
        return KumAlan(gw, gh, st, g, mx)
    }

    /** Yürüyen kareler: [c] eşiğindeki seviye eğrisini parça parça çıkarır.
     * Her segment [x1,y1,x2,y2] biçiminde döner. */
    private fun kumKontur(alan: KumAlan, c: Float): List<FloatArray> {
        val g = alan.g; val gw = alan.gw; val gh = alan.gh; val st = alan.st
        val seg = ArrayList<FloatArray>()
        fun ar(a: Float, bb: Float): Float = if (abs(bb - a) < 1e-9f) .5f else (c - a) / (bb - a)
        for (j in 0 until gh - 1) {
            for (i in 0 until gw - 1) {
                val a = g[j * gw + i]
                val b = g[j * gw + i + 1]
                val d = g[(j + 1) * gw + i + 1]
                val e = g[(j + 1) * gw + i]
                var k = 0
                if (a < c) k = k or 1
                if (b < c) k = k or 2
                if (d < c) k = k or 4
                if (e < c) k = k or 8
                if (k == 0 || k == 15) continue
                val x = i * st; val y = j * st
                val ux = x + st * ar(a, b); val uy = y
                val rx = x + st; val ry = y + st * ar(b, d)
                val dx = x + st * ar(e, d); val dy = y + st
                val lx = x; val ly = y + st * ar(a, e)
                when (k) {
                    1, 14 -> seg.add(floatArrayOf(lx, ly, ux, uy))
                    2, 13 -> seg.add(floatArrayOf(ux, uy, rx, ry))
                    3, 12 -> seg.add(floatArrayOf(lx, ly, rx, ry))
                    4, 11 -> seg.add(floatArrayOf(rx, ry, dx, dy))
                    6, 9 -> seg.add(floatArrayOf(ux, uy, dx, dy))
                    7, 8 -> seg.add(floatArrayOf(lx, ly, dx, dy))
                    5 -> {
                        seg.add(floatArrayOf(lx, ly, ux, uy))
                        seg.add(floatArrayOf(rx, ry, dx, dy))
                    }
                    10 -> {
                        seg.add(floatArrayOf(ux, uy, rx, ry))
                        seg.add(floatArrayOf(lx, ly, dx, dy))
                    }
                }
            }
        }
        return seg
    }

    /** Taşın dibinde sıcak (vurgu), açık kumda serin — ton kayması taşa olan
     * uzaklıktan geliyor, "tek renk" değil. */
    private fun kumCizgiRengi(vurgu: Int, serin: Int, q: Float): Int {
        val t = .10f + .90f * Math.pow(q.coerceIn(0f, 1f).toDouble(), .70).toFloat()
        val hsvA = FloatArray(3); Color.colorToHSV(vurgu, hsvA)
        val hsvB = FloatArray(3); Color.colorToHSV(serin, hsvB)
        var ha = hsvA[0]; var hb = hsvB[0]
        if (abs(hb - ha) > 180f) { if (hb > ha) hb -= 360f else ha -= 360f }
        val h = ((ha + (hb - ha) * t) % 360f + 360f) % 360f
        val s = (hsvA[1] + (hsvB[1] - hsvA[1]) * t).coerceIn(0f, 1f)
        val v = (hsvA[2] + (hsvB[2] - hsvA[2]) * t).coerceIn(0f, 1f)
        return Color.HSVToColor(floatArrayOf(h, s, v))
    }

    private fun kumTasYolu(t: KumTas): Path {
        val path = Path()
        val n = 26
        for (i in 0..n) {
            val ang = (i.toDouble() / n) * Math.PI * 2
            val rr = t.r * (.85f + fbm(cos(ang) * 2.1 + 3, sin(ang) * 2.1 + 7, t.tohum).toFloat() * .33f)
            val px = cos(ang).toFloat() * rr
            val py = sin(ang).toFloat() * rr
            if (i == 0) path.moveTo(px, py) else path.lineTo(px, py)
        }
        path.close()
        return path
    }

    /** Taş MAT: gradyan/parlaklık yok. Kütle duygusu gölgeden geliyor. */
    private fun kumTasCiz(c: Canvas, t: KumTas, renk: Int, alfaCarpan: Float) {
        val boya = Paint(Paint.ANTI_ALIAS_FLAG)
        c.save()
        c.translate(t.x, t.y)
        c.rotate(Math.toDegrees(t.a.toDouble()).toFloat())
        c.scale(1f, t.e)
        boya.style = Paint.Style.FILL
        boya.color = alfa(renk, .90f * alfaCarpan)
        c.drawPath(kumTasYolu(t), boya)
        c.restore()
    }

    private fun kumTasGolgeCiz(c: Canvas, t: KumTas, taban: Float) {
        val boya = Paint(Paint.ANTI_ALIAS_FLAG)
        c.save()
        c.translate(t.x, t.y)
        c.rotate(Math.toDegrees(t.a.toDouble()).toFloat())
        val rx = max(1f, t.r * 1.02f * 1.18f)
        val ry = max(1f, t.r * t.e * 1.18f)
        val cx = t.r * .17f; val cy = t.r * .26f
        boya.shader = RadialGradient(
            cx, cy, rx,
            intArrayOf(alfa(Color.BLACK, .42f * taban), alfa(Color.BLACK, .16f * taban), alfa(Color.BLACK, 0f)),
            floatArrayOf(0f, .62f, 1f),
            Shader.TileMode.CLAMP
        )
        c.drawOval(cx - rx, cy - ry, cx + rx, cy + ry, boya)
        c.restore()
    }

    private fun kumYolCiz(c: Canvas, boya: Paint, seg: List<FloatArray>, amp: Float, tohum: Int, ofs: Float) {
        val path = Path()
        for (s in seg) {
            val j1 = (vnoise(s[0] * .09, s[1] * .09, tohum) - .5).toFloat() * amp
            val j2 = (vnoise(s[2] * .09, s[3] * .09, tohum) - .5).toFloat() * amp
            path.moveTo(s[0] + j1, s[1] + j1 * .6f + ofs)
            path.lineTo(s[2] + j2, s[3] + j2 * .6f + ofs)
        }
        c.drawPath(path, boya)
    }

    /**
     * Günün kum bahçesi: bahçe biçimi (ust/alt/sol/sag/capraz/ada) [gun]'un
     * tohumundan doğar; [tasSayisi] kadar taş "en iyi aday" yöntemiyle yerleşir.
     * Aynı [gun] + aynı [tasSayisi] için widget her yenilendiğinde AYNI bahçe çıkar.
     */
    fun kumBahcesiTuvali(
        genislikPx: Int,
        yukseklikPx: Int,
        gun: String,
        tasSayisi: Int,
        gece: Boolean,
        p: Palet
    ): Bitmap? {
        var w = genislikPx.coerceAtLeast(32)
        var h = yukseklikPx.coerceAtLeast(32)
        val olcek = kucult(w, h)
        w = (w * olcek).toInt().coerceAtLeast(32)
        h = (h * olcek).toInt().coerceAtLeast(32)

        val bm = try {
            Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        } catch (e: OutOfMemoryError) {
            return null
        }
        val c = Canvas(bm)
        val wf = w.toFloat(); val hf = h.toFloat()

        val tohum = hash32("kumbahce|$gun")
        val bicim = kumBicimUret(tohum)
        val taslar = kumTasUret(tohum, tasSayisi, wf, hf)

        // İki geçişli aralık kalibrasyonu: önce bahçenin derinliğini ölç, sonra
        // aralığı o derinliğe göre kur (kaynaktaki kumKur ile aynı mantık).
        var ara = (46f * (hf / 780f)).coerceAtLeast(4f)
        var alan = kumAlanKur(wf, hf, tohum, bicim, taslar, ara)
        ara = ((alan.maxF / KUM_BANT).coerceIn(KUM_ARA_MIN, KUM_ARA_MAX) * bicim.araKat.toFloat() * (hf / 780f))
            .coerceAtLeast(4f)
        alan = kumAlanKur(wf, hf, tohum, bicim, taslar, ara)

        val boya = Paint(Paint.ANTI_ALIAS_FLAG)

        // 1. Kum zemini
        boya.style = Paint.Style.FILL
        boya.color = p.kagit
        c.drawRect(0f, 0f, wf, hf, boya)

        // 2. Kumun kendi alacası — doku değil, ölü düzlüğü kıran ince bir titreşim
        val rz = Rng(tohum + 91)
        val benekSayisi = min(700, ((w.toLong() * h.toLong()) / 820L).toInt())
        boya.color = alfa(p.cizgi, if (gece) .05f else .042f)
        for (i in 0 until benekSayisi) {
            val bx = rz.next().toFloat() * wf
            val by = rz.next().toFloat() * hf
            c.drawRect(bx, by, bx + 1.15f, by + 1.15f, boya)
        }

        // 3. Kraterler — her taşın kumda bıraktığı halka
        if (taslar.isNotEmpty()) {
            boya.style = Paint.Style.STROKE
            boya.strokeWidth = .9f
            boya.color = alfa(p.cizgi, .17f)
            val kraterYolu = Path()
            for (t in taslar) {
                kraterYolu.reset()
                for (i in 0..34) {
                    val ang = (i / 34.0) * Math.PI * 2
                    val rr = t.r * (1.42f + fbm(cos(ang) * 2.0, sin(ang) * 2.0, t.tohum).toFloat() * .28f)
                    val px = t.x + cos(ang).toFloat() * rr
                    val py = t.y + sin(ang).toFloat() * rr * t.e
                    if (i == 0) kraterYolu.moveTo(px, py) else kraterYolu.lineTo(px, py)
                }
                c.drawPath(kraterYolu, boya)
            }
        }

        // 4. Taşlar tırmıktan ÖNCE (widget'ta canlı kadran maskesi yok, bu yüzden
        // uygulamanın "resim/anlık görüntü" sırasıyla aynı: taş önce, iz sonra).
        val tabanGolge = if (gece) .30f else .46f
        for (t in taslar) {
            kumTasGolgeCiz(c, t, tabanGolge)
            kumTasCiz(c, t, p.tas, 1f)
        }

        // 5. Tırmık izleri — yalnız kademe 0 (widget'ın verisinde rüzgar/difüzyon
        // aşınmasını hesaplayacak mola geçmişi yok; bahçe hep "tam kurulmuş" gösterilir)
        boya.style = Paint.Style.STROKE
        boya.strokeCap = Paint.Cap.ROUND
        boya.strokeJoin = Paint.Join.ROUND
        val maxF = alan.maxF
        val opBaz = if (gece) .58f else .62f
        var m = 0
        var cizilen = 0
        while (m * ara <= maxF + ara && cizilen < 160) {
            val cVal = m * ara
            val seg = kumKontur(alan, cVal)
            if (seg.isNotEmpty()) {
                val q = min(1f, cVal / max(1f, maxF * .62f))
                val cizgiTohum = tohum + m
                // kumun kabarttığı kenar
                boya.color = alfa(p.cizgi, opBaz * .50f)
                boya.strokeWidth = 2.30f
                kumYolCiz(c, boya, seg, .95f, cizgiTohum, 1.05f)
                // izin kendisi
                boya.color = alfa(kumCizgiRengi(p.vurgu, p.serin, q), opBaz)
                boya.strokeWidth = 1.15f
                kumYolCiz(c, boya, seg, .95f, cizgiTohum, 0f)
            }
            m++
            cizilen++
        }

        return bm
    }

    // ============================================================
    // 3. C · KERTİK: ORİJİNAL KALAS VE V-KESİT ÇİZİCİ
    // ============================================================
    fun cizCKertik(
        v: WidgetDurum.Cubuk,
        p: Palet,
        genislikPx: Int,
        yukseklikPx: Int,
        solma: Float = 0f
    ): Bitmap? {
        val dk = v.dk.coerceAtLeast(1)
        val kolon = ((dk + 59) / 60).coerceAtLeast(1)
        val satir = if (kolon > 1) 60 else dk

        var w = genislikPx.coerceAtLeast(16)
        var h = yukseklikPx.coerceAtLeast(24)
        val olcek = kucult(w, h)
        w = (w * olcek).toInt().coerceAtLeast(16)
        h = (h * olcek).toInt().coerceAtLeast(24)

        val bm = try {
            Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        } catch (e: OutOfMemoryError) {
            return null
        }
        val c = Canvas(bm)
        val boya = Paint(Paint.ANTI_ALIAS_FLAG)
        val kalma = 1f - solma * 0.70f

        val sw = (w.toFloat() / kolon) * 0.85f
        val kalasW = sw * 0.65f
        val gap = (w.toFloat() / kolon) * 0.15f
        val top = 4f
        val rp = (h.toFloat() - top * 2f) / max(1, satir - 1)

        val r = Rng(hash32(v.id.ifEmpty { "c-kertik" }))
        val j = DoubleArray(dk * 5 + 40) { r.next() }

        fun colX(k: Int) = k * (sw + gap) + 2f
        fun yOf(m: Int) = top + (m % 60) * rp

        // 1. KALAS GÖVDESİ & DAMARLAR
        for (k in 0 until kolon) {
            val son = min(60, dk - k * 60)
            val y0 = top - 2f
            val y1 = yOf(son - 1) + 2f
            val x = colX(k)

            val kalasPath = Path()
            val rK = Rng(hash32("${v.id}k$k"))
            kalasPath.moveTo(x, y0)

            val n = max(6, ((y1 - y0) / 8f).toInt())
            val sagNoktalar = ArrayList<Pair<Float, Float>>()
            for (i in 0..n) {
                val t = i.toFloat() / n
                val yy = y0 + (y1 - y0) * t
                val solX = x + (rK.next().toFloat() - 0.5f) * 0.8f
                kalasPath.lineTo(solX, yy)
                sagNoktalar.add(Pair(x + kalasW + (rK.next().toFloat() - 0.5f) * 0.9f, yy))
            }
            for (i in sagNoktalar.size - 1 downTo 0) {
                kalasPath.lineTo(sagNoktalar[i].first, sagNoktalar[i].second)
            }
            kalasPath.close()

            // Ahşap gövde dolgusu
            boya.style = Paint.Style.FILL
            boya.color = alfa(p.kopru, 0.35f * kalma)
            c.drawPath(kalasPath, boya)

            // Ahşap damarları
            boya.style = Paint.Style.STROKE
            boya.strokeWidth = 0.7f
            boya.color = alfa(p.kopru, 0.42f * kalma)
            val rD = Rng(hash32("${v.id}damar$k"))
            for (dnr in 0..1) {
                val dx = kalasW * (0.25f + rD.next().toFloat() * 0.50f)
                val damarPath = Path()
                damarPath.moveTo(x + dx, y0)
                for (step in 1..8) {
                    val t = step / 8f
                    damarPath.lineTo(
                        x + dx + (rD.next().toFloat() - 0.5f) * kalasW * 0.14f,
                        y0 + (y1 - y0) * t
                    )
                }
                c.drawPath(damarPath, boya)
            }

            // Kenar sınırları (sol ışık, sağ gölge)
            boya.strokeWidth = 0.9f
            boya.color = alfa(p.murekkep, 0.40f * kalma)
            c.drawLine(x, y0, x, y1, boya)
            boya.strokeWidth = 0.7f
            boya.color = alfa(p.murekkep, 0.22f * kalma)
            c.drawLine(x + kalasW, y0, x + kalasW, y1, boya)
        }

        // 2. MOLA BANDI
        for (b in v.molalar) {
            var a = b[0]
            while (a < min(b[1], dk)) {
                val k = a / 60
                val son = min(b[1], min(dk, (k + 1) * 60))
                if (son > a) {
                    val x = colX(k)
                    val mY0 = yOf(a) - rp * 0.45f
                    val mY1 = yOf(son - 1) + rp * 0.45f

                    // Mola gölgesi
                    boya.style = Paint.Style.FILL
                    boya.color = alfa(p.mola1, 0.18f * kalma)
                    c.drawRect(x + 0.5f, mY0, x + kalasW - 0.5f, mY1, boya)

                    // Sol kenar mola izi
                    boya.style = Paint.Style.STROKE
                    boya.strokeWidth = max(1.5f, sw * 0.08f)
                    boya.strokeCap = Paint.Cap.ROUND
                    boya.color = alfa(p.mola2, 0.80f * kalma)
                    c.drawLine(x - 3f, mY0, x - 3f, mY1, boya)

                    // Başlangıç ve bitiş sınır çizgileri
                    boya.strokeWidth = 0.8f
                    boya.color = alfa(p.mola2, 0.55f * kalma)
                    c.drawLine(x - 4f, mY0, x + kalasW * 0.5f, mY0, boya)
                    c.drawLine(x - 4f, mY1, x + kalasW * 0.5f, mY1, boya)
                }
                a = son
            }
        }

        // 3. V-KESİT ÇENTİKLER
        val pathV = Path()
        for (m in 0 until dk) {
            if (v.molalar.any { m >= it[0] && m < it[1] }) continue
            val k = m / 60
            val mm = m % 60
            val r1 = j[m * 5].toFloat()
            val r2 = j[m * 5 + 1].toFloat()
            val r3 = j[m * 5 + 2].toFloat()
            val r4 = j[m * 5 + 3].toFloat()

            val derin = kalasW * (when {
                mm == 0 -> 0.94f
                mm % 15 == 0 -> 0.80f
                mm % 5 == 0 -> 0.66f
                else -> 0.48f
            }) * (1f + (r1 - 0.5f) * 0.25f)

            val x = colX(k)
            val y = yOf(m) + (r2 - 0.5f) * rp * 0.30f
            val kal = rp * (when {
                mm == 0 -> 0.62f
                mm % 5 == 0 -> 0.50f
                else -> 0.38f
            }) * (1f + (r3 - 0.5f) * 0.30f)
            val egim = (r4 - 0.5f) * rp * 0.45f

            // V-kesit gölge yüzü
            pathV.reset()
            pathV.moveTo(x, y + kal * 0.5f)
            pathV.lineTo(x + derin, y + egim + kal * 0.16f)
            pathV.lineTo(x + derin, y + egim - kal * 0.16f)
            pathV.lineTo(x, y - kal * 0.5f)
            pathV.close()

            boya.style = Paint.Style.FILL
            val tonRenk = if (mm == 0) p.murekkep else if (mm % 5 == 0) p.soluk else p.cizgi
            val op = (if (mm == 0) 0.98f else 0.80f + r3 * 0.2f) * kalma
            boya.color = alfa(tonRenk, op)
            c.drawPath(pathV, boya)

            // V-kesit üst ışık yüzü
            boya.style = Paint.Style.STROKE
            boya.strokeWidth = kal * 0.30f
            boya.color = alfa(p.kagit, 0.50f * kalma)
            c.drawLine(x, y - kal * 0.5f, x + derin * 0.92f, y + egim - kal * 0.14f, boya)

            // Dip gölgesi
            boya.strokeWidth = kal * 0.24f
            boya.color = alfa(p.murekkep, 0.25f * kalma)
            c.drawLine(x + 0.4f, y + kal * 0.52f, x + derin * 0.85f, y + egim + kal * 0.20f, boya)
        }

        return bm
    }

    // ============================================================
    // 4. DUVAR: 30 GÜNLÜK ARŞİV — TEK MOD, TEK ÖLÇEK
    // ============================================================
    /**
     * Son 30 günü çizer.
     *
     * İki ayrı duvar kararı (19 Ağustos 2026) burada da geçerli: dar bir
     * widget şeridinde iki ölçek yan yana gelemez. Bu yüzden duvar TEK moda
     * aittir; hangi mod olduğunu web tarafı seçip yollar ([mod]).
     * Kronometre günü süreyle (dk), pomodoro günü sayıyla (taş) ölçülür.
     *
     * Pomodoro günündeki taşlar artık her gün AYNI olmayan, o günün kendi
     * tohumundan (gunAnahtari) türeyen küçük, düzensiz kümeler: dikey bir
     * istif (cairn) değil, kumun üstündeki gerçek taş kümesinin minyatürü.
     */
    fun duvarGalerisi(
        gunler: List<WidgetDurum.Gun>,
        mod: String,
        p: Palet,
        genislikPx: Int,
        yukseklikPx: Int
    ): Bitmap? {
        var w = genislikPx.coerceAtLeast(60)
        var h = yukseklikPx.coerceAtLeast(40)
        val olcek = kucult(w, h)
        w = (w * olcek).toInt().coerceAtLeast(60)
        h = (h * olcek).toInt().coerceAtLeast(40)

        val bm = try {
            Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888)
        } catch (e: OutOfMemoryError) {
            return null
        }
        val c = Canvas(bm)
        val boya = Paint(Paint.ANTI_ALIAS_FLAG)

        val gunSayisi = 30
        val sutunW = w.toFloat() / gunSayisi
        val gunHaritasi = gunler.associateBy { it.oncekiGun }
        val tasYolu = Path()

        for (g in 0 until gunSayisi) {
            val oncekiGun = gunSayisi - 1 - g
            val solma = (oncekiGun.toFloat() / (gunSayisi - 1).toFloat()) * 0.70f
            val kalma = 1f - solma
            val cx = g * sutunW + sutunW * 0.5f

            val veri = gunHaritasi[oncekiGun]
            val pomodoroMu = (mod == "pomodoro")
            val dk = veri?.dk ?: 0
            val tas = veri?.tas ?: 0
            val doluMu = if (pomodoroMu) tas > 0 else dk > 0

            if (!doluMu) {
                // Boş gün taban çizgisi
                boya.style = Paint.Style.STROKE
                boya.strokeWidth = 1.2f
                boya.color = alfa(p.cizgi, 0.40f * kalma)
                c.drawLine(cx - sutunW * 0.28f, h - 4f, cx + sutunW * 0.28f, h - 4f, boya)
                continue
            }

            // Organik karekök ölçeklendirmesi: Kısa seanslar görünür kalır, uzun seanslar yükselir
            val oran = if (pomodoroMu) sqrt(tas.toFloat() / 6f).coerceIn(0.26f, 0.95f)
            else sqrt(dk.toFloat() / 150f).coerceIn(0.26f, 0.95f)
            val boyPx = oran * (h - 10f)
            val yTop = (h - 4f) - boyPx

            if (pomodoroMu) {
                // Pomodoro Günü: o günün taşları — dayKey'den türeyen küçük, düzensiz
                // bir küme (uydurma cairn istifi değil), sayı veriden geliyor.
                val gun = gunAnahtari(oncekiGun)
                val rTas = Rng(hash32("duvartas|$gun"))
                val tasCount = min(6, tas)
                val rTop = min(sutunW * 0.30f, 5.5f)
                val adim = (boyPx / max(1, tasCount)).coerceAtLeast(rTop * 1.1f)
                for (t in 0 until tasCount) {
                    val rr = rTop * (1f - t * 0.10f)
                    val jitX = (rTas.next().toFloat() - 0.5f) * sutunW * 0.30f
                    val jitY = (rTas.next().toFloat() - 0.5f) * adim * 0.20f
                    val tcx = cx + jitX
                    val tcy = (h - 5f) - t * adim + jitY
                    val tohumTas = hash32("duvartas|$gun|$t")

                    tasYolu.reset()
                    val nPts = 10
                    for (i in 0..nPts) {
                        val ang = (i.toDouble() / nPts) * Math.PI * 2
                        val rw = rr * (.82f + fbm(cos(ang) * 2.3, sin(ang) * 2.3, tohumTas).toFloat() * .30f)
                        val px = tcx + cos(ang).toFloat() * rw
                        val py = tcy + sin(ang).toFloat() * rw * 0.82f
                        if (i == 0) tasYolu.moveTo(px, py) else tasYolu.lineTo(px, py)
                    }
                    tasYolu.close()

                    boya.style = Paint.Style.FILL
                    boya.color = alfa(p.tas, 0.90f * kalma)
                    c.drawPath(tasYolu, boya)

                    boya.color = alfa(p.tasIsik, 0.50f * kalma)
                    c.drawCircle(tcx - rr * 0.30f, tcy - rr * 0.28f, rr * 0.28f, boya)
                }
            } else {
                // Kronometre Günü: C · Kertik Kalası ve V-Kesitler
                val kalasW = max(5.0f, sutunW * 0.60f)
                val x0 = cx - kalasW / 2f

                // Kalas gövdesi
                boya.style = Paint.Style.FILL
                boya.color = alfa(p.kopru, 0.34f * kalma)
                c.drawRect(x0, yTop, x0 + kalasW, h - 4f, boya)

                // Kenarlar
                boya.style = Paint.Style.STROKE
                boya.strokeWidth = 0.8f
                boya.color = alfa(p.murekkep, 0.40f * kalma)
                c.drawLine(x0, yTop, x0, h - 4f, boya)
                boya.strokeWidth = 0.6f
                boya.color = alfa(p.murekkep, 0.22f * kalma)
                c.drawLine(x0 + kalasW, yTop, x0 + kalasW, h - 4f, boya)

                // V-Kesitler
                val centikSayisi = min(18, max(2, (boyPx / 4.5f).toInt()))
                for (cnt in 0 until centikSayisi) {
                    val cy = yTop + (boyPx / centikSayisi) * cnt
                    val isSaat = (cnt % 5 == 0)
                    val derin = kalasW * (if (isSaat) 0.94f else 0.68f)

                    boya.strokeWidth = if (isSaat) 1.4f else 0.9f
                    boya.color = alfa(if (isSaat) p.murekkep else p.soluk, 0.92f * kalma)
                    c.drawLine(x0, cy, x0 + derin, cy + (if (isSaat) 0.8f else 0.4f), boya)

                    boya.strokeWidth = 0.6f
                    boya.color = alfa(p.kagit, 0.48f * kalma)
                    c.drawLine(x0, cy - (if (isSaat) 0.6f else 0.4f), x0 + derin * 0.9f, cy, boya)
                }
            }
        }

        return bm
    }
}
