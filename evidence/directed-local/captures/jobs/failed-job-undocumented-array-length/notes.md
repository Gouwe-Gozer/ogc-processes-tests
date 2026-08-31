# Failed asynchronous DIRECTED job

Source server: `directed-local`

The process description accepts an array without documenting its required
length. The processor requires exactly three values, so this two-value request
was accepted as an asynchronous job and then failed during execution.

The exchange shows two separate facts a client must preserve:

1. HTTP 201 and `status: accepted` mean only that the job was created.
2. The later job status contains the processor's useful validation message.

The job ID and job URL are replaced by placeholders. Timestamps and all other
response fields are kept as observed.
