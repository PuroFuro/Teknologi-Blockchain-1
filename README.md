# 🧱 Blockchain Simulation with Flask API

Proyek ini merupakan simulasi sederhana sistem **Blockchain** menggunakan Python dan Flask API.  
Sistem ini mendukung konsep dasar blockchain seperti **digital signature**, **multi-node network**, **mining reward**, dan **sinkronisasi blockchain**.

---

## 🚀 Fitur Utama

### 🔐 Digital Signature
Setiap transaksi ditandatangani menggunakan **private key** dan diverifikasi menggunakan **public key**.  
Hal ini memastikan:
- Keaslian transaksi
- Keamanan data
- Tidak bisa dipalsukan

---

### ⛏️ Mining Reward
Node yang melakukan proses mining akan mendapatkan reward sebesar:
```67```


Reward diberikan melalui transaksi khusus dari `SYSTEM`.

---

### 🌐 Multi Node (3 Node)
Sistem menggunakan 3 node yang berjalan secara terpisah:

| Node  | Port |
|------|------|
| Node1 | 5000 |
| Node2 | 5001 |
| Node3 | 5002 |

Setiap node saling terhubung (mesh network) dan dapat berkomunikasi satu sama lain.

---

### 🔗 Flask API + Postman
Seluruh sistem dijalankan menggunakan **Flask REST API** dan diuji menggunakan **Postman**.

---

## ⚙️ Instalasi

Install dependency:
```bash
pip install flask requests cryptography
```
### ▶️ Menjalankan Node
Jalankan 3 terminal berbeda:

```bash
python node.py -n Node1 -p 5000
python node.py -n Node2 -p 5001
python node.py -n Node3 -p 5002
```
### 🔗 Menghubungkan Node (Mesh Network)
Gunakan Postman atau curl:

Endpoint:
```bash
POST /register
```
Contoh Request:
```bash
{
  "node": "http://127.0.0.1:5001"
}
```
Lakukan untuk semua kombinasi node:

Node1 → Node2 & Node3
Node2 → Node1 & Node3
Node3 → Node1 & Node2

### 🔍 Mengecek Node
```bash
GET /nodes
```
### 💸 Mengirim Transaksi

Endpoint:
```bash
POST /transaction
```
Body:
```bash
{
  "sender": "PUBLIC_KEY",
  "receiver": "PUBLIC_KEY",
  "amount": 1,
  "signature": "SIGNATURE_HEX"
}
```
### ⛏️ Mining Block

Endpoint:
```bash
GET /mine
```
Fungsi:

- Mengambil transaksi dari mempool
- Menambahkan reward
- Membuat block baru

### 🔄 Sinkronisasi Blockchain

Endpoint:
```bash
GET /sync
```
Node akan:

- Membandingkan chain dengan node lain
- Mengambil chain terpanjang (longest chain)

### 👤 Cek Profil & Saldo

Endpoint:
```bash
👤 Cek Profil & Saldo
```
### 🧠 Cara Kerja Sistem

1. User membuat transaksi
2. Transaksi ditandatangani dengan private key
3. Node memverifikasi digital signature
4. Transaksi masuk ke mempool
5. Miner melakukan mining
6. Block ditambahkan ke blockchain
7. Node lain melakukan sinkronisasi

### Hasil Demo





