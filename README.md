# **🛡️ AwasLink Dashboard — Analisis Deteksi Pesan Phishing**

## **Deskripsi**
AwasLink Dashboard merupakan aplikasi interaktif berbasis Streamlit untuk menganalisis data pesan berbahasa Indonesia serta membangun model deteksi spam menggunakan pendekatan machine learning, mencakup distribusi data, kata dominan, karakteristik pesan, hingga perbandingan performa model.

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

**Jalankan Notebook**
```bash
Buka file `Capstone_Project_Data_Scientist.ipynb` menggunakan Jupyter Notebook atau Google Colab, kemudian jalankan seluruh cell secara berurutan.

Tahapan analisis dalam notebook meliputi:
- Eksplorasi data (distribusi kelas, kata dominan, fitur numerik)
- Feature engineering (TF-IDF + fitur manual)
- A/B Testing: Model A (TF-IDF) vs Model B (TF-IDF + fitur manual), dievaluasi dengan Recall dan Z-test proporsi (α = 0.05)
```

**Run streamlit app**
```bash
streamlit run dashboard-awaslink.py
```

## **Dashboard Online**
https://awaslink-dashboard.streamlit.app/
