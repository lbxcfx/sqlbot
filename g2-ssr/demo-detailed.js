const http = require('http');

// 详细的测试数据
const detailedTestData = {
    type: 'column',
    axis: JSON.stringify([
        { name: '地区', value: 'region', type: 'x' },
        { name: '销售额', value: 'sales', type: 'y' },
        { name: '产品类型', value: 'product', type: 'series' }
    ]),
    data: JSON.stringify([
        { region: '北京', product: '手机', sales: 1200 },
        { region: '北京', product: '电脑', sales: 800 },
        { region: '上海', product: '手机', sales: 1500 },
        { region: '上海', product: '电脑', sales: 900 },
        { region: '广州', product: '手机', sales: 1000 },
        { region: '广州', product: '电脑', sales: 600 },
        { region: '深圳', product: '手机', sales: 1300 },
        { region: '深圳', product: '电脑', sales: 1100 }
    ])
};

function testDetailedChart() {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify(detailedTestData);
        
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: '/',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };
        
        const req = http.request(options, (res) => {
            let responseData = '';
            
            res.on('data', (chunk) => {
                responseData += chunk;
            });
            
            res.on('end', () => {
                try {
                    const result = JSON.parse(responseData);
                    resolve(result);
                } catch (error) {
                    reject(error);
                }
            });
        });
        
        req.on('error', (error) => {
            reject(error);
        });
        
        req.write(postData);
        req.end();
    });
}

async function runDetailedDemo() {
    console.log('🎯 详细图表配置演示\n');
    console.log('📊 测试数据:');
    console.log('   图表类型: 柱状图 (column)');
    console.log('   数据维度: 地区 × 产品类型 × 销售额');
    console.log('   数据条数: 8条');
    console.log('');
    
    try {
        const result = await testDetailedChart();
        
        if (result.success) {
            console.log('✅ 图表配置生成成功！\n');
            
            console.log('📋 图表配置详情:');
            console.log('   图表类型:', result.chartType);
            console.log('   图表宽度:', result.config.width + 'px');
            console.log('   图表高度:', result.config.height + 'px');
            console.log('   图片格式:', result.config.imageType);
            console.log('');
            
            console.log('🎨 样式配置:');
            console.log('   背景色:', result.config.theme.view.viewFill);
            console.log('   图表类型:', result.config.type);
            console.log('   坐标轴:', result.config.coordinate ? '有' : '无');
            console.log('');
            
            console.log('📈 数据配置:');
            console.log('   X轴字段:', result.config.encode.x);
            console.log('   Y轴字段:', result.config.encode.y);
            console.log('   颜色字段:', result.config.encode.color || '无');
            console.log('   数据条数:', result.config.data.length);
            console.log('');
            
            console.log('🔧 交互配置:');
            console.log('   高亮效果:', result.config.interaction ? '启用' : '禁用');
            console.log('   工具提示:', result.config.tooltip ? '启用' : '禁用');
            console.log('   标签显示:', result.config.labels ? '启用' : '禁用');
            console.log('');
            
            console.log('📊 示例数据预览:');
            result.config.data.slice(0, 3).forEach((item, index) => {
                console.log(`   ${index + 1}. ${item.region} - ${item.product}: ${item.sales}`);
            });
            console.log('   ...');
            console.log('');
            
            console.log('🎉 图表服务运行正常！');
            console.log('   服务地址: http://localhost:3000');
            console.log('   支持类型: bar, column, line, pie');
            
        } else {
            console.log('❌ 图表配置生成失败:', result.message);
        }
        
    } catch (error) {
        console.error('❌ 请求失败:', error.message);
    }
}

// 运行详细演示
runDetailedDemo();
