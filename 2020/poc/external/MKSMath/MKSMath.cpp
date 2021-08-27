#include "MKSMath.h"

float CalculateMAVGNoBuffer(MovingAVGNoBuffer_t * data, float sample) {
	// IIR - avg = ((1-(1 / w_size)*avg) + (1 / w_size) * sample
	if (data->avg) {
		data->avg = ((1.0 - (1.0 / (float)(data->window_size))) * data->avg) + (1.0 / (float)(data->window_size)) * sample;
	} else {
		data->avg = sample;
	}
	return data->avg;
}