# Driver I²C STM32 — Capteur LM75

Driver I²C générique pour STM32 (HAL), démontré avec un capteur de température LM75.
Architecture en couches : driver I²C bas niveau → driver capteur → application.

## Structure
- `Core/Inc/` — headers (`driver_i2c.h`, `sensor_lm75.h`)
- `Core/Src/` — implémentation (`driver_i2c.c`, `sensor_lm75.c`, `main.c`)
- `Tests/` — tests unitaires offline (`test_lm75.c`, `test_runner.h`)

## Fonctionnement
Le STM32 lit la température du LM75 via I²C toutes les secondes et envoie les résultats sur UART (115200 baud).

## Câblage
| STM32 | LM75 |
|-------|------|
| PB6 (SCL) | SCL |
| PB7 (SDA) | SDA |
| 3.3V | VCC |
| GND | GND, A0, A1, A2 |

Adresse I²C : `0x48` (A0=A1=A2=GND)

## Tests
11 tests automatisés, exécutables sans hardware :
```bash
cd Tests/
gcc test_lm75.c -o test_lm75 -lm && ./test_lm75
```
```
Results: 8/8  ALL PASSED   (conversion température)
Results: 3/3  ALL PASSED   (limites et résolution)
```