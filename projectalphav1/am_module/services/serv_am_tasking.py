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
    NoteSaleTask,
    FCSale,
    REOData,
    DIL,
    ShortSale,
    Modification,
    NoteSale,
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
    # WHAT: Define task sequences for each outcome type
    # WHY: Need to know the order of tasks to determine which is "most recent"
    # HOW: Map model class to ordered sequence of task_type values
    TASK_SEQUENCES = {
        FCTask: ['nod_noi', 'fc_filing', 'mediation', 'judgement', 'redemption', 'sale_scheduled', 'sold'],
        REOtask: ['eviction', 'trashout', 'renovation', 'marketing', 'under_contract', 'sold'],
        DILTask: ['pursuing_dil', 'owner_contacted', 'dil_failed', 'dil_drafted', 'dil_executed'],
        ShortSaleTask: ['list_price_accepted', 'listed', 'under_contract', 'sold'],
        ModificationTask: ['mod_drafted', 'mod_executed', 'mod_rpl', 'mod_failed'],
        NoteSaleTask: ['potential_note_sale', 'out_to_market', 'pending_sale', 'sold'],
    }
    
    # WHAT: Define which task types actually close the track
    # WHY: Some final tasks close the track (sold, failed), others don't (re-performing)
    # HOW: Map model class to list of task_type values that mean "track closed"
    TRACK_CLOSING_TYPES = {
        FCTask: ['sold'],
        REOtask: ['sold'],
        DILTask: ['dil_executed'],
        ShortSaleTask: ['sold'],
        ModificationTask: ['mod_failed'],  # Only 'failed' closes track, not 're-performing'
        NoteSaleTask: ['sold'],
    }
    
    active_tasks = []
    completed_tasks = []
    
    # WHAT: Process each task model to categorize tasks
    # WHY: Need to determine which task is most recent and which are superseded
    # HOW: For each model, find highest task in sequence and mark others as completed
    for task_model, sequence in TASK_SEQUENCES.items():
        tasks = task_model.objects.filter(asset_hub_id=hub_id).select_related('asset_hub')
        
        if not tasks:
            continue
        
        # WHAT: Find the highest (most recent) task in the sequence
        # WHY: Only the most recent task should be active, all previous are completed
        # HOW: Check each task's position in sequence, keep track of highest
        highest_index = -1
        highest_task = None
        closing_types = TRACK_CLOSING_TYPES.get(task_model, [])
        
        for task in tasks:
            task_type_lower = task.task_type.lower() if task.task_type else ''
            try:
                index = sequence.index(task_type_lower)
                if index > highest_index:
                    highest_index = index
                    highest_task = task
            except ValueError:
                # Task type not in sequence, skip it
                continue
        
        # WHAT: Categorize all tasks based on highest task found
        # WHY: Most recent task is active (unless it closes track), all others are completed
        # HOW: Compare each task's index to highest_index
        for task in tasks:
            task_type_lower = task.task_type.lower() if task.task_type else ''
            
            try:
                index = sequence.index(task_type_lower)
            except ValueError:
                # Task type not in sequence, skip it
                continue
            
            # WHAT: Check if this is the highest task
            if task.id == highest_task.id:
                # WHAT: Check if this task type closes the track
                if task_type_lower in closing_types:
                    # Track is closed, add to completed
                    completed_tasks.append({
                        'model': task_model.__name__,
                        'task': task,
                    })
                else:
                    # Most recent task but track still active
                    active_tasks.append({
                        'model': task_model.__name__,
                        'task': task,
                    })
            else:
                # WHAT: This task is superseded by a more recent task
                # WHY: Earlier tasks in sequence are considered "completed" when later tasks exist
                completed_tasks.append({
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
        
        # WHAT: Map outcome type to track prefix for badge labels
        # WHY: Show which track each task belongs to (e.g., "FC: Mediation")
        # HOW: Dictionary lookup with friendly track names
        track_prefix_map = {
            'fc': 'FC',
            'modification': 'Mod',
            'shortsale': 'Sh.Sale',
            'dil': 'DIL',
            'reo': 'REO',
            'notesale': 'Note Sale',
        }
        track_prefix = track_prefix_map.get(outcome_type, outcome_type.upper())
        
        # WHAT: Get human-readable label from task_type choices
        # WHY: Display friendly names like "Sold" instead of "sold"
        # HOW: Use get_task_type_display() Django method
        task_label = task.get_task_type_display() if hasattr(task, 'get_task_type_display') else task.task_type.upper()
        
        # WHAT: Combine track prefix with task label
        # WHY: Show context of which track the task belongs to
        # HOW: Format as "Track: Task" (e.g., "FC: Mediation", "Mod: Drafted")
        label = f"{track_prefix}: {task_label}"
        
        # WHAT: Use track-specific color for both active and completed tasks
        # WHY: Maintain visual consistency - track color should persist in completed state
        # HOW: Always use outcome-specific tone regardless of completion status
        tone = _get_outcome_tone(outcome_type)
        
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
        'modification': 'modification-green',
        'notesale': 'secondary',
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
            'completion_types': ['dil_executed'],
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
            'completion_types': ['mod_failed'],  # Fixed: must match task_type value with mod_ prefix
            'label': 'Modification',
            'tone': 'modification-green',
        },
        'note_sale': {
            'outcome_model': NoteSale,
            'task_model': NoteSaleTask,
            'completion_types': ['sold'],
            'label': 'Note Sale',
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
        # HOW: Use exists() with __in for single optimized query instead of N+1 loop
        has_completed_task = config['task_model'].objects.filter(
            asset_hub_id=hub_id,
            task_type__in=config['completion_types']
        ).exists()
        
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


def get_track_milestones(hub_id: int) -> List[Dict[str, Any]]:
    """
    WHAT: Get current and upcoming tasks for each active track
    WHY: Provide milestone progression view for tasking dashboard
    WHERE: Called by view_am_tasking.py endpoint for milestones card
    HOW: Define task sequences, find current task, determine next task
    
    Args:
        hub_id: The asset hub ID to get milestones for
        
    Returns:
        List of track groups with current and upcoming tasks:
        [
            {
                'track_name': 'Foreclosure',
                'current_task': {'id': 1, 'label': 'Mediation', 'due_date': '2025-10-27', 'tone': 'danger'},
                'upcoming_task': {'id': 2, 'label': 'Sheriff Sale', 'due_date': '2025-11-15', 'tone': 'warning'}
            }
        ]
    """
    # WHAT: Define task sequences for each outcome track
    # WHY: Each track has a specific order of tasks that must be completed
    # HOW: Map track to ordered list of task_type values
    TRACK_SEQUENCES = {
        'fc': {
            'label': 'Foreclosure',
            'tone': 'danger',
            'task_model': FCTask,
            'sequence': [
                'nod_noi',        # NOD/NOI (Notice of Default/Notice of Intent)
                'fc_filing',      # FC Filing
                'mediation',      # Mediation
                'judgement',      # Judgement
                'redemption',     # Redemption period
                'sale_scheduled', # Sale Scheduled
                'sold',           # Sold (completion)
            ]
        },
        'modification': {
            'label': 'Modification',
            'tone': 'modification-green',
            'task_model': ModificationTask,
            'sequence': [
                'mod_drafted',      # Drafted
                'mod_executed',     # Executed
                'mod_rpl',          # Re-Performing
                'mod_failed',       # Failed
            ]
        },
        'short_sale': {
            'label': 'Short Sale',
            'tone': 'warning',
            'task_model': ShortSaleTask,
            'sequence': [
                'list_price_accepted', # List Price Accepted (matches ShortSaleCard)
                'listed',             # Listed
                'under_contract',     # Under Contract
                'sold',              # Sold (completion)
            ]
        },
        'dil': {
            'label': 'Deed-in-Lieu',
            'tone': 'primary',
            'task_model': DILTask,
            'sequence': [
                'pursuing_dil',             # Pursuing DIL
                'owner_contacted',          # Owner/Heirs contacted
                'dil_failed',               # DIL Failed
                'dil_drafted',              # DIL Drafted
                'dil_executed',             # DIL Executed (completion)
            ]
        },
        'reo': {
            'label': 'REO',
            'tone': 'info',
            'task_model': REOtask,
            'sequence': [
                'eviction',       # Eviction
                'trashout',       # Trashout
                'renovation',     # Renovation
                'marketing',      # Marketing
                'under_contract', # Under Contract
                'sold',          # Sold (completion)
            ]
        },
        'note_sale': {
            'label': 'Note Sale',
            'tone': 'secondary',
            'task_model': NoteSaleTask,
            'sequence': [
                'potential_note_sale', # Potential Note Sale
                'out_to_market',       # Out to Market
                'pending_sale',        # Pending Sale
                'sold',               # Sold (completion)
            ]
        }
    }
    
    track_groups = []
    
    # WHAT: Get active tracks for this hub
    # WHY: Only show milestones for tracks that are currently active
    # HOW: Use existing get_active_outcome_tracks function
    active_data = get_active_outcome_tracks(hub_id)
    active_tracks = active_data['active_tracks']
    
    for track_type in active_tracks:
        if track_type not in TRACK_SEQUENCES:
            continue
            
        config = TRACK_SEQUENCES[track_type]
        task_model = config['task_model']
        sequence = config['sequence']
        
        # WHAT: Get all tasks for this track and hub
        # WHY: Need to find current task position in sequence
        # HOW: Query task model, order by creation date
        tasks = task_model.objects.filter(asset_hub_id=hub_id).order_by('created_at')
        
        if not tasks.exists():
            continue
            
        # WHAT: Find current task (latest non-completion task)
        # WHY: Current task is the active step in the workflow
        # HOW: Get latest task that isn't a completion task_type
        current_task = None
        current_index = -1
        
        for task in tasks:
            task_type_lower = task.task_type.lower() if task.task_type else ''
            if task_type_lower in sequence:
                current_index = sequence.index(task_type_lower)
                current_task = task
        
        if not current_task:
            continue
            
        # WHAT: Determine upcoming task (next in sequence)
        # WHY: Show what's coming next in the workflow
        # HOW: Get next task_type in sequence, create placeholder with estimated date
        upcoming_task = None
        if current_index < len(sequence) - 1:
            next_task_type = sequence[current_index + 1]
            
            # WHAT: Calculate estimated due date for upcoming task
            # WHY: Provide timeline expectations
            # HOW: Add standard intervals based on task type
            from datetime import datetime, timedelta
            
            # Standard intervals between tasks (in days)
            TASK_INTERVALS = {
                # Foreclosure intervals
                'fc_filing': 30,        # 30 days after NOD/NOI
                'mediation': 45,        # 45 days after filing
                'judgement': 60,        # 60 days after mediation
                'redemption': 30,       # 30 days redemption period
                'sale_scheduled': 21,   # 21 days to schedule sale
                # Modification intervals
                'mod_executed': 30,         # 30 days to execute
                'mod_rpl': 60,              # 60 days for re-performing status
                'mod_failed': 30,           # 30 days if process fails
                # Short Sale intervals
                'listed': 14,           # 14 days after price acceptance
                'under_contract': 45,   # 45 days to get under contract
                # DIL intervals
                'pursuing_dil': 14,         # 14 days for initial pursuit
                'owner_contacted': 7,       # 7 days after contact
                'dil_failed': 21,           # 21 days if DIL process fails
                'dil_drafted': 14,          # 14 days to draft documents
                'dil_executed': 30,         # 30 days to execute
                # REO intervals
                'trashout': 7,          # 7 days for trashout
                'renovation': 30,       # 30 days for renovation
                'marketing': 14,        # 14 days to start marketing
                'under_contract': 60,   # 60 days to get under contract
            }
            
            interval_days = TASK_INTERVALS.get(next_task_type, 14)  # Default 2 weeks
            estimated_date = datetime.now() + timedelta(days=interval_days)
            
            upcoming_task = {
                'id': f"upcoming_{track_type}_{next_task_type}",
                'label': _format_task_label(next_task_type),
                'due_date': estimated_date.strftime('%Y-%m-%d'),
                'tone': _get_task_urgency_tone(interval_days)
            }
        
        # WHAT: Format current task data
        # WHY: Consistent format for frontend display
        # HOW: Extract task details and format for UI
        current_task_data = {
            'id': current_task.id,
            'label': _format_task_label(current_task.task_type),
            'due_date': current_task.due_date.strftime('%Y-%m-%d') if hasattr(current_task, 'due_date') and current_task.due_date else datetime.now().strftime('%Y-%m-%d'),
            'tone': _get_current_task_tone(current_task)
        }
        
        track_group = {
            'track_name': config['label'],
            'current_task': current_task_data,
            'upcoming_task': upcoming_task
        }
        
        track_groups.append(track_group)
    
    return track_groups


def _format_task_label(task_type: str) -> str:
    """
    WHAT: Convert task_type to human-readable label
    WHY: Display friendly names in UI
    WHERE: Helper for get_track_milestones
    HOW: Map task_type values to display labels
    """
    label_map = {
        # Foreclosure labels
        'nod_noi': 'NOD/NOI Filed',
        'fc_filing': 'FC Filing',
        'mediation': 'Mediation',
        'judgement': 'Judgement',
        'redemption': 'Redemption Period',
        'sale_scheduled': 'Sale Scheduled',
        'sold': 'Property Sold',
        # Modification labels
        'mod_drafted': 'Drafted',
        'mod_executed': 'Executed',
        'mod_rpl': 'Re-Performing',
        'mod_failed': 'Failed',
        # Short Sale labels
        'list_price_accepted': 'List Price Accepted',
        'listed': 'Listed',
        'under_contract': 'Under Contract',
        # DIL labels
        'pursuing_dil': 'Pursuing DIL',
        'owner_contacted': 'Owner/Heirs Contacted',
        'dil_failed': 'DIL Failed',
        'dil_drafted': 'Drafted',
        'dil_executed': 'Executed',
        # REO labels
        'eviction': 'Eviction',
        'trashout': 'Trashout',
        'renovation': 'Renovation',
        'marketing': 'Marketing',
        # Note Sale labels
        'potential_note_sale': 'Potential Note Sale',
        'out_to_market': 'Out to Market',
        'pending_sale': 'Pending Sale',
    }
    return label_map.get(task_type.lower(), task_type.title())


def _get_task_urgency_tone(days_until_due: int) -> str:
    """
    WHAT: Determine urgency tone based on days until due
    WHY: Visual indicators for task priority
    WHERE: Helper for get_track_milestones
    HOW: Map day ranges to tone colors
    """
    if days_until_due <= 3:
        return 'danger'   # Urgent - red
    elif days_until_due <= 7:
        return 'warning'  # Soon - yellow
    elif days_until_due <= 14:
        return 'info'     # Upcoming - blue
    else:
        return 'secondary' # Future - gray


def _get_current_task_tone(task) -> str:
    """
    WHAT: Determine tone for current task based on due date
    WHY: Show urgency of current tasks
    WHERE: Helper for get_track_milestones
    HOW: Calculate days until due, map to tone
    """
    if not hasattr(task, 'due_date') or not task.due_date:
        return 'secondary'
        
    from datetime import datetime
    days_until_due = (task.due_date - datetime.now().date()).days
    return _get_task_urgency_tone(days_until_due)
