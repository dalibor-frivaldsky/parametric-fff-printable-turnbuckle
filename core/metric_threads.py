# Copyright (c) 2020-2024, Nerius Anthony Landys.  All rights reserved.
#   neri-engineering 'at' protonmail.com
#   https://svn.code.sf.net/p/nl10/code/cq-code/common/metric_threads.py
# This file is public domain.  Use it for any purpose, including commercial
# applications.  Attribution would be nice, but is not required.  There is no
# warranty of any kind, including its correctness, usefulness, or safety.
#
# Simple code example to create meshing M3x0.5 threads:
###############################################################################
#
#     male   = external_metric_thread(3.0, 0.5, 4.0, z_start= -0.85,
#                                     top_lead_in=True)
#
#     # Please note that the female thread is meant for a hole which has
#     # radius equal to metric_thread_major_radius(3.0, 0.5, internal=True),
#     # which is in fact very slightly larger than a 3.0 diameter hole.
#
#     female = internal_metric_thread(3.0, 0.5, 1.5,
#                                     bottom_chamfer=True, base_tube_od= 4.5)
#
###############################################################################
# Left hand threads can be created by employing one of the "mirror" operations.
# Thanks for taking the time to understand and use this code!

import math
import cadquery as cq

###############################################################################
# The functions which have names preceded by '__' are not meant to be called
# externally; the remaining functions are written with the intention that they
# will be called by external code.  The first section of code consists of
# lightweight helper functions; the meat and potatoes of this library is last.
###############################################################################

# Return value is in degrees, and currently it's fixed at 30.  Essentially this
# results in a typical 60 degree equilateral triangle cutting bit for threads.
def metric_thread_angle():
    return 30

# Helper func. to make code more intuitive and succinct.  Degrees --> radians.
def __deg2rad(degrees):
    return degrees * math.pi / 180

# In the absence of flat thread valley and flattened thread tip, returns the
# amount by which the thread "triangle" protrudes outwards (radially) from base
# cylinder in the case of external thread, or the amount by which the thread
# "triangle" protrudes inwards from base tube in the case of internal thread.
def metric_thread_perfect_height(pitch):
    return pitch / (2 * math.tan(__deg2rad(metric_thread_angle())))

# Up the radii of internal (female) thread in order to provide a little bit of
# wiggle room around male thread.  Right now input parameter 'diameter' is
# ignored.  This function is only used for internal/female threads.  Currently
# there is no practical way to adjust the male/female thread clearance besides
# to manually edit this function.  This design route was chosen for the sake of
# code simplicity.
def __metric_thread_internal_radius_increase(diameter, pitch):
    return 0.1 * metric_thread_perfect_height(pitch)

# Returns the major radius of thread, which is always the greater of the two.
def metric_thread_major_radius(diameter, pitch, internal=False):
    return (__metric_thread_internal_radius_increase(diameter, pitch) if
            internal else 0.0) + (diameter / 2)

# What portion of the total pitch is taken up by the angled thread section (and
# not the squared off valley and tip).  The remaining portion (1 minus ratio)
# will be divided equally between the flattened valley and flattened tip.
def __metric_thread_effective_ratio():
    return 0.7

# Returns the minor radius of thread, which is always the lesser of the two.
def metric_thread_minor_radius(diameter, pitch, internal=False):
    return (metric_thread_major_radius(diameter, pitch, internal)
            - (__metric_thread_effective_ratio() *
               metric_thread_perfect_height(pitch)))

# What the major radius would be if the cuts were perfectly triangular, without
# flat spots in the valleys and without flattened tips.
def metric_thread_perfect_major_radius(diameter, pitch, internal=False):
    return (metric_thread_major_radius(diameter, pitch, internal)
            + ((1.0 - __metric_thread_effective_ratio()) *
               metric_thread_perfect_height(pitch) / 2))

# What the minor radius would be if the cuts were perfectly triangular, without
# flat spots in the valleys and without flattened tips.
def metric_thread_perfect_minor_radius(diameter, pitch, internal=False):
    return (metric_thread_perfect_major_radius(diameter, pitch, internal)
            - metric_thread_perfect_height(pitch))

# Returns the lead-in and/or chamfer distance along the z axis of rotation.
# The lead-in/chamfer only depends on the pitch and is made with the same angle
# as the thread, that being 30 degrees offset from radial.
def metric_thread_lead_in(pitch, internal=False):
    return (math.tan(__deg2rad(metric_thread_angle()))
            * (metric_thread_major_radius(256.0, pitch, internal)
               - metric_thread_minor_radius(256.0, pitch, internal)))

# Returns the width of the flat spot in thread valley of a standard thread.
# This is also equal to the width of the flat spot on thread tip, on a standard
# thread.
def metric_thread_relief(pitch):
    return (1.0 - __metric_thread_effective_ratio()) * pitch / 2


###############################################################################
# A few words on modules external_metric_thread() and internal_metric_thread().
# The parameter 'z_start' is added as a convenience in order to make the male
# and female threads align perfectly.  When male and female threads are created
# having the same diameter, pitch, and n_starts (usually 1), then so long as
# they are not translated or rotated (or so long as they are subjected to the
# same exact translation and rotation), they will intermesh perfectly,
# regardless of the value of 'z_start' used on each.  This is in order that
# assemblies be able to depict perfectly aligning threads.

# Generates threads with base cylinder unless 'base_cylinder' is overridden.
# Please note that 'use_epsilon' is activated by default, which causes a slight
# budge in the minor radius, inwards, so that overlaps would be created with
# inner cylinders.  (Does not affect thread profile outside of cylinder.)
###############################################################################
def external_metric_thread(diameter,  # Required parameter, e.g. 3.0 for M3x0.5
                           pitch,     # Required parameter, e.g. 0.5 for M3x0.5
                           length,    # Required parameter, e.g. 2.0
                           z_start=0.0,
                           n_starts=1,
                           bottom_lead_in=False, # Lead-in is at same angle as
                           top_lead_in   =False, # thread, namely 30 degrees.
                           bottom_relief=False, # Add relief groove to start or
                           top_relief   =False, # end of threads (shorten).
                           force_outer_radius=-1.0, # Set close to diameter/2.
                           use_epsilon=True, # For inner cylinder overlap.
                           base_cylinder=True, # Whether to include base cyl.
                           cyl_extend_bottom=-1.0,
                           cyl_extend_top=-1.0,
                           envelope=False): # Draw only envelope, don't cut.

    cyl_extend_bottom = max(0.0, cyl_extend_bottom)
    cyl_extend_top    = max(0.0, cyl_extend_top)

    z_off             = (1.0 - __metric_thread_effective_ratio()) * pitch / 4
    t_start           = z_start
    t_length          = length
    if bottom_relief:
        t_start       = t_start  + (2 * z_off)
        t_length      = t_length - (2 * z_off)
    if top_relief:
        t_length      = t_length - (2 * z_off)
    outer_r           = (force_outer_radius if (force_outer_radius > 0.0) else
                         metric_thread_major_radius(diameter,pitch))
    inner_r           = metric_thread_minor_radius(diameter,pitch)
    epsilon           = 0
    inner_r_adj       = inner_r
    inner_z_budge     = 0
    if use_epsilon:
        epsilon       = (z_off/3) / math.tan(__deg2rad(metric_thread_angle()))
        inner_r_adj   = inner_r - epsilon
        inner_z_budge = math.tan(__deg2rad(metric_thread_angle())) * epsilon

    if envelope:
        threads = cq.Workplane("XZ")
        threads = threads.moveTo(inner_r_adj, -pitch)
        threads = threads.lineTo(outer_r, -pitch)
        threads = threads.lineTo(outer_r, t_length + pitch)
        threads = threads.lineTo(inner_r_adj, t_length + pitch)
        threads = threads.close()
        threads = threads.revolve()

    else: # Not envelope, cut the threads.
        wire = cq.Wire.makeHelix(pitch=pitch*n_starts,
                                 height=t_length+pitch,
                                 radius=inner_r)
        wire = wire.translate((0,0,-pitch/2))
        wire = wire.rotate(startVector=(0,0,0), endVector=(0,0,1),
                           angleDegrees=360*(-pitch/2)/(pitch*n_starts))
        d_mid = ((metric_thread_major_radius(diameter,pitch) - outer_r)
                 * math.tan(__deg2rad(metric_thread_angle())))
        thread = cq.Workplane("XZ")
        thread = thread.moveTo(inner_r_adj, -pitch/2 + z_off - inner_z_budge)
        thread = thread.lineTo(outer_r, -(z_off + d_mid))
        thread = thread.lineTo(outer_r, z_off + d_mid)
        thread = thread.lineTo(inner_r_adj, pitch/2 - z_off + inner_z_budge)
        thread = thread.close()
        thread = thread.sweep(wire, isFrenet=True)
        threads = thread
        for addl_start in range(1, n_starts):
            thread = thread.rotate(axisStartPoint=(0,0,0),
                                   axisEndPoint=(0,0,1),
                                   angleDegrees=360/n_starts)
            threads = threads.union(thread)

    square_shave = cq.Workplane("XY")
    square_shave = square_shave.box(length=outer_r*3, width=outer_r*3,
                                    height=pitch*2, centered=True)
    square_shave = square_shave.translate((0,0,-pitch)) # Because centered.
    # Always cut the top and bottom square.  Otherwise things don't play nice.
    threads = threads.cut(square_shave)

    if bottom_lead_in:
        delta_r = outer_r - inner_r
        rise = math.tan(__deg2rad(metric_thread_angle())) * delta_r
        lead_in = cq.Workplane("XZ")
        lead_in = lead_in.moveTo(inner_r - delta_r, -rise)
        lead_in = lead_in.lineTo(outer_r + delta_r, 2 * rise)
        lead_in = lead_in.lineTo(outer_r + delta_r, -pitch - rise)
        lead_in = lead_in.lineTo(inner_r - delta_r, -pitch - rise)
        lead_in = lead_in.close()
        lead_in = lead_in.revolve()
        threads = threads.cut(lead_in)

    # This was originally a workaround to the anomalous B-rep computation where
    # the top of base cylinder is flush with top of threads, without the use of
    # lead-in.  It turns out that preferring the use of the 'render_cyl_early'
    # strategy alleviates other problems as well.
    render_cyl_early = (base_cylinder and ((not top_relief) and
                                           (not (cyl_extend_top > 0.0)) and
                                           (not envelope)))
    render_cyl_late = (base_cylinder and (not render_cyl_early))
    if render_cyl_early:
        cyl = cq.Workplane("XY")
        cyl = cyl.circle(radius=inner_r)
        cyl = cyl.extrude(until=length+pitch+cyl_extend_bottom)
        # Make rotation of cylinder consistent with non-workaround case.
        cyl = cyl.rotate(axisStartPoint=(0,0,0), axisEndPoint=(0,0,1),
                         angleDegrees=-(360*t_start/(pitch*n_starts)))
        cyl = cyl.translate((0,0,-t_start+(z_start-cyl_extend_bottom)))
        threads = threads.union(cyl)

    # Next, make cuts at the top.
    square_shave = square_shave.translate((0,0,pitch*2+t_length))
    threads = threads.cut(square_shave)

    if top_lead_in:
        delta_r = outer_r - inner_r
        rise = math.tan(__deg2rad(metric_thread_angle())) * delta_r
        lead_in = cq.Workplane("XZ")
        lead_in = lead_in.moveTo(inner_r - delta_r, t_length + rise)
        lead_in = lead_in.lineTo(outer_r + delta_r, t_length - (2 * rise))
        lead_in = lead_in.lineTo(outer_r + delta_r, t_length + pitch + rise)
        lead_in = lead_in.lineTo(inner_r - delta_r, t_length + pitch + rise)
        lead_in = lead_in.close()
        lead_in = lead_in.revolve()
        threads = threads.cut(lead_in)

    # Place the threads into position.
    threads = threads.translate((0,0,t_start))
    if (not envelope):
        threads = threads.rotate(axisStartPoint=(0,0,0), axisEndPoint=(0,0,1),
                                 angleDegrees=360*t_start/(pitch*n_starts))

    if render_cyl_late:
        cyl = cq.Workplane("XY")
        cyl = cyl.circle(radius=inner_r)
        cyl = cyl.extrude(until=length+cyl_extend_bottom+cyl_extend_top)
        cyl = cyl.translate((0,0,z_start-cyl_extend_bottom))
        threads = threads.union(cyl)

    return threads


###############################################################################
# Generates female threads without a base tube, unless 'base_tube_od' is set to
# something which is sufficiently greater than 'diameter' parameter.  Please
# note that 'use_epsilon' is activated by default, which causes a slight budge
# in the major radius, outwards, so that overlaps would be created with outer
# tubes.  (Does not affect thread profile inside of tube or beyond extents.)
###############################################################################
def internal_metric_thread(diameter,  # Required parameter, e.g. 3.0 for M3x0.5
                           pitch,     # Required parameter, e.g. 0.5 for M3x0.5
                           length,    # Required parameter, e.g. 2.0.
                           z_start=0.0,
                           n_starts=1,
                           bottom_chamfer=False, # Chamfer is at same angle as
                           top_chamfer   =False, # thread, namely 30 degrees.
                           bottom_relief=False, # Add relief groove to start or
                           top_relief   =False, # end of threads (shorten).
                           use_epsilon=True, # For outer cylinder overlap.
                           # The base tube outer diameter must be sufficiently
                           # large for tube to be rendered.  Otherwise ignored.
                           base_tube_od=-1.0,
                           tube_extend_bottom=-1.0,
                           tube_extend_top=-1.0,
                           envelope=False): # Draw only envelope, don't cut.

    tube_extend_bottom = max(0.0, tube_extend_bottom)
    tube_extend_top    = max(0.0, tube_extend_top)

    z_off              = (1.0 - __metric_thread_effective_ratio()) * pitch / 4
    t_start            = z_start
    t_length           = length
    if bottom_relief:
        t_start        = t_start  + (2 * z_off)
        t_length       = t_length - (2 * z_off)
    if top_relief:
        t_length       = t_length - (2 * z_off)
    outer_r            = metric_thread_major_radius(diameter,pitch,
                                                    internal=True)
    inner_r            = metric_thread_minor_radius(diameter,pitch,
                                                    internal=True)
    epsilon            = 0
    outer_r_adj        = outer_r
    outer_z_budge      = 0
    if use_epsilon:
        # High values of 'epsilon' sometimes cause entire starts to disappear.
        epsilon        = (z_off/5) / math.tan(__deg2rad(metric_thread_angle()))
        outer_r_adj    = outer_r + epsilon
        outer_z_budge  = math.tan(__deg2rad(metric_thread_angle())) * epsilon

    if envelope:
        threads = cq.Workplane("XZ")
        threads = threads.moveTo(outer_r_adj, -pitch)
        threads = threads.lineTo(inner_r, -pitch)
        threads = threads.lineTo(inner_r, t_length + pitch)
        threads = threads.lineTo(outer_r_adj, t_length + pitch)
        threads = threads.close()
        threads = threads.revolve()

    else: # Not envelope, cut the threads.
        wire = cq.Wire.makeHelix(pitch=pitch*n_starts,
                                 height=t_length+pitch,
                                 radius=inner_r)
        wire = wire.translate((0,0,-pitch/2))
        wire = wire.rotate(startVector=(0,0,0), endVector=(0,0,1),
                           angleDegrees=360*(-pitch/2)/(pitch*n_starts))
        thread = cq.Workplane("XZ")
        thread = thread.moveTo(outer_r_adj, -pitch/2 + z_off - outer_z_budge)
        thread = thread.lineTo(inner_r, -z_off)
        thread = thread.lineTo(inner_r, z_off)
        thread = thread.lineTo(outer_r_adj, pitch/2 - z_off + outer_z_budge)
        thread = thread.close()
        thread = thread.sweep(wire, isFrenet=True)
        threads = thread
        for addl_start in range(1, n_starts):
            thread = thread.rotate(axisStartPoint=(0,0,0),
                                   axisEndPoint=(0,0,1),
                                   angleDegrees=360/n_starts)
            threads = threads.union(thread)
        # Rotate so that the external threads would align.
        threads = threads.rotate(axisStartPoint=(0,0,0), axisEndPoint=(0,0,1),
                                 angleDegrees=180/n_starts)

    square_len = max(outer_r*3, base_tube_od*1.125)
    square_shave = cq.Workplane("XY")
    square_shave = square_shave.box(length=square_len, width=square_len,
                                    height=pitch*2, centered=True)
    square_shave = square_shave.translate((0,0,-pitch)) # Because centered.
    # Always cut the top and bottom square.  Otherwise things don't play nice.
    threads = threads.cut(square_shave)

    if bottom_chamfer:
        delta_r = outer_r - inner_r
        rise = math.tan(__deg2rad(metric_thread_angle())) * delta_r
        chamfer = cq.Workplane("XZ")
        chamfer = chamfer.moveTo(inner_r - delta_r, 2 * rise)
        chamfer = chamfer.lineTo(outer_r + delta_r, -rise)
        chamfer = chamfer.lineTo(outer_r + delta_r, -pitch - rise)
        chamfer = chamfer.lineTo(inner_r - delta_r, -pitch - rise)
        chamfer = chamfer.close()
        chamfer = chamfer.revolve()
        threads = threads.cut(chamfer)

    # This was originally a workaround to the anomalous B-rep computation where
    # the top of base tube is flush with top of threads w/o the use of chamfer.
    # This is now being made consistent with the 'render_cyl_early' strategy in
    # external_metric_thread() whereby we prefer the "render early" plan of
    # action even in cases where a top chamfer or lead-in is used.
    render_tube_early = ((base_tube_od > (outer_r * 2)) and
                         (not top_relief) and
                         (not (tube_extend_top > 0.0)) and
                         (not envelope))
    render_tube_late = ((base_tube_od > (outer_r * 2)) and
                        (not render_tube_early))
    if render_tube_early:
        tube = cq.Workplane("XY")
        tube = tube.circle(radius=base_tube_od/2)
        tube = tube.circle(radius=outer_r)
        tube = tube.extrude(until=length+pitch+tube_extend_bottom)
        # Make rotation of cylinder consistent with non-workaround case.
        tube = tube.rotate(axisStartPoint=(0,0,0), axisEndPoint=(0,0,1),
                           angleDegrees=-(360*t_start/(pitch*n_starts)))
        tube = tube.translate((0,0,-t_start+(z_start-tube_extend_bottom)))
        threads = threads.union(tube)

    # Next, make cuts at the top.
    square_shave = square_shave.translate((0,0,pitch*2+t_length))
    threads = threads.cut(square_shave)

    if top_chamfer:
        delta_r = outer_r - inner_r
        rise = math.tan(__deg2rad(metric_thread_angle())) * delta_r
        chamfer = cq.Workplane("XZ")
        chamfer = chamfer.moveTo(inner_r - delta_r, t_length - (2 * rise))
        chamfer = chamfer.lineTo(outer_r + delta_r, t_length + rise)
        chamfer = chamfer.lineTo(outer_r + delta_r, t_length + pitch + rise)
        chamfer = chamfer.lineTo(inner_r - delta_r, t_length + pitch + rise)
        chamfer = chamfer.close()
        chamfer = chamfer.revolve()
        threads = threads.cut(chamfer)

    # Place the threads into position.
    threads = threads.translate((0,0,t_start))
    if (not envelope):
        threads = threads.rotate(axisStartPoint=(0,0,0), axisEndPoint=(0,0,1),
                                 angleDegrees=360*t_start/(pitch*n_starts))

    if render_tube_late:
        tube = cq.Workplane("XY")
        tube = tube.circle(radius=base_tube_od/2)
        tube = tube.circle(radius=outer_r)
        tube = tube.extrude(until=length+tube_extend_bottom+tube_extend_top)
        tube = tube.translate((0,0,z_start-tube_extend_bottom))
        threads = threads.union(tube)

    return threads
