let bar_composite_chart = new Chart ({
	parent: "#chart-composite-1",
	title: "Hourly Readings",
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
  console.log("hey", e.index)
  console.log("hey", [co2_hour[e.index]['values']])
});
