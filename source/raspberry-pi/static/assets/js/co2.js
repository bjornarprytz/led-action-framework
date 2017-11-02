let bar_composite_chart = new Chart ({
	parent: "#chart-composite-1",
	title: "Fireball/Bolide Events - Yearly (more than 5 reports)",
	data: bar_composite_data,
	type: 'bar',
	height: 180,
	is_navigable: 1,
	is_series: 1
	// region_fill: 1
});

let line_composite_chart1 = new Chart ({
	parent: "#chart-composite-2",
	data: line_composite_co2,
	type: 'line',
	height: 180,
	is_series: 1
});


bar_composite_chart.parent.addEventListener('data-select', (e) => {
	line_composite_chart1.update_values([co2[e.index]]);
	// line_composite_chart2.update_values([more_line_data[e.index]]);
	// line_composite_chart3.update_values([more_line_data[e.index]]);
});
