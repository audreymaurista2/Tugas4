from flask_sqlalchemy import SQLAlchemy

# Inisialisasi objek SQLAlchemy
db = SQLAlchemy()

class Institusi(db.Model):
    __tablename__ = 'institusi'
    id_institusi = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_institusi = db.Column(db.String(100), nullable=False)
    negara = db.Column(db.String(50), nullable=False)
    
    # Relasi ke tabel Peneliti
    peneliti_rel = db.relationship('Peneliti', backref='institusi_asal', lazy=True)

class Peneliti(db.Model):
    __tablename__ = 'peneliti'
    id_peneliti = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_depan = db.Column(db.String(50), nullable=False)
    nama_belakang = db.Column(db.String(50), nullable=False)
    
    # --- DUA BARIS INI YANG BARU DITAMBAHKAN ---
    alamat_email = db.Column(db.String(100), nullable=True)
    bidang_keahlian = db.Column(db.String(50), nullable=True)
    # ------------------------------------------
    
    kata_sandi = db.Column(db.String(255), nullable=False)
    id_institusi = db.Column(db.Integer, db.ForeignKey('institusi.id_institusi'), nullable=False)
class SuratKabar(db.Model):
    __tablename__ = 'surat_kabar'
    id_suratkabar = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_suratkabar = db.Column(db.String(150), nullable=False)
    penerbit = db.Column(db.String(100), nullable=False)
    
    # Relasi ke tabel Edisi
    edisi_rel = db.relationship('Edisi', backref='surat_kabar_induk', lazy=True)

class Edisi(db.Model):
    __tablename__ = 'edisi'
    id_edisi = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tanggal_terbit = db.Column(db.Date, nullable=False)
    kota_terbit = db.Column(db.String(50), nullable=False)
    
    # db.Text untuk menampung data digitalisasi masif sesuai studi kasus British Library
    konten_teks_digital = db.Column(db.Text, nullable=False) 
    
    # Foreign Key ke tabel Surat Kabar
    id_suratkabar = db.Column(db.Integer, db.ForeignKey('surat_kabar.id_suratkabar'), nullable=False)