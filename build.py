import core.config as _config
_config.IS_DEVELOPMENT_MODE = False

import cadquery as cq
import core.iso as iso
from core.iso import MM
from pathlib import Path
from turnbuckle import *

body_part = body(
    take_up_length=100*MM,
    thread_diameter=iso.Fdm.M10_INTERNAL,
    thread_pitch=iso.Standard.M10_THREAD_PITCH_COARSE,
    handle_diameter=20*MM
)

eye_end_fitting_part_left = eye_end_fitting(
    diameter=iso.Fdm.M10_EXTERNAL,
    pitch=iso.Standard.M10_THREAD_PITCH_COARSE,
    take_up_length=100*MM,
    eye_inner_radius=8*MM,
    hand='left'
).rotateAboutCenter((1, 0, 0), -90)

eye_end_fitting_part_right = eye_end_fitting(
    diameter=iso.Fdm.M10_EXTERNAL,
    pitch=iso.Standard.M10_THREAD_PITCH_COARSE,
    take_up_length=100*MM,
    eye_inner_radius=8*MM,
    hand='right'
).rotateAboutCenter((1, 0, 0), -90)

format = 'step'
build_dir = Path('.') / 'build' / format
build_dir.mkdir(parents=True, exist_ok=True)
cq.exporters.export(body_part, str(build_dir / f'body.{format}'))
cq.exporters.export(eye_end_fitting_part_left, str(build_dir / f'eye_end_fittng_left.{format}'))
cq.exporters.export(eye_end_fitting_part_right, str(build_dir / f'eye_end_fittng_right.{format}'))
