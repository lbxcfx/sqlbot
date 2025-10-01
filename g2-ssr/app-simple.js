const http = require('http');
const url = require("url");
const util = require('util');
const port = 3000;
const { getPieOptions } = require('./charts/pie.js');
const { getLineOptions } = require('./charts/line.js');
const { getColumnOptions } = require('./charts/column.js');
const { getBarOptions } = require('./charts/bar.js');

http.createServer((req, res) => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json;charset=utf-8');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.end();
        return;
    }
    
    if (req.method === 'GET') {
        toGet(req, res);
    } else if (req.method === 'POST') {
        toPost(req, res);
    }
}).listen(port, () => {
    console.info(`Chart service listening on: http://localhost:${port}`);
    console.info('Available chart types: bar, column, line, pie');
});

function getOptions(type, axis, data) {
    const base_options = {
        width: 640,
        height: 480,
        imageType: 'png',
        theme: {
            view: {
                viewFill: '#FFFFFF',
            },
        }
    }

    switch (type) {
        case 'bar':
            return getBarOptions(base_options, axis, data);
        case 'column':
            return getColumnOptions(base_options, axis, data);
        case 'line':
            return getLineOptions(base_options, axis, data);
        case 'pie':
            return getPieOptions(base_options, axis, data);
    }

    return base_options
}

// 创建图表配置（不生成实际图片）
async function GenerateChartConfig(obj) {
    try {
        const options = getOptions(obj.type, JSON.parse(obj.axis), JSON.parse(obj.data));
        return {
            success: true,
            chartType: obj.type,
            config: options,
            message: 'Chart configuration generated successfully'
        };
    } catch (error) {
        return {
            success: false,
            error: error.message,
            message: 'Failed to generate chart configuration'
        };
    }
}

// 获取GET请求内容
function toGet(req, res) {
    const response = {
        service: 'g2-ssr-chart-service',
        status: 'running',
        version: '1.0.0',
        supportedTypes: ['bar', 'column', 'line', 'pie'],
        endpoints: {
            'POST /': 'Generate chart configuration',
            'GET /': 'Service status'
        }
    };
    res.end(JSON.stringify(response, null, 2));
}

// 获取POST请求内容
function toPost(req, res) {
    let body = '';
    
    req.on('data', function (chunk) {
        body += chunk.toString();
    });
    
    req.on('end', async function () {
        try {
            const requestData = JSON.parse(body);
            console.log('Received chart request:', requestData.type);
            
            const result = await GenerateChartConfig(requestData);
            res.end(JSON.stringify(result, null, 2));
        } catch (error) {
            const errorResponse = {
                success: false,
                error: error.message,
                message: 'Invalid request data'
            };
            res.end(JSON.stringify(errorResponse, null, 2));
        }
    });
}
