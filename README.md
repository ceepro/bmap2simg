# Bmap2simg
A tool for creating Android sparse image from a block map (bmap)

```
usage: bmap2simg [-h] [--version] [-q] [-d] image bmap output

A tool for creating Android sparse image files (.simg) from a block mapped file (.bmap)

positional arguments:
  image        the block mapped image to generate Android sparse image from (e.g. .wic, .img, .ext4, ..)
  bmap         the block map file (.bmap) for the image. Generated from bmaptools
  output       the output file for the generated Android sparse image file (.simg)

optional arguments:
  -h, --help   show this help message and exit
  --version    show program's version number and exit
  -q, --quiet  be quiet
  -d, --debug  print debugging information
```