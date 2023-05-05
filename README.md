# Dot-to-Dot Generator

Converts silhouette SVGs to dot-to-dog SVGs.

## Usage

```commandline
python dot2dot.py [-h] [--font_scale FONT_SCALE] [--min_dist MIN_DIST] filename
```

| Argument                  | Description                                           |
|---------------------------|-------------------------------------------------------|
| `filename`                | Input SVG file from which the Dot-to-Dot is generated |
| `-h`, `--help`            | Show help message and exit |
| `--font_scale FONT_SCALE` | Increase or decrease font size. A floating-point value; default is 1. |
| `--min_dist MIN_DIST`     | Minimum distance between consecutive points. Default is 10. |

## Examples

### Input

![Input svg](examples/sherlock.svg)

### Output

![Output svg](examples/sherlock_dot2dot.svg)
