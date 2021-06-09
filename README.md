# Integration

This repository contains Fuchsia's Global Integration manifest files.

## Making changes

All changes should be made to the [internal version] of this repository.
Our infrastructure automatically updates this version when the internal one
changes.

Currently all changes must be made by a Google employee. Non-Google employees
wishing to make a change can ask for assistance via the IRC channel `#fuchsia`
on Freenode.

## Obtaining the source

First install [Jiri].

Next run:

```sh
$ jiri init
$ jiri import minimal https://fuchsia.googlesource.com/integration
$ jiri update
```

## Third party

Third party projects should have their own subdirectory in `./third_party`.

[internal version]: https://goto.google.com/fuchsia-internal-integration
[Jiri]: https://fuchsia.googlesource.com/jiri#Bootstrapping
