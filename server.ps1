$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:8080/")
$listener.Start()
Write-Host "Servidor rodando em http://localhost:8080/"
try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $response = $context.Response
        $path = $context.Request.Url.LocalPath
        if ($path -eq "/" -or $path -eq "/index.html") {
            if (Test-Path "index.html") {
                $buffer = [System.IO.File]::ReadAllBytes((Join-Path (Get-Location) "index.html"))
                $response.ContentType = "text/html; charset=utf-8"
                $response.ContentLength64 = $buffer.Length
                $response.OutputStream.Write($buffer, 0, $buffer.Length)
            } else {
                $response.StatusCode = 404
            }
        } else {
            $response.StatusCode = 404
        }
        $response.Close()
    }
} finally {
    $listener.Stop()
}
