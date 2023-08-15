import usocket as socket
from common import *
from Wifi import wifi

html = """
<html lang="en"><head>
	<base target="_top">
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>LOCAT Map View</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
	<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/ion-rangeslider/2.3.1/css/ion.rangeSlider.min.css"/>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/ion-rangeslider/2.3.1/js/ion.rangeSlider.min.js"></script>
	<style>
		img.huechange { filter: hue-rotate(150deg); }
		.irs--flat .irs-bar {
			background-color: #29a0e5;
		}
		.irs--flat .irs-from, .irs--flat .irs-to, .irs--flat .irs-single {
			background-color: #29a0e5;
		}
		.irs--flat .irs-handle>i:first-child {
			background-color: #29a0e5;
		}
		.irs--flat .irs-from:before, .irs--flat .irs-to:before, .irs--flat .irs-single:before {
			border-top-color: #29a0e5;
		}
		.irs--flat .irs-handle.state_hover>i:first-child, .irs--flat .irs-handle:hover>i:first-child {
			background-color: #29a0e5;
		}
	</style>
</head>
<body>
<button id="refresh" style="margin:5px;" onclick="refreshPage()" type="button">Stop Refresh</button>
<div id="map" style="width: 100%%; height: 90%%; position: relative;" class="leaflet-container leaflet-touch leaflet-fade-anim leaflet-grab leaflet-touch-drag leaflet-touch-zoom" tabindex="0"></div>
<input type="text" class="js-range-slider" name="my_range" value="" />
<script>


	var array = %s;

	
	let map;
	let markers = [];
	let polyline;

	if (array.length > 0) {
		map = L.map('map').setView([array[array.length - 1].lat, array[array.length - 1].lon], 19);
	} else {
		map = L.map('map').setView([0, 0], 2);
	}

	L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	}).addTo(map);


	function clearAllObjectsOnMap() {
		if (polyline !== undefined) {
			// clear lines
			map.removeLayer(polyline);
			// clear all markers if any
			if (markers != null ){
			  for(var i=0; i < markers.length; i++){
				map.removeLayer(markers[i]);
			  }
			}
		
		}
	}


	function connectTheDots(data){
		var c = [];
		var number_of_elements = data.length - 1;
		var counter = 0;
		for(i in data) {
			var x = data[i].lat;
			var y = data[i].lon;
			// Set color for last Position
			if (number_of_elements === counter) {
				var marker = L.marker([data[i].lat, data[i].lon]).addTo(map).bindPopup("Date: " + data[i].date + "<br/>Time:" + data[i].time + "<br/>Precision:" + data[i].precision);
				marker._icon.classList.add("huechange");
				markers.push(marker);
			} else {
				var marker = L.marker([data[i].lat, data[i].lon]).addTo(map).bindPopup("Date: " + data[i].date + "<br/>Time:" + data[i].time + "<br/>Precision:" + data[i].precision);
				markers.push(marker);
			}
			counter = counter + 1;
			c.push([x, y]);
		}
		return c;
	}


	var numberValuesToDisplay = 3;
	if (array.length > 0) {
		$(".js-range-slider").ionRangeSlider({
			type: "double",
			min: 1,
			max: array.length,
			from: (array.length > numberValuesToDisplay) ? array.length - numberValuesToDisplay : 0,
			
			
			onStart: function (data) {
				// Called right after range slider instance initialised
				polyline = L.polyline(connectTheDots((array.length > numberValuesToDisplay) ? array.slice(-numberValuesToDisplay-1) : array)).addTo(map);
			},
			onChange: function (data) {
				// Called every time handle position is changed
				clearAllObjectsOnMap();
				polyline = L.polyline(connectTheDots((array.length > numberValuesToDisplay) ? array.slice(data.from-1, data.to) : array)).addTo(map);
			},
		});
	} else {
		$(".js-range-slider").ionRangeSlider({
			min: 0,
			max: 0,
		});
	}

	let refreshingPageVal;
	function refreshingPage(){
		 refreshingPageVal = setTimeout(function(){
			window.location.reload(1);
		}, 5000);
	}
	refreshingPage();

	
	function refreshPage()
	{
		if (document.getElementById("refresh").innerHTML  == "Stop Refresh" ) {
			document.getElementById("refresh").innerHTML  = "Start Refresh";
			clearTimeout(refreshingPageVal);
		} else {
			document.getElementById("refresh").innerHTML  = "Stop Refresh";
			refreshingPage();
		}
	}



</script>
</body>
</html>
"""
def run_web_server():

    print("connect to wifi")
    if wifi.connect_wifi():
        print("connected to wifi!")
    else:
        print("cannot connect to wifi!")

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(1)


    while True:
        client_socket, addr = server_socket.accept()

        request = client_socket.recv(4096).decode()
        response = ""

        if "GET /sensor" in request:
            print("Sensor request received...")
            # Read sensor data and create the response
            lines = ""
            with open("locations.txt", 'r') as file:
                lines = file.readlines()
            data = []

            for line in lines:
                line = line.strip()
                data.append(eval(line))

            response = html % (str(data),)

        # Send the response
        client_socket.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{}".format(response))
        client_socket.close()
