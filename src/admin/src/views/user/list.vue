<template>
  <div class="app-container">

    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column align="center" label="ID" width="80">
        <template #default="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="Date">
        <template #default="scope">
          <span>{{ parseTime(scope.row.created_at, '{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="Name">
        <template #default="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="Email">
        <template #default="scope">
          <span>{{ scope.row.email }}</span>
        </template>
      </el-table-column>

      <el-table-column width="120px" align="center" label="Actived">
        <template #default="scope">
          <span>{{ scope.row.active ? 'Yes' : 'No' }}</span>
        </template>
      </el-table-column>

      <el-table-column label="Actions" align="center" width="230" class-name="small-padding fixed-width">
        <template #default="scope">
          <router-link :to="'/user/' + scope.row.id + '/edit'">
            <el-button type="primary" size="small"><svg-icon icon-class="edit"/>Edit</el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>

  </div>
</template>

<script>
import { parseTime } from '@/utils/filter'
import { getUserList } from '@/api'

export default {
    name: 'UserList',
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
    getList() {
      this.listLoading = true
      getUserList().then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      })
    }
  }
}
</script>
