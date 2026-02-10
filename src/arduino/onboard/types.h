#ifndef TYPES_INCLUS
#define TYPES_INCLUS

#include <Arduino.h>

typedef unsigned int idx_t;
typedef volatile unsigned int vol_idx_t;

#ifdef ENTIERS
typedef long int val_t;
typedef volatile long int vol_val_t;
#else
typedef float val_t;
typedef volatile float vol_val_t;
#endif

typedef unsigned int int_t;
typedef volatile unsigned int vol_int_t;
typedef float float_t;

#endif
