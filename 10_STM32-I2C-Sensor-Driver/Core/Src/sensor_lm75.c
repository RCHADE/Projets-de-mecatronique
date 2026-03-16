#include "sensor_lm75.h"
#include <string.h>

static float lm75_raw_to_celsius(uint8_t msb, uint8_t lsb)
{
    int16_t raw = (int16_t)((msb << 8) | lsb);
    raw >>= 5;
    if (raw & 0x0400) raw |= (int16_t)0xF800;
    return (float)raw * LM75_TEMP_RESOLUTION;
}

static void lm75_celsius_to_reg(float temp_c, uint8_t *msb, uint8_t *lsb)
{
    int16_t raw = (int16_t)(temp_c / 0.5f);
    raw <<= 7;
    *msb = (uint8_t)((raw >> 8) & 0xFF);
    *lsb = (uint8_t)(raw & 0xFF);
}

I2C_Drv_Status LM75_Init(LM75_Handle *dev, uint8_t addr)
{
    if (dev == NULL) return I2C_DRV_ERR_ARG;
    memset(dev, 0, sizeof(LM75_Handle));
    dev->addr = addr;

    if (!I2C_Drv_IsDeviceReady(addr)) return I2C_DRV_ERR_NACK;

    dev->is_init = true;
    return I2C_DRV_OK;
}

float LM75_ReadTemp(const LM75_Handle *dev)
{
    if (dev == NULL || !dev->is_init) return LM75_TEMP_ERR;

    uint8_t buf[2] = {0};
    I2C_Drv_Status status = I2C_Drv_ReadReg(dev->addr, LM75_REG_TEMP, buf, 2);
    if (status != I2C_DRV_OK) return LM75_TEMP_ERR;

    return lm75_raw_to_celsius(buf[0], buf[1]);
}

I2C_Drv_Status LM75_SetShutdown(const LM75_Handle *dev, bool shutdown)
{
    if (dev == NULL || !dev->is_init) return I2C_DRV_ERR_ARG;

    uint8_t conf = 0;
    I2C_Drv_Status status = I2C_Drv_ReadReg(dev->addr, LM75_REG_CONF, &conf, 1);
    if (status != I2C_DRV_OK) return status;

    if (shutdown) conf |=  LM75_CONF_SHUTDOWN_BIT;
    else          conf &= ~LM75_CONF_SHUTDOWN_BIT;

    return I2C_Drv_WriteReg(dev->addr, LM75_REG_CONF, &conf, 1);
}

I2C_Drv_Status LM75_SetThreshold(const LM75_Handle *dev, float threshold)
{
    if (dev == NULL || !dev->is_init) return I2C_DRV_ERR_ARG;

    uint8_t buf[2];
    lm75_celsius_to_reg(threshold, &buf[0], &buf[1]);
    return I2C_Drv_WriteReg(dev->addr, LM75_REG_TOS, buf, 2);
}