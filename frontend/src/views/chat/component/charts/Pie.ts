import { BaseG2Chart } from '@/views/chat/component/BaseG2Chart.ts'
import type { ChartAxis, ChartData } from '@/views/chat/component/BaseChart.ts'
import type { G2Spec } from '@antv/g2'
import { checkIsPercent } from '@/views/chat/component/charts/utils.ts'

export class Pie extends BaseG2Chart {
  constructor(id: string) {
    super(id, 'pie')
  }

  init(axis: Array<ChartAxis>, data: Array<ChartData>) {
    super.init(axis, data)
    const y = this.axis.filter((item) => item.type === 'y')
    const series = this.axis.filter((item) => item.type === 'series')

    if (series.length == 0 || y.length == 0) {
      return
    }

    // %
    const _data = checkIsPercent(y[0], data)

    const options: G2Spec = {
      ...this.chart.options(),
      type: 'interval',
      coordinate: { type: 'theta', outerRadius: 0.8 },
      transform: [{ type: 'stackY' }],
      data: _data.data,
      encode: {
        y: y[0].value,
        color: series[0].value,
      },
      legend: {
        color: { position: 'bottom', layout: { justifyContent: 'center' } },
      },
      labels: [
        {
          position: 'outside',
          text: (data: any) => {
            return `${data[series[0].value]}: ${data[y[0].value]}${_data.isPercent ? '%' : ''}`
          },
          transform: [{ type: 'exceedAdjust' }, { type: 'overlapHide' }],
        },
      ],
      tooltip: {
        title: (data: any) => data[series[0].value],
        items: [
          (data: any) => {
            return {
              name: y[0].name,
              value: `${data[y[0].value]}${_data.isPercent ? '%' : ''}`,
            }
          },
        ],
      },
    }

    this.chart.options(options)
  }
}
