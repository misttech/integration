# Integration

This repository contains Fuchsia's global integration manifest files.

## Obtaining the source

First install [Jiri].

Next run:

```sh
$ jiri init
$ jiri import minimal https://fuchsia.googlesource.com/integration
$ jiri update
```

## Third party Projects

Third party projects should have their own subdirectory in `./third_party`.

[Jiri]: https://fuchsia.googlesource.com/jiri#Bootstrapping
