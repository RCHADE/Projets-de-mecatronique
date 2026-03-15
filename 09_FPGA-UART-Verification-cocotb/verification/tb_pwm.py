import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset(dut):
    """Reset le composant pendant 10 cycles"""
    dut.rst.value = 1
    dut.duty_cycle.value = 0
    for _ in range(10):
        await RisingEdge(dut.clk)
    dut.rst.value = 0


async def mesurer_duty_cycle(dut, nb_periodes=100):
    """Mesure le ratio HIGH/LOW sur nb_periodes cycles d'horloge"""
    compteur_high = 0
    for _ in range(nb_periodes):
        await RisingEdge(dut.clk)
        if dut.pwm_out.value == 1:
            compteur_high += 1
    return compteur_high


@cocotb.test()
async def test_reset(dut):
    """Vérifie que le reset met pwm_out à 0"""
    cocotb.start_soon(Clock(dut.clk, 83, units="ns").start())

    dut.rst.value = 1
    dut.duty_cycle.value = 0
    await Timer(500, units="ns")

    assert dut.pwm_out.value == 0, "ERREUR : pwm_out devrait être 0 pendant le reset"
    cocotb.log.info("✅ Test reset : OK")


@cocotb.test()
async def test_duty_25(dut):
    """Vérifie un duty cycle de 25%"""
    cocotb.start_soon(Clock(dut.clk, 83, units="ns").start())
    await reset(dut)

    dut.duty_cycle.value = 25
    await RisingEdge(dut.clk)  # laisser le temps au signal de se propager

    ratio = await mesurer_duty_cycle(dut, nb_periodes=100)

    assert ratio == 25, f"ERREUR : attendu 25 cycles HIGH, obtenu {ratio}"
    cocotb.log.info(f"✅ Test duty 25% : {ratio}/100 cycles HIGH → OK")


@cocotb.test()
async def test_duty_50(dut):
    """Vérifie un duty cycle de 50%"""
    cocotb.start_soon(Clock(dut.clk, 83, units="ns").start())
    await reset(dut)

    dut.duty_cycle.value = 50
    await RisingEdge(dut.clk)

    ratio = await mesurer_duty_cycle(dut, nb_periodes=100)

    assert ratio == 50, f"ERREUR : attendu 50 cycles HIGH, obtenu {ratio}"
    cocotb.log.info(f"✅ Test duty 50% : {ratio}/100 cycles HIGH → OK")


@cocotb.test()
async def test_duty_75(dut):
    """Vérifie un duty cycle de 75%"""
    cocotb.start_soon(Clock(dut.clk, 83, units="ns").start())
    await reset(dut)

    dut.duty_cycle.value = 75
    await RisingEdge(dut.clk)

    ratio = await mesurer_duty_cycle(dut, nb_periodes=100)

    assert ratio == 75, f"ERREUR : attendu 75 cycles HIGH, obtenu {ratio}"
    cocotb.log.info(f"✅ Test duty 75% : {ratio}/100 cycles HIGH → OK")