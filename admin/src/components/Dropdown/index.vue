<template>
  <el-dropdown :show-timeout="100" trigger="click">
    <el-button plain>{{ enabled === enabledLabel ? enabledText : disabledText }}
      <i class="el-icon-caret-bottom el-icon--right"/>
    </el-button>
    <el-dropdown-menu slot="dropdown" class="no-padding">
      <el-dropdown-item>
        <el-radio-group v-model="enabled" style="padding: 10px;">
          <el-radio :label="enabledLabel">{{ enabledText }}</el-radio>
          <el-radio :label="disabledLabel">{{ disabledText }}</el-radio>
        </el-radio-group>
      </el-dropdown-item>
    </el-dropdown-menu>
  </el-dropdown>
</template>

<script>
export default {
  name: 'Dropdown',
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
  computed: {
    enabled: {
      get() {
        return this.value
      },
      set(val) {
        this.$emit('input', val)
      }
    }
  }
}
</script>
