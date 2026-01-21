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
└── colors/
    ├── colorPalette.ts    # Global color palette
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

## To Change Badge Settings

- **Badge sizes/dimensions**: Edit `badges/badgeConfig.ts` → `BADGE_DIMENSIONS`
- **Badge colors**: Edit `badges/badgeColors.ts` → `BADGE_TONE_CONFIG`
- **Category colors**: Edit `badges/badgeColors.ts` → `PROPERTY_TYPE_COLORS`, `LOAN_PERFORMANCE_COLORS`, etc.
- **Global colors**: Edit `colors/colorPalette.ts`

All changes cascade automatically to all components using the badge system.
