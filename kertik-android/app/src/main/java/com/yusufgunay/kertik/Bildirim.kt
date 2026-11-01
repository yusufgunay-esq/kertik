// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

package com.yusufgunay.kertik

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat

/**
 * Bildirim çubuğundaki canlı sayaç.
 *
 * Foreground service **bilerek kullanılmadı.** Android'in kronometreli bildirimi
 * saati kendisi işletiyor (`setUsesChronometer`), yani saniyede bir uyanıp
 * bildirimi yenilememize gerek yok. Böylece:
 *   - pil tüketimi yok denecek kadar az,
 *   - Android 14'ün "foreground service türü" beyanı ve onun Play gerekçesi gerekmiyor,
 *   - uygulama öldürülse bile bildirim ve saydığı süre doğru kalmaya devam ediyor.
 *
 * Bedeli: bildirimdeki tuşlar uygulamayı bir an öne getirir, işini yapar ve geri
 * çekilir. Tam yerinde çalışması için foreground service şart olur; o karar
 * gerçek kullanımdan sonra verilecek.
 *
 * **Dil.** Başlık ve alt satır sayfadan geliyor; sayfa hangi dildeyse bildirim de
 * o dilde. Kanal adı ve tuş etiketleri ise Android kaynaklarından (`values-XX/`)
 * okunuyor: bunlar sistemin dilini izler. İkisi ayrı bilerek — kullanıcı uygulama
 * içinden başka bir dil seçse bile, sistem tuşlarının telefonun dilinde kalması
 * doğru olan. Metinleri çevirmek için `res/values-XX/strings.xml` yeter,
 * burada kod değişmez.
 */
class Bildirim(private val ctx: Context) {

    init {
        kanalKur()
    }

    /** Uygulamanın "rahatsız etmeyin"i değiştirme yetkisi var mı. */
    private fun politikaVar(): Boolean = try {
        ctx.getSystemService(NotificationManager::class.java)?.isNotificationPolicyAccessGranted == true
    } catch (e: Exception) {
        false
    }

    /**
     * Kullanılacak kanalı kurar ve kimliğini döndürür.
     *
     * Seans başlarken telefonu **biz** sessize alıyoruz; sonra kendi sayacımızın
     * da o sessizliğin altında kaybolması saçmaydı — kullanıcı süreyi göremez
     * oluyordu. Çözüm: rahatsız etmeyin modunu delen bir kanal.
     *
     * `setBypassDnd` yalnız kanal KURULURKEN ve uygulamanın politika yetkisi
     * varken işliyor; kurulmuş bir kanalda sonradan değiştirilemiyor. Bu yüzden
     * tek kanalı güncellemeye çalışmak yerine iki ayrı kimlik tutuluyor, o an
     * geçerli olmayan siliniyor — ayarlar ekranında yine tek bir kanal görünür,
     * kullanıcı hiçbir seçimle uğraşmaz.
     */
    private fun kanalKur(): String {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return KANAL
        val nm = ctx.getSystemService(NotificationManager::class.java) ?: return KANAL
        val delsin = politikaVar()
        val id = if (delsin) KANAL_DND else KANAL
        /* Aynı kimlikle yeniden çağırmak adı ve açıklamayı günceller:
           telefonun dili değiştiyse kanal da yeni dilde görünür. */
        val kanal = NotificationChannel(
            id, ctx.getString(R.string.bildirim_kanal), NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = ctx.getString(R.string.bildirim_kanal_aciklama)
            setShowBadge(false)
            enableVibration(false)
            enableLights(false)
            setSound(null, null)
            lockscreenVisibility = Notification.VISIBILITY_PUBLIC
            setBypassDnd(delsin)
        }
        try {
            nm.createNotificationChannel(kanal)
            nm.deleteNotificationChannel(if (delsin) KANAL else KANAL_DND)
        } catch (e: Exception) {
            // kanal kurulamadıysa bildirim yine de denenecek; sessizce geç
        }
        return id
    }

    fun izinVar(): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true
        return ContextCompat.checkSelfPermission(ctx, Manifest.permission.POST_NOTIFICATIONS) ==
            PackageManager.PERMISSION_GRANTED
    }

    /**
     * @param temelMs kronometrenin dayandığı an (duvar saati).
     *        Yukarı sayarken: seansın başladığı an. Geri sayarken: hedefin dolacağı an.
     */
    @android.annotation.SuppressLint("MissingPermission")   // izinVar() ile bir satır yukarıda bakılıyor
    fun goster(baslik: String, alt: String, temelMs: Long, geriSayim: Boolean, molada: Boolean) {
        if (!izinVar()) return

        /* Her gösterimde kanal tazeleniyor: politika yetkisi seans akışının
           içinde verilebiliyor, kanalın da o anda doğrusuna geçmesi gerek. */
        val b = NotificationCompat.Builder(ctx, kanalKur())
            .setSmallIcon(R.drawable.ic_bildirim)
            .setContentTitle(baslik)
            .setContentText(alt)
            .setOngoing(true)
            .setShowWhen(true)
            .setWhen(temelMs)
            .setUsesChronometer(true)
            .setChronometerCountDown(geriSayim)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setCategory(NotificationCompat.CATEGORY_STOPWATCH)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setContentIntent(niyet(null))

        if (molada) b.addAction(0, ctx.getString(R.string.bildirim_devam), niyet("resume"))
        else b.addAction(0, ctx.getString(R.string.bildirim_mola), niyet("break"))
        b.addAction(0, ctx.getString(R.string.bildirim_bitir), niyet("end"))

        try {
            NotificationManagerCompat.from(ctx).notify(ID, b.build())
        } catch (e: SecurityException) {
            // izin sonradan alınmışsa sessizce geç; uygulama bildirimsiz de tam çalışır
        }
    }

    fun gizle() {
        try {
            NotificationManagerCompat.from(ctx).cancel(ID)
        } catch (e: Exception) {
        }
    }

    private fun niyet(eylem: String?): PendingIntent {
        if (eylem == null) {
            // Bildirimin gövdesine dokunulduğunda uygulamayı öne getir
            val i = Intent(ctx, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_NEW_TASK
            }
            return PendingIntent.getActivity(
                ctx, 0, i,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        } else {
            // Butonlara (Mola / Devam / Bitir) dokunulduğunda uygulamayı ASLA öne fırlatma!
            // KertikEylemAlici (BroadcastReceiver) üzerinden sessizce arka planda hallet.
            val i = Intent(ctx, KertikEylemAlici::class.java).apply {
                action = MainActivity.EYLEM_BROADCAST
                putExtra(MainActivity.EXTRA_EYLEM, eylem)
            }
            return PendingIntent.getBroadcast(
                ctx, eylem.hashCode(), i,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        }
    }

    companion object {
        const val KANAL = "kertik_sayac_v2"
        /** Rahatsız etmeyin modunu delen kanal — yalnız politika yetkisi varken kurulur. */
        const val KANAL_DND = "kertik_sayac_v3_dnd"
        const val ID = 1
    }
}
