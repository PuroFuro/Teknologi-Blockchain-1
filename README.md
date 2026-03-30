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

Node Registered

<img width="1446" height="916" alt="Screenshot 2026-03-29 164436" src="https://github.com/user-attachments/assets/4c24a0bd-dd72-4bf8-bd81-58ae5fba767c" />

---

Node Sudah saling terhubung satu sama lain

<img width="1453" height="952" alt="Screenshot 2026-03-29 164520" src="https://github.com/user-attachments/assets/38dfdf00-a0e2-467d-9cb0-0c97ef22f9f3" />
<img width="1448" height="895" alt="Screenshot 2026-03-29 164637" src="https://github.com/user-attachments/assets/575023c3-732c-4d0b-b8ed-563373f27b3c" />
<img width="1462" height="924" alt="Screenshot 2026-03-29 164706" src="https://github.com/user-attachments/assets/86da3919-03aa-4f58-87a4-826872701639" />

---

Mining Reward

<img width="527" height="210" alt="Screenshot 2026-03-29 165517" src="https://github.com/user-attachments/assets/8583dd16-f12b-4bcc-bc47-e7f690b0bf04" />

---

Node 1 Sudah terhubung ke Node 2 dan 3

<img width="1460" height="1028" alt="Screenshot 2026-03-29 172159" src="https://github.com/user-attachments/assets/b954a38f-bf83-46b7-8fd4-f2a74554968b" />

---

Node 2 Sudah Terhubung ke Node 1 dan 3

<img width="1460" height="1047" alt="Screenshot 2026-03-29 172514" src="https://github.com/user-attachments/assets/a181b5f8-cee5-4235-9c22-253c8b2a59d5" />

---

Node 3 Sudah Terhubung ke Node 1 dan 2

<img width="1458" height="1010" alt="Screenshot 2026-03-29 172647" src="https://github.com/user-attachments/assets/52232197-ea02-4ac6-8807-d40fe3a1e188" />

---

Hasil ```GET```

<img width="1458" height="956" alt="Screenshot 2026-03-29 172737" src="https://github.com/user-attachments/assets/8e71b6e1-63dc-481f-9b5d-5566be15fd78" />

---




