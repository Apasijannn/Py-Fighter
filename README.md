# Py-Fighter 🥊

[![Project Status](https://img.shields.io/badge/Status-Development-orange.svg)](https://github.com/Apasijannn/Py-Fighter)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Library](https://img.shields.io/badge/Library-Pygame_2.6.1-green.svg)](https://www.pygame.org/)

**Py-Fighter** adalah sebuah permainan pertarungan (fighting game) 2D yang dibangun menggunakan bahasa pemrograman Python dan library Pygame. Proyek ini dirancang sebagai media katarsis interaktif untuk melatih refleks, koordinasi mata-tangan, dan strategi pengambilan keputusan cepat melalui lingkungan virtual yang terkontrol.

---

## 🌟 Latar Belakang & Manfaat
Di tengah ritme hidup yang cepat, Py-Fighter hadir untuk membantu pengguna melepaskan stres dan kejenuhan harian. Dengan menyalurkan emosi ke dalam pertarungan virtual, game ini membantu menjaga kesehatan mental sekaligus melatih kemampuan kognitif seperti pengenalan pola dan waktu reaksi.

## 🚀 Fitur Utama
* **Menu Utama:** Tampilan navigasi bagi user untuk mulai bermain atau keluar.
* **Selection System:** User dapat memilih karakter dan arena pertarungan yang diinginkan.
* **Battle Mode 2D:** Mode pertarungan intens antar dua pemain di satu komputer.
* **Mekanik Karakter:** Sistem yang mengatur sprite, pergerakan dasar (maju, mundur, lompat), animasi, serta variasi serangan dan bertahan.
* **Health Bar System:** Visualisasi HP karakter secara real-time yang berkurang sesuai serangan yang diterima.

## 🛠️ Lingkungan Pengembangan
* **Platform:** Python 3.12+ [cite: 58]
* **Library:** Pygame 2.6.1 [cite: 58]
* **IDE Disarankan:** VS Code + Python Extension

---

## 📐 Arsitektur Kode (OOP Design)
Proyek ini mengimplementasikan konsep Pemrograman Berorientasi Objek (OOP) dengan struktur sebagai berikut:

1.  **Main Class (`Game`):** Mengelola inti permainan (*game engine*), *game loop*, dan transisi antar *state*[cite: 69, 71].
2.  **UI Classes:** Menangani antarmuka pengguna seperti `Menu`, `CharacterSelect`, `ArenaSelect`, `HealthBar`, dan `VictoryScreen`.
3.  **Game Logic:**
    * `Fighter`: Mengatur atribut fisik (posisi, velocity), *hitbox*, animasi, dan aksi karakter[cite: 100, 101, 102].
    * `Battle`: Menangani logika pertarungan, deteksi serangan (*collision*), dan kondisi kemenangan[cite: 97, 98, 99].
    * `InputHandler`: Memproses input keyboard untuk kedua pemain secara simultan[cite: 103, 104, 105].



---

## 🕹️ Cara Menjalankan Project

1. **Clone repositori:**
   ```bash
   git clone [https://github.com/Apasijannn/Py-Fighter.git](https://github.com/Apasijannn/Py-Fighter.git)
   cd Py-Fighter
