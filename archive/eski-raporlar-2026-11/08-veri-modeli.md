# 08 — Veri Modeli

Tasarımın altın kuralı: **kayıt, olayların listesidir; sayılar ondan türetilir.**
Bir yere "toplam çalışma = 107 dakika" yazmıyoruz. Olaylara bakıp hesaplıyoruz.
Böylece kullanıcı geçmişi düzelttiğinde her şey kendiliğinden düzelir.

---

## Tablolar

### `session` — bir çalışma oturumu
| Alan | Tip | Not |
|---|---|---|
| `id` | UUID | |
| `started_at` | epoch ms | duvar saati |
| `ended_at` | epoch ms? | null = devam ediyor |
| `mode` | enum | `stopwatch` \| `countdown` |
| `planned_duration_ms` | long? | sadece countdown modunda |
| `task_id` | UUID? | isteğe bağlı bağlantı |
| `subject_id` | UUID? | ders/konu etiketi |
| `note` | text? | "türev tekrarı" |
| `day_key` | date | **başlangıç** gününe göre; gece yarısını geçen seans başladığı güne yazılır |
| `edited_at` | epoch ms? | elle düzeltildiyse dolu — şeffaflık için |
| `created_by` | enum | `live` \| `manual` (sonradan elle eklenen seans) |

### `session_event` — seansın içindeki her şey
Molalar ve onay durumları ayrı tablo değil, **tek bir olay akışı**. En esnek yapı bu.

| Alan | Tip | Not |
|---|---|---|
| `id` | UUID | |
| `session_id` | UUID | |
| `type` | enum | `start` \| `break_start` \| `break_end` \| `end` \| `presence_ping` \| `presence_ack` |
| `at` | epoch ms | |
| `at_monotonic` | long? | `elapsedRealtime`, çapraz doğrulama için |

Buradan hesaplananlar:
- **mola süresi** = tüm `break_start`→`break_end` aralıklarının toplamı
- **brüt süre** = `end.at − start.at`
- **net çalışma** = brüt − mola
- **onaylanmamış süre** = cevapsız kalan `presence_ping`'den sonraki, sonraki
  `presence_ack` veya kullanıcı etkileşimine kadar geçen süre
- **doğrulanmış çalışma** = net çalışma − onaylanmamış süre

> `unconfirmed_override` alanı: kullanıcı "hayır, orada da çalışıyordum" dediğinde
> onaylanmamış süreyi doğrulanmışa taşır. Ham olay silinmez, sadece işaretlenir.

### `task` — görev
| Alan | Tip | Not |
|---|---|---|
| `id` | UUID | |
| `title` | text | |
| `planned_for` | date | hangi güne planlandı |
| `subject_id` | UUID? | |
| `status` | enum | `bekliyor` \| `yapiliyor` \| `bitti` \| `olmadi` \| `tasindi` \| `iptal` |
| `reason` | enum? | `zaman` \| `enerji` \| `araya_girdi` \| `unuttum` \| `zorlandi` \| `fikir_degisti` |
| `moved_from_id` | UUID? | taşınan görevin kaynağı → erteleme zinciri |
| `move_count` | int | zincirin uzunluğu, `↻3` göstergesi için |
| `estimated_ms` | long? | tahmini süre (v2: tahmin vs gerçek) |
| `sort_order` | int | |
| `created_at` / `closed_at` | epoch ms | |

**Kritik karar:** görev taşındığında satır **güncellenmez**, eski satır `tasindi` olarak kapanır
ve **yeni bir satır** açılır (`moved_from_id` ile bağlı).
Neden: "o gün o görev vardı" bilgisi ancak böyle korunur. Şikâyetin özü buydu.

### `subject` — ders / konu
| Alan | Tip |
|---|---|
| `id` | UUID |
| `name` | text |
| `color` | int? |
| `archived` | bool |

### `day_log` — günün kapanışı
| Alan | Tip | Not |
|---|---|---|
| `day_key` | date (PK) | |
| `closed_at` | epoch ms? | gün sonu ritüeli yapıldı mı |
| `note` | text? | günlük tek satır not (opsiyonel, hoş bir dokunuş) |

### `settings`
Tek satırlık tablo ya da DataStore: teyit aralığı, dönüm noktası süresi, DND açık mı,
gün sonu ritüeli saati, tema.

---

## Türetilen görünümler (sorgu, tablo değil)

- **Günlük özet:** `day_key` → doğrulanmış çalışma, mola, onaylanmamış, görev durum dağılımı
- **Haftalık konu dağılımı:** `subject_id` × 7 gün
- **Tamamlanma oranı:** `bitti / (bitti + olmadi + tasindi)` — `iptal` sayılmaz
- **Sebep dağılımı:** son 30 gün `reason` histogramı
- **Erteleme zincirleri:** `moved_from_id` takip edilerek

---

## Şeffaflık kuralı

Elle düzeltilmiş her seans arayüzde küçük bir işaret taşır: `düzeltildi`.
Bu bir suçlama değil — tam tersine, uygulamanın "sana yalan söylemiyorum" iddiasının parçası.
Kendine karşı dürüst kalmanın en kolay yolu, neyin ölçülüp neyin tahmin edildiğini görmek.

---

## Göç (migration) uyarısı
MVP'de veri modeli değişecek, kesin. Room migration'larını baştan ciddiye al ya da
MVP boyunca `fallbackToDestructiveMigration` kullanıp **v1'e geçerken** temiz bir şema
dondur. İkincisi daha hızlı; ama o zaman MVP verini kaybetmeye razı ol.
