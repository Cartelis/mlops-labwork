# Naudotų automobilių kainų prognozavimas - Reikalavimai v1.6

Data: 2026-11-18 | Autorius: Deividas Šapalas

## 1.1 Problemos aprašymas

Sukurti naudotų automobilių kainų prognozavimo modelį pagal transporto priemonės gamybos metus ir ridą.
Tikslas: MAE (vidutinė absoliutinė paklaida) <= 1800 EUR, R2 (determinacijos koeficientas) >= 0.75.

## 2. Funkciniai reikalavimai

| ID    | Reikalavimas                                                                                                 | Prioritetas |
| ----- | ------------------------------------------------------------------------------------------------------------ | ----------- |
| FR-01 | Sistema privalo generuoti deterministinį duomenų rinkinį pagal fiksuotą SEED.                                | Must        |
| FR-02 | Duomenų paruošimo skriptas privalo paruošti duomenis ir suskaidyti juos į mokymo bei testavimo imtis.        | Must        |
| FR-03 | Modelis po apmokymo privalo išsaugoti savo artefaktus, kad juos būtų galima panaudoti vėlesnei inferencijai. | Must        |
| FR-04 | Sistema privalo registruoti mokymo eksperimentus MLflow sistemoje.                                           | Must        |
| FR-05 | Modelio hiperparametrų paieška privalo būti vykdoma naudojant Optuna.                                        | Must        |
| FR-06 | Geriausias modelis privalo būti registruojamas MLflow Model Registry ir pažymimas `champion` alias.          | Must        |
| FR-07 | Inferencijos servisas privalo naudoti registruotą modelį pagal `models:/car-price-model@champion` URI.       | Must        |
| FR-08 | Modelio diegimas į Kubernetes turi būti vykdomas tik sėkmingai praėjus kokybės vartus.                       | Must        |
| FR-09 | Sistema privalo pateikti sveikatos patikros (`/health`) ir prognozavimo (`/predict`) API galinius taškus.    | Must        |

## 3. Nefunkciniai reikalavimai

### 3.1. Modelio kokybė

| ID     | Kategorija | Reikalavimas                                                         | KPI                    |
|--------|------------|----------------------------------------------------------------------|------------------------|
| NFR-01 | Našumas    | Modelio mokymas turi būti pakankamai greitas laboratoriniam darbui.  | CPU aplinkoje <= 10 s  |
| NFR-02 | Kokybė     | Modelio kainų prognozės paklaida turi neviršyti nustatytos ribos.    | MAE <= 1800 EUR        |
| NFR-03 | Kokybė     | Modelis turi pasiekti nustatytą determinacijos koeficientą.          | R² score >= 0.75       |

## 3.2 Eksperimentų sekimo ir atkartojamumo NFR (v1.1)

| ID     | Kategorija       | Reikalavimas                                                    | KPI                                   |
|--------|------------------|-----------------------------------------------------------------|---------------------------------------|
| NFR-04 | Atkartojamumas   | Pipeline'o etapai turi būti valdomi DVC, o jų priklausomybės ir išvestys turi būti versijuojamos. | dvc repro sėkmingai įvykdomas; dvc.lock įtrauktas į Git. |
| NFR-05 | Atsekamumas      | Kiekvienas eksperimentas turi MLflow run ID   | 100 % run'ų |
| NFR-06 | Atsekamumas      | Kiekvienas mokymo run'as turi būti susietas su Git commit ir naudotų žaliavinių duomenų versija. | 100 % mokymo run'ų turi git_commit ir dvc_raw_md5 žymas. |

### 3.3. Modelio diegimo kokybės kontrolė

| ID     | Reikalavimas | Patikra |
| ------ | ------------ | ------- |
| NFR-07 | Modelis gali būti diegiamas į Kubernetes tik tada, kai jo MAE neviršija 2000. | CD proceso metu vykdomas automatinis MAE kokybės vartų patikrinimas. |
| NFR-08 | Modelis gali būti diegiamas į Kubernetes tik tada, kai jo R² yra ne mažesnis nei 0.90. | CD proceso metu vykdomas automatinis R² kokybės vartų patikrinimas. |
| NFR-09 | Nepraėjus bent vienam modelio kokybės vartų patikrinimui, naujo modelio diegimas turi būti sustabdytas. | CD procesas nutraukiamas, jei `check_model_gate.py` grąžina klaidos kodą. |
| NFR-10 | Nepavykus naujos API versijos diegimui, sistema turi grįžti prie ankstesnės veikiančios versijos. | Nepavykus Kubernetes diegimui, vykdomas `kubectl rollout undo`. |

### 3.4. Inferencijos API našumas

| ID     | Reikalavimas | Patikra |
| ------ | ------------ | ------- |
| NFR-11 | Inferencijos API 95-ojo procentilio (P95) atsako laikas turi būti ne didesnis kaip 100 ms. | Atlikus 100 užklausų išmatuotas P95 atsako laikas – 20.08 ms. |
| NFR-12 | Vidutinis inferencijos API atsako laikas turi būti ne didesnis kaip 50 ms. | Atlikus 100 užklausų išmatuotas vidutinis atsako laikas – 8.92 ms. |
| NFR-13 | Inferencijos API pralaidumas turi būti ne mažesnis nei 100 užklausų per sekundę. | Atlikus 100 užklausų išmatuotas pralaidumas – 107.51 užklausos per sekundę. |

Našumo matavimai atlikti naudojant `load-test.ps1`, siunčiant 100 nuoseklių užklausų per `kubectl port-forward`. Vienu metu buvo vykdoma viena užklausa, todėl rezultatai apibūdina vieno kliento lokalią testavimo aplinką, o ne lygiagrečią ar produkcinę apkrovą. Išsamūs rezultatai pateikiami `docs/load-test-results.md`.

### 3.5. Modelio artefaktų saugojimas

| ID     | Reikalavimas | Patikra |
| ------ | ------------ | ------- |
| NFR-14 | Registruoto modelio artefaktai turi būti išsaugoti MLflow sistemoje ir prieinami vėlesnei inferencijai. | MLflow Model Registry modelio `car-price-model`, `champion` versijos artefaktai sėkmingai pasiekiami. |
| NFR-15 | Modelio artefaktų dydis turi būti pagrįstas naudojamam modeliui ir neturi apimti nereikalingų failų. | Patikrinti 8 artefaktų failai, kurių bendras dydis – 9640 baitų (9.41 KiB); pagrindinio modelio failo `model.skops` dydis – 7702 baitai (7.52 KiB). |

Artefaktų dydis patikrintas atsisiuntus registruoto `car-price-model` modelio `champion` versijos artefaktus iš MLflow Model Registry. Šis dydis apima modelio failą ir papildomus aplinkos bei modelio aprašo failus; tai nėra Docker konteinerio dydis.

## 7. Keitimo istorija

| Versija | Data       | Autorius | Pakeitimai |
|---------|------------|----------|------------|
| 1.0     | 2026-10-15 | Deividas Šapalas | Pradinė naudotų automobilių kainų prognozavimo projekto versija. |
| 1.1     | 2026-10-20 | Deividas Šapalas | Patikslinti funkciniai reikalavimai, modelio kokybės KPI, DVC atkartojamumo, MLflow sekimo, duomenų versijavimo ir artefaktų patvarumo reikalavimai. |
| 1.2     | 2026-11-11 | Deividas Šapalas | MLflow metrikos, aplinka, hiperparametrų paieška su Optuna. |
| 1.3     | 2026-11-11 | Deividas Šapalas | Modelis registre ir turi alias @champion. |
| 1.4     | 2026-11-11 | Deividas Šapalas | Mokymo Job klasteryje, inferencijos API ir apkrovos testas. |
| 1.5     | 2026-11-18 | Deividas Šapalas | CI/CD su kokybės vartu ir rollback |
| 1.6     | 2026-11-18 | Deividas Šapalas | Sukurti/papildyti reikalavimų ir užduoties raporto dokumentai. |
