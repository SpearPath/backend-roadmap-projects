$pythonExe = (Get-Command python -ErrorAction SilentlyContinue)?.Source
if (-not $pythonExe) {
    $pythonExe = "C:\Users\dmtol\AppData\Local\Programs\Python\Python313\python.exe"
}
& $pythonExe -m unittest discover tests -v
