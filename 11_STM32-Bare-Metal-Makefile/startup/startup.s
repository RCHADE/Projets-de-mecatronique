.syntax unified
.cpu cortex-m4
.thumb

.section .isr_vector, "a"
.word _estack
.word Reset_Handler
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0
.word 0

.section .text
.global Reset_Handler
.type Reset_Handler, %function
Reset_Handler:
    ldr sp, =_estack

    ldr r0, =_sdata
    ldr r1, =_edata
    ldr r2, =_sidata
copy_data:
    cmp r0, r1
    bge zero_bss
    ldr r3, [r2], #4
    str r3, [r0], #4
    b copy_data

zero_bss:
    ldr r0, =_sbss
    ldr r1, =_ebss
    mov r2, #0
zero_bss_loop:
    cmp r0, r1
    bge call_main
    str r2, [r0], #4
    b zero_bss_loop

call_main:
    bl main
    b .
