#  Componente principale

- **ESP32** (microcontroler Wi-Fi)  
- **RFID reader** (ex. MFRC522 sau PN532)  
- **Tag-uri RFID** (ex. Mifare Classic, NTAG213)  
- **LED + buzzer** pentru feedback  
  -  verde = acces permis  
  -  roșu = acces respins  
- **Server simplu** (Node.js / Python Flask)  
- **Bază de date** (SQLite sau MySQL)

---

<img width="942" height="509" alt="image" src="https://github.com/user-attachments/assets/43b7bb7a-62f3-4655-ae1c-712521f95e65" />

---


#  Funcționalități

## 1️ Citirea tag-ului RFID
ESP32 citește UID-ul unui tag și îl trimite la server (prin HTTP/HTTPS).



## 2️ Verificarea accesului
Serverul caută UID-ul în baza de date:
- Dacă `enabled = true`, trimite răspuns **„Acces Permis”** 
- Dacă `enabled = false` sau lipsă → **„Acces Respins”**   



## 3️ Criptarea datelor
- Datele introduse (nume, UID, status) sunt **criptate** în baza de date.  
- Folosesc **AES-256-GCM** (cheie fixă pentru demo).



## 4️ Interfață de administrare (simplă)
- Formular web: adaugă / șterge utilizatori.  
- Activează / dezactivează carduri.



## 5️ Feedback vizual / audio
-  LED verde + beep = **Acces permis**  
-  LED roșu = **Acces refuzat**
