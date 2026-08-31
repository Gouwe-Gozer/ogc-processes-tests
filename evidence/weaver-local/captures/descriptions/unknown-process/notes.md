# Unknown process

With `Accept: application/json`, Weaver returned a structured `NoSuchProcess`
HTTP 404 response containing the missing process ID. The same endpoint returns
HTML when the client does not request JSON; that form is captured separately.
