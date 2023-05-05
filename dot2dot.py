import argparse
import os
from typing import List, Sequence, Tuple

import numpy as np
import svgpathtools


def dist(pts1: Sequence[complex], pts2: Sequence[complex]) -> float:
  """Distance between two lists of points."""
  if not pts1 or not pts2:
    return float('inf')
  return min(abs(pt1 - pt2) for pt1 in pts1 for pt2 in pts2)


def nearest_pt_indices(pts1: Sequence[complex], pts2: Sequence[complex]
                       ) -> Tuple[int, int]:
  dists = [abs(pt1 - pt2) for pt1 in pts1 for pt2 in pts2]
  n = np.argmin(dists)
  pts2_idx = n % len(pts2)
  pts1_idx = n // len(pts2)
  return pts1_idx, pts2_idx


def path_to_pts(path) -> List[complex]:
  # TODO: include intermediate points if the path is too short.
  return [seg.point(0) for seg in path]


def combine_paths(paths) -> List[complex]:
  all_paths = []
  for path in paths:
    all_paths.extend(path.continuous_subpaths())
  print(f'SVG contains {len(all_paths)} continuous paths')

  if len(all_paths) == 1:
    return path_to_pts(all_paths[0])

  print(f'Attempting to combine paths.')

  # First, remove non-closed paths.
  i = 0
  while i < len(all_paths):
    if not all_paths[i].isclosed():
      print(f'Removed path {i} as it is non-closed.')
      del all_paths[i]
    else:
      i += 1

  all_pts = [path_to_pts(path) for path in all_paths]

  while len(all_pts) > 1:
    # Combine two closest paths. Note that both paths are closed.
    best_pair = None
    best_dist = float('inf')
    for i in range(len(all_pts)):
      for j in range(i):
        cur_dist = dist(all_pts[i], all_pts[j])
        if cur_dist < best_dist:
          best_pair = (i, j)
          best_dist = cur_dist
    print(f'Joining pair {best_pair} with dist {best_dist}.')
    pts1 = all_pts[best_pair[0]]
    pts2 = all_pts[best_pair[1]]
    idx_pts1, idx_pts2 = nearest_pt_indices(pts1, pts2)
    print(f'Splice point is {pts1[idx_pts1]} : {pts2[idx_pts2]}')
    pts_spliced = (
        pts1[:idx_pts1] + pts2[idx_pts2:] + pts2[:idx_pts2] + pts1[idx_pts1:])
    all_pts[best_pair[0]] = pts_spliced
    del all_pts[best_pair[1]]
    print(f'{len(all_pts)} path(s) remaining.')

    # Find splice point.

  return all_pts[0]


def make_dot2dot(paths, font_scale: float, min_dist: float
                 ) -> Tuple[str, svgpathtools.Path]:
  pts = combine_paths(paths)

  min_x = min(pt.real for pt in pts)
  min_y = min(pt.imag for pt in pts)
  max_x = max(pt.real for pt in pts)
  max_y = max(pt.imag for pt in pts)
  radius = max(max_x - min_x, max_y - min_y) / 400
  min_x -= 50 * radius
  min_y -= 50 * radius
  max_x += 50 * radius
  max_y += 50 * radius
  width = max_x - min_x
  height = max_y - min_y
  font_size = int(min(width, height) * 0.01 * font_scale) + 1

  print(f'Combined path contains {len(pts)} points')
  print(f'Width: {width}, Height: {height}, Font size: {font_size} px')

  # Remove points that are too close together
  i = 0
  while i < len(pts) - 1:
    if abs(pts[i] - pts[i + 1]) < radius * min_dist:
      del pts[i + 1]
    else:
      i += 1

  print(f'Reduced to {len(pts)} points after removing neighbors')

  dot2dot_svg = [
    f'<svg viewBox="{min_x} {min_y} {width} {height}" '
    'xmlns="http://www.w3.org/2000/svg">',
    '<style>',
    f'.num {{ font: {font_size}px sans-serif; }}',
    '</style>',
  ]

  for i, pt in enumerate(pts):
    dot2dot_svg.append(
      f'<circle cx="{pt.real}" cy="{pt.imag}" r="{radius}" />')
    if dist([pt], pts[:i]) < radius * 5:
      text_x = pt.real
      text_y = pt.imag + 6 * radius
    else:
      text_x = pt.real + 2 * radius
      text_y = pt.imag
    dot2dot_svg.append(
      f'<text x="{text_x}" y="{text_y}" class="num">{i + 1}</text>')
  dot2dot_svg.append('</svg>')
  dot2dot_svg = '\n'.join(dot2dot_svg)

  solution_path = svgpathtools.Path()
  for i in range(len(pts) - 1):
    solution_path.append(svgpathtools.Line(pts[i], pts[i + 1]))

  return dot2dot_svg, solution_path


def main():
  parser = argparse.ArgumentParser(prog='dot2dot',
                                   description='Generate Dot-to-Dot SVG files')
  parser.add_argument(
    'filename',
    help='Input SVG file from which the Dot-to-Dot is generated')
  parser.add_argument(
    '--font_scale',
    default=1,
    help='Increase or decrease font size. '
         'A floating-point value; default is 1.',
    type=float
  )
  parser.add_argument(
    '--min_dist',
    default=10,
    help='Minimum distance between consecutive points. Default is 10.',
    type=float
  )
  args = parser.parse_args()

  input_fname = args.filename
  paths, _ = svgpathtools.svg2paths(input_fname)
  dot2dot_svg, solution_path = make_dot2dot(paths, font_scale=args.font_scale,
                                            min_dist=args.min_dist)

  output_fname = os.path.splitext(args.filename)[0] + '_dot2dot.svg'
  with open(output_fname, 'wt') as f:
    f.write(dot2dot_svg)
  solution_fname = os.path.splitext(args.filename)[0] + '_solution.svg'
  svgpathtools.wsvg(solution_path, filename=solution_fname)


if __name__ == '__main__':
  main()
