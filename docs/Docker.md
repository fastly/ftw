# Building and using Docker image

This document describes how to build and run a docker image containing
all the CRS tests with FTW.

## Building image

```
	% docker build -t ftw-test .
```

## Running the image

Run through the entire CRS v3 test corpus with `<hostname>` as the target. *NOTE:* the `-i` is required to attach stdin to the docker container.

```
	% docker run -i ftw-test -d <hostname>
```

Test individual rule files:

```
	% docker run -i ftw-test -d <hostname> -f - < mytest.yaml
```

If you are testing through the CDN, you can use `-F` to use the target specification has the host header.

```
        % docker run -i ftw-test -F -d <hostname> -f - < mytest.yaml
```
