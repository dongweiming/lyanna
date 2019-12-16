module.exports = {
    indexPath: 'index.html',
    productionSourceMap: false,  // 生产环境禁用
    configureWebpack: {
        devtool: 'eval-source-map',
        output: {
            filename: 'static/js/activity/[name].js',
            chunkFilename: 'static/js/activity/[name].js'
        }
    },
    css: {
        extract: {
            filename: 'static/css/activity/[name].css',
            chunkFilename: 'static/css/activity/[name].css'
        }
    },
    devServer: {
        proxy: {
            ...['/api', '/j', '/static'].reduce(
                (acc, ctx) => ({
                    ...acc,
                    [ctx]: { target: 'http://127.0.0.1:8000',
                             changeOrigin: true },
                }),
                {}
            ),
        }
    }
}

var path = require('path')

function resolve(dir) {
    return path.join(__dirname, './', dir)
}
