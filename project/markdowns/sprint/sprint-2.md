# Sprint 2

## Tahmin Edilen Tamamlanacak Puan – Tahmin Mantığı  
*(Doldurulacak)*

---

## Daily Scrum  
- Her gün yapılan daily toplantılarında görev durumları paylaşıldı.  
- Model eğitimi süreci ve Django arayüz geliştirmeleri tartışıldı.  
- Gömme (embedding) işlemlerinde API sınırları nedeniyle yaşanan gecikmelere çözüm olarak batch işleme önerildi.  

---

## Sprint Board  
*(Sprint süresince tamamlanan görevlerin takibi için görsel veya tablo eklenecek alan)*

---

## Sprint Review

Kaynak olarak belirtilen dosyalar (PDF) `Python` ve `Gemini API` kullanılarak işlenmiş, bu verilerle oluşturulan model RAG sistemi ile entegre edilmiştir.  

Modelin kullanıcıya sunumu için, Python tabanlı `Django` framework kullanılarak web arayüzü geliştirilmeye başlanmıştır.  

---

## Model Eğitimi

Gemini AI altyapısı ve RAG (Retrieval-Augmented Generation) sistemini kullanan modelimiz ile dökümanlardan vektörleştirme yoluyla anlamlı sonuçlar elde edilmiştir.

Bu süreçte 3 kişi paralel olarak RAG yapılarını kurmuş ve test etmiştir. Yapılan testlerin karşılaştırılması sonucunda en verimli yapı birleştirilerek daha güçlü ve kararlı bir sistem oluşturulmuştur.

**Model Eğitiminde Çalışan Kişiler:**  
- Zeynep ATİK  
- Mevlüt Han AŞCI  
- Doğukan VATANSEVER  

---

## RAG Pipeline – 4 Aşamalı Süreç

Bu sistem, PDF dosyalarını parçalara ayırıp, embedding işlemi ile vektör veritabanına ekleyerek sorulara bağlamsal cevaplar üretecek şekilde tasarlanmıştır. Süreç 4 temel aşamadan oluşur:

### 1. Chunking (PDF Bölme İşlemi)  
**Sınıf**: `PDFChunker`  

- PDF dosyası başlıklar (`Title`, `Heading`, `Subtitle`) ve metin yapısı dikkate alınarak parçalara bölünür.  
- Her parça anlamlı bir bilgi taşıyacak şekilde yapılandırılır.  
- PDF dosyalarından tüm sayfa metinlerini çıkaran bir yardımcı fonksiyon geliştirilmiştir.

---

### 2. Embedding (Vektörleştirme)  
**Sınıf**: `GeminiEmbedder`  

- Oluşturulan metin parçaları Gemini API aracılığıyla vektör haline getirilir.  
- Bu embedding’ler ChromaDB'ye aktarılmak üzere hazırlanır.  
- Bu yapı, kullanıcı sorularına en uygun cevabı verecek LLM sisteminin temel altyapısını oluşturur.

---

### 3. Indexing (Vektör Veritabanına Kaydetme)  
**Sınıf**: `ChromaDBWrapper`  

- Her parçanın ID’si, metni ve vektörü kullanılarak ChromaDB’ye eklenir.  
- Birden fazla PDF için `create_index_from_folder()` metodu kullanılabilir.  
- Bu işlemle RAG sisteminin bilgi tabanı oluşturulmuş olur.

---

### 4. Question Answering (Soru-Cevaplama)  
**Sınıf**: `RAGPipeline`  

- Kullanıcıdan gelen sorular vektörleştirilir ve en alakalı parça(lar) veritabanından alınır.  
- Bu parçalar, bağlam olarak Gemini LLM’e iletilir ve anlamlı cevap oluşturulur.  
- Gerekirse `chat()` metodu ile bağlamsız yanıt üretilebilir.

---

## Frontend

Django framework kullanılarak sistemin web arayüzü geliştirilmeye başlanmıştır.

**Frontend Geliştiren Kişiler:**  
- Helin Hümeyra SARAÇOĞLU  
- Hatice Ece KIRIK  

---

## Sprint Retrospective

- Ekip içi görev dağılımı başarılıydı, paralel ilerleyen model eğitim süreçleri etkili sonuç verdi.  
- API kısıtlamaları nedeniyle yaşanan teknik aksaklıklar öğrenildi ve çözüm stratejileri üretildi.  
- Frontend ile backend entegrasyonuna yönelik daha sık iletişim gerekliliği görüldü.

---

> **[Click to return to the main file](../../README.md)**