/**
 * Egnyte Document Management Service
 * 
 * This service handles all API calls to the Django backend
 * which in turn communicates with Egnyte REST API.
 * 
 * HOW REST API WORKS:
 * 1. Vue Frontend makes HTTP request to Django Backend
 * 2. Django Backend processes request and calls Egnyte API
 * 3. Egnyte responds to Django
 * 4. Django sends response back to Vue Frontend
 */

import axios from 'axios';

// Base URL for your Django API
const API_BASE_URL = '/api/core/documents';

/**
 * Egnyte Document Service
 * Provides methods to interact with document storage via Django backend
 */
const egnyteService = {
  /**
   * Upload a file to Egnyte
   * 
   * @param {File} file - The file object from input element
   * @param {string} folderPath - Destination folder (optional)
   * @returns {Promise} - Response with upload status
   * 
   * REST API: POST /api/core/documents/upload/
   */
  async uploadDocument(file, folderPath = '/Shared/Documents') {
    try {
      // Create FormData object (required for file uploads)
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder_path', folderPath);

      // Make HTTP POST request to Django backend
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  },

  /**
   * List documents in a folder
   * 
   * @param {string} folderPath - Path to folder
   * @returns {Promise} - Response with folder contents
   * 
   * REST API: GET /api/core/documents/list/?folder_path=/Shared
   */
  async listDocuments(folderPath = '/Shared') {
    try {
      // Make HTTP GET request with query parameters
      const response = await axios.get(`${API_BASE_URL}/list/`, {
        params: {
          folder_path: folderPath
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error listing documents:', error);
      throw error;
    }
  },

  /**
   * Download a document from Egnyte
   * 
   * @param {string} filePath - Path to the file
   * @returns {Promise} - File blob
   * 
   * REST API: GET /api/core/documents/download/?file_path=/Shared/file.pdf
   */
  async downloadDocument(filePath) {
    try {
      // Make HTTP GET request with responseType 'blob' for binary data
      const response = await axios.get(`${API_BASE_URL}/download/`, {
        params: {
          file_path: filePath
        },
        responseType: 'blob' // Important for file downloads
      });

      // Create a download link and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filePath.split('/').pop()); // Extract filename
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return response.data;
    } catch (error) {
      console.error('Error downloading document:', error);
      throw error;
    }
  },

  /**
   * Delete a document from Egnyte
   * 
   * @param {string} filePath - Path to the file
   * @returns {Promise} - Response with deletion status
   * 
   * REST API: DELETE /api/core/documents/delete/
   */
  async deleteDocument(filePath) {
    try {
      // Make HTTP DELETE request
      const response = await axios.delete(`${API_BASE_URL}/delete/`, {
        data: {
          file_path: filePath
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error deleting document:', error);
      throw error;
    }
  },

  /**
   * Create a new folder in Egnyte
   * 
   * @param {string} folderPath - Path for new folder
   * @returns {Promise} - Response with creation status
   * 
   * REST API: POST /api/core/documents/folder/create/
   */
  async createFolder(folderPath) {
    try {
      // Make HTTP POST request
      const response = await axios.post(`${API_BASE_URL}/folder/create/`, {
        folder_path: folderPath
      });

      return response.data;
    } catch (error) {
      console.error('Error creating folder:', error);
      throw error;
    }
  },

  /**
   * Search for documents in Egnyte
   * 
   * @param {string} query - Search query
   * @param {string} folderPath - Folder to search in (optional)
   * @returns {Promise} - Response with search results
   * 
   * REST API: GET /api/core/documents/search/?query=invoice&folder_path=/Shared
   */
  async searchDocuments(query, folderPath = '/Shared') {
    try {
      // Make HTTP GET request with query parameters
      const response = await axios.get(`${API_BASE_URL}/search/`, {
        params: {
          query: query,
          folder_path: folderPath
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error searching documents:', error);
      throw error;
    }
  },

  /**
   * Create a shareable link for a file
   * 
   * @param {string} filePath - Path to the file
   * @param {string} linkType - 'file' or 'folder'
   * @param {string} expiryDate - Optional expiry date (YYYY-MM-DD)
   * @returns {Promise} - Response with shareable link
   * 
   * REST API: POST /api/core/documents/share/
   */
  async createShareLink(filePath, linkType = 'file', expiryDate = null) {
    try {
      const payload = {
        file_path: filePath,
        link_type: linkType
      };

      if (expiryDate) {
        payload.expiry_date = expiryDate;
      }

      // Make HTTP POST request
      const response = await axios.post(`${API_BASE_URL}/share/`, payload);

      return response.data;
    } catch (error) {
      console.error('Error creating share link:', error);
      throw error;
    }
  },

  /**
   * Get file metadata/information
   * 
   * @param {string} filePath - Path to the file
   * @returns {Promise} - Response with file metadata
   * 
   * REST API: GET /api/core/documents/info/?file_path=/Shared/file.pdf
   */
  async getFileInfo(filePath) {
    try {
      // Make HTTP GET request
      const response = await axios.get(`${API_BASE_URL}/info/`, {
        params: {
          file_path: filePath
        }
      });

      return response.data;
    } catch (error) {
      console.error('Error getting file info:', error);
      throw error;
    }
  }
};

export default egnyteService;

