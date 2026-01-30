# GlobalStandardizations

**Single source of truth for all UI standards across the application.**

## Structure

```
GlobalStandardizations/
├── badges/
│   ├── badgeConfig.ts     # Badge sizes & dimensions
│   ├── badgeColors.ts     # Badge color tones & mappings
│   ├── badgeHelpers.ts    # Helper functions & enum maps
│   └── index.ts           # Public API
├── colors/
│   ├── colorPalette.ts    # Global color palette
│   └── index.ts           # Public API
└── ui/
    ├── uiTokens.ts        # UI design tokens (spacing, typography, shadows, etc.)
    └── index.ts           # Public API

Related Components (in components/ui/):
├── UiBadge.vue            # Standalone badge component
└── BadgeCell.vue          # AG Grid cell renderer for badges
```

## Usage

### Import badges:
```typescript
import { resolveBadgeTokens, BadgeToneKey, propertyTypeEnumMap } from '@/GlobalStandardizations/badges'
```

### Import colors:
```typescript
import { STATUS_COLORS, getTagColor } from '@/GlobalStandardizations/colors'
```

### Import UI tokens:
```typescript
import { UI_BACKGROUNDS, UI_SPACING, UI_TYPOGRAPHY, UI_SHADOWS, AM_TASKING_TOKENS } from '@/GlobalStandardizations/ui'
```

### Simple badge:
```vue
<UiBadge tone="success" size="md" label="Active" />
```

### AG Grid badge column:
```typescript
import BadgeCell from '@/components/ui/BadgeCell.vue'
import { propertyTypeEnumMap } from '@/GlobalStandardizations/badges'

{
  field: 'propertyType',
  cellRenderer: BadgeCell,
  cellRendererParams: {
    mode: 'enum',
    enumMap: propertyTypeEnumMap,
    size: 'sm'
  }
}
```

## To Change Settings

### Badge Settings
- **Badge sizes/dimensions**: Edit `badges/badgeConfig.ts` → `BADGE_DIMENSIONS`
- **Badge colors**: Edit `badges/badgeColors.ts` → `BADGE_TONE_CONFIG`
- **Category colors**: Edit `badges/badgeColors.ts` → `PROPERTY_TYPE_COLORS`, `LOAN_PERFORMANCE_COLORS`, etc.

### Color Settings
- **Global colors**: Edit `colors/colorPalette.ts`

### UI Token Settings
- **Backgrounds**: Edit `ui/uiTokens.ts` → `UI_BACKGROUNDS`
- **Spacing**: Edit `ui/uiTokens.ts` → `UI_SPACING`
- **Typography**: Edit `ui/uiTokens.ts` → `UI_TYPOGRAPHY`
- **Shadows**: Edit `ui/uiTokens.ts` → `UI_SHADOWS`
- **Border radius**: Edit `ui/uiTokens.ts` → `UI_RADIUS`
- **Card padding**: Edit `ui/uiTokens.ts` → `UI_CARD_PADDING`
- **AM-specific tokens**: Edit `ui/uiTokens.ts` → `AM_TASKING_TOKENS`

All changes cascade automatically to all components using these standardizations.
