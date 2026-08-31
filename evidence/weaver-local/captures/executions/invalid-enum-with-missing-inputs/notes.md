# Invalid enum value is not the first reported problem

`stringInput` only allows `Value1`, `Value2`, or `Value3`, but this request uses
`NotAllowed` and omits the remaining required inputs. Weaver reports the next
missing input, `measureInput`, rather than the invalid enum value.

This does not prove that Weaver would execute a complete request containing the
invalid value. It shows that one server error may describe only one of several
problems. The client should still validate the enum from the process
description and should present the server's returned message as-is.
