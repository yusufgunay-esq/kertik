// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

package com.yusufgunay.kertik

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/**
 * Bildirim çubuğundaki ve kilit ekranındaki "Mola", "Devam" ve "Bitir" eylemlerinin
 * tıklandığında UYGULAMAYI ÖNE AÇMADAN (sıfır sürtünmeyle) arka planda sessizce
 * çalışmasını sağlayan alıcı.
 */
class KertikEylemAlici : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent?) {
        val eylem = intent?.getStringExtra(MainActivity.EXTRA_EYLEM) ?: return
        val aktivite = MainActivity.aktifOrnek
        if (aktivite != null) {
            aktivite.runOnUiThread {
                aktivite.eylemGonder(eylem)
            }
        } else {
            // Aktivite sonlandırılmışsa bile kullanıcıyı rahatsız etmeden arka planda işlesin
            val i = Intent(ctx, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_MULTIPLE_TASK
                putExtra(MainActivity.EXTRA_EYLEM, eylem)
                putExtra(MainActivity.EXTRA_SESSIZ, true)
            }
            try {
                ctx.startActivity(i)
            } catch (e: Exception) {
            }
        }
    }
}
