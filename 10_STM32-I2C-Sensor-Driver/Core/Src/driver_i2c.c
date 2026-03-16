#include "driver_i2c.h"

static I2C_HandleTypeDef *s_hi2c = NULL;

I2C_Drv_Status I2C_Drv_MapHalStatus(HAL_StatusTypeDef hal_status)
{
    switch (hal_status) {
        case HAL_OK:      return I2C_DRV_OK;
        case HAL_TIMEOUT: return I2C_DRV_ERR_TO;
        case HAL_ERROR:
        default:          return I2C_DRV_ERR_BUS;
    }
}

I2C_Drv_Status I2C_Drv_Init(I2C_HandleTypeDef *hi2c)
{
    if (hi2c == NULL) return I2C_DRV_ERR_ARG;
    s_hi2c = hi2c;
    return I2C_DRV_OK;
}

I2C_Drv_Status I2C_Drv_WriteReg(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, uint16_t len)
{
    if (s_hi2c == NULL || data == NULL || len == 0) return I2C_DRV_ERR_ARG;

    HAL_StatusTypeDef status = HAL_I2C_Mem_Write(
        s_hi2c,
        (uint16_t)(dev_addr << 1),
        reg_addr,
        I2C_MEMADD_SIZE_8BIT,
        (uint8_t *)data,
        len,
        I2C_DRV_TIMEOUT_MS
    );

    return I2C_Drv_MapHalStatus(status);
}

I2C_Drv_Status I2C_Drv_ReadReg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, uint16_t len)
{
    if (s_hi2c == NULL || data == NULL || len == 0) return I2C_DRV_ERR_ARG;

    HAL_StatusTypeDef status = HAL_I2C_Mem_Read(
        s_hi2c,
        (uint16_t)(dev_addr << 1),
        reg_addr,
        I2C_MEMADD_SIZE_8BIT,
        data,
        len,
        I2C_DRV_TIMEOUT_MS
    );

    return I2C_Drv_MapHalStatus(status);
}

bool I2C_Drv_IsDeviceReady(uint8_t dev_addr)
{
    if (s_hi2c == NULL) return false;

    HAL_StatusTypeDef status = HAL_I2C_IsDeviceReady(
        s_hi2c,
        (uint16_t)(dev_addr << 1),
        3,
        I2C_DRV_TIMEOUT_MS
    );

    return (status == HAL_OK);
}