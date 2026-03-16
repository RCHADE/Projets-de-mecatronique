#ifndef SENSOR_LM75_H
#define SENSOR_LM75_H

#include "driver_i2c.h"
#include <stdint.h>
#include <stdbool.h>

#define LM75_ADDR(a2,a1,a0)  (0x48U | ((a2)<<2) | ((a1)<<1) | (a0))

#define LM75_REG_TEMP   0x00U
#define LM75_REG_CONF   0x01U
#define LM75_REG_THYST  0x02U
#define LM75_REG_TOS    0x03U

#define LM75_CONF_SHUTDOWN_BIT  (1U << 0)
#define LM75_TEMP_RESOLUTION    0.125f
#define LM75_TEMP_ERR           -999.0f

typedef struct {
    uint8_t addr;
    bool    is_init;
} LM75_Handle;

I2C_Drv_Status LM75_Init(LM75_Handle *dev, uint8_t addr);
float          LM75_ReadTemp(const LM75_Handle *dev);
I2C_Drv_Status LM75_SetShutdown(const LM75_Handle *dev, bool shutdown);
I2C_Drv_Status LM75_SetThreshold(const LM75_Handle *dev, float threshold);

#endif