# **🛡️ AwasLink Dashboard — Analisis Deteksi Pesan Phishing**

## **Deskripsi**
AwasLink Dashboard merupakan aplikasi interaktif berbasis Streamlit yang digunakan untuk mengeksplorasi dan menganalisis dataset pesan phishing berbahasa Indonesia. Dashboard menyajikan distribusi data, kata dominan, karakteristik pesan, serta hasil evaluasi model yang digunakan dalam pengembangan sistem deteksi phishing AwasLink.

## **Replikasi Analisis**
**Clone Repository**
```bash
git clone https://github.com/HanaTalitha03/AwasLink-Dashboard.git
cd AwasLink-Dashboard
```

**Setup Environment (venv)**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Jalankan Notebook

Buka file `Capstone_Project_Data_Scientist.ipynb` menggunakan Jupyter Notebook atau Google Colab, kemudian jalankan seluruh cell secara berurutan.

Tahapan analisis meliputi:
- Exploratory Data Analysis (EDA)
- Feature engineering
- Pembangunan dan evaluasi model
- A/B Testing Model A dan Model B

**Jalankan Dashboard**
```bash
streamlit run dashboard-awaslink.py
```

## **Dashboard Online**
https://awaslink-dashboard.streamlit.app/
