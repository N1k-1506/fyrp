#include "StreamCompressor.h"
#include <math.h>

StreamCompressor::StreamCompressor(uint8_t window_size, float k, float min_epsilon) {
    _window_size = (window_size > MAX_WINDOW_SIZE) ? MAX_WINDOW_SIZE : window_size;
    _k = k;
    _min_epsilon = min_epsilon;
    
    _t = 0;
    _is_first_point = true;
    _last_value = 0.0;
    
    _queue_index = 0;
    _queue_count = 0;
    
    _t_pivot = 0;
    _v_pivot = 0.0;
    _max_slope = INFINITY;
    _min_slope = -INFINITY;
    _last_t = 0;
    _last_abs_value = 0.0;
    
    _last_transmitted_abs_value = 0.0;
}

void StreamCompressor::_update_threshold_queue(float delta) {
    _delta_queue[_queue_index] = delta;
    _queue_index = (_queue_index + 1) % _window_size;
    if (_queue_count < _window_size) {
        _queue_count++;
    }
}

float StreamCompressor::_calculate_epsilon() {
    if (_queue_count < 2) {
        return _min_epsilon;
    }
    
    float sum = 0.0;
    for (uint8_t i = 0; i < _queue_count; i++) {
        sum += _delta_queue[i];
    }
    float mean = sum / _queue_count;
    
    float variance_sum = 0.0;
    for (uint8_t i = 0; i < _queue_count; i++) {
        float diff = _delta_queue[i] - mean;
        variance_sum += (diff * diff);
    }
    float variance = variance_sum / (_queue_count - 1);
    float std_dev = sqrt(variance);
    
    float epsilon = _k * std_dev;
    return (epsilon > _min_epsilon) ? epsilon : _min_epsilon;
}

CompressionResult StreamCompressor::_sdt_step(uint32_t t, float current_abs_value, float epsilon) {
    CompressionResult result;
    result.should_transmit = false;
    result.timestamp = t;
    result.payload_delta = 0.0;

    int32_t dt = t - _t_pivot;
    
    if (dt == 0) {
        return result;
    }
    
    float current_max_slope = (current_abs_value + epsilon - _v_pivot) / dt;
    float current_min_slope = (current_abs_value - epsilon - _v_pivot) / dt;
    
    float new_max_slope = (_max_slope < current_max_slope) ? _max_slope : current_max_slope;
    float new_min_slope = (_min_slope > current_min_slope) ? _min_slope : current_min_slope;
    
    if (new_max_slope < new_min_slope) {
        result.should_transmit = true;
        result.payload_delta = _last_abs_value - _last_transmitted_abs_value;
        result.timestamp = _last_t;
        
        _last_transmitted_abs_value = _last_abs_value;
        
        _t_pivot = _last_t;
        _v_pivot = _last_abs_value;
        
        int32_t dt_new = t - _t_pivot;
        if (dt_new > 0) {
            _max_slope = (current_abs_value + epsilon - _v_pivot) / dt_new;
            _min_slope = (current_abs_value - epsilon - _v_pivot) / dt_new;
        } else {
            _max_slope = INFINITY;
            _min_slope = -INFINITY;
        }
    } else {
        _max_slope = new_max_slope;
        _min_slope = new_min_slope;
    }
    
    _last_t = t;
    _last_abs_value = current_abs_value;
    
    return result;
}

CompressionResult StreamCompressor::process_data_point(float value) {
    CompressionResult result;
    result.should_transmit = false;
    result.timestamp = 0;
    result.payload_delta = 0.0;

    if (_is_first_point) {
        _is_first_point = false;
        _last_value = value;
        _t_pivot = _t;
        _v_pivot = value;
        _last_t = _t;
        _last_abs_value = value;
        _last_transmitted_abs_value = value;
        
        _update_threshold_queue(0.0);
        
        result.should_transmit = true;
        result.timestamp = _t;
        result.payload_delta = value; // Transmit initial anchor natively as Absolute Value
        
        _t++;
        return result;
    }
    
    float current_delta = value - _last_value;
    _last_value = value;
    
    _update_threshold_queue(current_delta);
    float epsilon = _calculate_epsilon();
    
    result = _sdt_step(_t, value, epsilon);
    
    _t++;
    return result;
}

CompressionResult StreamCompressor::flush() {
    CompressionResult result;
    result.should_transmit = true;
    result.timestamp = _last_t;
    result.payload_delta = _last_abs_value - _last_transmitted_abs_value;
    
    _last_transmitted_abs_value = _last_abs_value;
    return result;
}
