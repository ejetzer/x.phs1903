#ifndef TYPES_INCLUS
#define TYPES_INCLUS

typedef static unsigned int idx_t;

#ifndef Arduino_h
typedef unsigned char byte;
#endif

#ifdef RAPIDE
typedef static unsigned long chrono_t;
typedef unsigned int val_t;
#else
typedef static unsigned int chrono_t;
#endif

#endif
