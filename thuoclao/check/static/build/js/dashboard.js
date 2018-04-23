$(window).load(function(){
    // Ajax Code Here
    (function update() {
        $.ajax({
//            url: '{% url "get_data" %}',
            url: '/ajax/get_data',
            dataType: 'json',
            success: function (data) {
//                alert(data[0]['max']);

                var dps_max = [];
                var dps_min = [];
                var chart = new CanvasJS.Chart("chartContainer1", {
                    exportEnabled: true,
                    title: {
//                        text: "HOST"
                    },
                    axisY: {
                        includeZero: false,
                        suffix: " ms"
                    },
                    data: [{
                        name: "Max",
                        type: "spline",
                        markerSize: 0,
                        xValueType: "dateTime",
                        showInLegend: true,
                        dataPoints: dps_max
                    },
                    {
                        name: "Min",
                        type: "spline",
                        markerSize: 0,
                        xValueType: "dateTime",
                        showInLegend: true,
                        dataPoints: dps_min
                    }]
                });

                var xVal = data[0]['time'];
                var yMaxVal = data[0]['max'];
                var yMinVal = data[0]['min'];
                console.log(xVal);
                console.log(yMaxVal);
                console.log(yMinVal);
//                var updateInterval = 1000;
                var dataLength = data.length;
                var updateChart = function (count) {
                    count = count || 1;
                    // count is number of times loop runs to generate random dataPoints.
                    for (var j = 0; j < count; j++) {
                        yMaxVal = data[j]['max'];
                        yMinVal = data[j]['min'];
                        xVal = data[j]['time'];
                        dps_max.push({
                            x: xVal,
                            y: yMaxVal
                        });
                        dps_min.push({
                            x: xVal,
                            y: yMinVal
                        });
//                        xVal++;
                    }
                    if (dps_max.length > dataLength) {
                        dps_max.shift();
                    }
                    chart.render();
                };

                updateChart(dataLength);
//                setInterval(function () { updateChart() }, updateInterval);
            },
            failure: function(data) {
                alert('Got an error dude');
            }
        }).then(function() {           // on completion, restart
           setTimeout(update, 1000);  // function refers to itself
        });
    })();
});

