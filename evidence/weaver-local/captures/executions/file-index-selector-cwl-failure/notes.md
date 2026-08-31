# Valid input reaches a broken built-in CWL output definition

The request supplies two inline text files and a valid index. Weaver returned a
failed job document with HTTP 400 for the synchronous execution.

The job log reports: `Multiple matches for output item that is a single file.`
The built-in produces more than one matching file while its CWL output expects
one. This is a process-package defect, not invalid end-user input.
