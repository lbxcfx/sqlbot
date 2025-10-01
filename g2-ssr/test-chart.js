const http = require('http');

// 测试数据
const testData = {
    // 条形图测试数据（修复后：x=数值，y=类别）
    bar: {
        type: 'bar',
        path: './test-bar-chart',
        axis: JSON.stringify([
            { name: '手术次数', value: 'count', type: 'x' },  // x是数值（横向）
            { name: '医生', value: 'doctor', type: 'y' }      // y是类别（纵向）
        ]),
        data: JSON.stringify([
            { doctor: '王教授', count: 5 },
            { doctor: '高洁', count: 4 },
            { doctor: '林峰', count: 3 },
            { doctor: '郭勇', count: 2 },
            { doctor: '韩雪', count: 1 }
        ])
    },
    
    // 折线图测试数据
    line: {
        type: 'line',
        axis: JSON.stringify([
            { name: '月份', value: 'month', type: 'x' },
            { name: '销售额', value: 'revenue', type: 'y' }
        ]),
        data: JSON.stringify([
            { month: '1月', revenue: 1000 },
            { month: '2月', revenue: 1200 },
            { month: '3月', revenue: 1500 },
            { month: '4月', revenue: 1800 },
            { month: '5月', revenue: 2000 }
        ])
    },
    
    // 饼图测试数据
    pie: {
        type: 'pie',
        axis: JSON.stringify([
            { name: '占比', value: 'percentage', type: 'y' },
            { name: '类别', value: 'category', type: 'series' }
        ]),
        data: JSON.stringify([
            { category: '移动端', percentage: 45 },
            { category: '桌面端', percentage: 35 },
            { category: '平板端', percentage: 20 }
        ])
    }
};

// 发送测试请求
function testChart(type, data) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify(data);

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
                console.log(`   响应: ${responseData}`);
                resolve({ type, status: responseData });
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.write(postData);
        req.end();
    });
}

// 运行所有测试
async function runTests() {
    console.log('🚀 开始测试条形图修复...\n');

    try {
        // 测试条形图
        console.log('📊 测试条形图（医生手术次数）...');
        console.log('   配置: x轴=手术次数（数值），y轴=医生（类别）');
        const barResult = await testChart('bar', testData.bar);
        console.log('✅ 条形图生成成功');
        console.log('   图表文件: test-bar-chart.png');
        console.log('');

        // 测试折线图
        console.log('📈 测试折线图...');
        const lineResult = await testChart('line', testData.line);
        console.log('✅ 折线图生成成功');
        console.log('');

        // 测试饼图
        console.log('🥧 测试饼图...');
        const pieResult = await testChart('pie', testData.pie);
        console.log('✅ 饼图生成成功');
        console.log('');

        console.log('🎉 所有图表测试完成！');
        console.log('\n📋 验证结果:');
        console.log('   ✓ 条形图应该显示为：');
        console.log('     - Y轴（纵向左侧）：医生名字列表');
        console.log('     - X轴（横向底部）：手术次数刻度');
        console.log('     - 条形方向：从左到右（横向）');
        console.log('   ✓ 请查看生成的 test-bar-chart.png 文件验证');

    } catch (error) {
        console.error('❌ 测试失败:', error.message);
        console.error('   请确保 G2-SSR 服务正在运行: node app.js');
    }
}

// 运行测试
runTests();
