import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

/* ---------------------------------------------------------------------------
   Sırlar depoda DURMAZ.
   İki kaynaktan gelirler:
     1. gizli.properties  — yerel derleme / Android Studio (.gitignore'da)
     2. ortam değişkenleri — GitHub Actions sırları
   Hiçbiri yoksa: imzasız derlenir ve Google senkronu kapalı çıkar.
   Uygulama ikisi olmadan da tam çalışır.
   --------------------------------------------------------------------------- */
val gizli = Properties().apply {
    val f = rootProject.file("gizli.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}
fun sir(anahtar: String, ortam: String): String? =
    (gizli.getProperty(anahtar) ?: System.getenv(ortam))?.takeIf { it.isNotBlank() }

// --- imza ---
val anahtarDosyasi = sir("storeFile", "KERTIK_STORE_FILE")
val anahtarParolasi = sir("storePassword", "KERTIK_STORE_PASSWORD")
val anahtarAdi = sir("keyAlias", "KERTIK_KEY_ALIAS") ?: "kertik"
val anahtarKeyParolasi = sir("keyPassword", "KERTIK_KEY_PASSWORD") ?: anahtarParolasi

/* Göreli yol PROJE KÖKÜNE göre çözülür, app modülüne göre değil.
   (rootProject.file mutlak yolları olduğu gibi bırakır — CI böyle veriyor.) */
val anahtarYolu = anahtarDosyasi?.let { rootProject.file(it) }
val imzaVar = anahtarYolu != null && anahtarParolasi != null && anahtarYolu.exists()

android {
    namespace = "com.yusufgunay.kertik"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.yusufgunay.kertik"
        minSdk = 24
        targetSdk = 36
        versionCode = 40
        versionName = "1.3"

    }

    buildFeatures {
        buildConfig = true
    }

    signingConfigs {
        if (imzaVar) {
            create("yayin") {
                storeFile = anahtarYolu
                storePassword = anahtarParolasi
                keyAlias = anahtarAdi
                keyPassword = anahtarKeyParolasi
                enableV1Signing = true
                enableV2Signing = true
                enableV3Signing = true
            }
        }
    }

    buildTypes {
        release {
            // Tek dosyalık bir WebView uygulaması; küçültecek Kotlin kodu yok denecek kadar az.
            isMinifyEnabled = false
            isShrinkResources = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            if (imzaVar) signingConfig = signingConfigs.getByName("yayin")
        }
        debug {
            /* Google yetkilendirmesi kimliği paket adı + imza SHA-1'inden okur.
               Debug derlemesi ayrı bir paket adı ya da ayrı bir anahtar
               kullanırsa Google onu tanımaz ve "bağlan" hep başarısız olur.
               Bu yüzden debug, yayın kimliğinin aynısını taşır: aynı paket adı,
               aynı imza. Android Studio'dan çalıştırılan sürümde de senkron
               çalışsın diye. (Anahtar yoksa debug imzasıyla derlenir, senkron
               o durumda sessizce kapalı kalır — uygulama yine tam çalışır.) */
            versionNameSuffix = "-debug"
            if (imzaVar) signingConfig = signingConfigs.getByName("yayin")
        }
    }

    // İlk yeşil derlemeyi bir lint uyarısı yüzünden kaybetmemek için.
    // Proje oturunca kaldırılacak ve lint gerçekten okunacak.
    lint {
        abortOnError = true
        checkReleaseBuilds = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-ktx:1.9.1")
    implementation("androidx.webkit:webkit:1.11.0")   // WebViewAssetLoader
    implementation("androidx.core:core-splashscreen:1.0.1")
    // Google yetkilendirmesi (Drive appdata) — native hesap seçici, gömülü sır yok.
    implementation("com.google.android.gms:play-services-auth:21.6.0")
    /* Kertik Tam — tek seferlik uygulama içi ürün.
       Sürüm 8 ve üstü zorunlu: 31 Ağustos 2026'dan sonra Play, 7 ve altını
       kullanan yeni sürümleri kabul etmiyor. Bu kütüphane com.android.vending.BILLING
       iznini kendi manifestinde taşıyor, elle eklemeye gerek yok. */
    implementation("com.android.billingclient:billing:9.1.0")
}

/* Derleme başında ne gömüldüğünü tek satırda söyle — sessizce imzasız/senkronsuz
   çıktı üretip sonra şaşırmayalım. */
gradle.projectsEvaluated {
    logger.lifecycle("Kertik: imza=" + (if (imzaVar) "var" else "YOK"))
}
