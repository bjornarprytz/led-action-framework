let bar_composite_chart = new Chart ({
	parent: "#chart-composite-1",
	title: "Week Overview",
	data: week_composite,
	type: 'bar',
	height: 180,
	is_navigable: 1,
	is_series: 1
	// region_fill: 1
});

let line_composite_chart1 = new Chart ({
	parent: "#chart-composite-2",
	data: line_composite_temperature,
	type: 'line',
	height: 180,
	is_series: 1
});



bar_composite_chart.parent.addEventListener('data-select', (e) => {
	line_composite_chart1.update_values([temperature[e.index]]);
});
