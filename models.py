from flask_sqlalchemy import SQLAlchemy

# Inisialisasi objek SQLAlchemy
db = SQLAlchemy()

# ==========================================
# TABEL INSTITUSI
# ==========================================
class Institusi(db.Model):
    __tablename__ = 'institusi'
    id_institusi = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_institusi = db.Column(db.String(100), nullable=False)
    negara = db.Column(db.String(50), nullable=False)
    
    # Relasi ke tabel Peneliti
    peneliti_rel = db.relationship('Peneliti', backref='institusi_asal', lazy=True)

# ==========================================
# TABEL PENELITI
# ==========================================
class Peneliti(db.Model):
    __tablename__ = 'peneliti'
    id_peneliti = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_depan = db.Column(db.String(50), nullable=False)
    nama_belakang = db.Column(db.String(50), nullable=False)
    
    # Kolom tambahan
    alamat_email = db.Column(db.String(100), unique=True, nullable=False)
    bidang_keahlian = db.Column(db.String(50), nullable=True)
    
    kata_sandi = db.Column(db.String(255), nullable=False)
    id_institusi = db.Column(db.Integer, db.ForeignKey('institusi.id_institusi'), nullable=False)

# ==========================================
# TABEL SURAT KABAR (Koleksi Arsip)
# ==========================================
class SuratKabar(db.Model):
    __tablename__ = 'surat_kabar'
    id_suratkabar = db.Column(db.Integer, primary_key=True)
    nama_suratkabar = db.Column(db.String(100), nullable=False)
    kota_terbit = db.Column(db.String(50))
    tahun_berdiri = db.Column(db.Integer)
    penerbit = db.Column(db.String(100))
    bahasa_utama = db.Column(db.String(50))
    # Kolom untuk menyimpan nama file PDF
    dokumen_digital = db.Column(db.String(255))

# ==========================================
# TABEL EDISI
# ==========================================
class Edisi(db.Model):
    __tablename__ = 'edisi'
    id_edisi = db.Column(db.Integer, primary_key=True)
    id_suratkabar = db.Column(db.Integer, db.ForeignKey('surat_kabar.id_suratkabar'))
    tanggal_terbit = db.Column(db.String(50))
    jumlah_halaman = db.Column(db.Integer)
    format_digital = db.Column(db.String(50))
    status_kelengkapan = db.Column(db.String(50))
    file_path = db.Column(db.String(255))
    
    # === TAMBAHKAN BARIS INI ===
    # Ini adalah "tali gaib" yang menghubungkan Edisi langsung ke Surat Kabar
    surat_kabar = db.relationship('SuratKabar', backref='daftar_edisi')