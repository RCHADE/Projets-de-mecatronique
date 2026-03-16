#ifndef DRIVER_I2C_H
#define DRIVER_I2C_H

#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    I2C_DRV_OK       = 0,
    I2C_DRV_ERR_BUS  = 1,
    I2C_DRV_ERR_NACK = 2,
    I2C_DRV_ERR_TO   = 3,
    I2C_DRV_ERR_ARG  = 4
} I2C_Drv_Status;

#define I2C_DRV_TIMEOUT_MS 100U

I2C_Drv_Status I2C_Drv_Init(I2C_HandleTypeDef *hi2c);
I2C_Drv_Status I2C_Drv_WriteReg(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len);
I2C_Drv_Status I2C_Drv_ReadReg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len);
bool           I2C_Drv_IsDeviceReady(uint8_t dev_addr);
I2C_Drv_Status I2C_Drv_MapHalStatus(HAL_StatusTypeDef hal_status);

#endif