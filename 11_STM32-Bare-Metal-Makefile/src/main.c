#include <stdint.h>

#define PERIPH_BASE     0x40000000U
#define AHB1_BASE       (PERIPH_BASE + 0x00020000U)
#define RCC_BASE        (AHB1_BASE + 0x3800U)
#define GPIOA_BASE      (AHB1_BASE + 0x0000U)

#define RCC_AHB1ENR     (*(volatile uint32_t *)(RCC_BASE + 0x30U))
#define GPIOA_MODER     (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_ODR       (*(volatile uint32_t *)(GPIOA_BASE + 0x14U))

#define GPIOA_EN        (1U << 0)
#define LED_PIN         5

static void delay(volatile uint32_t n)
{
    while (n--);
}

int main(void)
{
    RCC_AHB1ENR |= GPIOA_EN;

    GPIOA_MODER &= ~(3U << (LED_PIN * 2));
    GPIOA_MODER |=  (1U << (LED_PIN * 2));

    while (1) {
        GPIOA_ODR ^= (1U << LED_PIN);
        delay(500000);
    }

    return 0;
}