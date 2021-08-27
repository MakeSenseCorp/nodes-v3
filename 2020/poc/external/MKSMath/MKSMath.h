#ifndef MKSMath_h
#define MKSMath_h

#include "Arduino.h"

typedef struct {
	float avg;
	uint16_t window_size;
} MovingAVGNoBuffer_t;

float CalculateMAVGNoBuffer(MovingAVGNoBuffer_t * data, float sample);

#endif
