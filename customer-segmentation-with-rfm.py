import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
#ufak ayarlar
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

########################################################################################################################
# Görev 1:
########################################################################################################################
# Veriyi Anlama ve Hazırlama

# 1. Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
# >>Çözüm:
df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
# 2.  Veri setinin betimsel istatistiklerini inceleyiniz.
# >>Çözüm:
df.shape
df.columns
df.describe().T
# 3.  Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
# >>Çözüm: #df.isnull() sadece bunu çalıştırmak gibi bir hataya düşmeyin derim xD
df.isnull().sum()
# 4.  Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
# >>Çözüm:
df.dropna(inplace=True)
# 5.  Eşsiz ürün sayısı kaçtır?
# >>Çözüm:
# df.nunique()
df.Description.nunique()
# 6.  Hangi üründen kaçar tane vardır?
# >>Çözüm:
df.Description.value_counts().head(10)
# 7.  En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
# >>Çözüm:
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
# 8.  Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
# >>Çözüm:
df = df[~df["Invoice"].str.contains("C", na=False)]
df[df["Invoice"].str.contains("C", na=False)] # bakalım gitmişler mi ;) hata verirse gitmişlerdir.
df.head()
# 9.  Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
# >>Çözüm:
df["TotalPrice"] = df["Quantity"] * df["Price"]

########################################################################################################################
# Görev 2:
########################################################################################################################
# RFM metriklerinin hesaplanması
# Recency, Frequency ve Monetary tanımlarını yapınız.
# ▪      Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız.
# ▪      Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
# ▪      Oluşturduğunuz metriklerin isimlerini  recency, frequency ve monetary olarak değiştiriniz.
# Not 1: recency değeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.
# Not 2: rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz.
########################################################################################################################
# >>Çözüm:

df["InvoiceDate"].max()                  # Timestamp('2011-12-09 12:50:00')   en son fatura işleminin tarihine bakıyoruz
                                         # Çünkü analizlerimizi yapacağımız tarihi belirleyeceğiz
today_date = dt.datetime(2011, 12, 11)   # Analizin yapıldığı tarihi belirliyoruz
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days, # recency
                                     'Invoice': lambda Invoice: Invoice.nunique(),                             # frequency
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})                       # monetary
rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']


########################################################################################################################
# Görev 3:
########################################################################################################################
# RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi
# ▪       Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
# ▪       Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
# ▪ Oluşan 2 farklı değişkenin değerini tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.
# Örneğin;
# Ayrı ayrı değişkenlerde sırasıyla 5, 2  olan recency_score, frequency_score skorlarını RFM_SCORE değişkeni
# isimlendirmesi ile oluşturunuz.
# DİKKAT! Monetary skoru dahil etmiyoruz.

# >>Çözüm:

rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"),5,labels=[1,2,3,4,5,])
rfm["monetary_score"] = pd.qcut(rfm["monetary"],5, labels=[1,2,3,4,5])
rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str)+rfm["frequency_score"].astype(str)) # Monetary i dikkate almadık
rfm[rfm["RFM_SCORE"]=="52"].head() # score değerlendirmemiz sadece recency ile frequency kapsadığı
rfm[rfm["RFM_SCORE"]=="25"].head() # için  koşul kısmına onların index ine göre değer verdik
rfm.head()

########################################################################################################################
# Görev 4:
########################################################################################################################
# RFM skorlarının segment olarak tanımlanması
# ▪      Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları yapınız.
# ▪      Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm["SEGMENT"] = rfm["RFM_SCORE"].replace(seg_map,regex=True)
rfm.head()


########################################################################################################################
# Görev 5:
########################################################################################################################
# Aksiyon Zamanı
# ▪     Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
# - Hem aksiyon kararları açısından,
# - Hem de segmentlerin yapısı açısından (ortalama RFM değerleri)
# yorumlayınız.
# ▪ "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
rfm[["SEGMENT", "recency", "frequency", "monetary"]].groupby("SEGMENT").agg(["mean", "count","max"])

rfm["SEGMENT"].value_counts().plot(kind='pie', rot=5, fontsize=6)
plt.show()
rfm["SEGMENT"].value_counts().plot(kind='barh', rot=5, fontsize=6)
plt.show()


#####<SEÇTİĞİM SEGMENTLER VE AKSİYON ÖNERİLERİ>#####


# <<< champions >>>  Şampiyonlaarrr. Onlar champions league müziğini sürekli dinlemek isteyen
# telefonlarında alarmlarını bile bu müziği ayarlayan haalaand gibiler.
# En iyi müşterilerimiz bu gruptalar.
# Son alışveriş tarihleri en yakın olan ve bizi en sık ziyaret eden gruptan oluşuyor.
# Bize ortalama olarak; 6857.96392 birim para kazandırmışlar
# Ziyaret etme sıklıkları 12.41706
# En son 6.36177 gün önce alışveriş yapmışlar.
rfm[rfm["SEGMENT"] == "champions"].head()
# << Aksiyon Önerileri >>
# << Kataloğumuza yeni ürünler eklediğimizde >> "selam yakışıklı/güzellik senin için yeni şeylerim var" diye mesaj atalım
# << belirli satın almaya ulaştıklarında son satın almalarına bizden bir indirim uyglayalım. >>
# << Bize yeni müşteri kazandırmaları durumunda onlara özel kampanyalar hazırlayabiliriz >>


# <<< loyal_customers >>> Bizim sadık arkadaşlarımız. Onlar En çok işlem yapan 2. gruptalar
# ama en bizim için en değerlilerden. Önemli bir durumda bizim hava yastığımız olabilirler.
# Yani güvenebiliriz belli alışkanlıkları var gibi görünüyor.
# Bize ortalama olarak; 2864.24779 birim para kazandırmışlar
# Ziyaret etme sıklıkları 6.47985
# En son 33.60806 gün önce alışveriş yapmışlar.
rfm[rfm["SEGMENT"] == "loyal_customers"].head()
# << Aksiyon Önerileri >>
# << En sık aldıkları ürünlerde onlara kısa süreli indirimler tanımlayabiliriz >>
# << Bize yeni müşteri kazandırmaları durumunda onlara özel kampanyalar hazırlayabiliriz >>


# <<< at risk >>> Woowo bu arkdaşlarla uzun zamandır görüşmemişiz dikkatlerini çekelim biraz
# Bize ortalama olarak; 1084.53530 birim para kazandırmışlar
# Ziyaret etme sıklıkları 2.87858
# En son 153.78583 gün önce alışveriş yapmışlar.
rfm[rfm["SEGMENT"] == "at_Risk"].head()
# << Aksiyon Önerileri >>
# << "Hey selam "NAME" bey/hanımefendi sizi çok özledik. size özel fırsatlarımıza göz atmak istermisiniz diye mail atalım. >>
# << Bize fena gelir getirmemişler. Kendimizi onlara hatırlatalım. Var olan kampanyalardan haberdar edebiliriz. >>


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
### LOYAL_CUSTOMERS ID LERİNİN XLSX OLARAK KAYIT EDİLMESİ
rfm[rfm["SEGMENT"] == "loyal_customers"].index
new_df = pd.DataFrame()
new_df["loyal_customers_id"] = rfm[rfm["SEGMENT"] == "loyal_customers"].index
new_df.to_excel("loyal_customers.xlsx")