// Composite Chart
// ================================================================================
	function Get(yourUrl){
		var Httpreq = new XMLHttpRequest(); // a new request
		Httpreq.open("GET",yourUrl,false);
		Httpreq.send(null);
		return Httpreq.responseText;
	}

let color_temp = "green";
let color_hum = "blue";
let color_co2 = "red";
let color_co2_ext = 'violet'
