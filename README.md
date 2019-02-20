Cave World
===

Students' project.

# How to run
## Requirements
Only `websockets` is required which can be installed manually:
`pip install --user websockets`
or from the provided `requirements.txt`
`pip install --user -r requirements.txt`

## Server
`python -m server [address [port]]`
To start the server on a different `address` than localhost or different `port`
than 5505 the additional arguments can be provided.

The terms in square brackets [] are optional

## Client
`python -m client [address [port]]`
To connect to a server different than localhost:5505 the `address` and `port`
can be provided.

## Building the docs
### Requirements
- sphinx
### Building
`./build_doc.sh`
