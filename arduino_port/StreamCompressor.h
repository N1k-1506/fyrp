#ifndef STREAM_COMPRESSOR_H
#define STREAM_COMPRESSOR_H

#include <Arduino.h>

// Physically locks maximum available memory bounding array over-runs cleanly at the compiler stage
#define MAX_WINDOW_SIZE 20

// Custom C++ Struct aggressively circumventing unbounded tuples for precise firmware memory alignment
struct CompressionResult {
    bool should_transmit;
    uint32_t timestamp;
    float payload_delta;
};

class StreamCompressor {
public:
    StreamCompressor(uint8_t window_size = 10, float k = 2.0, float min_epsilon = 0.05);
    
    CompressionResult process_data_point(float value);
    CompressionResult flush();

private:
    uint8_t _window_size;
    float _k;
    float _min_epsilon;
    
    uint32_t _t;
    
    // Delta Memory State
    bool _is_first_point;
    float _last_value;
    
    // Threshold Memory State (O(1) Circular Buffer implementation natively preventing Stack Leaks)
    float _delta_queue[MAX_WINDOW_SIZE];
    uint8_t _queue_index;
    uint8_t _queue_count;
    
    // SDT Geometric Processing State 
    uint32_t _t_pivot;
    float _v_pivot;
    float _max_slope;
    float _min_slope;
    uint32_t _last_t;
    float _last_abs_value;
    
    // Local Radio Transmitter Map
    float _last_transmitted_abs_value;

    void _update_threshold_queue(float delta);
    float _calculate_epsilon();
    CompressionResult _sdt_step(uint32_t t, float current_abs_value, float epsilon);
};

#endif
