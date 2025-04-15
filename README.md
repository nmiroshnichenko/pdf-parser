# PDF-Parser example
Compare structure of PDF files (finding key-value pairs).
Ignore content values — just their positioning.

## Run in Docker
### Build image from source
`docker build -t pdf-parser:latest .`

### Run for just parsing (output the ref file structure)
`DATADIR=/pdf-parser/data; docker run --rm -v "$PWD/data:$DATADIR" pdf-parser "$DATADIR"/example.pdf`

### Run for comparing
`DATADIR=/pdf-parser/data; docker run --rm -v "$PWD/data:$DATADIR" pdf-parser "$DATADIR"/example{,-equal,-equal-content,-modified-text,-modified-position,-modified-structure,-empty}.pdf`
