import path, { resolve } from 'path'
import vue from '@vitejs/plugin-vue'
// import legacy from '@vitejs/plugin-legacy'
import vueJsx from '@vitejs/plugin-vue-jsx'
import viteSvgIcons from 'vite-plugin-svg-icons'


//setup name
import VueSetupExtend from 'vite-plugin-vue-setup-extend'

//auto import element-plus has some issue
// import Components from 'unplugin-vue-components/vite'
// import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

//auto import vue https://www.npmjs.com/package/unplugin-auto-import
import AutoImport from 'unplugin-auto-import/vite'

//  import image
//  直接使用 <img :src="Logo" />
// import ViteImages from 'vite-plugin-vue-images'
import setting from './src/settings'
// import { loadEnv } from 'vite'
// import packageJson from './package.json'

export default ({ command, mode }) => {
  /*
   console.log(command, mode)
  * serve serve-dev
  * */
  return {
    /*
     * "/vue3-admin-plus" nginx deploy folder
     * detail to look https://vitejs.cn/config/#base
     * how to config, such as http://8.135.1.141/vue3-admin-plus/#/dashboard
     * "/vue3-admin-plus/" --> config to base is you need
     * http://8.135.1.141 --> if you config "/" , you can visit attached  to http://8.135.1.141
     * */
    base: setting.viteBasePath,
    //define global var
    define: {
      //fix "path" module issue
      'process.platform': null,
      'process.version': null,
      GLOBAL_STRING: JSON.stringify('i am global var from vite.config.js define'),
      GLOBAL_VAR: {
        test: 'i am global var from vite.config.js define'
      }
    },
    clearScreen: false,
    server: {
        proxy: {
            ...['/api', '/static', '/auth'].reduce(
                (acc, ctx) => ({
                    ...acc,
                    [ctx]: {
                        target: 'http://127.0.0.1:8000',
                        changeOrigin: true
                    },
                }),
                {}
            ),
        }
    },
    preview: {
      port: 5001,
      host: '0.0.0.0',
      strictPort: true
    },
    plugins: [
      vue(),
      vueJsx(),
      viteSvgIcons({
        // config svg dir that can config multi
        iconDirs: [path.resolve(process.cwd(), 'src/icons/common'), path.resolve(process.cwd(), 'src/icons/nav-bar')],
        // appoint svg icon using mode
        symbolId: 'icon-[dir]-[name]'
      }),
      VueSetupExtend(),
      //https://github.com/antfu/unplugin-auto-import/blob/HEAD/src/types.ts
      AutoImport({
        // resolvers: [ElementPlusResolver()],
        imports: [
          'vue',
          'vuex',
          'vue-router'
        ],
        eslintrc: {
          enabled: true, // Default `false`
          filepath: './.eslintrc-auto-import.json', // Default `./.eslintrc-auto-import.json`
          globalsPropValue: true // Default `true`, (true | false | 'readonly' | 'readable' | 'writable' | 'writeable')
        },
        dts: true //auto generation auto-imports.d.ts file
      })
      // Components({
      //   resolvers: [ElementPlusResolver()]
      // })
    ],
    build: {
      minify: 'terser',
      brotliSize: false,
      // 消除打包大小超过500kb警告
      chunkSizeWarningLimit: 2000,
      //remote console.log in prod
      terserOptions: {
        //detail to look https://terser.org/docs/api-reference#compress-options
        compress: {
          drop_console: false,
          pure_funcs: ['console.log', 'console.info'],
          drop_debugger: true
        }
      },
      //build assets Separate
      assetsDir: 'static/assets',
      rollupOptions: {
        output: {
          manualChunks: undefined,
          chunkFileNames: 'static/js/admin/[name].js',
          entryFileNames: 'static/js/admin/[name].js',
          assetFileNames: 'static/[ext]/admin/[name].[ext]'
        }
      }
    },
    resolve: {
      alias: {
        '~': resolve(__dirname, './'),
        '@': resolve(__dirname, 'src')
      }
      // why remove it , look for https://github.com/vitejs/vite/issues/6026
      // extensions: ['.js', '.ts', '.jsx', '.tsx', '.json', '.vue', '.mjs']
    },
    css: {
      postcss: {
        //remove build charset warning
        plugins: [
          {
            postcssPlugin: 'internal:charset-removal',
            AtRule: {
              charset: (atRule) => {
                if (atRule.name === 'charset') {
                  atRule.remove()
                }
              }
            }
          }
        ]
      },
      preprocessorOptions: {
        //define global scss variable
        scss: {
          additionalData: `@import "@/styles/variables.scss";`
        }
      }
    },
    optimizeDeps: {
      include: ['moment-mini']
    }
  }
}
