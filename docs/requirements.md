# Naudotų automobilių kainų prognozavimas - Reikalavimai v1.1

Data: 2026-10-20 | Autorius: Deividas Šapalas

## 1.1 Problemos aprašymas

Sukurti naudotų automobilių kainų prognozavimo modelį pagal transporto priemonės gamybos metus ir ridą.
Tikslas: MAE (vidutinė absoliutinė paklaida) <= 1800 EUR, R2 (determinacijos koeficientas) >= 0.75.

## 2. Funkciniai reikalavimai

| ID    | Reikalavimas                                                                                         | Prioritetas |
|-------|------------------------------------------------------------------------------------------------------|-------------|
| FR-01 | Sistema privalo generuoti deterministinį duomenų rinkinį pagal fiksuotą SEED.                        | Must        |
| FR-02 | Skriptas privalo paruošti ir suskaidyti duomenis į train/test imtis.                                 | Must        |
| FR-03 | Modelis po apmokymo privalo automatiškai eksportuoti ir išsaugoti svorius į failą (`.pkl` formatu).  | Must        |

## 3. Nefunkciniai reikalavimai

| ID     | Kategorija | Reikalavimas                                                         | KPI                    |
|--------|------------|----------------------------------------------------------------------|------------------------|
| NFR-01 | Našumas    | Modelio mokymas turi būti pakankamai greitas laboratoriniam darbui.  | CPU aplinkoje <= 10 s  |
| NFR-02 | Kokybė     | Modelio kainų prognozės paklaida turi neviršyti nustatytos ribos.    | MAE <= 1800 EUR        |
| NFR-03 | Kokybė     | Modelis turi pasiekti nustatytą determinacijos koeficientą.          | R² score >= 0.75       |

## 3.x Eksperimentų sekimo ir atkartojamumo NFR (v1.1)

| ID     | Kategorija       | Reikalavimas                                                    | KPI                                   |
|--------|------------------|-----------------------------------------------------------------|---------------------------------------|
| NFR-04 | Atkartojamumas   | Pipeline'o etapai turi būti valdomi DVC, o jų priklausomybės ir išvestys turi būti versijuojamos. | dvc repro sėkmingai įvykdomas; dvc.lock įtrauktas į Git. |
| NFR-05 | Atsekamumas      | Kiekvienas eksperimentas turi MLflow run ID   | 100 % run'ų |
| NFR-06 | Atsekamumas      | Kiekvienas mokymo run'as turi būti susietas su Git commit ir naudotų žaliavinių duomenų versija. | 100 % mokymo run'ų turi git_commit ir dvc_raw_md5 žymas. |

## 7. Keitimo istorija

| Versija | Data       | Autorius | Pakeitimai |
|---------|------------|----------|------------|
| 1.0     | 2026-10-15 | Deividas Šapalas | Pradinė naudotų automobilių kainų prognozavimo projekto versija. |
| 1.1     | 2026-10-20 | Deividas Šapalas | Patikslinti funkciniai reikalavimai, modelio kokybės KPI, DVC atkartojamumo, MLflow sekimo, duomenų versijavimo ir artefaktų patvarumo reikalavimai. |
