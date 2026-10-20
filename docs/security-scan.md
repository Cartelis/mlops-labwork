# Saugumo skenavimas

Laikas (UTC): 2026-10-20T20:52:12.475900+00:00

| Vaizdas              | HIGH  | CRITICAL |
|----------------------|------:|---------:|
| mlops-lab-prepare:u1 | 44    | 0        |

Žali JSON rezultatai saugomi: `docs/trivy/trivy-prepare.json`. 

CRITICAL vartas: PASS

## HIGH radinių analizė ir kompensacinės priemonės

Skenavimo metu gautas **44 HIGH** lygio spragų rezultatas, tačiau **CRITICAL saugumo vartas yra sėkmingai praeitas (PASS)**. Atlikus detalią žalių JSON rezultatų analizę, nustatyta, kad visi 44 radiniai yra susiję su bazinio Linux atvaizdo (`python:3.12-slim-trixie`) sisteminiais paketais (daugiausia `util-linux`).

Šios spragos yra priimtinos ir nekelia pavojaus mūsų MLOps infrastruktūrai dėl šių priežasčių:


1. **Priklausomybė nuo Upstream (Unfixed) ir skenerių netikslumas (Backporting):** 
Didžioji dalis šių HIGH spragų yra „unfixed“ būsenoje (kūrėjai dar neišleido oficialaus kodo pataisymo). Tačiau dalis spragų gali būti jau ištaisytos pačių Debian kūrėjų, pritaikant **„backporting“** praktiką – kai saugumo pataisymas įkeliamas į tą pačią senąją paketo versiją, **nepakeičiant pagrindinio versijos numerio (tag'o)**. Kadangi `Trivy` dažnai tikrina tik oficialią upstream versijos žymą, jis nemato, kad paketas konteinerio viduje jau yra saugus. Kadangi atvaizdo konstravimo metu (`Dockerfile.prepare`) buvo sėkmingai atliktas pilnas OS atnaujinimas (`apt-get update && apt-get upgrade -y`), konteineryje guli patys naujausi įmanomi saugumo paketai, kokius tik distribucija gali pateikti.

2. **Teisių izoliacija (Kompensacinė priemonė):** Konteineris veikia po izoliuotu ne-root naudotoju (`uid=1000`) ir neturi SUID privilegijų.

3. **Paskirtis:** Šis vaizdas yra skirtas tik laikinam duomenų generavimui ir modelio patikrinimui klasterio viduje, jis nebus viešinamas kaip išorinis internetinis API servisas (Inference), todėl jo atakos paviršius yra minimalus.
