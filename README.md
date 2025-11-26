# Sistem Distribuit de Control Acces în Timp Real folosind ESP32, 3 RFID Readers și Protocol de Comunicație către PC

Acest proiect implementează un **sistem embedded distribuit**, construit în jurul unei plăci **ESP32**, care controlează **3 cititoare RFID** și acționează **3 uși independente** în timp real. Sistemul integrează o componentă externă — un **PC** — folosit pentru managementul centralizat al cardurilor, vizualizarea logurilor și controlul global al sistemului printr-un **protocol personalizat de comunicație**.

Proiectul utilizează **FreeRTOS**, multiple task-uri, cozi de mesaje, semafoare și periferice hardware integrate în microcontroller, respectând toate cerințele unui sistem embedded de timp real.

---

## Schema bloc a proiectului - In Progress...

--- 

## 1. Scopul Proiectului

Scopul proiectului este dezvoltarea unui **sistem distribuit de control acces** care:

* Interoghează **3 cititoare RFID** în timp real
* Decide local accesul și acționează **3 mecanisme de ușă** (servo/releu)
* Comunică evenimentele și starea către un **PC**, printr-un protocol custom
* Primește configurații și actualizări ale bazei de carduri de la PC
* Asigură **sincronizare corectă** între multiple procese concurente
* Rulează într-un mediu **RTOS** și gestionează latențe reduse

Acest sistem poate fi extins ușor pentru clădiri, birouri, camere securizate sau laboratoare tehnice.

---

## 2. Arhitectura Generală

### 2.1 Componentele Sistemului

* **ESP32 DevKit V1** – nodul principal (microcontrollerul)
* **3 × RFID Readers** (RC522 sau PN532)
* **3 × actuatoare de ușă** (servo-motoare SG90 sau relee)
* **Indicatori vizuali și acustici** (LED, buzzer)
* **PC/Laptop** – nod central pentru:

  * administrarea cardurilor
  * loguri de acces
  * configurare sistem
* **Protocol de comunicație** între ESP32 și PC (UART/TCP/BLE)

---

## 3. Arhitectura Software (FreeRTOS)

ESP32 rulează **5 task-uri principale**:

### 1. DoorTask1 (Real-Time)

* citire RFID #1
* validare rapidă card
* acționare ușă 1
* trimitere evenimente către CommTask

### 2. DoorTask2 (Real-Time)

* identic pentru ușa 2

### 3. DoorTask3 (Real-Time)

* identic pentru ușa 3

### 4. CommTask

* implementează protocolul custom cu PC-ul
* trimite evenimente (card detectat, acces, eroare)
* primește comenzi (adăugare card, ștergere card, mod securitate)
* gestionează cozi de mesaje și parsing TLV

### 5. ConfigTask (opțional)

* menține baza de date a cardurilor în RAM + NVS Flash
* accesează resursele prin mutex (concurență sigură)

---

## 4. Cerințe de Timp Real și Analiză

Sistemul îndeplinește cerințele de real-time prin:

* ciclu de citire RFID la **10–20 ms**
* acționare servo/releu în **< 50 ms**
* jitter redus datorită prioritizării RTOS

### Măsurători realizabile:

* toggling GPIO pentru timpi task
* timestamp-uri interne
* analiză pe PC

---

## 5. Demonstrație Practică

Demonstrația de laborator include:

* apropierea cardului de unul din cititoarele RFID
* reacție în timp real (LED + servomotor)
* trimiterea evenimentelor spre PC
* vizualizare log în timp real pe aplicația de pe PC
* modificarea permisiunilor din PC și propagarea către ESP32

---

## 6. Concluzie

Proiectul oferă un exemplu foarte clar și complet de:

* sistem embedded distribuit
* proiectare cu FreeRTOS
* protocoale custom
* interacțiune real-time cu un proces fizic
* gestionarea concurenței și sincronizării

Arhitectura este scalabilă, robustă și evidențiază capabilitățile ESP32 în aplicații embedded profesionale.

---

## Dezvoltări ulterioare

* Logare în cloud
* Web server pe ESP32
* Criptare mesajelor
* Suport pentru zeci de uși (scalabilitate)
* Înlocuire servo cu electromagnet industrial

---
