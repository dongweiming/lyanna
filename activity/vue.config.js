const debug = process.env.NODE_ENV !== 'production'

module.exports = {
    indexPath: 'index.html',
    productionSourceMap: false,  // 生产环境禁用
    chainWebpack: (config)=>{
        config.resolve.alias
            .set('#', resolve('../common/src'))
    },
    configureWebpack: (config) => {
        if (debug) {
            config.devtool = 'eval-source-map'
        } else {
            config.devtool = false
        }
        config.output.filename = 'static/js/activity/[name].js'
        config.output.chunkFilename = 'static/js/activity/[name].js'
        config.externals = {
            'vue': 'Vue',
            'moment': 'moment'
        }
        config.optimization = {
            splitChunks: false
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
