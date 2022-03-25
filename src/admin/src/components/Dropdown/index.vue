<template>
  <el-dropdown :show-timeout="100" trigger="click">
    <el-button plain>{{ value === enabledLabel ? enabledText : disabledText }}
      <i class="el-icon-caret-bottom el-icon--right"/>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu class="no-padding">
        <el-dropdown-item>
          <el-radio-group v-model="value" style="padding: 10px;" @change="change">
            <el-radio :label="enabledLabel">{{ enabledText }}</el-radio>
            <el-radio :label="disabledLabel">{{ disabledText }}</el-radio>
          </el-radio-group>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script>
export default {
    name: 'Dropdown',
    emits: ['input', 'onUpdate:value'],
    props: {
        value: {
            type: [Boolean, Number, String]
        },
        enabledText: {
            type: String
        },
        disabledText: {
            type: String
        },
        enabledLabel: {
            default: true
        },
        disabledLabel: {
            default: false
        }
    },
    methods: {
        change(val) {
            this.$emit('onUpdate:value', val)
        }
    }
}
</script>
<style lang="scss" scoped>
  .el-dropdown {
     vertical-align: middle;
  }
</style>
