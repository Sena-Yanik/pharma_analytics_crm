import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from doktor_ekrani import Ui_MainWindow as Ui_DoktorEkrani
from login_ui import Ui_MainWindow as Ui_Login
import pyodbc
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import matplotlib
matplotlib.use('Qt5Agg') 

import os
from dotenv import load_dotenv

load_dotenv()

driver = os.getenv("DB_DRIVER")
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
trusted_conn = os.getenv("DB_TRUSTED_CONNECTION")

connection_string = (
    f'DRIVER={driver};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection={trusted_conn};'
)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    print("✅ Bağlantı başarılı!")
except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"❌ Bağlantı hatası: {sqlstate}")

# Örnek sorgu
"""
cursor.execute("SELECT * FROM doktor")
for row in cursor.fetchall():
    print(row)
"""
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.show_doktor_ekrani)
        self.doktor_ekrani = None

    def show_doktor_ekrani(self):
        if self.doktor_ekrani is None:
            self.doktor_ekrani = DoktorEkraniWindow()
        
        self.doktor_ekrani.show()
        self.close()

class DoktorEkraniWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_DoktorEkrani()
        self.ui.setupUi(self)
        
        # Doktor verilerini yükle
        self.load_doktorlar()
        
        self.ui.listWidget_doktorlar.itemSelectionChanged.connect(self.display_doktor_details)
        self.ui.Analiz.clicked.connect(self.show_toplam_satis_grafigi)
        self.ui.Tahmin.clicked.connect(self.get_satis_tahmini)

    def get_satis_tahmini(self):
        from PyQt5.QtWidgets import QMessageBox
        cursor = conn.cursor()
    
        cursor.execute("""
            SELECT
                tarih,
                SUM(ilac_sayisi) as toplam_satis
            FROM satis
            GROUP BY tarih
            ORDER BY tarih ASC
        """)

        satis_verileri = cursor.fetchall()

        if len(satis_verileri) < 3:
            QMessageBox.information(self, "Bilgi", "Tahmin için yeterli veri yok. En az 2 satış kaydı gereklidir.")
            return

        veri_listesi=[]
        for row in satis_verileri:
            veri_listesi.append([row[0],row[1]])

        df = pd.DataFrame(veri_listesi, columns=['tarih', 'toplam_satis'])
        df['tarih'] = pd.to_datetime(df['tarih'])

        window_size = min(3,len(df))
        df['hareketli_ortalama'] = df['toplam_satis'].rolling(window=window_size, min_periods=1).mean()



        #### Gelecek günün tahmini: Son birkaç günün hareketli ortalaması
        gunluk_ortalama = df['hareketli_ortalama'].iloc[-1]
        tahmin_1_gun = max(0, int(gunluk_ortalama))  # Tahmin negatif çıkarsa 0 yap
        
        if len(df)>= 5:
            son_5_gun = df ["hareketli_ortalama"].tail(5)
            trend_egim = (son_5_gun.iloc[-1]- son_5_gun.iloc[0])/4

            ortalama_deger = df['hareketli_ortalama'].mean()
            max_degisim = ortalama_deger * 0.02  
            trend_egim = max(-max_degisim, min(max_degisim, trend_egim))
        
        else :
            trend_egim =0

        toplam_30_gun =0
        gunluk_tahminler=[]


        for gun in range(1, 31):
            # Her gün için tahmin 
            gunluk_tahmin = gunluk_ortalama + (trend_egim * gun)
        
            # Minimum koruma - ortalama değerin %30'undan az olmasın
            gunluk_tahmin = max(gunluk_ortalama * 0.3, gunluk_tahmin)
        
            # Maksimum koruma - ortalama değerin 3 katından fazla olmasın
            gunluk_tahmin = min(gunluk_ortalama * 3, gunluk_tahmin)
        
            gunluk_tahminler.append(gunluk_tahmin)
            toplam_30_gun += gunluk_tahmin

        toplam_30_gun = int(toplam_30_gun)

        plt.figure(figsize=(14, 8))

        #Alt grafik 1: Geçmiş veriler ve trend
        plt.subplot(2, 1, 1)

        # Geçmiş verileri çizme
        plt.plot(df['tarih'], df['toplam_satis'], marker='o', linestyle='-', label='Geçmiş Günlük Satışlar' , color="blue", linewidth=2)

        # Hareketli ortalama çizgisi
        plt.plot(df['tarih'], df['hareketli_ortalama'], marker='s', linestyle='--',label=f'Hareketli Ortalama ({window_size} gün)', color='green', linewidth=2)


        tahmin_tarihi_1_gun = df['tarih'].iloc[-1] + pd.Timedelta(days=1)
        plt.plot(tahmin_tarihi_1_gun, tahmin_1_gun, marker='*', color='red', 
             markersize=15, label='Yarınki Tahmin')

        if len(df) >= 2:
            z = np.polyfit(range(len(df)), df['toplam_satis'], 1)
            trend_line = np.poly1d(z)
            plt.plot(df['tarih'], trend_line(range(len(df))), linestyle=':', color='orange', alpha=0.7, label='genel trend')
 
        plt.title("Geçmiş Satış Verileri ve Trend Analizi", fontsize=14, fontweight='bold')
        plt.xlabel("Tarih")
        plt.ylabel("Günlük Satış Adedi")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        # Alt grafik 2: 30 günlük tahmin görselleştirmesi
        plt.subplot(2, 1, 2)
        # Gelecek 30 günün tarihleri
        gelecek_tarihler = [df['tarih'].iloc[-1] + pd.Timedelta(days=i) for i in range(1, 31)]
    
        # 30 günlük tahminleri çiz
        plt.plot(gelecek_tarihler, gunluk_tahminler, marker='o', linestyle='-', 
                color='purple', linewidth=2, label='30 Günlük Günlük Tahminler')
    
        # Ortalama çizgisi
        ortalama_30_gun = toplam_30_gun / 30
        plt.axhline(y=ortalama_30_gun, color='red', linestyle='--', 
                    label=f'30 Günlük Ortalama: {ortalama_30_gun:.0f} adet/gün')
    
        # İlk ve son günleri vurgula
        plt.plot(gelecek_tarihler[0], gunluk_tahminler[0], marker='*', 
                color='green', markersize=12, label=f'1. Gün: {gunluk_tahminler[0]:.0f}')
        plt.plot(gelecek_tarihler[-1], gunluk_tahminler[-1], marker='D', 
                color='red', markersize=10, label=f'30. Gün: {gunluk_tahminler[-1]:.0f}')
 
        plt.title("Önümüzdeki 30 Günün Günlük Satış Tahminleri", fontsize=14, fontweight='bold')
        plt.xlabel("Tarih")
        plt.ylabel("Tahmini Günlük Satış")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
    
        plt.tight_layout()

        # Y ekseni formatlaması
        def format_number(num):
            if num >= 1000:
                return f'{num/1000:.1f}K'
            else:
                return f'{num:.0f}'

        # Grafiklerde binlik formatlaması
        for ax in plt.gcf().get_axes():
            y_max = max([tick.get_text() for tick in ax.get_yticklabels() if tick.get_text().replace('.', '').replace('-', '').isdigit()], 
                    default=['0'])
            if any(float(tick.get_text()) >= 1000 for tick in ax.get_yticklabels() 
                if tick.get_text().replace('.', '').replace('-', '').isdigit()):
                from matplotlib.ticker import FuncFormatter
                def format_thousands(x, pos):
                    if x >= 1000:
                        return f'{x/1000:.1f}K'
                    else:
                        return f'{x:.0f}'
                ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    
        plt.show()

        # Detaylı analiz hesaplamaları
        son_7_gun_ortalama = df['toplam_satis'].tail(7).mean()
        son_30_gun_ortalama = df['toplam_satis'].tail(min(30, len(df))).mean()
    
        # Haftalık tahminler
        haftalik_tahminler = []
        for hafta in range(4):
            hafta_baslangic = hafta * 7
            hafta_bitis = (hafta + 1) * 7
            haftalik_toplam = sum(gunluk_tahminler[hafta_baslangic:hafta_bitis])
            haftalik_tahminler.append(haftalik_toplam)
    
        # Trend yönü
        if trend_egim > 0:
            trend_yonu = "Artış"
            trend_ikon = "📈"
        elif trend_egim < 0:
            trend_yonu = "Azalış"
            trend_ikon = "📉"
        else:
            trend_yonu = "Stabil"
            trend_ikon = "➡️"

        mesaj = (f"30 Günlük TOPLAM Satış Tahmin Raporu:\n\n"
             f"🎯 TAHMİNLER:\n"
             f"• Yarın (1 gün): {format_number(tahmin_1_gun)} adet\n"
             f"• Önümüzdeki 30 günde TOPLAM: {format_number(toplam_30_gun)} adet\n"
             f"• 30 günlük günlük ortalama: {format_number(ortalama_30_gun)} adet\n\n"
             f"📊 HAFTALIK DAĞILIM:\n"
             f"• 1. Hafta (1-7 gün): {format_number(haftalik_tahminler[0])} adet\n"
             f"• 2. Hafta (8-14 gün): {format_number(haftalik_tahminler[1])} adet\n"
             f"• 3. Hafta (15-21 gün): {format_number(haftalik_tahminler[2])} adet\n"
             f"• 4. Hafta (22-28 gün): {format_number(haftalik_tahminler[3])} adet\n"
             f"• Son 2 gün (29-30): {format_number(sum(gunluk_tahminler[28:30]))} adet\n\n"
             f"📈 TREND ANALİZİ:\n"
             f"• Genel trend: {trend_ikon} {trend_yonu}\n"
             f"• Günlük değişim: {trend_egim:+.2f} adet/gün\n"
             f"• 30 günlük toplam değişim: {trend_egim*30:+.0f} adet\n\n"
             f"ℹ️ TEKNİK BİLGİLER:\n"
             f"• Son 7 günün ortalaması: {format_number(son_7_gun_ortalama)} adet\n"
             f"• Son 30 günün ortalaması: {format_number(son_30_gun_ortalama)} adet\n"
             f"• Tahmin vs geçmiş farkı: {((ortalama_30_gun/son_30_gun_ortalama-1)*100):+.1f}%\n\n"
             f"• Veri nokta sayısı: {len(df)} \n"
             f"• İlk gün tahmini: {format_number(gunluk_tahminler[0])} adet\n"
             f"• Son gün tahmini: {format_number(gunluk_tahminler[-1])} adet")  

        QMessageBox.information(self, "30 Günlük Toplam Satış Tahmini", mesaj)
        
    def load_doktorlar(self):
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                d.dr_id,
                d.isim,
                d.brans,
                b.bölge_ismi,
                d.hastane
            FROM doktor AS d
            JOIN bölge AS b ON d.bölge_id = b.bölge_id
        """)
        doktorlar = cursor.fetchall()
        
        self.doktor_verileri = {}
        for doktor in doktorlar:
            dr_id = doktor[0]
            isim = doktor[1]
            brans = doktor[2]
            bolge_ismi = doktor[3]
            hastane = doktor[4]
            
            self.ui.listWidget_doktorlar.addItem(isim)
            self.doktor_verileri[isim] = {
                "dr_id": dr_id,
                "brans": brans,
                "bolge": bolge_ismi,
                "hastane": hastane
            }

    def show_toplam_satis_grafigi(self):
        cursor = conn.cursor()

        cursor.execute("""
           SELECT 
              d.isim, 
              SUM(s.ilac_sayisi) as toplam_satis 
          FROM doktor AS d
          LEFT JOIN satis AS s ON d.dr_id = s.dr_id
          GROUP BY d.isim
          ORDER BY toplam_satis DESC
        """)
        satis_verileri = cursor.fetchall()
    
        if not satis_verileri:
            QMessageBox.warning(self, "Uyarı", "Veritabanında satış verisi bulunamadı.")
            return

        # verileri hazırla
        doktor_isimleri = [veri[0] for veri in satis_verileri]
        satis_sayilari = [veri[1] if veri[1] is not None else 0 for veri in satis_verileri]

        plt.figure(figsize=(12, 6))
        plt.bar(doktor_isimleri, satis_sayilari, color='skyblue')
    
        plt.title("Tüm Doktorların Toplam İlaç Satış Analizi")
        plt.xlabel("Doktor Adı")
        plt.ylabel("Toplam Satılan İlaç Sayısı")
        plt.xticks(rotation=45, ha='right') # İsimler uzunsa okunurluğu artırır
        plt.grid(axis='y', linestyle='--')
        plt.tight_layout() 

        plt.show()

    def display_doktor_details(self):
        selected_item = self.ui.listWidget_doktorlar.currentItem()
        
        if selected_item:
            doktor_ismi = selected_item.text()
            doktor_detaylari = self.doktor_verileri.get(doktor_ismi)
            
            if doktor_detaylari:
                self.ui.lineEdit_isim.setText(doktor_ismi)
                self.ui.lineEdit_brans.setText(doktor_detaylari["brans"])
                self.ui.lineEdit_bolge.setText(doktor_detaylari["bolge"])
                self.ui.lineEdit_hastane.setText(doktor_detaylari["hastane"])
                dr_id = doktor_detaylari["dr_id"]
                # İlaç sayısını yüklemek için dr_id'yi kullanıyoruz
                self.load_ilac_sayisi(doktor_detaylari["dr_id"])
                self.load_ilac_detaylari(dr_id)

    def load_ilac_sayisi(self, dr_id):
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                ilac_id,
                SUM(ilac_sayisi)
            FROM satis
            WHERE dr_id = ?
            GROUP BY ilac_id
        """, (dr_id,))
        
        ilac_sayilari = cursor.fetchall()
        
        ilac_toplamlari = {}
        toplam_ilac_sayisi = 0
        
        for ilac in ilac_sayilari:
            ilac_id = ilac[0]
            sayi = ilac[1]
            ilac_toplamlari[ilac_id] = sayi
            toplam_ilac_sayisi += sayi

        ilac_1_sayisi = ilac_toplamlari.get(1, 0)
        ilac_2_sayisi = ilac_toplamlari.get(2, 0)
        ilac_3_sayisi = ilac_toplamlari.get(3, 0)
        ilac_4_sayisi = ilac_toplamlari.get(4, 0)
        ilac_5_sayisi = ilac_toplamlari.get(5, 0)
        ilac_6_sayisi = ilac_toplamlari.get(6, 0)

        self.ui.lineEdit_ilac_1.setText(str(ilac_1_sayisi))
        self.ui.lineEdit_ilac_2.setText(str(ilac_2_sayisi))
        self.ui.lineEdit_ilac_3.setText(str(ilac_3_sayisi))
        self.ui.lineEdit_ilac_4.setText(str(ilac_4_sayisi))
        self.ui.lineEdit_ilac_5.setText(str(ilac_5_sayisi))
        self.ui.lineEdit_ilac_6.setText(str(ilac_6_sayisi))
        self.ui.lineEdit_toplam_ilac.setText(str(toplam_ilac_sayisi))

    def load_ilac_detaylari(self, dr_id):
        # Tabloyu temizle
        self.ui.tableWidget_ilac_detaylari.setRowCount(0)
    
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                s.tarih,
                i.ilac_ismi,
                s.ilac_sayisi
            FROM satis AS s
            JOIN ilac AS i ON s.ilac_id = i.ilac_id
            WHERE s.dr_id = ?
            ORDER BY s.tarih DESC
        """, (dr_id,))
    
        ilac_detaylari = cursor.fetchall()

        # Tablonun satır sayısını ayarlar
        self.ui.tableWidget_ilac_detaylari.setRowCount(len(ilac_detaylari))
    
        for row_index, row_data in enumerate(ilac_detaylari):
            for col_index, col_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(col_data))
                self.ui.tableWidget_ilac_detaylari.setItem(row_index, col_index, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())