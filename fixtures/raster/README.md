# Raster fixtures

`alkmaar_dem.asc` is a deliberately small 5-by-5 WGS 84 Arc/Info ASCII Grid
with a matching projection sidecar. `alkmaar_values.asc` is an aligned numeric
grid for repeated-input and zonal-statistics cases. `alkmaar_zones.asc` is an
aligned integer zone grid containing zones 1, 2, and 3. They cover the same
Alkmaar test area as the vector fixtures and are readable without binary
tooling.

`alkmaar_dem.tif` is the same 5-by-5 DEM encoded as a small GeoTIFF for OTB
process descriptions that advertise TIFF, JPEG, or PNG image inputs. It was
generated with GDAL 3.0.4:

```bash
gdal_translate -of GTiff -a_srs OGC:CRS84 \
  alkmaar_dem.asc alkmaar_dem.tif
```

The older selected `Gdal_*` process descriptions accept server-side filenames
rather than uploaded complex inputs. For the local Docker profile, run
`python3 scripts/stage_zoo_fixtures.py` to copy this fixture below ZOO's
configured `dataPath` before executing those cases.
