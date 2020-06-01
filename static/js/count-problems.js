// 告警线图
let AlertChart = echarts.init(document.getElementById('alert'));
let AlertChart2 = echarts.init(document.getElementById('alert2'));
let AlertChart3 = echarts.init(document.getElementById('alert3'));
let AlertChart4 = echarts.init(document.getElementById('alert4'));

String.prototype.format = function() {
    if (arguments.length === 0) return this;
    var param = arguments[0];
    var s = this;
    if (typeof (param) == 'object') {
        for (var key in param)
            s = s.replace(new RegExp("\\{" + key + "\\}", "g"), param[key]);
        return s;
    } else {
        for (var i = 0; i < arguments.length; i++)
            s = s.replace(new RegExp("\\{" + i + "\\}", "g"), arguments[i]);
        return s;
    }
};

function get_cards_sysdata(data, p_systems) {
    var cur_allsys_data = data.allsysdata.allsys_data;
    var ret = "";
    var systems = JSON.parse(p_systems);
    for (var s in systems) {
        ss = systems[s];
        var sys = cur_allsys_data['' + ss.fields.name + ''];
        ret += '<div class="col-lg-3 col-md-6">\n';
        if (sys.total_problems === 0) {
            ret += '<div class="panel panel-primary">\n';
        } else {
            ret += '<div class="panel panel-primary arrow_box_red">\n';
        }

        ret += '<div class="panel-heading"><div class="row">\n';
        var sdic = {sys_name: ss.fields.name, sys_desc: ss.fields.desc};
        if (sys.total_problems > 0) {
            ret += '<div class="col-xs-3">\n' +
                '<i class="fa fa-sitemap fa-3x"\n' +
                'aria-hidden="true"></i></div>\n' +
                '<div class="col-xs-9 text-right">\n';

            if (sdic.sys_desc) {
                ret += '<div class="panel-title"\n' +
                    'title="{sys_name} - {sys_desc}">{sys_desc}</div>'.format(sdic);
            } else {
                ret += '<div class="panel-title"\n' +
                    'title="{sys_name} - {sys_desc}">{sys_name}</div>'.format(sdic);
            }

            ret += '<div class="problem pull-left">\n' +
                '<span class="huge">' + sys.caution_problems + '</span>\n' +
                '<span style="color: #c1b690">个重要问题</span></div></div>';
        } else {
            ret += '<div class="col-xs-3">' +
                '<i class="fa fa-sitemap fa-3x" style="color: #afafaf"' +
                ' aria-hidden="true"></i></div>\n' +
                '<div class="col-xs-9 text-right">\n';

            if (sdic.sys_desc) {
                ret += '<div class="panel-title"  style="color: #afafaf"\n' +
                    'title="{sys_name} - {sys_desc}">{sys_desc}</div>'.format(sdic);
            } else {
                ret += '<div class="panel-title"  style="color: #afafaf"\n' +
                    'title="{sys_name} - {sys_desc}">{sys_name}</div>'.format(sdic);
            }

            ret += '<div class="problem pull-left">\n' +
                '<span class="huge2">' + sys.caution_problems + '</span>\n' +
                '<span style="color: #afafaf">个问题</span></div></div>';
        }

        ret += '</div>\n';
        ret += '</div>\n';
        // ###########<<

        sdic = {
            sys_id: ss.pk,
            surl: "/monitor/health/metric/system/{sys_id}/hosts/".format({sys_id: ss.pk}),
            total_services: sys.total_services,
            total_instances: sys.total_instances,
            total_items: sys.total_items
        };

        ret += '<a href="{surl}"><div class="my-panel-footer-total">组 <span>{total_services}&nbsp;&nbsp;</span>例 <span>{total_instances}&nbsp;&nbsp;</span>项 <span>{total_items}&nbsp;</span><br>'.format(sdic);
        if (sys.p3 > 0) {
            ret += '            <span class="fa fa-bell"\n' +
                '                  aria-hidden="true"\n' +
                '                  style="color: red"\n' +
                '                  data-toggle="tooltip"\n' +
                '                  data-placement="right"\n' +
                '                  title="严重"></span>';

        } else if (sys.p2 > 0){
            ret += '<span class="fa fa-bell"\n' +
                '                  aria-hidden="true"\n' +
                '                  style="color: darkorange"\n' +
                '                  data-toggle="tooltip"\n' +
                '                  data-placement="right"\n' +
                '                  title="中等"></span>\n';
        } else if (sys.p1 > 0){
            ret += '<span class="fa fa-bell"\n' +
                '                  aria-hidden="true"\n' +
                '                  style="color: #ffcc00"\n' +
                '                  data-toggle="tooltip"\n' +
                '                  data-placement="right"\n' +
                '                  title="一般"></span>';

        } else {
            ret += '            <span class="fa fa-bell"\n' +
                '                  aria-hidden="true"\n' +
                '                  style="color: #75d753"\n' +
                '                  data-toggle="tooltip"\n' +
                '                  data-placement="right"\n' +
                '                  title="正常"></span>';
        }

        ret += '&nbsp总&nbsp<span>' + sys.total_problems + '&nbsp;&nbsp;</span>';
        if (sys.p3 === 0){
            ret += '高&nbsp;<span style="color: grey">0&nbsp;&nbsp;</span>\n';
        } else {
            ret += '高&nbsp;<span style="color: red">' + sys.p3 + '&nbsp;&nbsp;</span>\n';
        }

        if (sys.p2 === 0) {
            ret += '中&nbsp;<span style="color: grey">0&nbsp;&nbsp;</span>\n';
        } else {
            ret += '中&nbsp;<span style="color: darkorange">' + sys.p2 + '&nbsp;&nbsp;</span>\n';
        }

        if (sys.p1 === 0) {
            ret += '低&nbsp;<span style="color: grey">0&nbsp;&nbsp;</span>\n';
        } else {
            ret += '低&nbsp;<span style="color: #ffcc00">' + sys.p1 + '&nbsp;&nbsp;</span>\n';
        }

        ret += '</div>\n';

        var sys_met_problems = sys.metric_problems;
        keys = Object.keys(sys_met_problems).sort();
        //keys.sort();
        // for (var met in sys_met_problems){
        for (var m in keys){
            let met = keys[m];
            let cur_met = sys_met_problems[met];
            ret += '<div class="panel-footer">\n';
            if (cur_met.p3 > 0) {
                ret += '<span class="fa fa-circle"\n' +
                    '                      aria-hidden="true"\n' +
                    '                      style="color: red"\n' +
                    '                      data-toggle="tooltip"\n' +
                    '                      data-placement="right"\n' +
                    '                      title="严重"></span>\n';
            } else if (cur_met.p2 > 0) {
                                ret += '<span class="fa fa-circle"\n' +
                    '                      aria-hidden="true"\n' +
                    '                      style="color: darkorange"\n' +
                    '                      data-toggle="tooltip"\n' +
                    '                      data-placement="right"\n' +
                    '                      title="中等"></span>\n';
            } else if (cur_met.p1 > 0){
                                ret += '<span class="fa fa-circle"\n' +
                    '                      aria-hidden="true"\n' +
                    '                      style="color: #ffcc00"\n' +
                    '                      data-toggle="tooltip"\n' +
                    '                      data-placement="right"\n' +
                    '                      title="一般"></span>\n';
            } else {
                ret += '<span class="fa fa-circle"\n' +
                    '                      aria-hidden="true"\n' +
                    '                      style="color: #75d753"\n' +
                    '                      data-toggle="tooltip"\n' +
                    '                      data-placement="right"\n' +
                    '                      title="正常"></span>\n';
            }

            ret += "" + met + ": ";
            if (cur_met.p3 === 0 ){
                ret += '<span style="color: grey">0 </span>\n';
            } else {
                ret += '<span style="color: red">' + cur_met.p3 + ' </span>\n';
            }
            ret += "/ ";

            if (cur_met.p2 === 0 ){
                ret += '<span style="color: grey">0 </span>\n';
            } else {
                ret += '<span style="color: darkorange">' + cur_met.p2 + ' </span>\n';
            }
            ret += "/ ";

            if (cur_met.p1 === 0 ){
                ret += '<span style="color: grey">0 </span>\n';
            } else {
                ret += '<span style="color: #ffcc00">' + cur_met.p1 + ' </span>\n';
            }
            ret += "</div>\n";
        }
        // ###<<
        ret += '</a></div>\n';
        ret += '</div>\n';
    }
    return ret;
}

function plat_view(thisObj) {
    Cookies.remove("aria_controls");
    let plat_id = thisObj.getAttribute('id');
    let plat_title = thisObj.text;
    plat = Cookies.get("plat");
    if (plat !== plat_id){
        Cookies.set("plat", plat_id);
        $('div[id="plat-title"] b').text(plat_title);
    }
    else {
        Cookies.remove("plat");
        $('div[id="plat-title"] b').text("平台概况");
    }
    $('.collapse:visible').hide();
    myinit();
    //window.location.reload();
}

function draw_cards(url) {
    $.get(url).done(function (resp) {
        var data = JSON.parse(resp);
        var ele_cards = document.getElementById("draw-cards");
        var cards_html = "";
        for (var x in data.allgrpdata) {
            grp = data.allgrpdata[x];
            cards_html += '<div class="col">\n' +
                '                            <div class="collapse multi-collapse"\n' +
                '                                 id="multiCollapse-' + grp.systemgroup.id + '">\n' +
                '                                <div class="card card-body">\n' +
                '                                    <div class="box-header">\n' +
                '                                        <hr class="h-divider">\n' +
                '                                        <p style="color: #878787">' +
                '平台: <button class="btn btn-info" id="' + grp.systemgroup.id + '" onclick="return plat_view(this);">' + grp.systemgroup.name + '</button></p>\n';

            cards_html += get_cards_sysdata(data, grp.systems);
            cards_html += '</div>\n';
            cards_html += '</div>\n';
            cards_html += '</div>\n';
            cards_html += '</div>\n';
        }

        ele_cards.innerHTML = cards_html;

        //
        let aria_controls = Cookies.get("aria_controls");
        if (typeof (aria_controls) !== "undefined") {
            $('.collapse[id="' + aria_controls + '"]').show();
        } else {
            if ((typeof (Cookies.get('plat')) !== "undefined")) {
                $('.collapse[id="multiCollapse-' + Cookies.get('plat') + '"]').show();
                return null;
            }
        }

    });
}

function latest5_host_info(url) {
    $.get(url).done(function (resp) {
        var data = JSON.parse(resp);
        var group_tags = document.getElementById("latest5-host-names");
        var host_names = ['<ul>'];

        if (0 !== data.length) {
            if (url.includes("hostid=")) {
                for (x = 0; x < data.length && x < data.length; x++) {
                    cur_html = '<li>' + data[x].problem.name + '</li>';
                    host_names.push(cur_html);
                }
            } else {
                for (x = 0; x < data.length && x < data.length; x++) {
                    cur_html = '<li><a target="_blank" href="/monitor/health/metric/host/' +
                        data[x].host_id + '/problems/">' + data[x].problem.instance + '</a>：<br>'
                        + data[x].problem.name + '</li>';
                    host_names.push(cur_html);
                }
            }

            host_names.push('</ul>');
            var tags_html = host_names.join('');
            group_tags.innerHTML = tags_html;
        } else {
            group_tags.innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" +
                "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;【无】<br><br><br>";
        }
    });
}

function lineHide(opt) {
    jQuery.each(opt.data, function (i, item) {
        if (item.value == 0) {
            item.label = {
                normal: {
                    show: false
                }
            };
            item.labelLine = {
                normal: {
                    show: false
                }
            };
        }
    });
}

function draw_histo(url) {
    $.get(url).done(function (resp) {
        let data = JSON.parse(resp);
        let x_data = [];
        let y_data = [];
        var index_now = 1;
        //var index_today = 1;
        var value_now = 0;
        var date_now = new Date();
        var date = new Date(Cookies.get('time-rng').split(' -- ')[1]);
        var str_today = date.getFullYear()
            + '-' + (date.getMonth() + 1)
            + '-' + date.getDate()
            + ' ' + date_now.getHours() + 'h';
            // + ' ' + date.getHours() + 'h';
        //data.forEach(function (v) {
        //        x_data.push(v.create_time);
        //        y_data.push(v.count);
        //    }
        //);
        String.prototype.replaceAll = function (s1, s2) {
            return this.replace(new RegExp(s1, "gm"), s2);
        };

        if (data.length === 0) {
            $("#alert").css('display', "none");
            return;
        } else {
            $("#alert").css('display', "block");
        }

        for (i = 0; i < data.length; i++) {
            var v = data[i];
            x_data.push(v.create_time.slice(5));
            y_data.push(v.count);
            // console.log("v.count: " + v.count);
            // console.log("str_today: " + str_today);
            // console.log("v.create_time: " + v.create_time.replaceAll("-0", "-").replace(" 0", " "));
            if (str_today === v.create_time.replaceAll("-0", "-").replace(" 0", " ")) {
                // console.log("str_today: " + str_today);
                // console.log("v.create_time: " + v.create_time.replaceAll("-0", "-").replace(" 0", " "));
                index_now = data.length - i;
                // console.log("index now: " + index_now);
                value_now = v.count;
                // console.log("v now: " + value_now);
                // console.log("Number(date.getHours()) : " + Number(date.getHours()) );
            }
        }
        //index_today = index_now - date.getHours();
        var max_value = Math.max.apply(Math, y_data.slice(0,));
        AlertChart.hideLoading();

        let e_show = true;
        let xaxis_show = true;
        if (url.includes("/system/") || url.includes("/host/") || url.includes("/service/")) {
            e_show = false;
            xaxis_show = false;
        }

        AlertChart.setOption({
            title: {
                show: e_show,
                text: 'Alerts'
            },
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            toolbox: {
                feature: {
                    //dataView: {show: true, readOnly: true},
                    //mark: {show: true},
                    //saveAsImage: {}
                }
            },
            xAxis: {
                show: xaxis_show,
                type: 'category',
                boundaryGap: false,
                data: x_data.slice(0,),
                axisLabel: {
                    rotate: 45,
                    color: '#cecece'
                }
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    name: '告警数',
                    type: 'bar',
                    //type: 'line',
                    //smooth: true,
                    //symbol: "none",
                    itemStyle: {
                        color: '#ff6526'
                    },
                    data: y_data.slice(0,),
                    markPoint: {
                        itemStyle: {
                            color: '#ff401d'
                        },
                        data: [
                            {type: 'max', name: '最大值'},
                        ]
                    },
                    markLine: {
                        lineStyle: {
                            color: '#9e9e9e',
                        },
                        symbol: 'none',
                        data: [
                            {type: 'average', name: '平均值'}
                        ]
                    }
                },
                {
                    name: '平行于y轴的趋势线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            // color: '#000',
                            // borderColor: 'blue',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: true,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "" + value_now;
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        //symbol:'none',
                        data: [
                            [
                                {coord: [data.length - index_now, 0]},
                                {coord: [data.length - index_now, 0.1]}
                            ]
                        ]
                    }
                },
                {
                    name: '今天分割线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            // color: '#000',
                            // borderColor: 'blue',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: true,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "零点";
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        symbol: 'none',
                        data: [
                            [
                                {coord: [data.length - index_now - Number(date_now.getHours()), 0]},
                                {
                                    coord: [data.length - index_now - Number(date_now.getHours()),
                                        Math.max(max_value, 1)]
                                }
                            ],
                        ]
                    }
                },
                {
                    name: '昨天分割线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            // color: '#000',
                            // borderColor: 'blue',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: false,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "昨天";
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        symbol: 'none',
                        data: [
                            [
                                {
                                    coord: [data.length
                                    - index_now - Number(date_now.getHours()) - 24, 0]
                                },
                                {
                                    coord: [data.length
                                    - index_now - Number(date_now.getHours()) - 24,
                                        Math.max(max_value, 1)]
                                }
                            ],
                        ]
                    }
                }
            ]
        });
    });
}

function replaceAll(str, find, replace) {
    return str.replace(new RegExp(find, 'g'), replace);
}

function reset_title(aria_controls) {
    plat = Cookies.get("plat");
    if (typeof (aria_controls) !== "undefined") {
        plat_title0 = $('button[aria-controls="' + aria_controls + '"]').text();
    } else if (typeof (plat) !== "undefined") {
        plat_title0 = $('button[aria-controls="multiCollapse-' + plat + '"]').text();
    } else {
        plat_title0 = "";
    }

    plat_title = plat_title0.replace(/\(\d+\)\s*$/g, '').replace(
        /^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');
    if (plat_title === "") {
        $('div[id="plat-title"] b').text("平台概况");
    } else {
        $('div[id="plat-title"] b').text(plat_title);
    }
}

function gen_tags(url) {
    $.get(url).done(function (resp) {
        var data = JSON.parse(resp);
        if (data.allgrphtml != null) {
            var tags_html = data.allgrphtml.join('');
            let tags_html000 = '<button id="reversed-sel-button" class="btn btn-primary" type="button"\n' +
                '                                data-toggle="collapse"\n' +
                '                                data-target=".multi-collapse" aria-expanded="false"\n' +
                '                                aria-controls="multiCollapse-"><i class="fa fa-adjust" aria-hidden="true"></i>\n' +
                '                        </button>';
            var group_tags = document.getElementById("btn-group-tags");
            group_tags.innerHTML = tags_html;
        }

        // 因定时刷新，重新标记，及修改b标签
        let aria_controls = Cookies.get("aria_controls");
        if (typeof(aria_controls) !== "undefined") {
            $("button[aria-controls='" + aria_controls + "']").css({"background-color": "#25416F",
                "border-bottom": "3px solid #FF8100"});
        }
        reset_title(aria_controls);

        let pie_data = data.pie_data;
        let title_list = [];
        let total = 0;
        let v_total = 0;
        for (x in pie_data) {
            total += (pie_data[x].value === 0) ? 0 : 1;
            v_total += pie_data[x].value;
        }

        let last_plat_total = parseInt(Cookies.get("last_plat_total"));
        //last_plat_total = (last_plat_total === undefined ? 0 : last_plat_total);
        //if ((last_plat_total !== 0 && total === 0) || (last_plat_total === 0 && total !== 0)) {
        if (last_plat_total !== total) {
            if (last_plat_total === 0){
                // console.log("clear 3 ...");
                AlertChart3.clear();
            }
            Cookies.set("last_plat_total", total);
        }

        let p_data = [];
        for (x = 0; x < pie_data.length && x < 5; x++) {
            title_list.push(pie_data[x].name);
            p_data.push(pie_data[x]);
        }

        let pie_title = '平台';
        // let pie_text = total + '/' + pie_data.length;
        let pie_text = total;
        let legend_show = true;
        if (url.includes("hosts")) {
            pie_title = '主机-Top5';
            pie_text = total + '/' + pie_data.length;
            legend_show = false;
        }

        if (url.includes("/getseveritypiedata/")) {
            pie_title = '级别';
            pie_text = v_total;
        }

        let option = "";
        if (v_total === 0) {
            option = {
                title: {
                    text: pie_title,
                    x: 'left'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "一切正常"
                },
                legend: {
                    show: legend_show,
                    orient: 'vertical',
                    x: 'right',
                },
                color: ['green'],
                graphic: {
                    type: 'text',
                    left: 'center',
                    top: 'middle',
                    style: {
                        fill: 'green',
                        text: pie_text,
                        font: '30px Microsoft YaHei'
                    }
                },
                series: [
                    {
                        name: '平台',
                        type: 'pie',
                        radius: ['45%', '65%'],
                        //center: ['55%', '55%'],
                        avoidLabelOverlap: false,
                        label: {
                            normal: {
                                show: true,
                                //position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '30',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: true
                            }
                        },
                        data: [{name: "所有", value: 0}]
                    }
                ]
            };
        } else {
            option = {
                title: {
                    text: pie_title,
                    x: 'left'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b}: {c} ({d}%)"
                },
                legend: {
                    show: legend_show,
                    orient: 'vertical',
                    x: 'right',
                },
                graphic: {
                    type: 'text',
                    left: 'center',
                    top: 'middle',
                    style: {
                        fill: '#ff0000',
                        text: pie_text,
                        font: '24px Microsoft YaHei'
                    }
                },
                series: [
                    {
                        name: '平台',
                        type: 'pie',
                        radius: ['45%', '65%'],
                        //center: ['55%', '55%'],
                        avoidLabelOverlap: false,
                        label: {
                            normal: {
                                show: true,
                                //position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '30',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: true
                            }
                        },
                        data: p_data
                    }
                ]
            };
        }

        let opt = option.series[0];
        lineHide(opt);
        AlertChart3.setOption(option);
        // 手动单击顶部平台标签按钮时，标记
        $('button[data-toggle="collapse"]').click(function () {
            let aria_controls = Cookies.get("aria_controls");
            let cur_aria_controls = this.getAttribute("aria-controls");
            // if ( cur_aria_controls === "multiCollapse-"){
            //     // 点击的是最后一个反转按钮?
            //     if (typeof(aria_controls) === "undefined") {
            //         alert("show all");
            //     }else{
            //         alert("collapse all");
            //     }
            //     return null;
            // }

            $("button").removeAttr("style");

            //是当前标记的平台的按钮
            if (typeof(aria_controls) !== "undefined") {
                if (aria_controls === cur_aria_controls) {
                    // 与标记的相同，取消标记
                    Cookies.remove("aria_controls");
                    $('div[id="plat-title"] b').text("平台概况");
                    $('.collapse:visible').hide();
                    $('.collapse:visible').hide();
                    myinit();
                    return null;
                }
            }

            //非已标记的平台的按钮
            // 1.
            if ((typeof(Cookies.get('plat')) !== "undefined")) {
                if ((aria_controls === 'null') || (typeof(aria_controls) === "undefined")) {
                    // 已点击只看某平台的按钮，且顶部按钮无标记
                    //$('.collapse[id="' + cur_aria_controls + '"]').toggle();
                    //根据plat_name
                    $('.collapse[id="multiCollapse-' + Cookies.get('plat') + '"]').show();
                    myinit();
                    return null;
                }
            }

            $('.collapse:visible').hide();
            $('.collapse:visible').hide();
            // 2.
            // 修改标记
            Cookies.set("aria_controls", cur_aria_controls);
            this.style = "background-color: #25416F; border-bottom: 3px solid #FF8100";
            //todo
            // 折叠其它，仅显示当前按下的
            //$('.collapse').removeClass('show');
            //$('.collapse:visible').hide().siblings('.accordion-heading ').find('a').addClass('collapsed');
            //$('.collapse:visible').toggle();
            $('.collapse[id="' + cur_aria_controls + '"]').show();
            myinit();
        });
    });
}

function draw_cur(url) {
    $.get(url).done(function (resp) {
        let data = JSON.parse(resp);
        if (data != null) {
            data.reverse();
        }
        // let title_list = [];
        let total = 0;
        for (i = 0; i < data.length; i++) {
            var v = data[i];
            // title_list.push(v.name + v.value.toString());
            total += v.value;
        }
        let last_cur_total = parseInt(Cookies.get("last_cur_total"));
        //last_cur_total = (last_cur_total === undefined ? 0 : last_cur_total);
        //if ((last_cur_total !== 0 && total === 0) || (last_cur_total === 0 && total !== 0)) {
        if (last_cur_total !== total) {
            if (last_cur_total === 0){
                //console.log("clear ...");
                AlertChart2.clear();
            }
            Cookies.set("last_cur_total", total);
        }

        let option = "";
        if (total === 0) {
            option = {
                title: {
                    text: '问题',
                    x: 'left'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "一切正常"
                },
                legend: {
                    orient: 'vertical',
                    x: 'right',
                },
                color: ['green'],
                graphic: {
                    type: 'text',
                    left: 'center',
                    top: 'middle',
                    style: {
                        fill: 'green',
                        text: '0',
                        font: '30px Microsoft YaHei'
                    }
                },
                series: [
                    {
                        name: '问题类别',
                        type: 'pie',
                        radius: ['45%', '65%'],
                        avoidLabelOverlap: false,
                        label: {
                            normal: {
                                show: true,
                                //position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '30',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: true
                            }
                        },
                        data: [{name: "正常", value: "0"}]
                    }
                ]
            };
        } else {
            option = {
                title: {
                    text: '问题',
                    x: 'left'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b}: {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    x: 'right',
                },
                graphic: {
                    type: 'text',
                    left: 'center',
                    top: 'middle',
                    style: {
                        fill: '#ff0000',
                        text: total,
                        font: '30px Microsoft YaHei'
                    }
                },
                series: [
                    {
                        name: '问题类别',
                        type: 'pie',
                        radius: ['45%', '65%'],
                        avoidLabelOverlap: false,
                        label: {
                            normal: {
                                show: true,
                                //position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '30',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: true
                            }
                        },
                        data: data
                    }
                ]
            };

        }
        var opt = option.series[0];
        lineHide(opt);
        AlertChart2.setOption(option);
    });
}

function draw_his(url) {
    $.get(url).done(function (resp) {
        let data = JSON.parse(resp);
        data.reverse();
        let title_list = [];
        let total = 0;
        for (i = 0; i < data.length; i++) {
            var v = data[i];
            title_list.push(v.name);
            total += v.value;
        }

        //todo
        let last_his_total = parseInt(Cookies.get("last_his_total"));
        //last_his_total = (last_his_total === undefined ? 0 : last_his_total);
        //if ((last_cur_total !== 0 && total === 0) || (last_his_total === 0 && total !== 0)) {
        if (last_his_total !== total) {
            if (last_his_total === 0){
                //console.log("clear 2 ...");
                AlertChart4.clear();
            }
            Cookies.set("last_his_total", total);
        }

        let option = "";
        if (total === 0) {
            option = {
                title: {
                    text: '历史',
                    x: 'left'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "一切正常"
                },
                legend: {
                    orient: 'vertical',
                    x: 'right',
                    // data: title_list
                },
                graphic: {
                    type: 'text',
                    left: 'center',
                    top: 'middle',
                    style: {
                        fill: 'green',
                        text: total,
                        font: '30px Microsoft YaHei'
                    }
                },
                color: ["green"],
                series: [
                    {
                        name: '问题类别',
                        type: 'pie',
                        radius: ['45%', '65%'],
                        avoidLabelOverlap: false,
                        label: {
                            normal: {
                                show: true,
                                //position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '30',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: true
                            }
                        },
                        data: [{name: "所有", value: 0}]
                    }
                ]
            };
        } else {
            option = {
                title: {
                    text: '历史',
                    x: 'left'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b}: {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    x: 'right',
                    data: title_list
                },
                graphic: {
                    type: 'text',
                    left: 'center',
                    top: 'middle',
                    style: {
                        fill: '#848cc0',
                        text: total,
                        font: '18px Microsoft YaHei'
                    }
                },
                series: [
                    {
                        name: '问题类别',
                        type: 'pie',
                        radius: ['45%', '65%'],
                        avoidLabelOverlap: false,
                        label: {
                            normal: {
                                show: true,
                                //position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '30',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: true
                            }
                        },
                        data: data
                    }
                ]
            };
        }

        opt = option.series[0];
        lineHide(opt);
        AlertChart4.setOption(option);
    });
}

function host_draw(url) {
    $.get(url).done(function (resp) {
        let data = JSON.parse(resp);
        let x_data = [];
        let y_data = [];
        var index_now = 1;
        var index_today = 1;
        var value_now = 0;
        var date = new Date();
        var str_today = date.getFullYear()
            + '-' + (date.getMonth() + 1)
            + '-' + date.getDate()
            + ' ' + date.getHours() + 'h';
        for (i = 0; i < data.length; i++) {
            var v = data[i];
            x_data.push(v.create_time.slice(8));
            y_data.push(v.count);
            if (str_today == v.create_time.replace("-0", "-").replace(" 0", " ")) {
                index_now = data.length - i;
                value_now = v.count;
            }
        }

        var max_value = Math.max.apply(Math, y_data.slice(-73,));
        AlertChart.hideLoading();
        AlertChart2.hideLoading();
        AlertChart.setOption({
            title: {
                text: '72h'
            },
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            toolbox: {
                feature: {
                    dataView: {show: true, readOnly: true},
                    mark: {show: true},
                    saveAsImage: {}
                }
            },
            xAxis: {
                show: true,
                type: 'category',
                boundaryGap: false,
                data: x_data.slice(-73,),
                axisLabel: {
                    rotate: 45,
                    color: '#cecece'
                }
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    name: '告警数',
                    type: 'bar',
                    itemStyle: {
                        color: '#ff8147'
                    },
                    data: y_data.slice(-73,),
                    markPoint: {
                        itemStyle: {
                            color: '#ff5123'
                        },
                        data: [
                            {type: 'max', name: '最大值'},
                        ]
                    },
                    markLine: {
                        lineStyle: {
                            color: '#9e9e9e',
                        },
                        symbol: 'none',
                        data: [
                            {type: 'average', name: '平均值'}
                        ]
                    }
                },
                {
                    name: '平行于y轴的趋势线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            // color: '#000',
                            // borderColor: 'blue',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: true,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "" + value_now;
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        //symbol:'none',
                        data: [
                            [
                                {coord: [Math.min(73, data.length) - index_now, 0]},
                                {coord: [Math.min(73, data.length) - index_now, 0.1]}
                            ]
                        ]
                    }
                },
                {
                    name: '今天分割线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            // color: '#000',
                            // borderColor: 'blue',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: true,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "零点";
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        symbol: 'none',
                        data: [
                            [
                                {coord: [Math.min(73, data.length) - index_now - Number(date.getHours()), 0]},
                                {
                                    coord: [Math.min(73, data.length) - index_now - Number(date.getHours()),
                                        Math.max(max_value, 1)]
                                }
                            ],
                        ]
                    }
                },
                {
                    name: '昨天分割线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            // color: '#000',
                            // borderColor: 'blue',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: false,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "昨天";
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        symbol: 'none',
                        data: [
                            [
                                {
                                    coord: [Math.min(73, data.length)
                                    - index_now - Number(date.getHours()) - 24, 0]
                                },
                                {
                                    coord: [Math.min(73, data.length)
                                    - index_now - Number(date.getHours()) - 24,
                                        Math.max(max_value, 1)]
                                }
                            ],
                        ]
                    }
                }
            ]
        });

        var max_value = Math.max.apply(Math, y_data);
        let x2_data = [];
        let y2_data = [];
        for (i = 0; i < data.length; i++) {
            var v = data[i];
            x2_data.push(v.create_time.slice(5));
            y2_data.push(v.count);
            if (str_today == v.create_time) {
                index_now = data.length - i;
                value_now = v.count;
            }
        }

        AlertChart2.setOption({
            title: {
                text: '30d'
            },
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            toolbox: {
                feature: {
                    saveAsImage: {}
                }
            },
            xAxis: {
                show: false,
                type: 'category',
                boundaryGap: false,
                data: x2_data.slice(-721,),
                //axisLabel: {
                //    rotate: 45,
                //    color: '#cecece'
                //}
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    name: '告警数',
                    smooth: true,
                    type: 'line',
                    symbol: 'none',
                    lineStyle: {
                        color: '#ff8147'
                    },
                    data: y2_data.slice(-721,),
                    markPoint: {
                        itemStyle: {
                            color: '#ff5123'
                        },
                        data: [
                            {type: 'max', name: '最大值'},
                        ]
                    },
                    markLine: {
                        lineStyle: {
                            color: '#9e9e9e',
                        },
                        symbol: 'none',
                        data: [
                            {type: 'average', name: '平均值'}
                        ]
                    }
                },
                {
                    name: '平行于y轴的趋势线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            //color: '#ffaa57',
                            //borderColor: '#ff5c4f',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: true,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "" + value_now;
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        //symbol:'none',
                        data: [[
                            {coord: [Math.min(721, data.length) - index_now, 0]},
                            {coord: [Math.min(721, data.length) - index_now, 0.1]}
                            //{coord: [Math.min(721,data.length)-index_now, value_now+0.1]}
                        ]]
                    }
                },
                {
                    name: '今天分割线',
                    type: 'line',
                    //data:[0],
                    markLine: {
                        itemStyle: {
                            // color: '#000',
                            // borderColor: 'blue',
                            // type: 'solid',
                            normal: {
                                lineStyle: {
                                    width: 1,
                                    color: '#616acb',
                                    type: 'dotted',
                                },
                                label: {
                                    show: true,
                                    position: 'end',
                                    color: '#46468b',
                                    formatter: function (params) {
                                        str = "零点";
                                        return str;
                                    },
                                }
                            }
                        },
                        name: 'cc',
                        yAxisIndex: 0,
                        symbol: 'none',
                        data: [
                            [
                                {coord: [Math.min(721, data.length) - index_now - Number(date.getHours()), 0]},
                                {
                                    coord: [Math.min(721, data.length) - index_now - Number(date.getHours()),
                                        max_value]
                                }
                            ],
                        ]
                    }
                }
            ]
        });
    });
}
