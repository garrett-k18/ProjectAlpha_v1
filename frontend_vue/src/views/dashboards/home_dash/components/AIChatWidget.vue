<template>
  <!--
    AI Chat Widget
    WHAT: Classic AI chat interface for company-wide RAG-powered assistant
    WHY: Provides a conversational interface for querying company data and knowledge base
    HOW: Modular component with message history, input field, and send functionality
    FUTURE: Will integrate with backend RAG API for intelligent responses
  -->
  <div class="bg-transparent mb-0">
    <!-- Input Area (Now at the top) -->
    <div class="pt-2 pb-3">
      <form @submit.prevent="sendMessage" class="chat-input-wrapper shadow-sm">
        <input
          v-model="inputText"
          type="text"
          class="form-control border-0 bg-white py-2 px-3"
          placeholder="Type your question..."
          :disabled="isLoading"
          ref="inputRef"
        />
        <button
          type="submit"
          class="btn btn-primary btn-sm rounded-square p-0 d-flex align-items-center justify-content-center"
          style="width: 32px; height: 32px; margin-right: 6px;"
          :disabled="!inputText.trim() || isLoading"
        >
          <i v-if="!isLoading" class="ri-arrow-up-line fs-5"></i>
          <span v-else class="spinner-border spinner-border-sm" role="status"></span>
        </button>
      </form>
    </div>

    <!-- Compact Label & Actions (Below input) -->
    <div class="py-1 d-flex justify-content-between align-items-center opacity-75">
      <div class="text-uppercase small fw-bold text-muted letter-spacing-1" style="font-size: 0.65rem;">
        AI Assistant
      </div>
      <!-- Clear chat button (minimalist) -->
      <button 
        v-if="messages.length > 0"
        type="button" 
        class="btn btn-link btn-sm text-muted p-0 text-decoration-none"
        style="font-size: 0.65rem;"
        @click="clearChat"
      >
        Clear History
      </button>
    </div>

    <!-- Chat Messages Area (Dynamic height) -->
    <div 
      class="p-0 overflow-y-auto transition-all" 
      :style="{ height: messages.length === 0 ? '0px' : '300px' }" 
      ref="messagesContainer"
    >
      <!-- Messages List -->
      <div v-if="messages.length > 0" class="p-3">
        <div 
          v-for="(message, index) in messages" 
          :key="`msg-${index}`"
          class="mb-2"
        >
          <!-- User Message -->
          <div v-if="message.role === 'user'" class="d-flex justify-content-end">
            <div class="message-bubble message-user shadow-none py-1 px-2">
              <div class="message-content small">
                {{ message.content }}
              </div>
            </div>
          </div>
          
          <!-- AI Message -->
          <div v-else class="d-flex justify-content-start">
            <div class="message-bubble message-ai shadow-none py-1 px-2">
              <div class="message-content small">
                <div v-html="formatMessage(message.content)"></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Loading indicator -->
        <div v-if="isLoading" class="d-flex justify-content-start mb-2">
          <div class="message-bubble message-ai py-1 px-2">
            <div class="typing-indicator py-1">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * WHAT: AI Chat Widget Component
 * WHY: Provides conversational interface for company data queries
 * HOW: Uses Vue 3 Composition API with TypeScript
 * FUTURE: Will integrate with backend RAG API endpoint
 */

import { ref, nextTick, watch } from 'vue'
import http from '@/lib/http'

// WHAT: Message interface for type safety
// WHY: Ensures consistent message structure
interface ChatMessage {
  role: 'user' | 'assistant' // WHAT: Message sender type
  content: string            // WHAT: Message text content
}

// WHAT: Reactive state for chat messages
// WHY: Stores conversation history
const messages = ref<ChatMessage[]>([])

// WHAT: Current input text from user
// WHY: Binds to input field for two-way data binding
const inputText = ref<string>('')

// WHAT: Loading state when AI is processing
// WHY: Prevents multiple simultaneous requests and shows loading indicator
const isLoading = ref<boolean>(false)

// WHAT: Reference to messages container for auto-scrolling
// WHY: Scroll to bottom when new messages arrive
const messagesContainer = ref<HTMLElement | null>(null)

// WHAT: Reference to input field for focus management
// WHY: Auto-focus input after sending message
const inputRef = ref<HTMLInputElement | null>(null)

/**
 * WHAT: Format message content (simple markdown-like support)
 * WHY: Allow basic formatting in AI responses (bold, lists, code)
 * HOW: Simple regex replacements for common markdown patterns
 * NOTE: For production, consider using a proper markdown parser library
 */
function formatMessage(content: string): string {
  // WHAT: Escape HTML to prevent XSS
  // WHY: Security best practice when rendering user/AI content
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  // WHAT: Convert **bold** to <strong>
  // WHY: Support basic markdown formatting
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  
  // WHAT: Convert *italic* to <em>
  // WHY: Support italic text formatting
  formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>')
  
  // WHAT: Convert line breaks to <br>
  // WHY: Preserve multi-line formatting
  formatted = formatted.replace(/\n/g, '<br>')
  
  return formatted
}

/**
 * WHAT: Scroll messages container to bottom
 * WHY: Auto-scroll to show latest message
 * HOW: Use scrollTop to scroll to bottom of container
 */
async function scrollToBottom(): Promise<void> {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

/**
 * WHAT: Add user message to chat
 * WHY: Display user's question in chat history
 * HOW: Create message object and add to messages array
 */
function addUserMessage(content: string): void {
  messages.value.push({
    role: 'user',
    content: content.trim(),
  })
  scrollToBottom()
}

/**
 * WHAT: Add AI response message to chat
 * WHY: Display AI's answer in chat history
 * HOW: Create message object and add to messages array
 */
function addAIMessage(content: string): void {
  messages.value.push({
    role: 'assistant',
    content: content,
  })
  scrollToBottom()
}

/**
 * WHAT: Send message to AI backend (placeholder for future RAG integration)
 * WHY: Process user query and get AI response
 * HOW: POST to backend API endpoint (to be implemented)
 * NOTE: Currently returns placeholder response until backend is ready
 */
async function sendToAI(query: string): Promise<string> {
  // WHAT: Placeholder implementation - will be replaced with actual API call
  // WHY: Frontend is ready, waiting for backend RAG endpoint
  // HOW: Will POST to /api/ai/chat/ or similar endpoint
  
  try {
    // TODO: Replace with actual API call when backend is ready
    // const response = await http.post('/api/ai/chat/', { query })
    // return response.data.response
    
    // WHAT: Simulate API delay for realistic UX
    // WHY: Test loading states and user experience
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // WHAT: Return placeholder response
    // WHY: Show that system is working, but not yet connected to RAG
    return `I understand you're asking: "${query}". This is a placeholder response. The RAG-powered AI backend integration is coming soon! I'll be able to search through your company data, answer questions about assets, trades, valuations, and more.`
  } catch (error: any) {
    console.error('[AIChatWidget] Error sending message to AI:', error)
    return 'Sorry, I encountered an error processing your request. Please try again later.'
  }
}

/**
 * WHAT: Handle form submission to send message
 * WHY: Process user input and get AI response
 * HOW: Add user message, call AI API, add AI response
 */
async function sendMessage(): Promise<void> {
  // WHAT: Validate input
  // WHY: Don't send empty messages
  if (!inputText.value.trim() || isLoading.value) return
  
  // WHAT: Get user's question
  // WHY: Store before clearing input
  const userQuery = inputText.value.trim()
  
  // WHAT: Clear input immediately for better UX
  // WHY: User can type next question while AI is thinking
  inputText.value = ''
  
  // WHAT: Add user message to chat
  // WHY: Show user's question in chat history
  addUserMessage(userQuery)
  
  // WHAT: Set loading state
  // WHY: Show typing indicator and prevent duplicate requests
  isLoading.value = true
  
  try {
    // WHAT: Get AI response
    // WHY: Process query and return answer
    const aiResponse = await sendToAI(userQuery)
    
    // WHAT: Add AI response to chat
    // WHY: Display answer to user
    addAIMessage(aiResponse)
  } catch (error: any) {
    // WHAT: Handle errors gracefully
    // WHY: Show user-friendly error message
    console.error('[AIChatWidget] Error:', error)
    addAIMessage('Sorry, I encountered an error. Please try again.')
  } finally {
    // WHAT: Clear loading state
    // WHY: Re-enable input and hide loading indicator
    isLoading.value = false
    
    // WHAT: Focus input for next question
    // WHY: Better UX - user can immediately type next question
    await nextTick()
    inputRef.value?.focus()
  }
}

/**
 * WHAT: Clear all chat messages
 * WHY: Allow users to start fresh conversation
 * HOW: Reset messages array
 */
function clearChat(): void {
  if (confirm('Clear all chat messages?')) {
    messages.value = []
    inputText.value = ''
    inputRef.value?.focus()
  }
}

// WHAT: Watch messages array to auto-scroll
// WHY: Ensure new messages are visible
watch(messages, () => {
  scrollToBottom()
}, { deep: true })
</script>

<style scoped>
/**
 * WHAT: Custom styles for AI Chat Widget
 * WHY: Create modern, clean chat interface matching Hyper UI design system
 * HOW: Use Bootstrap utilities + custom CSS for message bubbles
 */

/* WHAT: Message bubble base styles */
.message-bubble {
  max-width: 85%;
  border-radius: 0; /* Squared corners */
  word-wrap: break-word;
}

/* WHAT: User message bubble */
.message-user {
  background-color: #D4AF37; /* Accent Gold from your palette */
  color: white;
}

/* WHAT: AI message bubble */
.message-ai {
  background-color: #F5F3EE; /* Cream background */
  color: #333;
}

/* WHAT: Message content styling */
.message-content {
  line-height: 1.4;
}

/* Chat input wrapper - make it look like a search bar */
.chat-input-wrapper {
  display: flex;
  align-items: center;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0; /* Squared corners */
  overflow: hidden;
  transition: all 0.2s ease;
}

.chat-input-wrapper:focus-within {
  border-color: #D4AF37;
  box-shadow: 0 0 0 0.2rem rgba(212, 175, 55, 0.15);
}

.chat-input-wrapper .form-control:focus {
  box-shadow: none;
  background-color: transparent;
}

.rounded-square {
  border-radius: 0 !important; /* Squared corners */
}

/* Extra small buttons for suggestions */
.btn-xs {
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
  border-radius: 4px;
}

.letter-spacing-1 {
  letter-spacing: 1px;
}

.transition-all {
  transition: all 0.3s ease-in-out;
}

/* WHAT: Typing indicator animation */
/* WHY: Show AI is "thinking" with animated dots */
.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #6c757d;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* WHAT: Custom scrollbar for messages area */
/* WHY: Better visual appearance than default scrollbar */
.card-body::-webkit-scrollbar {
  width: 6px;
}

.card-body::-webkit-scrollbar-track {
  background: #f1f3fa;
  border-radius: 3px;
}

.card-body::-webkit-scrollbar-thumb {
  background: #6c757d;
  border-radius: 3px;
}

.card-body::-webkit-scrollbar-thumb:hover {
  background: #495057;
}

/* WHAT: Quick suggestion buttons styling */
.btn-outline-light:hover {
  background-color: #D4AF37 !important;
  border-color: #D4AF37 !important;
  color: white !important;
}
</style>
