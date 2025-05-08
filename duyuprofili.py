import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_pdf import PdfPages
import base64
import datetime 

st.set_page_config(page_title="Duyu Profili Testi", layout="wide")
st.title("🧠 Duyu Profili Testi")
st.markdown("""
    <style>
       
        body {
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            color: #333333;
            background-color: #f7f7f7;
        }
        .card {
            background-color: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        button {
            background-color: #4CAF50;
            color: blue;
            border-radius: 8px;
            padding: 10px 20px;
        }
        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

       
        html {
            font-size: clamp(16px, 2vw, 20px);
        }
    </style>
""", unsafe_allow_html=True)


if 'test_completed' not in st.session_state:
    st.session_state.test_completed = False
if 'kategori_skorlar' not in st.session_state:
    st.session_state.kategori_skorlar = {
        "Duyusal Kaçınma": 0, "Duyusal Arayış": 0,
        "Düşük Kayıt": 0, "Duyusal Hassasiyet": 0
    }
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"ad_soyad": "", "cinsiyet": "Seçiniz", "dogum_tarihi": None}
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
questions =[
    {"section": "Tat/Koku", "text": "Bir mağazadayken keskin bir koku alırsam o ortamı terk ederim ya da başka bir bölüme geçerim (örneğin banyo ürünleri, mumlar, parfümler)."},
    {"section": "Tat/Koku", "text": "Yemeğime baharat eklerim."},
    {"section": "Tat/Koku", "text": "Başkalarının kokuyor dediği şeylerin kokusunu almam."},
    {"section": "Tat/Koku", "text": "Parfüm ya da kolonya kullanan insanlara yakın olmaktan hoşlanırım."},
    {"section": "Tat/Koku", "text": "Sadece alışkın olduğum yiyecekleri yerim."},
    {"section": "Tat/Koku", "text": "Çoğu yiyecekler bana lezzetsiz gelir.(diğer bir deyişle yavan, tatsız tuzsuz gelir). "},
    {"section": "Tat/Koku", "text": "Keskin tadı olan şekerleri sevmem.(örneğin acı/tarçınlı ya da ekşi şeker) ya da nane şekerlerini sevmem."},
    {"section": "Tat/Koku", "text": "Taze çiçekler gördüğüm zaman koklamak için yanlarına giderim. "},
    {"section": "Hareket", "text": "Yüksekten korkarım."},
    {"section": "Hareket", "text": "Hareket halinde olmanın verdiği histen hoşlanırım (örneğin dans etmek, koşmak)."},
    {"section": "Hareket", "text": "Asansör ve/veya yürüyen merdiven kullanmaktan çekinirim çünkü hareketlerinden rahatsız olurum. "},
    {"section": "Hareket", "text": "Bir şeylere takılırım ya da çarparım."},
    {"section": "Hareket", "text": "Arabada giderken oluşan hareketlilikten rahatsız olurum."},
    {"section": "Hareket", "text": "Fiziksel aktivitelere katılmayı tercih ederim (yürüme, yüzme, koşma vb). "},
    {"section": "Hareket", "text": "Merdivenleri emin olamam (örneğin takılırım, dengemi kaybederim ve/veya tırabzanlardan tutmaya ihtiyaç duyarım)."},
    {"section": "Hareket", "text": "Kolayca başım döner (örneğin eğildikten sonra, çok hızlı ayağa kalkınca). "},
    {"section": "Görsel", "text": "Parlak ışıklı ve renkli yerlere gitmekten hoşlanırım."},
    {"section": "Görsel", "text": "Evdeyken gün boyu perdeleri kapalı tutarım. "},
    {"section": "Görsel", "text": "Renkli kıyafetler giymeyi severim"},
    {"section": "Görsel", "text": "Tıkış tıkış bir çekmeceden ya da dağınık bir odadan bir şey bulmaya çalışırken sinirlerim bozulur."},
    {"section": "Görsel", "text": "Yeni bir yere gitmeye çalışırken cadde, bina ve odalara ait işaretleri gözden kaçırırım. "},
    {"section": "Görsel", "text": "Televizyonda ya da sinemada düzensiz ya da hızlı hareket eden görsel görüntülerden rahatsız olurum. "},
    {"section": "Görsel", "text": "Odaya biri girdiğinde fark etmem. "},
    {"section": "Görsel", "text": "Küçük mağazalarda alışveriş yapmayı tercih ederim çünkü büyük mağazalarda bunalırım. "},
    {"section": "Görsel", "text": "Etrafımda çok fazla hareket gördüğümde rahatsız olurum (örneğin kalabalık alışveriş merkezinde, törende, şenlikte)."},
    {"section": "Görsel", "text": "Çalışırken dikkatimi dağıtan şeyleri azaltırım (örneğin kapıyı ya da televizyonu kapatırım). "},
    {"section": "Dokunma", "text": "Sırtımın ovulmasından rahatsız olurum."},
    {"section": "Dokunma", "text": "Saçımın kesilmesi hissinden hoşlanırım. "},
    {"section": "Dokunma", "text": "Ellerimi kirletecek aktivitelerden kaçınırım ya da o esnada eldiven giyerim. "},
    {"section": "Dokunma", "text": "Biriyle konuşurken ona dokunurum (örneğin elimi omzuna koyarım ya da elini sıkarım). "},
    {"section": "Dokunma", "text": "Sabah uyandığımda ağzımda oluşan histen rahatsız olurum."},
    {"section": "Dokunma", "text": "Çıplak ayakla yürümekten hoşlanırım."},
    {"section": "Dokunma", "text": "Belli kumaş kıyafetleri giymekten rahatsız olurum (örneğin pamuklu, ipek, fitilli kadife, kıyafetlerdeki etiketler). "},
    {"section": "Dokunma", "text": "Belli yiyeceklerin dokusundan rahatsız olurum (örneğin şeftalinin yüzeyi, elma püresi, süzme peynir, topak topak fındık ezmesi)."},
    {"section": "Dokunma", "text": "Birileri bana çok yakınlaştığı zaman uzaklaşırım."},
    {"section": "Dokunma", "text": "Yüzüm ya da ellerim kirli olduğunda bunu fark etmem."},
    {"section": "Dokunma", "text": "Sıyrık yada morluklarım olur fakat nasıl olduğunu hatırlamam. "},
    {"section": "Dokunma", "text": "Sırada insanlara yakın durmaktan ya da başkasına yakın durmaktan kaçınırım çünkü başkalarına çok yakın olmaktan rahatsız olurum."},
    {"section": "Dokunma", "text": "Biri koluma yada sırtıma dokunduğunda fark etmem.."},
    {"section": "Aktivite", "text": "Aynı anda iki ya da daha fazla iş üzerinde çalışırım. "},
    {"section": "Aktivite", "text": "Sabah uyanmak diğer insanlardan daha fazla zamanımı alır. "},
    {"section": "Aktivite", "text": "Bir şeyleri yaparken anlık karar veririm (diğer bir deyişle daha önceden plan yapmam). "},
    {"section": "Aktivite", "text": "Yoğun hayat temposundan uzaklaşmak için vakit bulurum ve kendi başıma zaman geçiririm. "},
    {"section": "Aktivite", "text": "Bir iş ya da aktiviteyi yapmaya çalışırken diğerlerinden daha yavaş görünürüm. "},
    {"section": "Aktivite", "text": "Şakaları diğerleri kadar çabuk algılayamam."},
    {"section": "Aktivite", "text": "Kalabalıktan uzak dururum."},
    {"section": "Aktivite", "text": "Başkalarının karşısında performans sergileyeceğim aktiviteler yaparım (örneğin müzik, spor, oyunculuk, toplum önünde konuşmak, sınıfta soruları cevaplamak). "},
    {"section": "Aktivite", "text": "Uzun bir derste ya da bir toplantıda oturduğumda dikkatimi toplamakta zorlanırım. "},
    {"section": "Aktivite", "text": "Beklenmeyen şeylerin olabileceği durumlardan kaçınırım (bilinmeyen yerlere gitmek ya da bilmediğim insanlar arasında olmak). "},
    {"section": "İşitsel", "text": "Mırıldanırım, ıslık çalarım, şarkı söylerim ya da farklı sesler çıkarırım.  "},
    {"section": "İşitsel", "text": "Beklenmeyen ya da yüksek sesler duyduğumda hemen irkilirim (örneğin süpürge, köpek havlaması, telefon çalması). "},
    {"section": "İşitsel", "text": "İnsanlar hızlı konuştuğunda ya da aşina olmadığım konular hakkında konuştuğunda dediklerini takip etmekte zorlanırım. "},
    {"section": "İşitsel", "text": "Birileri televizyon izliyorsa odadan ayrılırım ya da onlardan televizyonu kapatmalarını isterim. "},
    {"section": "İşitsel", "text": "Etrafımda çok fazla ses olursa dikkatim dağılır. "},
    {"section": "İşitsel", "text": "İsmim söylendiğinde fark etmem."},
    {"section": "İşitsel", "text": "Gürültüleri bastırmak için bazı yöntemler kullanırım (örneğin kapıyı kapatırım, kulaklarımı kapatırım, kulak tıkacı kullanırım)."},
    {"section": "İşitsel", "text": "Gürültülü ortamlardan uzak dururum."},
    {"section": "İşitsel", "text": "Gürültülü etkinliklere katılmaktan hoşlanırım."},
    {"section": "İşitsel", "text": "İnsanlardan söylediklerini tekrar etmelerini istemem gerekir."},
    {"section": "İşitsel", "text": "Arka fondaki sesle çalışmakta zorlanırım (örneğin fan ve radyo)"},
]


kategori_haritasi = {
    
    0: "Duyusal Kaçınma", 1: "Duyusal Arayış", 2: "Düşük Kayıt", 3: "Duyusal Arayış",
    4: "Duyusal Kaçınma", 5: "Düşük Kayıt", 6: "Duyusal Hassasiyet", 7: "Duyusal Arayış",
    
    
    8: "Duyusal Hassasiyet", 9: "Duyusal Arayış", 10: "Duyusal Kaçınma", 11: "Düşük Kayıt",
    12: "Duyusal Hassasiyet", 13: "Duyusal Arayış", 14: "Düşük Kayıt", 15: "Duyusal Hassasiyet",
    
    
    16: "Duyusal Arayış", 17: "Duyusal Kaçınma", 18: "Duyusal Arayış", 19: "Duyusal Hassasiyet",
    20: "Düşük Kayıt", 21: "Duyusal Hassasiyet", 22: "Düşük Kayıt", 23: "Duyusal Kaçınma",
    24: "Duyusal Hassasiyet", 25: "Duyusal Kaçınma",
    
   
    26: "Duyusal Hassasiyet", 27: "Duyusal Arayış", 28: "Duyusal Kaçınma", 29: "Duyusal Arayış",
    30: "Duyusal Hassasiyet", 31: "Duyusal Arayış", 32: "Duyusal Hassasiyet", 33: "Duyusal Hassasiyet",
    34: "Duyusal Kaçınma", 35: "Düşük Kayıt", 36: "Düşük Kayıt", 37: "Duyusal Kaçınma",
    38: "Düşük Kayıt", 39: "Duyusal Arayış",
    
   
    40: "Düşük Kayıt", 41: "Duyusal Arayış", 42: "Duyusal Kaçınma", 43: "Düşük Kayıt",
    44: "Düşük Kayıt", 45: "Duyusal Kaçınma", 46: "Duyusal Arayış", 47: "Duyusal Hassasiyet",
    48: "Duyusal Kaçınma", 49: "Duyusal Arayış", 50: "Duyusal Hassasiyet", 51: "Düşük Kayıt",
    
    
    52: "Duyusal Kaçınma", 53: "Duyusal Hassasiyet", 54: "Düşük Kayıt", 55: "Duyusal Kaçınma",
    56: "Duyusal Kaçınma", 57: "Duyusal Arayış", 58: "Düşük Kayıt", 59: "Duyusal Hassasiyet"
}


def yorum_getir(kategori, puan):
    yorum_araliklari = {
        "Duyusal Kaçınma": [
            (15, 19, "Çoğu insandan çok daha az"),
            (20, 26, "Çoğu insandan az"),
            (27, 41, "Çoğu insana benzer"),
            (42, 49, "Çoğu insandan fazla"),
            (50, 75, "Çoğu insandan çok daha fazla")
        ],
        "Duyusal Arayış": [
            (15, 27, "Çoğu insandan çok daha az"),
            (28, 41, "Çoğu insandan az"),
            (42, 58, "Çoğu insana benzer"),
            (59, 65, "Çoğu insandan fazla"),
            (66, 75, "Çoğu insandan çok daha fazla")
        ],
        "Düşük Kayıt": [
            (15, 18, "Çoğu insandan çok daha az"),
            (19, 26, "Çoğu insandan az"),
            (27, 40, "Çoğu insana benzer"),
            (41, 51, "Çoğu insandan fazla"),
            (52, 75, "Çoğu insandan çok daha fazla")
        ],
        "Duyusal Hassasiyet": [
            (15, 19, "Çoğu insandan çok daha az"),
            (20, 25, "Çoğu insandan az"),
            (26, 40, "Çoğu insana benzer"),
            (41, 48, "Çoğu insandan fazla"),
            (49, 75, "Çoğu insandan çok daha fazla")
        ]
    }
    for minv, maxv, yorum in yorum_araliklari.get(kategori, []):
        if minv <= puan <= maxv:
            return yorum
    return "Belirsiz"


def start_test():
    st.session_state.test_started = True
    st.session_state.user_info["ad_soyad"] = ad_soyad
    st.session_state.user_info["cinsiyet"] = cinsiyet
    st.session_state.user_info["dogum_tarihi"] = dogum_tarihi
    st.session_state.responses = []
    st.session_state.test_completed = False
    st.session_state.kategori_skorlar = {
        "Duyusal Kaçınma": 0, "Duyusal Arayış": 0,
        "Düşük Kayıt": 0, "Duyusal Hassasiyet": 0,
    }


def complete_test():
    st.session_state.test_completed = True
    point_map = {
        "Neredeyse Hiç": 1,
        "Nadiren": 2,
        "Ara Sıra": 3,
        "Sıklıkla": 4,
        "Neredeyse Her Zaman": 5
    }
    for idx, cevap in enumerate(st.session_state.responses):
        kategori = kategori_haritasi.get(idx, "Bilinmiyor")
        puan = point_map.get(cevap, 0)
        if kategori in st.session_state.kategori_skorlar:
            st.session_state.kategori_skorlar[kategori] += puan





def pdf_olustur():
    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(st.session_state.kategori_skorlar.keys(), st.session_state.kategori_skorlar.values(), color='skyblue')
        ax.set_title("Duyusal Profil Skorları")
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig2, ax2 = plt.subplots(figsize=(8.27, 11.69))
        ax2.axis('off')
        metin = f"""
Duyu Profili Testi Sonuçları

Ad Soyad: {st.session_state.user_info['ad_soyad']}
Cinsiyet: {st.session_state.user_info['cinsiyet']}
Doğum Tarihi: {st.session_state.user_info['dogum_tarihi']}

Skorlar ve Yorumlar:
"""
        for k, v in st.session_state.kategori_skorlar.items():
            yorum = yorum_getir(k, v)
            metin += f"{k}: {v} puan – {yorum}\n"
        ax2.text(0.05, 0.95, metin, va='top', fontsize=12)
        plt.tight_layout()
        pdf.savefig(fig2)

    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="duyu_profili_sonuc.pdf">📄 PDF Sonucunu İndir</a>'


if not st.session_state.test_started:
    with st.form("user_info_form"):
        st.header("👤 Kişisel Bilgiler")
        col1, col2 = st.columns(2)
        with col1:
            ad_soyad = st.text_input("Ad Soyad")
            cinsiyet = st.selectbox("Cinsiyet", ["Seçiniz", "Erkek", "Kadın"])
        with col2:
            dogum_tarihi = st.date_input(
                "Doğum Tarihi",
                min_value=datetime.date(1950, 1, 1),
                max_value=datetime.date.today()
            )
        basla = st.form_submit_button("Teste Başla")
        if basla:
            if not ad_soyad or cinsiyet == "Seçiniz":
                st.warning("Lütfen tüm kişisel bilgileri doldurunuz.")
            else:
                start_test()
                st.rerun()


if st.session_state.test_started and not st.session_state.test_completed:
    st.header("📝 Test Soruları")
    current_section = None
    with st.form("test_form"):
        for idx, q in enumerate(questions):
            if current_section != q["section"]:
                current_section = q["section"]
                st.subheader(f"📋 {current_section} Bölümü")
            answer = st.radio(
                f"{idx+1}. {q['text']}",
                ["Neredeyse Hiç", "Nadiren", "Ara Sıra", "Sıklıkla", "Neredeyse Her Zaman"],
                key=f"q_{idx}"
            )
            if len(st.session_state.responses) <= idx:
                st.session_state.responses.append(answer)
            else:
                st.session_state.responses[idx] = answer
        submit = st.form_submit_button("Testi Bitir")
        if submit:
            complete_test()
            st.rerun()


if st.session_state.test_completed:
    st.header("📊 Sonuçlar")
    df = pd.DataFrame.from_dict(st.session_state.kategori_skorlar, orient='index', columns=['Puan'])
    col1, col2 = st.columns([3, 2])
    with col1:
        st.bar_chart(df)
    with col2:
        st.subheader("📋 Puan Detayları")
        for kategori, puan in st.session_state.kategori_skorlar.items():
            st.metric(label=kategori, value=puan)

    st.subheader("📄 Yorumlar")
    for kategori, puan in st.session_state.kategori_skorlar.items():
        yorum = yorum_getir(kategori, puan)
        st.info(f"**{kategori}**: {puan} puan – _{yorum}_")

    st.markdown(pdf_olustur(), unsafe_allow_html=True)

    if st.button("Yeni Test Başlat"):
        st.session_state.test_started = False
        st.session_state.test_completed = False
        st.rerun()
