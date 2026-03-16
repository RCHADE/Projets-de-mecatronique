#include "test_runner.h"
#include <stdio.h>
#include <stdint.h>
#include <math.h>

static float raw_to_celsius(uint8_t msb, uint8_t lsb)
{
    int16_t raw = (int16_t)((msb << 8) | lsb);
    raw >>= 5;
    if (raw & 0x0400) raw |= (int16_t)0xF800;
    return (float)raw * 0.125f;
}

static void test_temp_conversion(void)
{
    TEST_SUITE_BEGIN("LM75 temperature conversion");

    TEST_ASSERT_FLOAT_NEAR(+125.000f, raw_to_celsius(0x7D, 0x00), 0.001f, "+125 C");
    TEST_ASSERT_FLOAT_NEAR( +80.000f, raw_to_celsius(0x50, 0x00), 0.001f, "+80 C");
    TEST_ASSERT_FLOAT_NEAR( +25.000f, raw_to_celsius(0x19, 0x00), 0.001f, "+25 C");
    TEST_ASSERT_FLOAT_NEAR(  +0.250f, raw_to_celsius(0x00, 0x40), 0.001f, "+0.25 C");
    TEST_ASSERT_FLOAT_NEAR(   0.000f, raw_to_celsius(0x00, 0x00), 0.001f, "0 C");
    TEST_ASSERT_FLOAT_NEAR(  -0.125f, raw_to_celsius(0xFF, 0xE0), 0.001f, "-0.125 C");
    TEST_ASSERT_FLOAT_NEAR( -25.000f, raw_to_celsius(0xE7, 0x00), 0.001f, "-25 C");
    TEST_ASSERT_FLOAT_NEAR( -55.000f, raw_to_celsius(0xC9, 0x00), 0.001f, "-55 C");

    TEST_SUITE_END();
}

static void test_range_checks(void)
{
    TEST_SUITE_BEGIN("LM75 range and boundary checks");

    float t_min = raw_to_celsius(0xC9, 0x00);
    float t_max = raw_to_celsius(0x7D, 0x00);

    TEST_ASSERT(t_min >= -55.1f && t_min <= -54.9f, "Min temp = -55 C");
    TEST_ASSERT(t_max >= 124.9f && t_max <= 125.1f, "Max temp = +125 C");

    float t1 = raw_to_celsius(0x19, 0x00);
    float t2 = raw_to_celsius(0x19, 0x20);
    TEST_ASSERT_FLOAT_NEAR(0.125f, t2 - t1, 0.001f, "Resolution = 0.125 C");

    TEST_SUITE_END();
}

void LM75_RunTests(void)
{
    printf("\r\n=== STM32-I2C-Sensor-Driver Tests ===\r\n");
    test_temp_conversion();
    test_range_checks();
    printf("\r\n[DONE]\r\n");
}

int main(void)
{
    LM75_RunTests();
    return 0;
}