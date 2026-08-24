# Raster fixtures

`alkmaar_dem.asc` is a deliberately small 5-by-5 WGS 84 Arc/Info ASCII Grid
with a matching projection sidecar. It covers the same Alkmaar test area as
the vector fixtures and is readable without binary tooling.

The older selected `Gdal_*` process descriptions accept server-side filenames
rather than uploaded complex inputs. For the local Docker profile, run
`python3 scripts/stage_zoo_fixtures.py` to copy this fixture below ZOO's
configured `dataPath` before executing those cases.
