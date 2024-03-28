# %%
import core.config as _config

import cadquery as cq
import core.iso as iso
import math
from core.iso import MM
from core.metric_threads import *

if _config.IS_DEVELOPMENT_MODE:
    from ocp_vscode import *


THREAD_MIRROR_PLANE = 'XZ'

def _hand_marker(radius: float, hand: str):
    return (
        cq.Workplane('XY')
        .polarArray(radius, -90, 360, 1 if hand == 'left' else 2)
        .sphere(1*MM)
    )

def _cutter_thickness(diameter: float, angle_with_print_bed: float):
    return diameter * math.cos(math.radians(angle_with_print_bed))
# %%

def body(
    take_up_length: float,
    thread_diameter: float,
    thread_pitch: float,
    handle_diameter: float
):
# %%
    if _config.IS_DEVELOPMENT_MODE:
        take_up_length = 100*MM
        thread_diameter = iso.Standard.M10
        thread_pitch = iso.Standard.M10_THREAD_PITCH_COARSE
        handle_diameter = 20*MM

    body = (
        cq.Workplane('XY')
        .sketch()
        .regularPolygon(handle_diameter/2, 6, 30)
        .vertices()
        .fillet(1*MM)
        .finalize()
        .extrude(take_up_length + 2*MM)
    )

    bottom_left_hand_thread = internal_metric_thread(
        diameter=thread_diameter,
        pitch=thread_pitch,
        length=take_up_length/2,
        bottom_chamfer=True
    )
    bottom_left_hand_thread = bottom_left_hand_thread.mirror(THREAD_MIRROR_PLANE)

    top_right_hand_thread = internal_metric_thread(
        diameter=thread_diameter,
        pitch=thread_pitch,
        length=take_up_length/2,
        top_chamfer=True
    ).translate((0, 0, take_up_length/2 + 2*MM))

    body = (
        cq.Workplane('XY', obj=body.val())
        .faces('>Z')
        .hole(thread_diameter)
        .union(bottom_left_hand_thread)
        .union(top_right_hand_thread)
    )

    handle_side_length = (handle_diameter/2) * math.sqrt(3) / 2
    body = (
        cq.Workplane('XZ', obj=body.val())
        .faces('<Y')
        .sketch()
        .rect(
            handle_side_length - 2*MM,
            take_up_length - 22*MM
        )
        .vertices()
        .fillet(1*MM)
        .finalize()
        .extrude(-handle_diameter, combine='s')
    )

    left_hand_marker = _hand_marker(handle_side_length, 'left')
    righ_hand_marker = (
        _hand_marker(handle_side_length, 'right')
        .translate((0, 0, take_up_length + 2*MM))
    )

    body = (
        cq.Workplane('XY', obj=body.val())
        .cut(left_hand_marker)
        .cut(righ_hand_marker)
    )

    if _config.IS_DEVELOPMENT_MODE:
        show(body)
# %%
    return body

def eye_end_fitting(
    diameter: float,
    pitch: float,
    take_up_length: float,
    eye_inner_radius: float,
    hand: str
):
# %%
    if _config.IS_DEVELOPMENT_MODE:
        diameter = 10*MM
        pitch = 1.5*MM
        take_up_length = 100*MM
        eye_inner_radius = 15*MM
        hand = 'left'

    no_thread_length = 5*MM

    thickness = _cutter_thickness(
        metric_thread_minor_radius(diameter, pitch)*2,
        30
    )
    cutter = (
        cq.Workplane('XY')
        .rect(2*(diameter+eye_inner_radius), thickness)
        .extrude(
            take_up_length/2
            + no_thread_length
            + diameter
            + eye_inner_radius
        )
    )

    hand_marker = _hand_marker(thickness/2, hand).mirror('XZ')

    thread = (
        cq.Workplane('XY')
        .union(external_metric_thread(
            diameter=diameter,
            pitch=pitch,
            length=take_up_length/2,
            bottom_lead_in=True,
            top_lead_in=False,
            base_cylinder=True
        ))
        .intersect(cutter)
        .cut(hand_marker)
    )
    if hand == 'left':
        thread = thread.mirror(THREAD_MIRROR_PLANE)

    revolve_axis_x = diameter/2 + eye_inner_radius
    eye = (
        cq.Workplane('XZ')
        .circle(diameter/2)
        .revolve(
            axisStart=(revolve_axis_x, 0, 0),
            axisEnd=(revolve_axis_x, 1, 0)
        )
        .rotateAboutCenter((1, 0, 0), 90)
        .translate((-revolve_axis_x, 0, 0))
    )

    no_thread_extrude_length = diameter/2 + no_thread_length
    fitting = (
        cq.Workplane('XY')
        .circle(diameter/2)
        .extrude(no_thread_extrude_length)
        .translate((0, 0, -(no_thread_extrude_length + revolve_axis_x)))
        .union(eye)
        .translate((0, 0, (no_thread_extrude_length + revolve_axis_x)))
        .intersect(cutter)
        .translate((0, 0, take_up_length/2))
        .union(thread)
    )

    if _config.IS_DEVELOPMENT_MODE:
        show(fitting.rotateAboutCenter((1, 0, 0), -90))
# %%
    return fitting
