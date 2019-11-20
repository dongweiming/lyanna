<template>
  <div class="app-container">

    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column align="center" label="ID" width="80">
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column width="140px" align="center" label="Date">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="Title">
        <template slot-scope="scope">
          <span>{{ scope.row.title }}</span>
        </template>
      </el-table-column>

      <el-table-column width="280px" align="center" label="Intro">
         <template slot-scope="scope">
           <span>{{ scope.row.intro }}</span>
         </template>
       </el-table-column>

      <el-table-column width="80px" align="center" label="N_Post">
        <template slot-scope="scope">
          <span>{{ scope.row.n_posts }}</span>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="Published" width="100">
        <template slot-scope="scope">
          <el-tooltip :content="scope.row.status | statusFilter" placement="top">
            <el-switch v-model="scope.row.status" :active-value=1 :inactive-value=0 @change="switchStatus(scope.row)"></el-switch>
          </el-tooltip>
        </template>
      </el-table-column>

      <el-table-column label="Actions" align="center" width="230" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <router-link :to="'/topic/' + scope.row.id + '/edit'">
            <el-button type="primary" size="small" icon="el-icon-edit">Edit</el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>

  </div>
</template>

<script>
import { getTopicList, updateTopicStatus } from '@/api'

export default {
  name: 'SpecialTopics',
  filters: {
    statusFilter(status) {
      const statusMap = {
        1: 'online',
        0: 'unpublished'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true
    }
  },
  created() {
    this.getList()
  },
  methods: {
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
