<template>
  <div class="app-container">

    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column align="center" label="ID" width="80">
        <template #default="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column width="140px" align="center" label="Date">
        <template #default="scope">
          <span>{{ parseTime(scope.row.created_at, '{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="Title">
        <template #default="scope">
          <span>{{ scope.row.title }}</span>
        </template>
      </el-table-column>

      <el-table-column width="280px" align="center" label="Intro">
         <template #default="scope">
           <span>{{ scope.row.intro }}</span>
         </template>
       </el-table-column>

      <el-table-column width="80px" align="center" label="N_Post">
        <template #default="scope">
          <span>{{ scope.row.n_posts }}</span>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="Published" width="100">
        <template #default="scope">
          <el-tooltip :content="statusFilter(parseInt(scope.row.status))" placement="top">
            <el-switch v-model="scope.row.status" :active-value=1 :inactive-value=0 @change="switchStatus(scope.row)"></el-switch>
          </el-tooltip>
        </template>
      </el-table-column>

      <el-table-column label="Actions" align="center" width="230" class-name="small-padding fixed-width">
        <template #default="scope">
          <router-link :to="'/topic/' + scope.row.id + '/edit'">
            <el-button type="primary" size="small"><svg-icon icon-class="edit"/>Edit</el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>

  </div>
</template>

<script>
import { parseTime } from '@/utils/filter'
import { getTopicList, updateTopicStatus } from '@/api'

export default {
    name: 'SpecialTopics',
    data() {
        return {
            list: null,
            total: 0,
            listLoading: true,
            parseTime
        }
    },
    created() {
        this.getList()
    },
    methods: {
        statusFilter(status) {
            const statusMap = {
                1: 'online',
                0: 'unpublished'
            }
            return statusMap[status]
     },
    getList() {
      this.listLoading = true
      getTopicList().then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      })
    },
    switchStatus(row) {
      const statusMap = {
        1: 'POST',
        0: 'DELETE'
      }
      updateTopicStatus(row.id, statusMap[row.status]).then(response => {
        if (!response.data.r) {
          row.status = !row.status
          this.$message.error('切换状态失败!');
        }
      })
    }
  }
}
</script>
