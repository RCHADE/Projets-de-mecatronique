# STM32 Bare Metal Makefile

Projet bare metal sur STM32F411 : clignotement LED sur PA5 sans CubeIDE ni HAL.
Compilation avec arm-none-eabi-gcc, flash via OpenOCD, debug avec GDB.

## Structure
- `src/main.c` — contrôle GPIO direct via registres
- `startup/startup.s` — vecteur d'interruption ARM, copie .data, zero .bss
- `linker/stm32f4.ld` — linker script (FLASH 512K, SRAM 128K)
- `Makefile` — compilation, flash, debug

## Compiler
```bash
make
```

## Flasher
```bash
make flash
```

## Déboguer avec GDB

Terminal 1 :
```bash
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg
```

Terminal 2 :
```bash
make debug
```

## Outils
| Outil | Rôle |
|-------|------|
| arm-none-eabi-gcc | Cross-compilation ARM |
| arm-none-eabi-objcopy | Génération du .bin |
| OpenOCD | Flash + serveur GDB |
| arm-none-eabi-gdb | Debug sur cible |