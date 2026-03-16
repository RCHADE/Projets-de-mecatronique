#ifndef TEST_RUNNER_H
#define TEST_RUNNER_H

#include <stdio.h>
#include <math.h>
#include <stdint.h>

static uint32_t _tests_run    = 0;
static uint32_t _tests_passed = 0;
static uint32_t _tests_failed = 0;

#define TEST_SUITE_BEGIN(name) \
    do { \
        printf("\r\n[ SUITE ] %s\r\n", (name)); \
        _tests_run = _tests_passed = _tests_failed = 0; \
    } while(0)

#define TEST_ASSERT(condition, desc) \
    do { \
        _tests_run++; \
        if (condition) { _tests_passed++; printf("  [PASS] %s\r\n", (desc)); } \
        else { _tests_failed++; printf("  [FAIL] %s  (line %d)\r\n", (desc), __LINE__); } \
    } while(0)

#define TEST_ASSERT_EQ_INT(expected, actual, desc) \
    do { \
        _tests_run++; \
        if ((int32_t)(expected) == (int32_t)(actual)) { \
            _tests_passed++; printf("  [PASS] %s\r\n", (desc)); \
        } else { \
            _tests_failed++; \
            printf("  [FAIL] %s — expected %ld, got %ld  (line %d)\r\n", \
                   (desc), (long)(expected), (long)(actual), __LINE__); \
        } \
    } while(0)

#define TEST_ASSERT_FLOAT_NEAR(expected, actual, tol, desc) \
    do { \
        _tests_run++; \
        float _diff = fabsf((float)(expected) - (float)(actual)); \
        if (_diff <= (float)(tol)) { \
            _tests_passed++; \
            printf("  [PASS] %s  (%.3f ~= %.3f)\r\n", (desc), (float)(expected), (float)(actual)); \
        } else { \
            _tests_failed++; \
            printf("  [FAIL] %s — expected %.3f, got %.3f  (line %d)\r\n", \
                   (desc), (float)(expected), (float)(actual), __LINE__); \
        } \
    } while(0)

#define TEST_SUITE_END() \
    do { \
        printf("─────────────────────────────────\r\n"); \
        if (_tests_failed == 0) \
            printf("  Results: %lu/%lu  ALL PASSED\r\n", (unsigned long)_tests_passed, (unsigned long)_tests_run); \
        else \
            printf("  Results: %lu/%lu  %lu FAILED\r\n", (unsigned long)_tests_passed, (unsigned long)_tests_run, (unsigned long)_tests_failed); \
    } while(0)

#endif