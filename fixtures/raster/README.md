# Raster fixtures

`alkmaar_dem.asc` is a deliberately small 5-by-5 WGS 84 Arc/Info ASCII Grid
with a matching projection sidecar. It covers the same Alkmaar test area as
the vector fixtures and is readable without binary tooling.

A GeoTIFF derivative can be added when fixture delivery to the server has been
settled. The older selected `Gdal_*` process descriptions accept server-side
filenames rather than uploaded complex inputs, so simply publishing this file
does not necessarily make it usable by those wrappers.
