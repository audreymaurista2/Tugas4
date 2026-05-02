// base
function toggleMenu() {
    // Menambah atau menghapus class 'show' saat avatar diklik
    document.getElementById("menuRahasia").classList.toggle("show");
}

// Fitur tambahan: Menutup menu otomatis jika pengguna mengklik area lain di luar avatar
window.onclick = function (event) {
    if (!event.target.matches('.avatar-bulat')) {
        var dropdowns = document.getElementsByClassName("dropdown-logout");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

// detail
function filterTabel() {
    var input = document.getElementById("cariTabel");
    // Ubah huruf kecil semua dan pisahkan berdasarkan spasi (agar "The Times 1788" dicek per kata)
    var filterKata = input.value.toLowerCase().split(" ");
    var table = document.getElementById("tabelKoleksi");
    var tr = table.getElementsByTagName("tr");

    // Looping semua baris tabel (Mulai dari indeks 1 untuk melewati baris Header/Judul Tabel)
    for (var i = 1; i < tr.length; i++) {
        // Gabungkan seluruh teks di baris itu (Judul + Tahun + Kategori)
        var teksBaris = tr[i].textContent.toLowerCase();
        var cocok = true;

        // Cek apakah SETIAP kata kunci yang diketik ada di dalam baris ini
        for (var j = 0; j < filterKata.length; j++) {
            // Jika ada satu kata kunci saja yang tidak ditemukan, berarti baris ini tidak cocok
            if (teksBaris.indexOf(filterKata[j]) === -1) {
                cocok = false;
                break;
            }
        }

        // Tampilkan jika cocok, sembunyikan jika tidak
        if (cocok) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}
