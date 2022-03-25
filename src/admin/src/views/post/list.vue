<template>
  <div class="app-container">

    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column align="center" label="ID" width="60">
        <template #default="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column width="300px" align="center" label="Title">
        <template #default="scope">
          <span>{{ scope.row.title }}</span>
        </template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="Tags">
        <template #default="scope">
          <el-tag v-for="tag in scope.row.tags" :key="tag">{{ tag }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column width="80px" align="center" label="Author">
        <template #default="scope">
          <span>{{ scope.row.author_name }}</span>
        </template>
      </el-table-column>

      <el-table-column width="140px" align="center" label="Date">
        <template #default="scope">
          <span>{{ parseTime(scope.row.created_at, '{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="Published" width="100">
        <template #default="scope">
          <el-tooltip :content="statusFilter(parseInt(scope.row.status))" placement="top">
            <el-switch v-model="scope.row.status" :active-value=1 :inactive-value=0 @change="switchStatus(scope.row)"></el-switch>
          </el-tooltip>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Actions">
        <template #default="scope">
          <router-link :to="'/post/' + scope.row.id + '/edit'">
            <el-button type="primary" size="small"><svg-icon icon-class="edit"/>Edit</el-button>
          </router-link>
          <el-button type="danger" size="small" class="del-btn" @click="deletePost(scope.$index, scope.row)"><svg-icon icon-class="delete"/>Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import { parseTime } from '@/utils/filter'
import { getPostList, updatePostStatus, deletePost } from '@/api'
import Pagination from '@/components/Pagination/index.vue'

export default {
    name: 'PostList',
    components: { Pagination },
    data() {
        return {
            list: null,
            total: 0,
            listLoading: true,
            listQuery: {
                page: 1,
                limit: 10,
                with_tag: 1
            },
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
      getPostList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      })
    },
    handleSizeChange(val) {
      this.listQuery.limit = val
      this.getList()
    },
    handleCurrentChange(val) {
      this.listQuery.page = val
      this.getList()
    },
    switchStatus(row) {
      const statusMap = {
        1: 'POST',
        0: 'DELETE'
      }
      updatePostStatus(row.id, statusMap[row.status]).then(response => {
        if (!response.data.r) {
          row.status = !row.status
          this.$message.error('切换状态失败!');
        }
      })
    },
    deletePost(index, row) {
      this.$confirm('此操作将永久删除这篇文章, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'danger'
      }).then(() => {
        deletePost(row.id).then(response => {
          if (response.data.r) {
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
            this.list.splice(index, 1)
          }
        })
      }).catch(() => {
        console.log('Cancel!')
      });
    }
  }
}
</script>

<style scoped>
.del-btn {
  margin-left: 20px;
}
</style>
