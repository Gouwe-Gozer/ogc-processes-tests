# Raster fixtures

| File | Contents |
|---|---|
| `alkmaar_dem.asc` | A 5-by-5 WGS 84 elevation grid |
| `alkmaar_values.asc` | A second aligned grid for repeated-input and statistics tests |
| `alkmaar_zones.asc` | An aligned integer grid containing zones 1, 2, and 3 |
| `alkmaar_dem.tif` | The same elevation grid stored as GeoTIFF for OTB tests |

The ASCII grids cover the same Alkmaar area as the vector fixtures. The
projection is stored in the matching sidecar file.

The GeoTIFF was generated with GDAL 3.0.4:

```bash
gdal_translate -of GTiff -a_srs OGC:CRS84 \
  alkmaar_dem.asc alkmaar_dem.tif
```

Some older `Gdal_*` processes expect filenames inside the ZOO container. After
starting ZOO, copy these fixtures with:

```bash
python3 scripts/stage_zoo_fixtures.py
```
