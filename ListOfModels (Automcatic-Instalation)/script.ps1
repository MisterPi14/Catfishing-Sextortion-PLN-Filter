# 1. Obtener la lista de modelos ya instalados
Write-Host "Verificando modelos instalados..."
# Se obtiene solo la primera columna (el nombre del modelo) de la salida de 'ollama list'
$modelosInstalados = (ollama list | Select-Object -Skip 1 | ForEach-Object { $_.Split(' ')[0] })
Write-Host "Modelos encontrados: $($modelosInstalados.Count)"
echo ""

# 2. Leer la lista de modelos deseados desde models.txt
$modelosDeseados = Get-Content .\models.txt

# 3. Comparar y descargar solo los que faltan
foreach ($modelo in $modelosDeseados) {
    if ($modelosInstalados -notcontains $modelo) {
        Write-Host "--- El modelo '$modelo' no está instalado. Descargando... ---"
        ollama pull $modelo

        # 4. Enviar una notificación al terminar
        # Este comando crea una notificación nativa de Windows
        #$notificacion = "Descarga completada: $modelo"
        #powershell -Command "[void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [void] [System.Windows.Forms.MessageBox]::Show('$notificacion', 'Ollama Script', 'OK', 'Information')"

        Write-Host "--- Descarga de '$modelo' finalizada. ---"
        echo ""
    } else {
        Write-Host "--- El modelo '$modelo' ya está instalado. Omitiendo. ---"
        echo ""
    }
}

Write-Host "--- Proceso completado. Todos los modelos necesarios están instalados. ---"
Start-Sleep -Seconds 5