<template>
  <!--
    AwardedAssetsUpload - Modal for uploading awarded assets list
    WHAT: UI for bulk dropping non-awarded assets
    WHY: Users need to process awarded assets after winning bids
    HOW: Upload file → AI extraction → Preview → Confirm drop
  -->
  <div
    class="modal fade"
    id="awardedAssetsModal"
    tabindex="-1"
    aria-labelledby="awardedAssetsModalLabel"
    aria-hidden="true"
    data-bs-backdrop="static"
  >
    <div class="modal-dialog modal-xl modal-dialog-scrollable">
      <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
          <h5 class="modal-title" id="awardedAssetsModalLabel">
            <i class="mdi mdi-trophy me-2"></i>Process Awarded Assets
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            :disabled="processing"
          ></button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <!-- Step 1: Upload File -->
          <div v-if="step === 1" class="text-center py-4">
            <h4 class="mb-3">Upload Awarded Assets List</h4>
            <p class="text-muted mb-4">
              Upload a file containing the IDs of assets you won. We'll automatically extract the IDs and show you what will be kept vs. dropped.
            </p>

            <!-- File Drop Zone -->
            <div
              class="file-drop-zone"
              :class="{ 'drag-over': dragOver }"
              @dragover.prevent="dragOver = true"
              @dragleave.prevent="dragOver = false"
              @drop.prevent="handleFileDrop"
              @click="$refs.fileInput.click()"
            >
              <i class="mdi mdi-cloud-upload display-1 text-muted mb-3"></i>
              <h5>Drag & drop file here or click to browse</h5>
              <p class="text-muted mb-0">
                Supports: CSV, Excel, PDF, Images
              </p>
              <input
                ref="fileInput"
                type="file"
                accept=".csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg,.gif,.webp"
                style="display: none"
                @change="handleFileSelect"
              />
            </div>

            <!-- Selected File Info -->
            <div v-if="selectedFile" class="alert alert-info mt-3">
              <i class="mdi mdi-file-document me-2"></i>
              <strong>{{ selectedFile.name }}</strong>
              ({{ formatFileSize(selectedFile.size) }})
              <button
                class="btn btn-sm btn-link text-danger float-end"
                @click="clearFile"
              >
                <i class="mdi mdi-close"></i>
              </button>
            </div>

            <!-- Upload Button -->
            <button
              v-if="selectedFile"
              class="btn btn-primary btn-lg mt-3"
              @click="uploadAndExtract"
              :disabled="uploading"
            >
              <span v-if="uploading">
                <span class="spinner-border spinner-border-sm me-2"></span>
                AI is analyzing your file...
              </span>
              <span v-else>
                <i class="mdi mdi-robot me-2"></i>Extract IDs with AI
              </span>
            </button>
          </div>

          <!-- Step 2: Preview -->
          <div v-if="step === 2">
            <div class="alert alert-warning">
              <i class="mdi mdi-alert me-2"></i>
              <strong>Review Before Confirming:</strong> This will mark {{ preview.summary.will_drop }} assets as DROPPED. This can be undone later.
            </div>

            <!-- Summary Stats -->
            <div class="row mb-3">
              <div class="col-md-3">
                <div class="card bg-light">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ preview.summary.total_in_trade }}</h3>
                    <p class="text-muted mb-0">Total Assets</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card bg-success text-white">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ preview.summary.will_keep }}</h3>
                    <p class="mb-0">Will Keep</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card bg-danger text-white">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ preview.summary.will_drop }}</h3>
                    <p class="mb-0">Will Drop</p>
                  </div>
                </div>
              </div>
              <div class="col-md-3">
                <div class="card bg-warning text-white">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ preview.summary.unmatched_from_file }}</h3>
                    <p class="mb-0">Not Found</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tabs for Keep/Drop/Unmatched -->
            <ul class="nav nav-tabs" role="tablist">
              <li class="nav-item">
                <a
                  class="nav-link active"
                  data-bs-toggle="tab"
                  href="#keepTab"
                  role="tab"
                >
                  <i class="mdi mdi-check-circle text-success me-1"></i>
                  Will Keep ({{ preview.summary.will_keep }})
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  data-bs-toggle="tab"
                  href="#dropTab"
                  role="tab"
                >
                  <i class="mdi mdi-close-circle text-danger me-1"></i>
                  Will Drop ({{ preview.summary.will_drop }})
                </a>
              </li>
              <li class="nav-item" v-if="preview.unmatched_ids.length > 0">
                <a
                  class="nav-link"
                  data-bs-toggle="tab"
                  href="#unmatchedTab"
                  role="tab"
                >
                  <i class="mdi mdi-alert-circle text-warning me-1"></i>
                  Not Found ({{ preview.unmatched_ids.length }})
                </a>
              </li>
            </ul>

            <!-- Tab Content -->
            <div class="tab-content border border-top-0 p-3" style="max-height: 400px; overflow-y: auto;">
              <!-- Keep Tab -->
              <div class="tab-pane fade show active" id="keepTab" role="tabpanel">
                <table class="table table-sm table-hover">
                  <thead>
                    <tr>
                      <th>Seller Tape ID</th>
                      <th>Address</th>
                      <th>City, State</th>
                      <th>Balance</th>
                      <th>Matched On</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="asset in preview.matched_assets" :key="asset.id">
                      <td><code>{{ asset.sellertape_id }}</code></td>
                      <td>{{ asset.street_address }}</td>
                      <td>{{ asset.city }}, {{ asset.state }}</td>
                      <td>${{ formatNumber(asset.current_balance) }}</td>
                      <td><span class="badge bg-success">{{ asset.matched_on }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Drop Tab -->
              <div class="tab-pane fade" id="dropTab" role="tabpanel">
                <table class="table table-sm table-hover">
                  <thead>
                    <tr>
                      <th>Seller Tape ID</th>
                      <th>Address</th>
                      <th>City, State</th>
                      <th>Balance</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="asset in preview.will_be_dropped" :key="asset.id">
                      <td><code>{{ asset.sellertape_id }}</code></td>
                      <td>{{ asset.street_address }}</td>
                      <td>{{ asset.city }}, {{ asset.state }}</td>
                      <td>${{ formatNumber(asset.current_balance) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Unmatched Tab -->
              <div class="tab-pane fade" id="unmatchedTab" role="tabpanel">
                <div class="alert alert-warning">
                  <i class="mdi mdi-alert me-2"></i>
                  These IDs were in your file but not found in the database. They may be typos or from a different trade.
                </div>
                <div class="d-flex flex-wrap gap-2">
                  <span
                    v-for="(id, index) in preview.unmatched_ids"
                    :key="index"
                    class="badge bg-warning text-dark"
                  >
                    {{ id }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Success -->
          <div v-if="step === 3" class="text-center py-5">
            <i class="mdi mdi-check-circle display-1 text-success mb-3"></i>
            <h4 class="text-success mb-3">Successfully Processed!</h4>
            <p class="text-muted">
              {{ result.kept_count }} assets kept, {{ result.dropped_count }} assets dropped.
            </p>
            <button class="btn btn-primary" @click="closeModal">
              <i class="mdi mdi-check me-1"></i>Done
            </button>
          </div>

          <!-- Error State -->
          <div v-if="error" class="alert alert-danger">
            <i class="mdi mdi-alert-circle me-2"></i>
            <strong>Error:</strong> {{ error }}
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer" v-if="step === 2">
          <button
            type="button"
            class="btn btn-secondary"
            @click="goBack"
            :disabled="processing"
          >
            <i class="mdi mdi-arrow-left me-1"></i>Back
          </button>
          <button
            type="button"
            class="btn btn-danger"
            @click="confirmDrop"
            :disabled="processing"
          >
            <span v-if="processing">
              <span class="spinner-border spinner-border-sm me-2"></span>
              Processing...
            </span>
            <span v-else>
              <i class="mdi mdi-delete me-1"></i>Drop {{ preview.summary.will_drop }} Assets
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import http from '@/lib/http';
import * as bootstrap from 'bootstrap';

export default {
  name: 'AwardedAssetsUpload',
  
  emits: ['assets-dropped', 'close'],
  
  props: {
    // WHAT: Trade ID to process
    // WHY: Scope operation to specific trade
    // HOW: Passed from parent component
    tradeId: {
      type: Number,
      required: true
    }
  },
  
  data() {
    return {
      // WHAT: Current step in workflow
      // WHY: Control UI flow
      // HOW: 1=upload, 2=preview, 3=success
      step: 1,
      
      // WHAT: Selected file
      // WHY: Track user's upload
      selectedFile: null,
      
      // WHAT: Drag over state
      // WHY: Visual feedback for drag-drop
      dragOver: false,
      
      // WHAT: Extracted IDs from AI
      // WHY: Store extraction results
      extractedIds: [],
      
      // WHAT: Preview data
      // WHY: Show user what will happen
      preview: null,
      
      // WHAT: Execution result
      // WHY: Show success message
      result: null,
      
      // WHAT: Loading states
      // WHY: Disable buttons during operations
      uploading: false,
      processing: false,
      
      // WHAT: Error message
      // WHY: Show user what went wrong
      error: null
    };
  },
  
  mounted() {
    console.log('[AwardedAssetsUpload] Component mounted for trade:', this.tradeId);
    const modalEl = document.getElementById('awardedAssetsModal');
    if (modalEl) {
      modalEl.addEventListener('hidden.bs.modal', () => {
        this.$emit('close');
      });
    }
  },
  
  methods: {
    /**
     * WHAT: Handle file selection from input
     * WHY: User clicked browse button
     * HOW: Get file from event
     */
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        this.error = null;
      }
    },
    
    /**
     * WHAT: Handle file drop
     * WHY: User dragged file into zone
     * HOW: Get file from dataTransfer
     */
    handleFileDrop(event) {
      this.dragOver = false;
      const file = event.dataTransfer.files[0];
      if (file) {
        this.selectedFile = file;
        this.error = null;
      }
    },
    
    /**
     * WHAT: Clear selected file
     * WHY: User wants to choose different file
     * HOW: Reset selectedFile
     */
    clearFile() {
      this.selectedFile = null;
      this.$refs.fileInput.value = '';
    },
    
    /**
     * WHAT: Upload file and extract IDs with AI
     * WHY: First step in workflow
     * HOW: POST to /api/acq/awarded-assets/upload/
     */
    async uploadAndExtract() {
      this.uploading = true;
      this.error = null;
      
      try {
        // WHAT: Build form data
        // WHY: Need multipart/form-data for file upload
        // HOW: Use FormData API
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('trade_id', this.tradeId);
        
        // WHAT: Upload and extract
        // WHY: Get IDs from file
        // HOW: POST request
        const response = await http.post('/acq/awarded-assets/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // WHAT: Check for errors
        // WHY: AI extraction may fail
        if (response.data.error) {
          this.error = response.data.error;
          return;
        }
        
        // WHAT: Store extracted IDs
        // WHY: Need for preview
        this.extractedIds = response.data.identifiers || [];
        
        if (this.extractedIds.length === 0) {
          this.error = 'No asset IDs found in file. Please check the file format.';
          return;
        }
        
        // WHAT: Automatically generate preview
        // WHY: Show user what will happen
        await this.generatePreview();
        
      } catch (error) {
        console.error('Upload failed:', error);
        this.error = error.response?.data?.error || 'Failed to upload file. Please try again.';
      } finally {
        this.uploading = false;
      }
    },
    
    /**
     * WHAT: Generate preview of drop operation
     * WHY: Show user what will be kept/dropped
     * HOW: POST to /api/acq/awarded-assets/preview/
     */
    async generatePreview() {
      this.processing = true;
      this.error = null;
      
      try {
        // WHAT: Request preview
        // WHY: Match IDs against database
        // HOW: POST request with extracted IDs
        const response = await http.post('/acq/awarded-assets/preview/', {
          trade_id: this.tradeId,
          awarded_ids: this.extractedIds
        });
        
        // WHAT: Store preview data
        // WHY: Display in UI
        this.preview = response.data;
        
        // WHAT: Move to preview step
        // WHY: Show user the results
        this.step = 2;
        
      } catch (error) {
        console.error('Preview failed:', error);
        this.error = error.response?.data?.error || 'Failed to generate preview. Please try again.';
      } finally {
        this.processing = false;
      }
    },
    
    /**
     * WHAT: Execute drop operation
     * WHY: User confirmed they want to drop
     * HOW: POST to /api/acq/awarded-assets/confirm/
     */
    async confirmDrop() {
      this.processing = true;
      this.error = null;
      
      try {
        // WHAT: Execute drop
        // WHY: User confirmed
        // HOW: POST request with awarded IDs
        const response = await http.post('/acq/awarded-assets/confirm/', {
          trade_id: this.tradeId,
          awarded_ids: this.extractedIds
        });
        
        // WHAT: Store result
        // WHY: Show success message
        this.result = response.data;
        
        // WHAT: Move to success step
        // WHY: Show completion
        this.step = 3;
        
        // WHAT: Emit event to parent immediately
        // WHY: Parent needs to refresh data right away
        // HOW: Emit event before showing success screen
        this.$emit('assets-dropped', this.result);
        
        // WHAT: Auto-close modal after showing success for 2 seconds
        // WHY: Give user time to see success message, then auto-close
        // HOW: Wait 2 seconds then close modal
        setTimeout(() => {
          this.closeModal();
        }, 2000);
        
      } catch (error) {
        console.error('Drop failed:', error);
        this.error = error.response?.data?.error || 'Failed to drop assets. Please try again.';
        this.processing = false;
      }
    },
    
    /**
     * WHAT: Go back to previous step
     * WHY: User wants to change file
     * HOW: Decrement step
     */
    goBack() {
      if (this.step > 1) {
        this.step--;
      }
    },
    
    /**
     * WHAT: Close modal
     * WHY: User is done
     * HOW: Bootstrap modal hide and cleanup
     */
    closeModal() {
      // WHAT: Get modal instance
      // WHY: Need to properly hide modal and remove backdrop
      // HOW: Get instance, hide, then manually remove backdrop
      const modalEl = document.getElementById('awardedAssetsModal');
      if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) {
          modal.hide();
        } else {
          // If no instance, create one and hide it
          const newModal = new bootstrap.Modal(modalEl);
          newModal.hide();
        }
        
        // WHAT: Remove backdrop if it exists
        // WHY: Bootstrap sometimes leaves backdrop behind
        // HOW: Find and remove backdrop element
        this.$nextTick(() => {
          const backdrop = document.querySelector('.modal-backdrop');
          if (backdrop) {
            backdrop.remove();
          }
          // Remove modal-open class from body if present
          document.body.classList.remove('modal-open');
          document.body.style.overflow = '';
          document.body.style.paddingRight = '';
        });
      }
      
      // WHAT: Reset state immediately
      // WHY: Clean up for next use
      // HOW: Reset all component state
      this.processing = false;
      this.uploading = false;
      this.step = 1;
      this.selectedFile = null;
      this.extractedIds = [];
      this.preview = null;
      this.result = null;
      this.error = null;
      
      // WHAT: Emit close event to parent
      // WHY: Parent needs to know modal is closed
      // HOW: Emit event
      this.$emit('close');
    },
    
    /**
     * WHAT: Format file size for display
     * WHY: Show human-readable size
     * HOW: Convert bytes to KB/MB
     */
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },
    
    /**
     * WHAT: Format number with commas
     * WHY: Make large numbers readable
     * HOW: Use toLocaleString
     */
    formatNumber(value) {
      if (!value) return '0';
      return parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      });
    }
  }
};
</script>

<style scoped>
/* WHAT: File drop zone styling */
/* WHY: Visual feedback for drag-drop */
/* HOW: Scoped CSS */

.file-drop-zone {
  border: 3px dashed #ccc;
  border-radius: 10px;
  padding: 60px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

.file-drop-zone:hover {
  border-color: #0d6efd;
  background-color: #e7f1ff;
}

.file-drop-zone.drag-over {
  border-color: #0d6efd;
  background-color: #e7f1ff;
  transform: scale(1.02);
}

.table {
  margin-bottom: 0;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 0.875rem;
}

.table td {
  font-size: 0.875rem;
  vertical-align: middle;
}

code {
  padding: 2px 6px;
  border-radius: 3px;
  background-color: #f8f9fa;
  color: #0d6efd;
  font-size: 0.875rem;
}
</style>
