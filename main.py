import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt

DB_NAME = "produk.db"

class ProdukDatabase:
    def __init__(self):
        self.koneksi = sqlite3.connect(DB_NAME)
        self.kursor = self.koneksi.cursor()
        self._buat_tabel()

    def _buat_tabel(self):
        self.kursor.execute('''
            CREATE TABLE IF NOT EXISTS produk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kategori TEXT NOT NULL,
                tahun INTEGER NOT NULL
            )
        ''')
        self.koneksi.commit()

    def tambah_produk(self, nama, kategori, tahun):
        self.kursor.execute("INSERT INTO produk (nama, kategori, tahun) VALUES (?, ?, ?)",
                            (nama, kategori, tahun))
        self.koneksi.commit()

    def ambil_semua(self, cari_nama=""):
        query = "SELECT * FROM produk WHERE nama LIKE ?"
        self.kursor.execute(query, (f"%{cari_nama}%",))
        return self.kursor.fetchall()

    def update_produk(self, id_produk, nama, kategori, tahun):
        self.kursor.execute("UPDATE produk SET nama=?, kategori=?, tahun=? WHERE id=?",
                            (nama, kategori, tahun, id_produk))
        self.koneksi.commit()

    def hapus_produk(self, id_produk):
        self.kursor.execute("DELETE FROM produk WHERE id=?", (id_produk,))
        self.koneksi.commit()

    def export_ke_csv(self, file_path="produk_export.csv"):
        data = self.ambil_semua()
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Nama", "Kategori", "Tahun"])
            writer.writerows(data)

class EditDialog(QDialog):
    def __init__(self, produk):
        super().__init__()
        self.setWindowTitle("Edit Produk")
        self.setFixedSize(280, 180)
        self.id_produk = produk[0]

        layout = QFormLayout()
        self.nama = QLineEdit(produk[1])
        self.kategori = QLineEdit(produk[2])
        self.tahun = QLineEdit(str(produk[3]))

        layout.addRow("Nama:", self.nama)
        layout.addRow("Kategori:", self.kategori)
        layout.addRow("Tahun:", self.tahun)

        tombol = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tombol.accepted.connect(self.accept)
        tombol.rejected.connect(self.reject)

        layout.addWidget(tombol)
        self.setLayout(layout)

    def ambil_data(self):
        return self.nama.text(), self.kategori.text(), self.tahun.text()

class ProdukUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Produk")
        self.setMinimumSize(800, 500)

        self.db = ProdukDatabase()
        self.setup_ui()
        self.muattabel()

    def setup_ui(self):
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.nama_input = QLineEdit()
        self.kategori_input = QLineEdit()
        self.tahun_input = QLineEdit()

        self.nama_input.setPlaceholderText("Nama Produk")
        self.kategori_input.setPlaceholderText("Kategori")
        self.tahun_input.setPlaceholderText("Tahun")

        input_layout.addWidget(self.nama_input)
        input_layout.addWidget(self.kategori_input)
        input_layout.addWidget(self.tahun_input)

        self.btn_tambah = QPushButton("Tambah")
        self.btn_tambah.clicked.connect(self.aksi_tambah)

        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Cari nama produk...")
        self.input_cari.textChanged.connect(self.muattabel)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Kategori", "Tahun"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.aksi_edit)

        aksi_layout = QHBoxLayout()
        self.btn_hapus = QPushButton("Hapus")
        self.btn_export = QPushButton("Export")
        self.btn_hapus.clicked.connect(self.aksi_hapus)
        self.btn_export.clicked.connect(self.aksi_export)

        aksi_layout.addWidget(self.btn_hapus)
        aksi_layout.addWidget(self.btn_export)

        footer = QLabel("Nama: Muhammad Ridho Fahru Rozy | NIM: F1D022076")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: gray; font-size: 10pt")

        layout.addLayout(input_layout)
        layout.addWidget(self.btn_tambah)
        layout.addWidget(self.input_cari)
        layout.addWidget(self.table)
        layout.addLayout(aksi_layout)
        layout.addWidget(footer)

        self.setLayout(layout)

    def muattabel(self):
        keyword = self.input_cari.text()
        data = self.db.ambil_semua(keyword)
        self.table.setRowCount(0)
        for row_data in data:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            for i, item in enumerate(row_data):
                self.table.setItem(row_index, i, QTableWidgetItem(str(item)))

    def aksi_tambah(self):
        nama = self.nama_input.text()
        kategori = self.kategori_input.text()
        tahun = self.tahun_input.text()

        if not (nama and kategori and tahun.isdigit()):
            QMessageBox.warning(self, "Input Salah", "Lengkapi semua kolom dengan benar.")
            return

        self.db.tambah_produk(nama, kategori, int(tahun))
        self.nama_input.clear()
        self.kategori_input.clear()
        self.tahun_input.clear()
        self.muattabel()

    def aksi_edit(self, baris, _):
        produk = [self.table.item(baris, i).text() for i in range(4)]
        produk[0] = int(produk[0])

        dialog = EditDialog(produk)
        if dialog.exec_():
            nama, kategori, tahun = dialog.ambil_data()
            if not (nama and kategori and tahun.isdigit()):
                QMessageBox.warning(self, "Input Salah", "Data tidak valid!")
                return
            self.db.update_produk(produk[0], nama, kategori, int(tahun))
            self.muattabel()

    def aksi_hapus(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Perhatian", "Pilih data yang akan dihapus.")
            return
        id_produk = int(self.table.item(row, 0).text())
        self.db.hapus_produk(id_produk)
        self.muattabel()

    def aksi_export(self):
        self.db.export_ke_csv()
        QMessageBox.information(self, "Sukses", "Data berhasil diekspor ke 'produk_export.csv'.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    jendela = ProdukUI()
    jendela.show()
    sys.exit(app.exec_())
