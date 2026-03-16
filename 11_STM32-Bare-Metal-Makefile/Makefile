TARGET  = firmware
CC      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
GDB     = arm-none-eabi-gdb

CFLAGS  = -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16
CFLAGS += -O0 -g3 -Wall
CFLAGS += -nostdlib -nostartfiles

LDFLAGS = -T linker/stm32f4.ld -Wl,--gc-sections

SRC     = src/main.c
STARTUP = startup/startup.s

all: $(TARGET).elf $(TARGET).bin

$(TARGET).elf: $(SRC) $(STARTUP)
	$(CC) $(CFLAGS) $(LDFLAGS) $(STARTUP) $(SRC) -o $@

$(TARGET).bin: $(TARGET).elf
	$(OBJCOPY) -O binary $< $@

flash: $(TARGET).bin
	openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
	-c "program $(TARGET).bin 0x08000000 verify reset exit"

debug: $(TARGET).elf
	$(GDB) -ex "target remote :3333" \
	       -ex "monitor reset halt" \
	       -ex "load" \
	       -ex "break main" \
	       -ex "continue" \
	       $(TARGET).elf

clean:
	rm -f $(TARGET).elf $(TARGET).bin