# U1 Užduoties Ataskaita - Naudotų automobilių kainų prognozavimas

**Autorius:** Deividas Šapalas  
**Data:** 2026-10-21

---

## 1. Kas buvo padaryta
* **U1-R1 & U1-R2:** Paruošta kodo struktūra pagal kurso reikalavimus. Sukurtas `src/bootstrap.py` skriptas autonominiam sintetinių duomenų generavimui ir `Ridge` regresijos modelio mokymui CPU aplinkoje. Sukonstruotas veikiantis 3 etapų DVC konvejeris (`prepare` -> `train` -> `evaluate`) su lokalia `.dvc_storage` duomenų saugykla, paslėpta po `.gitignore`.
* **U1-R3:** Sukurtas optimizuotas `docker/Dockerfile.prepare` mokymo įvaizdis (naudojant multi-stage build). Vaizdas sėkmingai nuskenuotas su `Trivy` (0 CRITICAL spragų) ir publikuotas į GHCR su unikaliu Git commit tag'u. Konteineris veikia saugiai iš po ne-root vartotojo (`uid=1000`).
* **U1-R4:** Lokaliame `Minikube` klasteryje sukurtas izoliuotas `mlops-labwork` namespace, jame pakeltas MLflow v3 Tracking serveris, PostgreSQL duomenų bazė metrikų saugojimui bei PVC diskas ilgalaikiam duomenų išlikimui.

## 2. Kas neveikė / Techniniai iššūkiai ir jų sprendimai
* **MLflow v3 saugumo middleware klaidos:** Naudojant naujausią `mlflow:v3.17.2-full` atvaizdą, serveris konteinerio viduje lūždavo ir persikraudavo (Child process died) dėl numatytųjų saugumo filtrų. Problema išspręsta manifestų argumentuose prirašius `--allowed-hosts "*"`, `--host 0.0.0.0` ir `--disable-security-middleware`.
* **Windows & Minikube tinklo izoliacija (Port-Forward / NodePort):** Standartinis `kubectl port-forward` metė `connection refused` arba `ERR_CONNECTION_RESET` klaidas dėl Windows ugniasienės ir Docker Desktop tinklo specifikos. Problema išspręsta tinkamai sukonfigūravus Kubernetes `Service` ir suteikus `Deployment` daugiau resursų (mlflow full vaizdas užima daugiau).

## 3. Kiek laiko užtruko
* Projekto kodo paruošimas ir DVC konvejerio derinimas: **~2 val.**
* Docker vaizdo optimizavimas, Trivy skenavimas ir GHCR konfigūracija: **~1.5 val.**
* Kubernetes manifestų rašymas, MLflow v3 bei PostgreSQL derinimas klasteryje: **~6 val.**
* **Iš viso:** ~9.5 val. intensyvaus inžinerinio darbo.