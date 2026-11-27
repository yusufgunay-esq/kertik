// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

package com.yusufgunay.kertik

import android.Manifest
import android.app.AlarmManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import org.json.JSONObject

/**
 * Mola haberi (41-dehb-dostu.md).
 *
 * Uzayan mola Kertik'in çizdiğini aşındırır; ama bunu yalnız ekrana bakan görür.
 * Molada telefonu alıp başka bir uygulamaya geçen kişi için mola sessizce uzar.
 * Zamanı hissetmekte zorlanan biri (DEHB'nin en bilinen yüzü) döndüğünde her şeyi
 * silinmiş bulur. Bu nesne o anı ekranın dışına taşır: mola başlarken sayfa en çok
 * iki an verir, Android o anlarda tek bir titreşimli haber gösterir.
 *
 * Zaman yine sayfanın: burada süre sayılmaz, yalnız sayfanın verdiği an kurulur.
 * Mola bitince ya da seans kapanınca sayfa [iptal] çağırır, kalan her şey geri alınır.
 *
 * İzin istemez. Kesin alarm hakkı varsa (Android 12 öncesi ya da kullanıcı vermişse)
 * dakikasında gelir; yoksa Android'in izin verdiği en dar pencereyle kurulur ve
 * birkaç dakika gecikebilir. Erken gelmez; metin süreyi saymadığı için geç gelse de
 * yanlış bir şey söylemez, süreyi bildirimin kendi kronometresi gösterir.
 *
 * Uygulama öndeyken haber gösterilmez: o durumda sayfa aynı anı kendi ekranında
 * karşılar (bkz. index.html `molaHaberiDenetle`). Aynı an iki kez titremesin diye.
 */
object MolaHaberi {
    private const val KANAL = "kertik_mola_haberi_v1"
    /** Rahatsız etmeyin modunu delen kanal; yalnız politika yetkisi varken kurulur. */
    private const val KANAL_DND = "kertik_mola_haberi_v1_dnd"
    private const val BILDIRIM_ID = 2
    private const val EN_COK = 2
    private const val ISTEK_TABAN = 700
    private const val ISTEK_DEVAM = 720
    private const val ISTEK_AC = 721
    /** Kesin alarm hakkı yoksa istenen pencere. Android 12+ bunu uzatabilir. */
    private const val PENCERE_MS = 60_000L
    /** Cepte fark edilen ama alarm gibi bağırmayan çift dokunuş. */
    private val DESEN = longArrayOf(0, 22, 90, 34)

    internal const val EXTRA_BASLIK = "kertik_haber_baslik"
    internal const val EXTRA_ALT = "kertik_haber_alt"
    internal const val EXTRA_BAS = "kertik_haber_bas"

    /**
     * @param json `{"bas": molanın başladığı an, "haberler": [{"at", "baslik", "alt"}]}`.
     *        Geçmişte kalan anlar atlanır; en çok [EN_COK] haber kurulur.
     */
    fun kur(ctx: Context, json: String) {
        iptal(ctx)
        val kok = try { JSONObject(json) } catch (e: Exception) { return }
        val bas = kok.optLong("bas", 0L)
        val liste = kok.optJSONArray("haberler") ?: return
        val am = ctx.getSystemService(AlarmManager::class.java) ?: return
        val simdi = System.currentTimeMillis()
        for (i in 0 until minOf(liste.length(), EN_COK)) {
            val h = liste.optJSONObject(i) ?: continue
            val an = h.optLong("at", 0L)
            val baslik = h.optString("baslik", "")
            if (an <= simdi || baslik.isBlank()) continue
            val pi = alarmNiyeti(ctx, i, baslik, h.optString("alt", ""), bas)
            try {
                val kesin = Build.VERSION.SDK_INT < Build.VERSION_CODES.S || am.canScheduleExactAlarms()
                if (kesin) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, an, pi)
                else am.setWindow(AlarmManager.RTC_WAKEUP, an, PENCERE_MS, pi)
            } catch (e: SecurityException) {
                try { am.setWindow(AlarmManager.RTC_WAKEUP, an, PENCERE_MS, pi) } catch (e2: Exception) {}
            } catch (e: Exception) {
                // kurulamadıysa mola yine sayılır; sadece haber gelmez
            }
        }
    }

    /** Kurulu anları ve gösterilmiş haberi geri alır. Hiçbir şey kurulu değilse zararsızdır. */
    fun iptal(ctx: Context) {
        val am = ctx.getSystemService(AlarmManager::class.java)
        for (i in 0 until EN_COK) {
            val pi = PendingIntent.getBroadcast(
                ctx, ISTEK_TABAN + i, Intent(ctx, MolaHaberAlici::class.java),
                PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
            ) ?: continue
            try { am?.cancel(pi) } catch (e: Exception) {}
            pi.cancel()
        }
        try { NotificationManagerCompat.from(ctx).cancel(BILDIRIM_ID) } catch (e: Exception) {}
    }

    private fun alarmNiyeti(ctx: Context, sira: Int, baslik: String, alt: String, bas: Long): PendingIntent {
        val i = Intent(ctx, MolaHaberAlici::class.java).apply {
            putExtra(EXTRA_BASLIK, baslik)
            putExtra(EXTRA_ALT, alt)
            putExtra(EXTRA_BAS, bas)
        }
        return PendingIntent.getBroadcast(
            ctx, ISTEK_TABAN + sira, i,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    private fun izinVar(ctx: Context): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true
        return ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) ==
            PackageManager.PERMISSION_GRANTED
    }

    /** Bildirim.kt ile aynı yol: politika yetkisi varsa rahatsız etmeyini delen kimlik. */
    private fun kanalKur(ctx: Context): String {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return KANAL
        val nm = ctx.getSystemService(NotificationManager::class.java) ?: return KANAL
        val delsin = try { nm.isNotificationPolicyAccessGranted } catch (e: Exception) { false }
        val id = if (delsin) KANAL_DND else KANAL
        val kanal = NotificationChannel(
            id, ctx.getString(R.string.haber_kanal), NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = ctx.getString(R.string.haber_kanal_aciklama)
            setShowBadge(false)
            enableLights(false)
            setSound(null, null)
            enableVibration(true)
            vibrationPattern = DESEN
            lockscreenVisibility = Notification.VISIBILITY_PUBLIC
            setBypassDnd(delsin)
        }
        try {
            nm.createNotificationChannel(kanal)
            nm.deleteNotificationChannel(if (delsin) KANAL else KANAL_DND)
        } catch (e: Exception) {
        }
        return id
    }

    @android.annotation.SuppressLint("MissingPermission")   // izinVar() ile bakılıyor
    fun goster(ctx: Context, baslik: String, alt: String, bas: Long) {
        if (!izinVar(ctx)) return
        if (MainActivity.onPlanda) return

        /* "devam et" uygulamayı öne getirir: işe dönen kişi kaldığı yeri görsün.
           Uzun mola sorusu açılacaksa da ekranda açılır, arkada asılı kalmaz. */
        val devam = PendingIntent.getActivity(
            ctx, ISTEK_DEVAM,
            Intent(ctx, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_NEW_TASK
                putExtra(MainActivity.EXTRA_EYLEM, "resume")
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val ac = PendingIntent.getActivity(
            ctx, ISTEK_AC,
            Intent(ctx, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_NEW_TASK
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val b = NotificationCompat.Builder(ctx, kanalKur(ctx))
            .setSmallIcon(R.drawable.ic_bildirim)
            .setContentTitle(baslik)
            .setAutoCancel(true)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setVibrate(DESEN)
            .setSound(null)
            .setContentIntent(ac)
            .addAction(0, ctx.getString(R.string.bildirim_devam), devam)
        if (alt.isNotBlank()) b.setContentText(alt)
        if (bas > 0) b.setWhen(bas).setShowWhen(true).setUsesChronometer(true)

        try {
            NotificationManagerCompat.from(ctx).notify(BILDIRIM_ID, b.build())
        } catch (e: SecurityException) {
        }
    }
}

/** Kurulan an geldiğinde haberi gösterir. Uygulama kapalı olsa da çalışır. */
class MolaHaberAlici : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent?) {
        val i = intent ?: return
        val baslik = i.getStringExtra(MolaHaberi.EXTRA_BASLIK) ?: return
        MolaHaberi.goster(
            ctx, baslik,
            i.getStringExtra(MolaHaberi.EXTRA_ALT) ?: "",
            i.getLongExtra(MolaHaberi.EXTRA_BAS, 0L)
        )
    }
}
