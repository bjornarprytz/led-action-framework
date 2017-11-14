


// Children(temp, hum, co2) Chart Lables
let times_of_day = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
										"06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
										"12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
										"18:00", "19:00", "20:00", "21:00", "22:00", "23:00"];

// Parent Chart Lables
let week = JSON.parse(Get("weeks"));

// Parent Chart Values (dummy)
let parent_values = [8, 8, 8, 8, 8, 8, 8];

let temp_day = JSON.parse(Get("temperature"));
let hum_day = JSON.parse(Get("humidity"));
let co2_day = JSON.parse(Get("carbon_dioxide"));

let week_composite = {
	labels: week,
	datasets: [{
		"title": "Events",
		"color": "yellow",
		"values": parent_values,
		// "formatted": report_count_list.map(d => d + " reports")
	}]
};

let line_composite_temperature_day = {
	labels: times_of_day,
	datasets: [{
		"title": "Temperature",
		"color": color_temp,
		"values": temp_day[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};

let line_composite_humidity_day = {
	labels: times_of_day,
	datasets: [{
		"title": "Humidity",
		"color": color_hum,
		"values": hum_day[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};

let line_composite_co2_day = {
	labels: times_of_day,
	datasets: [{
		"title": "CO2",
		"color": color_co2,
		"values": co2_day[0]['values'],
		// "formatted": ["₹ 0.00", "₹ 0.00", "₹ 0.00", "₹ 61,500.00", "₹ 82,936.88", "₹ 24,010.00", "₹ 0.00", "₹ 0.00", "₹ 25,840.00", "₹ 5,08,048.82", "₹ 1,16,820.00", "₹ 0.00"],
	}]
};


let bar_composite_chart = new Chart ({
	parent: "#chart-composite-1",
	title: "Daily readings",
	data: week_composite,
	type: 'bar',
	height: 180,
	is_navigable: 1,
	is_series: 1
	// region_fill: 1
});

let co2_day_chart = new Chart ({
	parent: "#co2-day-chart",
	data: line_composite_co2_day,
	type: 'line',
	height: 180,
	is_series: 1
});

let temp_day_chart = new Chart ({
	parent: "#temp-day-chart",
	data: line_composite_temperature_day,
	type: 'line',
	height: 180,
	is_series: 1
});

let hum_day_chart = new Chart ({
	parent: "#hum-day-chart",
	data: line_composite_humidity_day,
	type: 'line',
	height: 180,
	is_series: 1
});


bar_composite_chart.parent.addEventListener('data-select', (e) => {
	co2_day_chart.update_values([co2_day[e.index]]);
  temp_day_chart.update_values([temp_day[e.index]]);
  hum_day_chart.update_values([hum_day[e.index]]);
});
