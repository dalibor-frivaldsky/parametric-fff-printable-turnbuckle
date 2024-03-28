MM = 1.0

class Standard:
    M4 = 4*MM

    M5 = 5*MM

    M6 = 6*MM
    
    M10 = 10*MM
    M10_THREAD_PITCH_COARSE = 1.5*MM

    M12 = 12*MM
    M12_THREAD_PITCH_COARSE = 1.75*MM

class Fdm(Standard):
    _TOLERANCE = 0.2*MM / 2

    M10_INTERNAL = Standard.M10 + _TOLERANCE
    M10_EXTERNAL = Standard.M10 - _TOLERANCE

    M12_INTERNAL = Standard.M12 + _TOLERANCE
    M12_EXTERNAL = Standard.M12 - _TOLERANCE