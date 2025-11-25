# 💊 Doktor İlaç Satış Analizi ve Tahmin Sistemi

## 🌟 Genel Bakış

Bu proje, doktorların ilaç satış verilerini analiz etmek ve gelecekteki satış miktarlarını tahmin etmek amacıyla geliştirilmiş bir **PyQt5** masaüstü uygulamasıdır. Sistem, bir **SQL Server** veritabanı ile entegre çalışır ve doktor bazında ilaç kullanım detaylarını, toplam satış sayılarını gösterir ve **Lineer Regresyon** modelini kullanarak tahminler yapar.

## ✨ Özellikler

* **Kullanıcı Girişi:** Güvenli kullanıcı adı/şifre ile giriş ekranı (`login.ui`, `login_ui.py`).
* **Doktor Listeleme:** Sol panelde tüm doktorların listelenmesi.
* **Detay Görüntüleme:** Seçilen doktorun branş, bölge, hastane bilgilerini ve kullandığı ilk 6 ilacın toplam adetlerini görüntüleme.
* **İlaç Detay Tablosu:** Seçilen doktora ait tüm ilaç satış kayıtlarını (tarih, ilaç adı, adet) detaylı listeleme.
* **Tahmin Fonksiyonu:** Seçilen doktorun geçmiş satış verilerine dayanarak gelecekteki ilaç satışlarını **Lineer Regresyon** ile tahmin etme ve **grafiksel** olarak gösterme.
* **Analiz Fonksiyonu:** <Analiz butonu ile yapılan diğer spesifik analizleri/grafikleri buraya ekleyin, örneğin: Bölge/Branş bazında toplu analiz, en çok satan ilaçlar vb.>

## 🛠️ Teknolojiler

* **Python 3.x**
* **PyQt5:** Masaüstü uygulama arayüzü (UI) geliştirme
    * `doktor_ekrani.ui`, `login.ui`: Qt Designer ile oluşturulan arayüz dosyaları.
    * `doktor_ekrani.py`, `login_ui.py`: UI dosyalarının Python kodları.
* **pyodbc:** SQL Server veritabanı bağlantısı.
* **SQL Server:** Veritabanı yönetim sistemi.
* **Pandas & NumPy:** Veri işleme ve analiz.
* **scikit-learn (sklearn):** Lineer Regresyon modeli için.
* **Matplotlib:** Grafik ve tahmin sonuçlarının görselleştirilmesi.
* **dotenv:** Güvenli veritabanı bağlantı bilgileri yönetimi.

## ⚙️ Kurulum ve Çalıştırma

### Önkoşullar

1.  **Python 3.x** kurulu olmalı.
2.  **SQL Server** kurulu ve erişilebilir olmalı.
3.  Veritabanı yapısı ve tablolar (`doktor`, `satis`, `ilac`, vb.) oluşturulmuş olmalı.

### Adımlar

1.  **Projeyi Klonlayın:**
    ```bash
    git clone <projenizin-github-linki>
    cd <proje-adi>
    ```

2.  **Gerekli Kütüphaneleri Kurun:**
    ```bash
    pip install pyqt5 pyodbc pandas numpy scikit-learn matplotlib python-dotenv
    ```
    * *Not: pyodbc için sisteminizde uygun ODBC sürücüsünün (örneğin, ODBC Driver 17 for SQL Server) kurulu olması gerekebilir.*

3.  **Çevre Değişkenlerini Ayarlayın:**
    Projenin ana dizininde **`.env`** adında bir dosya oluşturun ve veritabanı bağlantı bilgilerinizi aşağıdaki gibi ekleyin:
    ```ini
    DB_DRIVER={ODBC Sürücünüzün Adı, örn: ODBC Driver 17 for SQL Server}
    DB_SERVER=<SQL Server Adınız>
    DB_DATABASE=<Veritabanı Adınız>
    DB_TRUSTED_CONNECTION=yes
    ```
    * *(Eğer Trusted_Connection kullanmıyorsanız, bu kısmı kaldırıp kullanıcı adı/şifre ile bağlantı dizesini düzenlemeniz gerekir.)*

4.  **Uygulamayı Başlatın:**
    ```bash
    python main.py
    ```

5.  **Giriş Yapın:**
    Uygulama açıldığında kullanıcı adı ve şifre ile giriş yapın.
    * *Not: Giriş kimlik bilgileri ve doğrulaması `main.py` dosyasında nasıl ele alındığını kontrol edin.*

## 📂 Dosya Yapısı

| Dosya Adı | Açıklama |
| :--- | :--- |
| `main.py` | Uygulamanın ana mantığı, veritabanı bağlantısı ve işlevsellik (giriş, doktor yükleme, analiz, tahmin) burada bulunur. |
| `login.ui` / `login_ui.py` | Giriş ekranı arayüz tanımı ve Python sınıfı. |
| `doktor_ekrani.ui` / `doktor_ekrani.py` | Doktor detay ve analiz ekranı arayüz tanımı ve Python sınıfı. |
| `resimm.qrc` / `resimm_rc.py` | PyQt5 arayüzü için kullanılan kaynak (resim) dosyaları. |
| `.env` | Veritabanı bağlantı bilgilerini içeren çevre değişkenleri dosyası. |

## 🤝 Katkıda Bulunma

Hata raporları, yeni özellik önerileri veya kod katkıları her zaman kabul edilir. Lütfen yeni bir **Issue** açın veya bir **Pull Request** gönderin.

## 🧑‍💻 Yazar

* **Sena Yanık**
* **www.linkedin.com/in/sena-yanık-03036327b**
