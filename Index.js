// src/index.js

// Importa los módulos necesarios
const express = require('express');
const bodyParser = require('body-parser')
const { spawn } = require('child_process');
const ws = require('express-ws'); // Import ws library
const { getFuturesTokenprMiddleware, getFuturesCandlesticksDataMiddleware, getStatusAccountMiddlewere } = require('./src/infrastructure/adapters/binanceApiAdapter');
const { getExchangeMiddleware, getCandelsUMFutMiddleware,testConectionMiddleware,CreateTFR} = require('./src/infrastructure/adapters/binanceApiFutAdapter');
//importar TensorFlow para node   

const fs = require('fs');  
// Crea una instancia de Express
const app = express();  
const port = 3000;
ws(app);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));




// Connect and subscribe on route access
// app.ws('/ws', connectAndSubscribe);


app.get('/', (req, res) => {

  res.send('¡Bienvenido a la aplicación DATI!'); 
});

// app.ws('/ws/socket', (ws, req) => {
//   ws.on('connect', () => {
//     console.log('Cliente conectado');
//   });

//   ws.on('disconnect', () => {
//     console.log('Cliente desconectado');
//   });

//   ws.on('message', (message) => {
//     console.log('Mensaje recibido:', message);
//     ws.send('Mensaje de respuesta desde el servidor');
//   });
// });

app.get('/trainData', async (req, res) => {
    try {
      // Llama al middleware para obtener datos de velas y crear archivos de entrenamiento
      await getFuturesCandlesticksDataMiddleware(req, res, () => {}); 
  
      // Responde al cliente con un mensaje de éxito
      res.json({ message: 'Datos de entrenamiento creados correctamente.' });
    } catch (error) {
      // console.error('Error al crear datos de entrenamiento:', error);
      res.status(500).send({ error });
    }
  });


 // index route
// index.js
// index route
app.get('/fexchange', async (req, res) => {
  try {
    req.body = req.body || [];
    let datas = await getExchangeMiddleware(req, res, () => {}); // Await the promise
   
      req.body = await datas.exchangeInfo
      // console.log(req.body);
      // console.log(await req);
    let velas = await getCandelsUMFutMiddleware(req,res,()=>{})
    //   let candles = await getCandelsUMFut(await req,res,()=>{})
    console.log(await velas);
    nameDat = 'dataTrain'
    const dataFutFilePath = 'src\\trinity_ai\\datasets\\'+nameDat+'.json';

    // Overwrite the file with the new candles data
    fs.writeFileSync(dataFutFilePath, JSON.stringify(await velas), 'utf8');
  
    console.log(nameDat+'.json file created successfully!');
      console.log("fin velas")
    // // Send the response
     res.status(200).json(await velas)
  } catch (error) {
    console.error('Error in /fexchange route:', error);
    res.status(500).send({ message: 'Internal Server Error' });
  }
});

app.get('/run',async (req,res)=>{
  initializeAI()
  res.json({message:"Has iniciado Dati Con exito"})
})

app.get('/train',(req,res)=>{
  trainModel()
})

  // app.get('/acc',async (req,res)=>{
  //     await getStatusAccountMiddlewere(req,res,()=>{});
      
  // })

// Función para probar la conexión con Binance al iniciar la aplicación



async function testConection() {
  try {
    let conn = await testConectionMiddleware(); // Pass 'req' and 'res' to the middleware
   console.log('conexion a api correcta');
  } catch (error) {
    console.error(error); // Handle any errors from the middleware or service
    process.exit(1)
  }
}


  // Función para inicializar la AI de Python
async function initializeAI() {
    try {
      // Ejecutar el script de Python para inicializar la AI
      const pythonProcess = spawn('python', ['./src/run_trinity_model.py']);
      // Manejar la salida del script de Python
             // Handle output from the Python script
             pythonProcess.stdout.on('data', (data) => {
              console.log(`Salida del script de Python: ${data}`);
          });
  
          // Handle errors from the Python script
          pythonProcess.stderr.on('data', (data) => {
              console.error(`Error en el script de Python: ${data}`);
              // You can choose to handle the error differently here, 
              // for example, by logging it to a file or sending an alert.
              // process.exit(1); // Exit with an error code
          });
  
          // Wait for the Python script to finish
          await new Promise((resolve) => pythonProcess.on('close', resolve));
          
      pythonProcess.stderr.on('data', (data) => {
        console.error(`Error en el script de Python: ${data}`);
        process.exit(1);
      });
  
      // Esperar a que el script de Python termine
      await new Promise((resolve) => pythonProcess.on('close', resolve));
  
      console.log('AI de Python inicializada correctamente.');
    } catch (error) {
      console.error('Error al inicializar la AI de Python:', error);
      process.exit(1); // Cierra la aplicación con código de error
    }
  }


// Register the WebSocket connection middleware
// app.ws('/ws', webSocketConnection(wsServer));

// Inicia el servidor y prueba la conexión con Binance
app.listen(port, async () => {
    await testConection();
    await initializeAI()
    console.log(`La aplicación DATI está corriendo en http://localhost:${port}`);
    // console.log(`el Socket DATI está corriendo en http://localhost:8080`);
});
