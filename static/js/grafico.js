function builChart(data, _title_legenda) {
    Highcharts.chart("container-high", {
        credits: {
            enabled: false
        },
        chart: {
            type: 'line',
            zoomType: 'y',
            style: {
                fontFamily: 'Calibri'
            }
        },
        title: {
            text: ''
        },
        yAxis: {
            title: {
                text: 'Presupuesto Institucional Modificado (S/)',
                style: {
                    color: "#000000"
                }
            },
            lineColor: "#000000",
            lineWidth: 1
        },
        xAxis: {
            accessibility: {
                rangeDescription: 'Range: 2015 to 2020'
            },
            labels: {
                style: {
                    fontSize: "18px",
                    color: "#000000"
                }
            },
            lineColor: "#000000"
        },

        legend: {
            borderColor: "#999999",
            width: 232,
            borderWidth: 1,
            borderRadius: 8,
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            title: {
                text: _title_legenda,
                style: {
                    fontStyle: 'normal',
                    fontSize: "14px"
                }
            },
        },

        plotOptions: {
            line: {
                dataLabels: {
                    enabled: true,
                    style: {
                        fontSize: '14px'
                    }
                },
                enableMouseTracking: true
            },

            series: {
                color: '#9b59b6',
                label: {
                    connectorAllowed: true
                },
                pointStart: 2012
            }
        },
        series: data,
        tooltip: {

            formatter: function() {
                let dev = this.series.userOptions.dev[this.point.index];
                let pim = this.y
                return '<div class="columns v-centered"><div class="column"><b>Presupuesto:' + numComas(pim) + '</b><br/><b>Devengado:' + numComas(dev) + '</b><br/></div>' + avance_per(this.point.index, avance(pim, dev))

            },
            useHTML: true

        }

    });
}

function ReDrawChart(sw) {
    var obj = document.getElementById('container-high');
    var chart = Highcharts.charts[obj.getAttribute('data-highcharts-chart')];
    let btn = document.getElementById('btnShow');
    if (sw) {
        chart.series.forEach(function(item, index) {
            item.setVisible(true, false);
        });
        chart.redraw();
        btn.innerHTML = 'Desactivar todo';
    } else {
        SetGrafico();
        btn.innerHTML = 'Activar todo';
    }
}

function avance_per(t, per) {
    let color_per = '';
    if (t == 8) {
        if (per < 10)
            color_per = '#FF2424'
        else if (per >= 10 && per < 20)
            color_per = '#FFE527'
        else if (per >= 20)
            color_per = '#4EF22C'


    } else {
        if (per < 50)
            color_per = '#FF2424'
        else if (per >= 50 && per < 75)
            color_per = '#FFE527'
        else if (per >= 75)
            color_per = '#4EF22C'
    }
    return '<div class="column" style="background-color:' + color_per + ';"><span style="font-size: 14px;color: white;">' + per + '%</span></div></div>'
}