# Result returned by reference

Process: `SAGA.grid_tools.0`
Source server: `zoo-local`

The request supplies a referenced raster and asks for the output with
`transmissionMode: reference`. The response returns an `href` and the declared
`image/tiff` media type.

The protocol core should expose the link and media type without treating the
link as inline raster data. Downloading or persisting the file is a separate
consumer action.
