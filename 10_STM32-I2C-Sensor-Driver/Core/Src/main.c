#include "main.h"
#include "driver_i2c.h"
#include "sensor_lm75.h"
#include <stdio.h>

extern I2C_HandleTypeDef  hi2c1;
extern UART_HandleTypeDef huart2;

int _write(int file, char *ptr, int len)
{
    (void)file;
    HAL_UART_Transmit(&huart2, (uint8_t *)ptr, (uint16_t)len, HAL_MAX_DELAY);
    return len;
}

void App_Run(void)
{
    printf("\r\n=== STM32 I2C Sensor Driver ===\r\n");

    if (I2C_Drv_Init(&hi2c1) != I2C_DRV_OK) {
        printf("[ERROR] I2C init failed\r\n");
        return;
    }

    LM75_Handle lm75;
    if (LM75_Init(&lm75, LM75_ADDR(0, 0, 0)) != I2C_DRV_OK) {
        printf("[ERROR] LM75 not found — check wiring\r\n");
        return;
    }
    printf("[OK] LM75 at 0x%02X\r\n", lm75.addr);

    LM75_SetThreshold(&lm75, 30.0f);

    uint32_t n = 0;
    while (1) {
        float temp = LM75_ReadTemp(&lm75);
        if (temp == LM75_TEMP_ERR)
            printf("[%04lu] Read error\r\n", n);
        else
            printf("[%04lu] %.3f C\r\n", n, temp);
        n++;
        HAL_Delay(1000);
    }
}