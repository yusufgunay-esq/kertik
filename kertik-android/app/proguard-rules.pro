# JS köprüsü yansımayla çağrılıyor, isimleri korunmalı.
-keepclassmembers class com.yusufgunay.kertik.MainActivity$Kopru {
    @android.webkit.JavascriptInterface <methods>;
}
