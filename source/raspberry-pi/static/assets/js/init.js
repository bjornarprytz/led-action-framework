// Composite Chart
// ================================================================================
let report_count_list = [8, 8, 8, 8, 8, 8,
	8];

	function Get(yourUrl){
		var Httpreq = new XMLHttpRequest(); // a new request
		Httpreq.open("GET",yourUrl,false);
		Httpreq.send(null);
		return Httpreq.responseText;
	}

let week = JSON.parse(Get("weeks"));

let times_of_day = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
										"06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
										"12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
										"18:00", "19:00", "20:00", "21:00", "22:00", "23:00"];

let temperature = JSON.parse(Get("temperature"))
let humidity = JSON.parse(Get("humidity"));
let co2 = JSON.parse(Get("carbon_dioxide"));

let bar_composite_data = {
	labels: week,
	datasets: [{
		"title": "Events",
		"color": "yellow",
		"values": report_count_list,
		// "formatted": report_count_list.map(d => d + " reports")
	}]
};

let line_composite_temperature = {
	labels: times_of_day,
	datasets: [{
		"title": "Temperature",
		"color": "green",
		"values": temperature[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};

let line_composite_humidity = {
	labels: times_of_day,
	datasets: [{
		"title": "Humidity",
		"color": "blue",
		"values": humidity[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};

let line_composite_co2 = {
	labels: times_of_day,
	datasets: [{
		"title": "CO2",
		"color": "red",
		"values": co2[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};
