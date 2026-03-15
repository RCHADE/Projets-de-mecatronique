# Contrôle PWM sur FPGA via UART

Générateur PWM sur FPGA contrôlé depuis un PC via protocole UART.

## Fichiers
- `vhdl/uart_receiver.vhd` — récepteur UART (VHDL)
- `vhdl/pwm_generator.vhd` — générateur PWM (VHDL)
- `verilog/uart_receiver.v` — récepteur UART (Verilog)
- `verilog/pwm_generator.v` — générateur PWM (Verilog)
- `python/uart_controller.py` — script de contrôle PC

## Fonctionnement
Le PC envoie une commande série (115200 baud) → le FPGA reçoit et ajuste le rapport cyclique PWM.

## Commandes
| Commande | Effet |
|----------|-------|
| `b50` | Rapport cyclique 50% |
| `b100` | Rapport cyclique 100% |
| `r` | Reset |

## Lancer
```bash
pip install pyserial
python python/uart_controller.py
```