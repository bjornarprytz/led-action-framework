
// Children(temp, hum, co2) Chart Lables
let minutes = [":00", ":01", ":02", ":03", ":04", ":05", ":06", ":07", ":08", ":09",
							 ":10", ":11", ":12", ":13", ":14", ":15", ":16", ":17", ":18", ":19",
						 	 ":20", ":21", ":22", ":23", ":24", ":25", ":26", ":27", ":28", ":29",
						   ":30", ":31", ":32", ":33", ":34", ":35", ":36", ":37", ":38", ":39",
						   ":40", ":41", ":42", ":43", ":44", ":45", ":46", ":47", ":48", ":49",
						   ":50", ":51", ":52", ":53", ":54", ":55", ":56", ":57", ":58", ":59",];

// Parent Chart Lables
let recent = JSON.parse(Get("recent"));
// Parent Chart Values (dummy)
let parent_values = [8,8,8,8,8,8];


let temp_hour = JSON.parse(Get("temp_hour"));
let hum_hour = JSON.parse(Get("hum_hour"));
let co2_hour = JSON.parse(Get("co2_hour"));



let hour_composite = {
	labels: recent,
	datasets: [{
		"title": "Last Hours",
		"color": "yellow",
		"values": parent_values,
		// "formatted": report_count_list.map(d => d + " reports")
	}]
};

let line_composite_temperature_hour = {
	labels: minutes,
	datasets: [{
		"title": "Temperature",
		"color": color_temp,
		"values": temp_hour[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};

let line_composite_humidity_hour = {
	labels: minutes,
	datasets: [{
		"title": "Humidity",
		"color": color_hum,
		"values": hum_hour[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};

let line_composite_co2_hour = {
	labels: minutes,
	datasets: [{
		"title": "CO2",
		"color": color_co2,
		"values": co2_hour[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};

let bar_composite_chart = new Chart ({
	parent: "#chart-composite-1",
	title: "Readings each minute",
	data: hour_composite,
	type: 'bar',
	height: 180,
	is_navigable: 1,
	is_series: 1
	// region_fill: 1
});

let co2_hour_chart = new Chart ({
	parent: "#co2-hour-chart",
	data: line_composite_co2_hour,
	type: 'line',
	height: 180,
	is_series: 1
});

let temp_hour_chart = new Chart ({
	parent: "#temp-hour-chart",
	data: line_composite_temperature_hour,
	type: 'line',
	height: 180,
	is_series: 1
});

let hum_hour_chart = new Chart ({
	parent: "#hum-hour-chart",
	data: line_composite_humidity_hour,
	type: 'line',
	height: 180,
	is_series: 1
});


bar_composite_chart.parent.addEventListener('data-select', (e) => {
	co2_hour_chart.update_values([co2_hour[e.index]]);
  temp_hour_chart.update_values([temp_hour[e.index]]);
  hum_hour_chart.update_values([hum_hour[e.index]]);
});
