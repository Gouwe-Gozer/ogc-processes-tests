# Unknown job

With `Accept: application/json`, Weaver returned a structured `NoSuchJob`
HTTP 404 response containing the requested job ID. This is more useful than a
generic HTTP error and can be shown to the user.
