# U2 – Modelio mokymas su MLflow ir hostingas klasteryje

## 1. Projekto architektūra

Projekte sukurta naudotų automobilių kainų prognozavimo MLOps sistema, apimanti duomenų paruošimą, modelio mokymą, eksperimentų sekimą, modelio registravimą ir inferencijos API veikimą Kubernetes klasteryje.

Pagrindinis procesas:

1. **Duomenys:** žali duomenys versijuojami naudojant DVC. `src/prepare_data.py` paruošia mokymo ir testavimo rinkinius.
2. **Mokymas:** Kubernetes Job vykdo `src/hpo.py`. Hiperparametrų paieškai naudojama Optuna, o mokymas vyksta CPU aplinkoje.
3. **Eksperimentų sekimas:** MLflow saugo parametrus, metrikas, sistemos metrikas, duomenų rinkinio informaciją ir modelio aplinką. Eksperimentai susiejami su Git commit ir DVC duomenų versija.
4. **Modelio registravimas:** geriausias modelis registruojamas MLflow Model Registry kaip `car-price-model` ir pažymimas `champion` alias.
5. **Inferencija:** FastAPI servisas Kubernetes klasteryje naudoja modelį pagal `models:/car-price-model@champion` URI. API pateikia `/health` ir `/predict` galinius taškus.

Mokymo Job konfigūracija perduodama per Kubernetes ConfigMap, o modelio mokymo ir inferencijos aplinkos naudoja tą patį U1 MLflow serverį.

## 2. CI/CD procesas

**CI:** GitHub Actions workflow atlieka Python kodo lint patikrą su Ruff, vykdo vienetinius testus ir sukuria bei publikuoja API Docker vaizdą į GHCR.

**CD:** po sėkmingo CI paleidimo Windows self-hosted runner vykdo šiuos veiksmus:

1. Atsisiunčia duomenis iš DVC saugyklos.
2. Paruošia mokymo duomenis ir sukuria mokymo Docker vaizdą.
3. Įkelia vaizdą į Minikube ir paleidžia Kubernetes mokymo Job.
4. Iš Job žurnalų ištraukia `metrics.json` metrikas.
5. Vykdo modelio kokybės vartus: MAE ≤ 2000 ir R² ≥ 0.90.
6. Tik sėkmingai praėjus kokybės vartus, publikuoja CI sukurtam API vaizdui skirtą `release` žymą ir atnaujina Kubernetes Deployment.
7. Patikrina API Deployment būseną. Nepavykus naujam diegimui, numatytas ankstesnės versijos atkūrimas naudojant `kubectl rollout undo`.

Kokybės vartų patikra vykdoma naudojant `scripts/check_model_gate.py`. Jei metrikos neatitinka nustatytų ribų, CD procesas sustabdomas prieš API diegimą.

**CI/CD patikros būsena:** workflow failai paruošti, tačiau GitHub Actions vykdymus šiuo metu blokuoja GitHub paskyros atsiskaitymo problema. Todėl sėkmingas CI/CD paleidimas, nesėkmingo modelio scenarijus ir automatinio rollback demonstracija dar nėra patvirtinti GitHub Actions vykdymo įrodymais.

## 3. Modelio ir inferencijos matavimai

### 3.1. Inferencijos API našumas

Atliktas apkrovos testas su 100 nuoseklių užklausų, naudojant `load-test.ps1` ir `kubectl port-forward`.

| Rodiklis | Išmatuota reikšmė |
|---|---:|
| Užklausų skaičius | 100 |
| P95 atsako laikas | 20.08 ms |
| Vidutinis atsako laikas | 8.92 ms |
| Pralaidumas | 107.51 užklausos/s |

Testas vykdytas siunčiant po vieną užklausą vienu metu. Todėl rezultatai apibūdina vieno kliento lokalią testavimo aplinką, o ne lygiagrečią produkcinę apkrovą. Išsamesni rezultatai pateikiami `docs/load-test-results.md`.

### 3.2. Modelio artefaktai

MLflow Model Registry patikrinta registruoto `car-price-model` modelio `champion` versija 1. Jos artefaktai sėkmingai pasiekiami.

| Rodiklis | Reikšmė |
|---|---:|
| Artefaktų failų skaičius | 8 |
| Bendras artefaktų dydis | 9640 baitų (9.41 KiB) |
| Pagrindinio modelio failo `model.skops` dydis | 7702 baitai (7.52 KiB) |

Bendras dydis apima modelio failą ir papildomus MLflow aplinkos bei modelio aprašo failus, o ne Docker konteinerio dydį.

## 4. Išvados

Sukurta pagrindinė MLOps sistemos dalis: duomenų paruošimas su DVC, hiperparametrų paieška su Optuna, eksperimentų sekimas MLflow, modelio registravimas su `champion` alias, mokymo Job Kubernetes klasteryje ir inferencijos API.

Pagal atliktus patikrinimus API veikia Kubernetes klasteryje, o inferencijos servisas naudoja registruotą modelį pagal `champion` alias. Atlikti inferencijos našumo ir modelio artefaktų dydžio matavimai.

CI/CD automatizavimo grandinė paruošta, tačiau galutiniam jos patvirtinimui dar reikia sėkmingo GitHub Actions paleidimo, kokybės vartų nesėkmingo scenarijaus ir rollback demonstracijos.