import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Institusi, Peneliti, SuratKabar, Edisi

app = Flask(__name__)

# ==========================================
# KONFIGURASI APLIKASI & DATABASE
# ==========================================
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'british_library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Kunci rahasia untuk mengamankan Session
app.secret_key = 'kunci_rahasia_british_library_super_aman'

# --- PERBAIKAN 1: PENGATURAN FOLDER UPLOAD ---
# Ini wajib ditaruh di sini agar sistem tahu ke mana PDF harus disimpan
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'pdf')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Perintah agar Python otomatis membuat foldernya kalau belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

# ==========================================
# 1. HALAMAN UTAMA (DIBUKA UNTUK PUBLIK)
# ==========================================
@app.route('/')
def home():
    # Menghitung jumlah data langsung dari database
    total_koran = SuratKabar.query.count()
    total_edisi = Edisi.query.count()
    total_peneliti = Peneliti.query.count()
    
    nama = session.get('nama_depan', 'Pengunjung')
    
    # Kirim variabel jumlah ke template index.html
    return render_template('index.html', 
                           nama_user=nama, 
                           total_sk=total_koran, 
                           total_ea=total_edisi, 
                           total_p=total_peneliti)
# ==========================================
# 2. RUTE LOGIN & LOGOUT
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('alamat_email')
        password = request.form.get('kata_sandi')
        
        user = Peneliti.query.filter_by(alamat_email=email, kata_sandi=password).first()
        
        if user:
            session['user_id'] = user.id_peneliti
            session['nama_depan'] = user.nama_depan

            # JALUR VIP ADMIN
            if email == 'adminbritishlibrary@gmail.com':  
                session['role'] = 'admin'
            else:
                session['role'] = 'peneliti'

            inisial = f"{user.nama_depan[0]}{user.nama_belakang[0]}".upper()
            session['inisial'] = inisial
            
            flash('Login berhasil! Selamat datang di British Library.', 'success')
            return redirect(url_for('home'))

        else:
            flash('Login Gagal: Email atau Kata Sandi salah!', 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Cara lebih bersih untuk menghapus semua session
    return redirect(url_for('login'))

# ==========================================
# 3. RUTE REGISTER (CREATE PENELITI)
# ==========================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            nama_depan = request.form.get('nama_depan')
            nama_belakang = request.form.get('nama_belakang')
            alamat_email = request.form.get('alamat_email')
            bidang_keahlian = request.form.get('bidang_keahlian')
            kata_sandi = request.form.get('kata_sandi')
            
            if not nama_depan or not nama_belakang or not alamat_email or not kata_sandi:
                return "Error 400: Semua kolom wajib diisi!", 400

            peneliti_baru = Peneliti(
                nama_depan=nama_depan,
                nama_belakang=nama_belakang,
                alamat_email=alamat_email,
                bidang_keahlian=bidang_keahlian,
                kata_sandi=kata_sandi,
                id_institusi=1 
            )
            db.session.add(peneliti_baru)
            db.session.commit()
            
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Pendaftaran Gagal: Email tersebut sudah terdaftar!', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

# ==========================================
# 4. HALAMAN DAFTAR SURAT KABAR & EDISI
# ==========================================
@app.route('/surat_kabar')
def surat_kabar():
    semua_koran = SuratKabar.query.all()
    return render_template('surat_kabar.html', data_koran=semua_koran)

@app.route('/edisi_arsip')
def edisi_arsip():
    semua_edisi = Edisi.query.all()
    return render_template('edisi_arsip.html', data_edisi=semua_edisi)

# ==========================================
# 5. CRUD PENELITI (TUGAS 11)
# ==========================================
@app.route('/peneliti')
def read_data():
    semua_peneliti = Peneliti.query.all()
    return render_template('read.html', data=semua_peneliti)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    peneliti = Peneliti.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # --- PERBAIKAN 2: UPDATE SEMUA FIELD ---
            peneliti.nama_depan = request.form.get('nama_depan')
            peneliti.nama_belakang = request.form.get('nama_belakang')
            peneliti.alamat_email = request.form.get('alamat_email')
            peneliti.bidang_keahlian = request.form.get('bidang_keahlian')
            db.session.commit() 
            flash('Data peneliti berhasil diupdate!', 'success')
            return redirect(url_for('read_data'))
        except Exception as e:
            db.session.rollback()
            return "Update Gagal", 500

    return render_template('update.html', p=peneliti)

@app.route('/delete/<int:id>')
def delete(id):
    peneliti = Peneliti.query.get_or_404(id)
    try:
        db.session.delete(peneliti)
        db.session.commit()
        return redirect(url_for('read_data'))
    except Exception as e:
        db.session.rollback()
        return "Delete Gagal", 500

# ==========================================
# 6. CRUD SURAT KABAR (Koleksi Arsip) KHUSUS ADMIN
# ==========================================
@app.route('/tambah_koleksi', methods=['GET', 'POST'])
def tambah_koleksi():
    # Validasi Admin
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        nama = request.form.get('nama_suratkabar')
        kota = request.form.get('kota_terbit')
        tahun = request.form.get('tahun_berdiri')
        penerbit = request.form.get('penerbit')
        bahasa = request.form.get('bahasa_utama')

        file = request.files.get('file_pdf')
        nama_file_pdf = None 
        
        if file and file.filename != '':
            nama_file_pdf = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nama_file_pdf))
        
        koleksi_baru = SuratKabar(
            nama_suratkabar=nama,
            kota_terbit=kota,
            tahun_berdiri=tahun,
            penerbit=penerbit,
            bahasa_utama=bahasa,
            dokumen_digital=nama_file_pdf 
        )
        
        db.session.add(koleksi_baru)
        db.session.commit() 
        
        flash('Koleksi surat kabar dan PDF berhasil ditambahkan!', 'success')
        return redirect(url_for('surat_kabar'))

    return render_template('tambah_koleksi.html')

@app.route('/edit_koleksi/<int:id>', methods=['GET', 'POST'])
def edit_koleksi(id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    koran = SuratKabar.query.get_or_404(id)
    
    if request.method == 'POST':
        koran.nama_suratkabar = request.form['nama_suratkabar']
        koran.penerbit = request.form['penerbit']
        db.session.commit()
        # --- PERBAIKAN 3: KEMBALI KE surat_kabar, bukan kelola_koleksi ---
        return redirect(url_for('surat_kabar'))
        
    return render_template('edit_koleksi.html', k=koran)

@app.route('/hapus_koleksi/<int:id>')
def hapus_koleksi(id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    koran = SuratKabar.query.get_or_404(id)
    db.session.delete(koran)
    db.session.commit()
    # --- PERBAIKAN 4: KEMBALI KE surat_kabar, bukan kelola_koleksi ---
    return redirect(url_for('surat_kabar'))

@app.route('/tambah_edisi', methods=['GET', 'POST'])
def tambah_edisi():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    # Ambil daftar koran untuk dropdown di form
    daftar_koran = SuratKabar.query.all()

    if request.method == 'POST':
        file = request.files.get('file_pdf')
        nama_file_pdf = None
        
        if file and file.filename != '':
            nama_file_pdf = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nama_file_pdf))
        
        edisi_baru = Edisi(
            id_suratkabar=request.form.get('id_suratkabar'),
            tanggal_terbit=request.form.get('tanggal_terbit'),
            jumlah_halaman=request.form.get('jumlah_halaman'),
            format_digital=request.form.get('format_digital'),
            status_kelengkapan=request.form.get('status_kelengkapan'),
            file_path=nama_file_pdf 
        
        )
        db.session.add(edisi_baru)
        db.session.commit()
        flash('Edisi arsip berhasil diunggah!', 'success')
        return redirect(url_for('edisi_arsip'))

    return render_template('tambah_edisi.html', koran=daftar_koran)

@app.route('/hapus_edisi/<int:id>')
def hapus_edisi(id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    edisi = Edisi.query.get_or_404(id)
    try:
        db.session.delete(edisi)
        db.session.commit()
        flash('Edisi berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Gagal menghapus data.', 'error')
        
    return redirect(url_for('edisi_arsip'))
# ==========================================
# EKSEKUSI SERVER & DATABASE SETUP
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Institusi.query.first():
            inst_default = Institusi(nama_institusi="British Library", negara="UK")
            db.session.add(inst_default)
            db.session.commit()
            
    app.run(debug=True)

    