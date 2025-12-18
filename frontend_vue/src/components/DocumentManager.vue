<template>
  <div class="document-manager">
    <h2>Document Manager</h2>
    
    <!-- Upload Section -->
    <div class="upload-section">
      <h3>Upload Document</h3>
      <input 
        type="file" 
        ref="fileInput" 
        @change="handleFileSelect"
        class="file-input"
      />
      <button 
        @click="uploadFile" 
        :disabled="!selectedFile || uploading"
        class="btn-primary"
      >
        {{ uploading ? 'Uploading...' : 'Upload' }}
      </button>
      
      <div v-if="uploadMessage" class="message" :class="uploadSuccess ? 'success' : 'error'">
        {{ uploadMessage }}
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <h3>Search Documents</h3>
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Search documents..."
        @keyup.enter="searchDocuments"
        class="search-input"
      />
      <button @click="searchDocuments" class="btn-secondary">Search</button>
    </div>

    <!-- Search Results -->
    <div v-if="searchResults.length > 0" class="search-results">
      <h4>Search Results</h4>
      <ul>
        <li v-for="(result, index) in searchResults" :key="index">
          {{ result.name || result.path }}
        </li>
      </ul>
    </div>

    <!-- Document List Section -->
    <div class="documents-section">
      <h3>Documents in Current Folder</h3>
      <button @click="loadDocuments" class="btn-secondary">Refresh</button>
      
      <div v-if="loading" class="loading">Loading documents...</div>
      
      <div v-if="documents.length > 0" class="document-list">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in documents" :key="doc.entry_id">
              <td>{{ doc.name }}</td>
              <td>{{ doc.is_folder ? 'Folder' : 'File' }}</td>
              <td>
                <button 
                  v-if="!doc.is_folder" 
                  @click="downloadFile(doc.path)"
                  class="btn-small"
                >
                  Download
                </button>
                <button 
                  v-if="!doc.is_folder" 
                  @click="createShareLink(doc.path)"
                  class="btn-small"
                >
                  Share
                </button>
                <button 
                  @click="deleteFile(doc.path)"
                  class="btn-small btn-danger"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="!loading" class="no-documents">
        No documents found in this folder.
      </div>
    </div>

    <!-- Share Link Modal -->
    <div v-if="shareLink" class="modal">
      <div class="modal-content">
        <h3>Share Link Created</h3>
        <p>{{ shareLink }}</p>
        <button @click="copyShareLink" class="btn-primary">Copy Link</button>
        <button @click="shareLink = null" class="btn-secondary">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * DocumentManager Component
 * 
 * This component demonstrates how Vue.js calls Django REST API
 * which then communicates with Egnyte.
 * 
 * Flow:
 * 1. User clicks "Upload" button
 * 2. Vue calls egnyteService.uploadDocument()
 * 3. egnyteService makes HTTP request to Django (/api/core/documents/upload/)
 * 4. Django receives request and calls Egnyte REST API
 * 5. Egnyte processes the upload and responds to Django
 * 6. Django sends response back to Vue
 * 7. Vue displays success/error message to user
 */

import egnyteService from '@/services/egnyteService';

export default {
  name: 'DocumentManager',
  
  data() {
    return {
      selectedFile: null,
      uploading: false,
      uploadMessage: '',
      uploadSuccess: false,
      
      documents: [],
      loading: false,
      currentFolder: '/Shared',
      
      searchQuery: '',
      searchResults: [],
      
      shareLink: null
    };
  },
  
  mounted() {
    // Load documents when component is mounted
    this.loadDocuments();
  },
  
  methods: {
    /**
     * Handle file selection from input
     * This happens BEFORE the REST API call
     */
    handleFileSelect(event) {
      this.selectedFile = event.target.files[0];
      this.uploadMessage = '';
    },
    
    /**
     * Upload file to Egnyte via Django REST API
     * 
     * REST API Flow:
     * Vue --HTTP POST--> Django --HTTP POST--> Egnyte
     * Vue <--JSON------- Django <--JSON------- Egnyte
     */
    async uploadFile() {
      if (!this.selectedFile) return;
      
      this.uploading = true;
      this.uploadMessage = '';
      
      try {
        // Call Django REST API (which calls Egnyte)
        const response = await egnyteService.uploadDocument(
          this.selectedFile,
          this.currentFolder
        );
        
        if (response.success) {
          this.uploadMessage = 'File uploaded successfully!';
          this.uploadSuccess = true;
          this.selectedFile = null;
          this.$refs.fileInput.value = '';
          
          // Refresh document list
          this.loadDocuments();
        } else {
          this.uploadMessage = `Upload failed: ${response.error}`;
          this.uploadSuccess = false;
        }
      } catch (error) {
        this.uploadMessage = `Error: ${error.message}`;
        this.uploadSuccess = false;
      } finally {
        this.uploading = false;
      }
    },
    
    /**
     * Load documents from current folder
     * 
     * REST API Flow:
     * Vue --HTTP GET--> Django --HTTP GET--> Egnyte
     * Vue <--JSON----- Django <--JSON----- Egnyte
     */
    async loadDocuments() {
      this.loading = true;
      
      try {
        const response = await egnyteService.listDocuments(this.currentFolder);
        
        if (response.success) {
          // Extract files and folders from response
          const data = response.data;
          this.documents = [
            ...(data.folders || []).map(f => ({ ...f, is_folder: true })),
            ...(data.files || []).map(f => ({ ...f, is_folder: false }))
          ];
        }
      } catch (error) {
        console.error('Error loading documents:', error);
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * Download a file
     * 
     * REST API Flow:
     * Vue --HTTP GET--> Django --HTTP GET--> Egnyte
     * Vue <--BLOB----- Django <--BLOB----- Egnyte
     */
    async downloadFile(filePath) {
      try {
        await egnyteService.downloadDocument(filePath);
      } catch (error) {
        alert(`Error downloading file: ${error.message}`);
      }
    },
    
    /**
     * Delete a file
     * 
     * REST API Flow:
     * Vue --HTTP DELETE--> Django --HTTP DELETE--> Egnyte
     * Vue <--JSON--------- Django <--JSON--------- Egnyte
     */
    async deleteFile(filePath) {
      if (!confirm(`Are you sure you want to delete ${filePath}?`)) {
        return;
      }
      
      try {
        const response = await egnyteService.deleteDocument(filePath);
        
        if (response.success) {
          alert('File deleted successfully');
          this.loadDocuments(); // Refresh list
        } else {
          alert(`Delete failed: ${response.error}`);
        }
      } catch (error) {
        alert(`Error deleting file: ${error.message}`);
      }
    },
    
    /**
     * Search for documents
     * 
     * REST API Flow:
     * Vue --HTTP GET--> Django --HTTP GET--> Egnyte
     * Vue <--JSON----- Django <--JSON----- Egnyte
     */
    async searchDocuments() {
      if (!this.searchQuery.trim()) return;
      
      try {
        const response = await egnyteService.searchDocuments(
          this.searchQuery,
          this.currentFolder
        );
        
        if (response.success) {
          this.searchResults = response.results;
        }
      } catch (error) {
        console.error('Error searching documents:', error);
      }
    },
    
    /**
     * Create a shareable link for a file
     * 
     * REST API Flow:
     * Vue --HTTP POST--> Django --HTTP POST--> Egnyte
     * Vue <--JSON------ Django <--JSON------ Egnyte
     */
    async createShareLink(filePath) {
      try {
        const response = await egnyteService.createShareLink(filePath);
        
        if (response.success) {
          this.shareLink = response.link;
        } else {
          alert(`Error creating share link: ${response.error}`);
        }
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    },
    
    /**
     * Copy share link to clipboard
     */
    copyShareLink() {
      navigator.clipboard.writeText(this.shareLink);
      alert('Link copied to clipboard!');
    }
  }
};
</script>

<style scoped>
.document-manager {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.upload-section,
.search-section,
.documents-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
}

h2 {
  color: #333;
  margin-bottom: 20px;
}

h3 {
  color: #555;
  margin-bottom: 15px;
}

.file-input,
.search-input {
  padding: 8px 12px;
  margin-right: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary,
.btn-secondary,
.btn-small {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 5px;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
  background: #28a745;
  color: white;
}

.btn-small:hover {
  background: #218838;
}

.btn-danger {
  background: #dc3545;
}

.btn-danger:hover {
  background: #c82333;
}

.message {
  margin-top: 10px;
  padding: 10px;
  border-radius: 4px;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.document-list table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.document-list th,
.document-list td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.document-list th {
  background: #f0f0f0;
  font-weight: bold;
}

.loading,
.no-documents {
  padding: 20px;
  text-align: center;
  color: #666;
}

.search-results {
  margin-top: 15px;
}

.search-results ul {
  list-style: none;
  padding: 0;
}

.search-results li {
  padding: 8px;
  background: #FDFBF7;
  margin-bottom: 5px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #FDFBF7;
  padding: 30px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal-content p {
  word-break: break-all;
  margin: 15px 0;
  padding: 10px;
  background: #f0f0f0;
  border-radius: 4px;
}
</style>

