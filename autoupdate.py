import json
from urllib import request
import in_place

resp = request.urlopen('https://github.com/nyfair/nginx-nosni/raw/master/old.json')
x = json.loads(resp.read().decode('utf-8'))
mingw = x['Mingw-w64'][:x['Mingw-w64'].find('ucrt')+4]
with in_place.InPlace('.github/workflows/toolchain.yml', newline='') as f:
  for l in f:
    if (i:=l.find('key: mcf_')) > -1:
      l = '%s%s\n' % (l[:i+9], mingw)
    elif (i:= l.find('curl')) > -1:
      l = '%s%s.7z\n' % (l[:i+55], x['Mingw-w64'])
    f.write(l)
pkgs = {}
pkgs['mcfgthread'] = mingw[:8]
# pkgs['libvorbis_aotuv-dev'] = x['libvorbis']
pkgs['luajit'] = x['LuaJIT']
pkgs['python-embed'] = x['Python']
pkgs['vapoursynth'] = x['VapourSynth'][1:]
pkgs['ffmpeg'] = x['ffmpeg']
pkgs['mpv'] = x['mpv']
for p in ['ffnvcodec', 'freetype2', 'fribidi', 'harfbuzz', 'lame', 'lcms2', 'libass', 'libbluray', 'libdvdcss', 'libdvdnav', 'libogg', 'libplacebo', 'opus', 'shaderc', 'spirv-cross', 'vulkan']:
  pkgs['%s-dev' % p] = x[p]
for p in pkgs:
  with in_place.InPlace('%s/PKGBUILD' % p, newline='') as f:
    for l in f:
      if l.startswith('pkgver'):
        l = 'pkgver=%s\n' % pkgs[p]
      f.write(l)
pkgs['luajit-dev'] = x['LuaJIT']
pkgs['ffmpeg-dev'] = x['ffmpeg']
for t in ['batch-stable.yml', 'batch-bleeding_edge-weekly.yml']:
  with in_place.InPlace('.github/workflows/%s' % t, newline='') as f:
    for l in f:
      if (i:=l.find('key: mcf_')) > -1:
        l = '%s%s\n' % (l[:i+9], mingw)
      elif (i:=l.find('/dev/')) > -1:
        r = l.find('-1-x86_64')
        rr = l.rfind('-', i, r)
        p = l[i+5:rr]
        if p in pkgs:
          l = '%s%s-%s%s' % (l[:i+5], p, pkgs[p], l[r:])
      elif (i:=l.find('/latest/')) > -1:
        r = l.find('-1-x86_64')
        rr = l.rfind('-', i, r)
        p = l[i+8:rr]
        if p in pkgs:
          l = '%s%s-%s%s' % (l[:i+8], p, pkgs[p], l[r:])
      f.write(l)