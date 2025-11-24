<template>
  <div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="!entries || entries.length === 0" class="text-center py-5 text-muted">
      <i class="uil uil-file-search-alt" style="font-size: 3rem;"></i>
      <p class="mt-2">No entries found</p>
    </div>
    <div v-else>
      <div class="table-responsive">
        <table class="table table-hover table-sm">
          <thead>
            <tr>
              <th>Entry #</th>
              <th>Posting Date</th>
              <th>Company</th>
              <th>Account</th>
              <th class="text-end">Debit</th>
              <th class="text-end">Credit</th>
              <th class="text-end">Net</th>
              <th>Tag</th>
              <th>Bucket</th>
              <th>Status</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in entries" :key="entry.id" :class="{ 'table-warning': entry.requires_review }">
              <td>
                <span class="fw-bold">{{ entry.entry }}</span>
              </td>
              <td>{{ formatDate(entry.posting_date) }}</td>
              <td>
                <div class="text-truncate" style="max-width: 150px;" :title="entry.company_name">
                  {{ entry.company_name }}
                </div>
              </td>
              <td>
                <div class="text-truncate" style="max-width: 120px;" :title="entry.account_number + ' - ' + entry.account_name">
                  {{ entry.account_number }}
                </div>
              </td>
              <td class="text-end text-success">{{ formatCurrency(entry.debit_amount) }}</td>
              <td class="text-end text-danger">{{ formatCurrency(entry.credit_amount) }}</td>
              <td class="text-end fw-bold" :class="getNetColorClass(entry.net_amount)">
                {{ formatCurrency(entry.net_amount) }}
              </td>
              <td>
                <span v-if="entry.tag" class="badge" :class="getTagBadgeClass(entry.tag)">
                  {{ formatTag(entry.tag) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span v-if="entry.bucket" class="badge bg-secondary">
                  {{ formatBucket(entry.bucket) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span v-if="entry.requires_review" class="badge bg-warning">
                  <i class="mdi mdi-flag"></i> Review
                </span>
                <span v-else class="badge bg-success">
                  <i class="mdi mdi-check"></i> OK
                </span>
              </td>
              <td class="text-center">
                <div class="btn-group btn-group-sm">
                  <button class="btn btn-light" title="Edit" @click="$emit('edit-entry', entry)">
                    <i class="mdi mdi-pencil"></i>
                  </button>
                  <button 
                    v-if="!entry.requires_review"
                    class="btn btn-light" 
                    title="Flag for Review" 
                    @click="$emit('flag-entry', entry)"
                  >
                    <i class="mdi mdi-flag text-warning"></i>
                  </button>
                  <button class="btn btn-light text-danger" title="Delete" @click="$emit('delete-entry', entry)">
                    <i class="mdi mdi-delete"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="d-flex justify-content-between align-items-center mt-3">
        <div class="text-muted">
          Showing {{ ((currentPage - 1) * pageSize) + 1 }} to {{ Math.min(currentPage * pageSize, totalEntries) }} of {{ totalEntries }} entries
        </div>
        <nav>
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <a class="page-link" href="#" @click.prevent="$emit('page-change', currentPage - 1)">
                <i class="mdi mdi-chevron-left"></i>
              </a>
            </li>
            <li 
              v-for="page in visiblePages" 
              :key="page" 
              class="page-item" 
              :class="{ active: page === currentPage }"
            >
              <a class="page-link" href="#" @click.prevent="$emit('page-change', page)">
                {{ page }}
              </a>
            </li>
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <a class="page-link" href="#" @click.prevent="$emit('page-change', currentPage + 1)">
                <i class="mdi mdi-chevron-right"></i>
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GLEntryListItem } from '@/stores/generalLedger'

const props = defineProps<{
  entries: GLEntryListItem[]
  loading: boolean
  currentPage: number
  pageSize: number
  totalEntries: number
}>()

defineEmits<{
  (e: 'page-change', page: number): void
  (e: 'edit-entry', entry: GLEntryListItem): void
  (e: 'delete-entry', entry: GLEntryListItem): void
  (e: 'flag-entry', entry: GLEntryListItem): void
}>()

const totalPages = computed(() => Math.ceil(props.totalEntries / props.pageSize))

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  let start = Math.max(1, props.currentPage - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatCurrency(value: any): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (num === 0) return '-'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(Math.abs(num || 0))
}

function getNetColorClass(amount: any): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (num > 0) return 'text-success'
  if (num < 0) return 'text-danger'
  return 'text-secondary'
}

function formatTag(tag: string): string {
  return tag.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

function formatBucket(bucket: string): string {
  return bucket.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

function getTagBadgeClass(tag: string): string {
  const tagColors: Record<string, string> = {
    'loan_origination': 'bg-primary',
    'loan_payment': 'bg-success',
    'property_acquisition': 'bg-info',
    'property_disposition': 'bg-warning',
    'interest_income': 'bg-success',
    'interest_expense': 'bg-danger',
  }
  return tagColors[tag] || 'bg-secondary'
}
</script>

<style scoped>
.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  background-color: #f8f9fa;
}

.table-hover tbody tr:hover {
  background-color: #f1f3fa;
}

.table-warning {
  background-color: #fff3cd !important;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}
</style>

