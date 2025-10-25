# Auto-Refresh Implementation Guide

## **Problem Solved**
When you add/delete tracks or tasks in one component, other components don't automatically update and you have to manually refresh the page.

## **Solution: Event Bus Pattern**

### **1. Event Bus (`src/lib/eventBus.ts`)**
- Central event system for cross-component communication
- Type-safe event definitions
- Emit events when data changes
- Listen for events to auto-refresh

### **2. Composable (`src/composables/useDataRefresh.ts`)**
- Reusable hook for auto-refresh functionality
- Provides event listeners and emit helpers
- Handles cleanup automatically

## **Implementation Steps**

### **Step 1: Add Auto-Refresh to Display Components**

For components that **display** data (like Milestones, KeyContacts):

```typescript
// In your component script
import { useDataRefresh } from '@/composables/useDataRefresh'

// Setup auto-refresh
const { emitDataRefresh } = useDataRefresh(props.hubId, () => {
  // Your refresh function here
  loadYourData()
})
```

### **Step 2: Emit Events When Modifying Data**

For components that **modify** data (like outcome cards):

```typescript
// In your component script
import { useDataRefresh } from '@/composables/useDataRefresh'

const { emitTaskAdded, emitTaskDeleted, emitTaskUpdated } = useDataRefresh(props.hubId, refreshCallback)

// When adding a task
async function addTask(taskType: string) {
  const newTask = await api.createTask(...)
  await refreshLocalData()
  emitTaskAdded('modification', newTask.id) // 🔥 This triggers auto-refresh!
}

// When deleting a task  
async function deleteTask(taskId: number) {
  await api.deleteTask(taskId)
  await refreshLocalData()
  emitTaskDeleted('modification', taskId) // 🔥 This triggers auto-refresh!
}

// When updating a task
async function updateTask(taskId: number, data: any) {
  await api.updateTask(taskId, data)
  await refreshLocalData()
  emitTaskUpdated('modification', taskId) // 🔥 This triggers auto-refresh!
}
```

## **Available Events**

### **Track Events**
- `emitTrackAdded(trackType)` - When outcome/track is created
- `emitTrackUpdated(trackType)` - When outcome/track is modified  
- `emitTrackDeleted(trackType)` - When outcome/track is removed

### **Task Events**
- `emitTaskAdded(trackType, taskId)` - When task is created
- `emitTaskUpdated(trackType, taskId)` - When task is modified
- `emitTaskDeleted(trackType, taskId)` - When task is removed

### **General Events**
- `emitDataRefresh()` - Force refresh all components

## **Example: ModificationCard Integration**

```typescript
// ✅ Already implemented in ModificationCard.vue
const { emitTaskAdded, emitTaskDeleted, emitTaskUpdated } = useDataRefresh(props.hubId, async () => {
  tasks.value = await store.listModificationTasks(props.hubId, true)
})

// When adding task
function onSelectPill(tp: ModificationTaskType) {
  store.createModificationTask(props.hubId, tp)
    .then(async (newTask) => { 
      tasks.value = await store.listModificationTasks(props.hubId, true)
      emitTaskAdded('modification', newTask?.id || 0) // 🔥 Auto-refresh trigger
    })
}

// When deleting task
async function confirmDeleteTask() {
  await store.deleteModificationTask(props.hubId, taskId)
  tasks.value = await store.listModificationTasks(props.hubId, true)
  emitTaskDeleted('modification', taskId) // 🔥 Auto-refresh trigger
}
```

## **Components Updated**

### **✅ Already Implemented**
- `milestonesCard.vue` - Listens for all events, auto-refreshes
- `KeyContacts.vue` - Listens for contact events, auto-refreshes  
- `ModificationCard.vue` - Emits events when tasks change

### **🔄 Need Implementation**
Apply the same pattern to:
- `ForeClosureCard.vue`
- `DILCard.vue` 
- `ShortSaleCard.vue`
- `REOCard.vue`
- Any other outcome cards

## **Benefits**

1. **No Manual Refresh** - Data updates automatically across all components
2. **Real-time Sync** - Changes appear immediately in all views
3. **Type Safety** - TypeScript ensures correct event usage
4. **Memory Safe** - Auto cleanup prevents memory leaks
5. **Reusable** - Same pattern works for all components

## **Testing**

1. Open AM Tasking page
2. Add a task in ModificationCard
3. Watch Milestones card update automatically ✨
4. Delete a task in ModificationCard  
5. Watch Milestones card refresh automatically ✨

**No more manual page refreshes needed!** 🎉
