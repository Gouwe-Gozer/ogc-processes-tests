#!/usr/bin/env python3
"""Generate the deterministic five-point LAS 1.2 fixture used by SAGA tests."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


POINTS = (
    (4.741, 52.626, 2.1),
    (4.752, 52.632, 3.4),
    (4.764, 52.627, 1.8),
    (4.747, 52.641, 4.2),
    (4.760, 52.638, 2.9),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("fixtures/pointcloud/five_points.las"),
        help="LAS fixture output path",
    )
    return parser.parse_args()


def fixed_ascii(value: str, length: int) -> bytes:
    encoded = value.encode("ascii")
    return encoded[:length].ljust(length, b"\0")


def build_las() -> bytes:
    scale_x, scale_y, scale_z = 0.000001, 0.000001, 0.001
    offset_x, offset_y, offset_z = 4.0, 52.0, 0.0
    xs, ys, zs = zip(*POINTS)

    header = bytearray()
    header.extend(b"LASF")
    header.extend(struct.pack("<HH", 0, 0))
    header.extend(b"\0" * 16)
    header.extend(struct.pack("<BB", 1, 2))
    header.extend(fixed_ascii("OGC Processes tests", 32))
    header.extend(fixed_ascii("generate_las_fixture.py", 32))
    header.extend(struct.pack("<HH", 237, 2026))
    header.extend(struct.pack("<HI", 227, 227))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<BH", 0, 20))
    header.extend(struct.pack("<I", len(POINTS)))
    header.extend(struct.pack("<5I", len(POINTS), 0, 0, 0, 0))
    header.extend(struct.pack("<3d", scale_x, scale_y, scale_z))
    header.extend(struct.pack("<3d", offset_x, offset_y, offset_z))
    header.extend(
        struct.pack(
            "<6d",
            max(xs),
            min(xs),
            max(ys),
            min(ys),
            max(zs),
            min(zs),
        )
    )
    if len(header) != 227:
        raise AssertionError(f"unexpected LAS header size: {len(header)}")

    records = bytearray()
    for x, y, z in POINTS:
        xi = round((x - offset_x) / scale_x)
        yi = round((y - offset_y) / scale_y)
        zi = round((z - offset_z) / scale_z)
        records.extend(
            struct.pack(
                "<iiiHBBbBH",
                xi,
                yi,
                zi,
                0,
                9,
                1,
                0,
                0,
                0,
            )
        )
    return bytes(header + records)


def main() -> int:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(build_las())
    print(f"generated {len(POINTS)} points in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
