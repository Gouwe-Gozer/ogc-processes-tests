# Point-cloud fixture

`five_points.las` is a LAS 1.2 file with five Alkmaar points and elevation
values. It tests base64 transfer and SAGA's LAS input without adding a large
binary file.

Regenerate it with:

```bash
python3 scripts/generate_las_fixture.py
```
