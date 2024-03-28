import core.iso as iso
from core.iso import MM

# Base turnbuckle parameters
thread_diameter_external = iso.Fdm.M10_EXTERNAL
thread_diameter_internal = iso.Fdm.M10_INTERNAL
thread_pitch = iso.Standard.M10_THREAD_PITCH_COARSE
take_up_length = 100*MM

# Body parameters
handle_diameter = 20*MM

# Eye end fitting parameters
eye_inner_radius = 8*MM


import core.config as _config
_config.IS_DEVELOPMENT_MODE = False

import cadquery as cq
import timeit
from pathlib import Path
from turnbuckle import *
from typing import Any, Callable


def _timeit(fn: Callable) -> Any:
    start_time = timeit.default_timer()
    part = fn()
    elapsed_time = timeit.default_timer() - start_time
    print(f'Took: {elapsed_time:.3f}s')
    print()
    return part

print('Building body')
body_part = _timeit(lambda: body(
    take_up_length=take_up_length,
    thread_diameter=thread_diameter_internal,
    thread_pitch=thread_pitch,
    handle_diameter=handle_diameter
))

print('Building left-threaded eye end fitting')
eye_end_fitting_part_left = _timeit(lambda:eye_end_fitting(
    diameter=thread_diameter_external,
    pitch=thread_pitch,
    take_up_length=take_up_length,
    eye_inner_radius=eye_inner_radius,
    hand='left'
).rotateAboutCenter((1, 0, 0), -90))

print('Building right-threaded eye end fitting')
eye_end_fitting_part_right = _timeit(lambda: eye_end_fitting(
    diameter=thread_diameter_external,
    pitch=thread_pitch,
    take_up_length=take_up_length,
    eye_inner_radius=eye_inner_radius,
    hand='right'
).rotateAboutCenter((1, 0, 0), -90))

format = 'step'
build_dir = Path('.') / 'build' / format
build_dir.mkdir(parents=True, exist_ok=True)
cq.exporters.export(body_part, str(build_dir / f'body.{format}'))
cq.exporters.export(eye_end_fitting_part_left, str(build_dir / f'eye_end_fittng_left.{format}'))
cq.exporters.export(eye_end_fitting_part_right, str(build_dir / f'eye_end_fittng_right.{format}'))
