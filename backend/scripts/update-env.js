const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('\n🔄 Update Env Script: Actualizando configuración del Frontend...');

try {
  // 1. Obtener APIs de LocalStack usando AWS CLI
  // Asumimos que aws cli está disponible ya que el usuario lo usa manual
  const cmd = 'aws apigateway get-rest-apis --endpoint-url=http://localhost:4566 --output json';
  const stdout = execSync(cmd).toString();
  const data = JSON.parse(stdout);
  
  // 2. Buscar nuestra API. El nombre del stack es 'pln-filter-backend-local', 
  // APIGateway en serverless-localstack suele nombrarla 'local-<service>'
  const apiName = 'local-pln-filter-backend';
  const api = data.items.find(item => item.name === apiName);
  
  if (!api) {
    console.error(`❌ No se encontró la API "${apiName}" en LocalStack. APIs disponibles: ${data.items.map(i => i.name).join(', ')}`);
    process.exit(0); // No fallar el deploy, solo avisar
  }
  
  const apiId = api.id;
  const newUrl = `http://localhost:4566/restapis/${apiId}/local/_user_request_`;
  console.log(`✅ API ID detectada: ${apiId}`);
  
  // 3. Ruta al archivo .env del frontend (subir un nivel desde backend/scripts, luego ir a frontend)
  const envPath = path.resolve(__dirname, '../../frontend/.env');
  
  if (!fs.existsSync(envPath)) {
      console.error(`❌ No se encontró el archivo .env en: ${envPath}`);
      process.exit(0);
  }
  
  // 4. Leer y actualizar
  let envContent = fs.readFileSync(envPath, 'utf8');
  
  const regex = /^VITE_API_URL=.*$/m;
  const newLine = `VITE_API_URL=${newUrl}`;
  
  if (regex.test(envContent)) {
    // Si ya existe y es diferente, actualizamos
    if (!envContent.includes(newLine)) {
        envContent = envContent.replace(regex, newLine);
        fs.writeFileSync(envPath, envContent);
        console.log(`📝 Frontend .env actualizado con nueva URL.`);
    } else {
        console.log(`👌 La URL en .env ya es correcta.`);
    }
  } else {
    // Si no existe, agregamos
    envContent += `\n${newLine}`;
    fs.writeFileSync(envPath, envContent);
    console.log(`📝 Frontend .env actualizado (Variable agregada).`);
  }
  
  console.log(`🔗 VITE_API_URL=${newUrl}\n`);

} catch (error) {
  console.error('⚠️ Advertencia: No se pudo actualizar el .env automáticamente.');
  console.error('Detalle:', error.message);
  // No hacemos exit(1) para no romper el flujo de deploy si esto falla
}
