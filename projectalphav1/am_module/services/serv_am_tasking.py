# ============================================================
# WHAT: Service functions for task completion metrics and status logic
# WHY: Centralize business logic for determining active vs completed tasks
# WHERE: Called by view_am_tasking.py to provide dashboard metrics
# HOW: Filter tasks by completion status based on task_type values
# ============================================================

from typing import Dict, List, Any
from am_module.models.am_data import (
    FCTask,
    REOtask,
    DILTask,
    ShortSaleTask,
    ModificationTask,
    FCSale,
    REOData,
    DIL,
    ShortSale,
    Modification,
)


def get_task_metrics(hub_id: int) -> Dict[str, Any]:
    """
    WHAT: Calculate active and completed task counts for a hub
    WHY: Provide task completion metrics for the tasking dashboard UI
    WHERE: Called by view_am_tasking.py endpoint for dashboard data
    HOW: Query all task types, filter by completion status, aggregate counts
    
    Args:
        hub_id: The asset hub ID to get metrics for
        
    Returns:
        dict: {
            'active_count': int,
            'completed_count': int,
            'active_items': list of task pill data for UI badges,
            'completed_items': list of task pill data for UI badges
        }
    
    Business Rules:
        - FC Task "sold" = completed
        - REO Task "sold" = completed  
        - DIL Task "dil_successful" = completed
        - Short Sale Task "sold" = completed
        - Modification Task "mod_accepted" = completed
        - All other task types = active
    """
    # WHAT: Define completion task_type values per outcome
    # WHY: Different outcomes have different completion criteria
    # HOW: Map model class to list of task_type values that mean "done"
    COMPLETION_TASK_TYPES = {
        FCTask: ['sold'],
        REOtask: ['sold'],
        DILTask: ['dil_successful'],
        ShortSaleTask: ['sold'],
        ModificationTask: ['mod_accepted'],
    }
    
    active_tasks = []
    completed_tasks = []
    
    # WHAT: Query each task type for this hub
    # WHY: Tasks are stored in separate tables per outcome type
    # HOW: Iterate through each model, filter by hub_id, check completion status
    for task_model, completion_types in COMPLETION_TASK_TYPES.items():
        tasks = task_model.objects.filter(asset_hub_id=hub_id).select_related('asset_hub')
        
        for task in tasks:
            # WHAT: Check if task_type indicates completion
            # WHY: task_type field holds the workflow stage (e.g., "sold", "executed")
            # HOW: Compare task.task_type against completion list (case-insensitive)
            task_type_lower = task.task_type.lower() if task.task_type else ''
            
            if task_type_lower in completion_types:
                completed_tasks.append({
                    'model': task_model.__name__,
                    'task': task,
                })
            else:
                active_tasks.append({
                    'model': task_model.__name__,
                    'task': task,
                })
    
    return {
        'active_count': len(active_tasks),
        'completed_count': len(completed_tasks),
        'active_items': _serialize_task_pills(active_tasks, is_completed=False),
        'completed_items': _serialize_task_pills(completed_tasks, is_completed=True),
    }


def _serialize_task_pills(task_data_list: List[Dict[str, Any]], is_completed: bool = False) -> List[Dict[str, str]]:
    """
    WHAT: Convert task objects to pill badge data for UI
    WHY: Frontend needs label, tone, and key for each badge display
    WHERE: Helper for get_task_metrics
    HOW: Map task data to UI badge format with outcome-specific colors
    
    Args:
        task_data_list: List of dicts with 'model' (str) and 'task' (model instance)
        is_completed: If True, use 'success' tone for all tasks (green for sold/completed)
        
    Returns:
        List of dicts with 'key', 'label', 'tone' for UI badges
    """
    pills = []
    
    for item in task_data_list:
        model_name = item['model']
        task = item['task']
        
        # WHAT: Extract outcome type from model name
        # WHY: Model names like "FCTask" map to outcome types like "fc"
        # HOW: Remove "Task" suffix and lowercase
        outcome_type = model_name.replace('Task', '').replace('task', '').lower()
        
        # WHAT: Get human-readable label from task_type choices
        # WHY: Display friendly names like "Sold" instead of "sold"
        # HOW: Use get_task_type_display() Django method
        label = task.get_task_type_display() if hasattr(task, 'get_task_type_display') else task.task_type.upper()
        
        # WHAT: Use 'success' (green) tone for all completed tasks
        # WHY: All sold/executed/completed tasks should be green per project standards
        # HOW: Check is_completed flag, otherwise use outcome-specific tone
        tone = 'success' if is_completed else _get_outcome_tone(outcome_type)
        
        pills.append({
            'key': f"{outcome_type}_{task.id}",
            'label': label,
            'tone': tone,
        })
    
    return pills


def _get_outcome_tone(outcome_type: str) -> str:
    """
    WHAT: Map outcome type to UI badge color tone
    WHY: Consistent color coding across the application matching project badge standards
    WHERE: Helper for _serialize_task_pills
    HOW: Simple dictionary lookup using badgeTokens.ts standard tones
    
    Args:
        outcome_type: String like 'fc', 'reo', 'dil', 'shortsale', 'modification'
        
    Returns:
        String tone value for UiBadge component matching badgeTokens.ts
        - 'success' (green) for completed/sold tasks
        - Other tones for active tasks
    """
    tone_map = {
        'fc': 'danger',
        'reo': 'info',
        'dil': 'primary',
        'shortsale': 'warning',
        'modification': 'secondary',
    }
    return tone_map.get(outcome_type, 'secondary')


def get_active_outcome_tracks(hub_id: int) -> Dict[str, Any]:
    """
    WHAT: Determine which outcome tracks are active vs completed for a hub
    WHY: Active Tracks should only show outcomes that haven't reached completion
    WHERE: Called by view_am_tasking.py endpoint for dashboard data
    HOW: Check if outcome has any tasks with completion status
    
    Args:
        hub_id: The asset hub ID to get active tracks for
        
    Returns:
        dict: {
            'active_tracks': list of outcome types that are active,
            'completed_tracks': list of outcome types that are completed,
            'active_track_badges': list of badge data for active tracks
        }
    
    Business Rules:
        - If an outcome has ANY task with completion status, the track is completed
        - FC with "sold" task → completed track
        - REO with "sold" task → completed track
        - DIL with "executed" task → completed track
        - Short Sale with "sold" task → completed track
        - Modification with "completed" task → completed track
    """
    # WHAT: Map outcome models to their task models and completion types
    # WHY: Need to check if outcome has completed tasks
    # HOW: Query outcome, then check its tasks for completion status
    OUTCOME_CONFIG = {
        'fc': {
            'outcome_model': FCSale,
            'task_model': FCTask,
            'completion_types': ['sold'],
            'label': 'FC',
            'tone': 'danger',
        },
        'reo': {
            'outcome_model': REOData,
            'task_model': REOtask,
            'completion_types': ['sold'],
            'label': 'REO',
            'tone': 'info',
        },
        'dil': {
            'outcome_model': DIL,
            'task_model': DILTask,
            'completion_types': ['executed'],
            'label': 'DIL',
            'tone': 'primary',
        },
        'short_sale': {
            'outcome_model': ShortSale,
            'task_model': ShortSaleTask,
            'completion_types': ['sold'],
            'label': 'Short Sale',
            'tone': 'warning',
        },
        'modification': {
            'outcome_model': Modification,
            'task_model': ModificationTask,
            'completion_types': ['completed'],
            'label': 'Modification',
            'tone': 'secondary',
        },
    }
    
    active_tracks = []
    completed_tracks = []
    active_track_badges = []
    
    for outcome_type, config in OUTCOME_CONFIG.items():
        # WHAT: Check if this outcome exists for this hub
        # WHY: Only show tracks that have been created
        # HOW: Query outcome model by asset_hub_id
        outcome_exists = config['outcome_model'].objects.filter(asset_hub_id=hub_id).exists()
        
        if not outcome_exists:
            continue
        
        # WHAT: Check if outcome has any completed tasks
        # WHY: Completed tasks mean the track is done
        # HOW: Query tasks and check for completion task_types
        tasks = config['task_model'].objects.filter(asset_hub_id=hub_id)
        has_completed_task = False
        
        for task in tasks:
            task_type_lower = task.task_type.lower() if task.task_type else ''
            if task_type_lower in config['completion_types']:
                has_completed_task = True
                break
        
        if has_completed_task:
            completed_tracks.append(outcome_type)
        else:
            active_tracks.append(outcome_type)
            active_track_badges.append({
                'key': f"track_{outcome_type}",
                'label': config['label'],
                'tone': config['tone'],
            })
    
    return {
        'active_tracks': active_tracks,
        'completed_tracks': completed_tracks,
        'active_track_badges': active_track_badges,
        'active_track_count': len(active_tracks),
        'completed_track_count': len(completed_tracks),
    }
