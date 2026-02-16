# FPGA PWM Control over UART

FPGA PWM controller controlled from PC via UART.

## Files
- `/verilog/uart_receiver.v` - UART module
- `/verilog/pwm_generator.v` - PWM module  
- `/python/uart_controller.py` - PC control software

## How it works
1. PC sends commands via UART (115200 baud)
2. FPGA receives commands and adjusts PWM duty cycle
3. PWM output changes accordingly

## Commands
- `b50` - Set duty cycle to 50%
- `b100` - Set duty cycle to 100%  
- `r` - Reset system

## Requirements
- Python: pyserial
- FPGA: Any board with UART capability

## Test
```bash
cd python
python uart_controller.py