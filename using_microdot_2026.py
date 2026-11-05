from microdot import Microdot, Response
import ujson as json
import time
import network
from machine import ADC,Pin
ADC20=ADC(Pin(20,Pin.IN) )

# ---------------- WIFI ----------------
ssid = 'PUACJ'
password = 'PUACJ2024'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)

ip = wlan.ifconfig()[0]
print("Servidor en: http://" + ip + "/")

# ---------------- APP ----------------
app = Microdot()

# Buffer de datos
datos = {
    "tiempo": [],
    "adc1": [],
    "umbral": 2
}


# ---------------- HTML (inline) ----------------
HTML = """ <!DOCTYPE html>
<html>
<head>
    <title>ESP32 Dashboard</title>
</head>

<body>

<h2>ADC</h2>
<h3 id="adc">0</h3>

<script>

function actualizar(){
    fetch('/refresh')
        .then(res => {return res.json();})
        .then(data => {
            let ultimo = data.adc1[data.adc1.length - 1];
            document.getElementById("adc").innerText = ultimo;
            console.log(ultimo);
        });
}

setInterval(actualizar, 1000);
</script>

</body>
</html>
"""

# ---------------- ROUTES ----------------

# Página principal
@app.route('/')
def index(request):
    return HTML, 200, {'Content-Type': 'text/html'}

# POST → recibir datos (como Flask)
@app.route('/refresh', methods=['GET', 'POST'])
def recibir_datos(request):
    global datos
    if request.method == 'GET':
        val_uv=ADC20.read_uv()
        VoltajeReal=val_uv*0.000001
        datos['adc1'].append(str(VoltajeReal))
        if len(datos["adc1"]) > 20:
            datos["adc1"].pop(0)
        return datos
        
# ---------------- RUN ----------------
app.run(host='0.0.0.0', port=80)

