# Naudotų automobilių kainų prognozavimas - Reikalavimai v1.1

Data: 2026-10-20 | Autorius: Deividas Šapalas

## 1.1 Problemos aprašymas

Sukurti naudotų automobilių kainų prognozavimo modelį pagal transporto priemonės gamybos metus ir ridą.
Tikslas: MAE (vidutinė absoliutinė paklaida) <= 1500 EUR, R2 (determinacijos koeficientas) >= 0.75.

## 2. Funkciniai reikalavimai

| ID    | Reikalavimas                                                                                         | Prioritetas |
|-------|------------------------------------------------------------------------------------------------------|-------------|
| FR-01 | Sistema privalo automatiškai atsisiųsti raw duomenis iš viešai pasiekiamo šaltinio.                  | Must        |
| FR-02 | Skriptas privalo paruošti ir suskaidyti duomenis į train/test imtis pagal `params.yaml` proporcijas. | Must        |
| FR-03 | Modelis po apmokymo privalo automatiškai eksportuoti ir išsaugoti svorius į failą (`.pkl` formatu).  | Must        |

## 3. Nefunkciniai reikalavimai

| ID     | Kategorija | Reikalavimas           | KPI                    |
|--------|------------|------------------------|------------------------|
| NFR-01 | Našumas    | Modelio mokymo laikas  | CPU aplinkoje <= 10 s  |
| NFR-02 | Kokybė     | Kainos prognozė        | MAE <= 1500 EUR        |
| NFR-03 | Kokybė     | Modelio atitikimas     | R2 score >= 0.75       |

## 3.x Eksperimentų sekimo ir atkartojamumo NFR (v1.1)

| ID     | Kategorija       | Reikalavimas                                                    | KPI                                   |
|--------|------------------|-----------------------------------------------------------------|---------------------------------------|
| NFR-08 | Atkartojamumas   | Bet kuris istorinis run atkuriamas `dvc repro` arba per skriptą | <= 2 min (be duomenų atsisiuntimo), delta R2 <= 0.005 |
| NFR-09 | Atsekamumas      | Kiekvienas eksperimentas turi MLflow run ID, git commit ir duomenų md5 tag'us | 100 % run'ų |
| NFR-10 | Duomenų versija  | Mokymo duomenų versija fiksuota DVC (`dvc.lock` md5 = run'o `dvc_raw_md5`) | 100 % run'ų |

## 7. Keitimo istorija

| Versija | Data       | Autorius | Pakeitimai |
|---------|------------|----------|------------|
| 1.0     | 2026-10-15 | Studentas | Pradinis dokumentas (Automobilių kainų prognozavimo idėja) |
| 1.1     | 2026-10-20 | Studentas | Pridėtas MLflow + DVC pipeline bei atkartojamumo NFR (NFR-08–NFR-10) |
