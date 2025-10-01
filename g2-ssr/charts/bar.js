const {checkIsPercent} = require("./utils");

function getBarOptions(baseOptions, axis, data) {

    const x = axis.filter((item) => item.type === 'x')
    const y = axis.filter((item) => item.type === 'y')
    const series = axis.filter((item) => item.type === 'series')

    console.log(`[BAR CHART] 接收到的axis参数:`, JSON.stringify(axis));
    console.log(`[BAR CHART] 过滤后 - x: ${JSON.stringify(x)}, y: ${JSON.stringify(y)}, series: ${JSON.stringify(series)}`);

    if (x.length === 0 || y.length === 0) {
        console.error(`[BAR CHART] 缺少必要的x或y轴配置`);
        return
    }

    const _data = checkIsPercent(x[0], data)  // x[0]是数值字段，检查是否为百分比
    console.log(`[BAR CHART] 数据检查完成，总计 ${_data.data.length} 条数据`);
    console.log(`[BAR CHART] x[0].value=${x[0].value}, y[0].value=${y[0].value}`);

    const options = {
        ...baseOptions,
        type: 'interval',
        data: _data.data,
        coordinate: {transform: [{type: 'transpose'}]},
        encode: {
            // 由于transpose，需要交换x和y：
            // x是数值(横向) → transpose后变纵向，但我们想要横向，所以放在y位置
            // y是类别(纵向) → transpose后变横向，但我们想要纵向，所以放在x位置
            x: y[0].value,  // 类别字段
            y: x[0].value,  // 数值字段
            color: series.length > 0 ? series[0].value : undefined,
        },
        style: {
            radiusTopLeft: (d) => {
                if (d[x[0].value] && d[x[0].value] > 0) {
                    return 4
                }
                return 0
            },
            radiusTopRight: (d) => {
                if (d[x[0].value] && d[x[0].value] > 0) {
                    return 4
                }
                return 0
            },
            radiusBottomLeft: (d) => {
                if (d[x[0].value] && d[x[0].value] < 0) {
                    return 4
                }
                return 0
            },
            radiusBottomRight: (d) => {
                if (d[x[0].value] && d[x[0].value] < 0) {
                    return 4
                }
                return 0
            },
        },
        axis: {
            x: {
                // transpose后，axis.x控制纵向轴，显示类别
                title: y[0].name,  // 类别名称
                labelFontSize: 12,
                labelAutoHide: {
                    type: 'hide',
                    keepHeader: true,
                    keepTail: true,
                },
                labelAutoRotate: false,
                labelAutoWrap: true,
                labelAutoEllipsis: true,
            },
            // transpose后，axis.y控制横向轴，显示数值
            y: {title: x[0].name},  // 数值名称
        },
        scale: {
            x: {
                nice: true,
            },
            y: {
                nice: true,
            },
        },
        interaction: {
            elementHighlight: {background: true},
        },
        tooltip: (data) => {
            if (series.length > 0) {
                return {
                    name: data[series[0].value],
                    value: `${data[x[0].value]}${_data.isPercent ? '%' : ''}`,  // x[0]是数值字段
                }
            } else {
                return {name: x[0].name, value: `${data[x[0].value]}${_data.isPercent ? '%' : ''}`}  // x[0]是数值字段
            }
        },
        labels: [
            {
                text: (data) => {
                    const value = data[x[0].value]  // x[0]是数值字段
                    if (value === undefined || value === null) {
                        return ''
                    }
                    return `${value}${_data.isPercent ? '%' : ''}`
                },
                position: (data) => {
                    if (data[x[0].value] < 0) {  // x[0]是数值字段
                        return 'bottom'
                    }
                    return 'top'
                },
                transform: [
                    {type: 'contrastReverse'},
                    {type: 'exceedAdjust'},
                    {type: 'overlapHide'},
                ],
            },
        ],
    }

    if (series.length > 0) {
        options.transform = [{type: 'stackY'}]
    }

    console.log(`[BAR CHART] 最终生成的options.encode:`, JSON.stringify(options.encode));
    console.log(`[BAR CHART] 最终生成的options.axis:`, JSON.stringify(options.axis));

    return options
}

module.exports = {getBarOptions}