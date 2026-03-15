# Vérification VHDL avec cocotb

Environnement de vérification automatisé pour un générateur PWM VHDL, 
utilisant cocotb (Python) et GHDL comme simulateur.

## Structure
- `rtl/` — code VHDL du générateur PWM
- `verification/` — testbench cocotb + Makefile
- `resultats/` — rapport XML, waveform VCD, captures

## Tests
4 tests automatisés :
| Test | Vérification |
|------|-------------|
| `test_reset` | pwm_out = 0 pendant le reset |
| `test_duty_25` | 25 cycles HIGH sur 100 |
| `test_duty_50` | 50 cycles HIGH sur 100 |
| `test_duty_75` | 75 cycles HIGH sur 100 |

## Résultats
```
TESTS=4  PASS=4  FAIL=0  SKIP=0
```
![Waveform PWM](resultats/waveform_pwm.png)

## Lancer
```bash
python3 -m venv venv
source venv/bin/activate
pip install cocotb
sudo apt install ghdl
cd verification && make
```

## Rapport
Le fichier `resultats/results.xml` (format JUnit) 
est compatible avec les pipelines CI/CD (GitLab CI, GitHub Actions).