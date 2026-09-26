# CI-only software OpenGL. Nothing from this directory enters player archives.
$ErrorActionPreference = 'Stop'
if (-not $env:RUNNER_TEMP -or -not $env:GITHUB_ENV -or -not $env:GITHUB_PATH) {
    throw 'Run this setup only inside GitHub Actions.'
}
$destination = Join-Path $env:RUNNER_TEMP ('tidebound-ci-mesa-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $destination | Out-Null
$archive = Join-Path $destination 'mesa.7z'
$url = 'https://github.com/pal1000/mesa-dist-win/releases/download/26.2.1/mesa3d-26.2.1-release-msvc.7z'
$expected = '78a0305844074535e73dfb6dcb5eb2a65f1d9dc445102e1f4c3c3e97dace19bf'
Invoke-WebRequest -Uri $url -OutFile $archive -MaximumRetryCount 3
if ((Get-FileHash $archive -Algorithm SHA256).Hash -ne $expected) {
    throw 'Mesa CI dependency checksum mismatch'
}
& 7z x $archive "-o$destination" -y | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not extract the Mesa CI dependency' }
$driver = Join-Path $destination 'x64/opengl32.dll'
if (-not (Test-Path $driver)) { throw 'Missing x64 OpenGL library' }
"SDL_OPENGL_LIBRARY=$driver" | Out-File -FilePath $env:GITHUB_ENV -Append -Encoding utf8
'GALLIUM_DRIVER=llvmpipe' | Out-File -FilePath $env:GITHUB_ENV -Append -Encoding utf8
(Join-Path $destination 'x64') | Out-File -FilePath $env:GITHUB_PATH -Append -Encoding utf8
