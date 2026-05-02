import os
from flask import Flask, render_template, request, redirect, url_for, abort, session, flash
from models import db, Institusi, Peneliti, SuratKabar, Edisi

app = Flask(__name__)

# Konfigurasi Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'british_library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Kunci rahasia untuk mengamankan Session
app.secret_key = 'kunci_rahasia_british_library_super_aman'

db.init_app(app)
# ==========================================
# 1. HALAMAN UTAMA (TERKUNCI!)
# ==========================================
@app.route('/')
def home():
    # CEK KARTU PENGUNJUNG: Jika tidak ada session 'user_id', usir ke halaman login
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', nama_user=session['nama_depan'])

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
            
            # --- TAMBAHAN UNTUK INISIAL ---
            inisial = f"{user.nama_depan[0]}{user.nama_belakang[0]}".upper()
            session['inisial'] = inisial
            # PESAN LOGIN SUKSES
            flash('Login berhasil! Selamat datang di British Library.', 'success')

            return redirect(url_for('home'))
        else:
            # ---  KOTAK ERROR  ---
            flash('Login Gagal: Email atau Kata Sandi salah!', 'error')
            return redirect(url_for('login'))
            # -------------------------------------------------------
            
    return render_template('login.html')
# ==========================================
# RUTE LOGOUT
# ==========================================
@app.route('/logout')
def logout():
    # Hapus semua data dari Kartu Pengunjung (Session)
    session.pop('user_id', None)
    session.pop('nama_depan', None)
    session.pop('inisial', None)
    return redirect(url_for('login'))
# ==========================================
# 3. RUTE REGISTER (CREATE)
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
            return f"Terjadi kesalahan Database: {str(e)}", 500

    return render_template('register.html')

# ==========================================
# 4. RUTE DETAIL KOLEKSI
# ==========================================
@app.route('/detail')
def detail():
    # Tangkap kata kunci dan tahun dari form pencarian di Home (jika ada)
    kata_kunci = request.args.get('kata_kunci', '')
    tahun = request.args.get('tahun', '')
    
    # Gabungkan teksnya. Misal user isi "The Times" dan "1788", jadi "The Times 1788"
    query_pencarian = f"{kata_kunci} {tahun}".strip()
    
    # Kirim query tersebut ke halaman detail.html
    return render_template('detail.html', query=query_pencarian)

# ==========================================
# 5. RUTE TUGAS 11 (CRUD: READ, UPDATE, DELETE)
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
            peneliti.nama_depan = request.form.get('nama_depan')
            peneliti.nama_belakang = request.form.get('nama_belakang')
            db.session.commit() 
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
# EKSEKUSI SERVER & DATABASE SETUP
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Membuat 1 Institusi otomatis agar tidak error Foreign Key
        if not Institusi.query.first():
            inst_default = Institusi(nama_institusi="British Library", negara="UK")
            db.session.add(inst_default)
            db.session.commit()
            
    app.run(debug=True)