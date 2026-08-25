# Point-cloud fixture

`five_points.las` is a deterministic LAS 1.2 file containing five Alkmaar
points with elevation values. Regenerate it with:

```bash
python3 scripts/generate_las_fixture.py
```

The fixture is intentionally tiny and only exercises transport and SAGA LAS
import; it is not representative point-cloud data.
