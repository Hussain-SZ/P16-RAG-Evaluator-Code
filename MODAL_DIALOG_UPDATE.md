# Save Report Modal Dialog Update

## Summary
Replaced three separate `prompt()` dialogs with a single, user-friendly modal dialog for saving evaluation reports.

## Changes Made

### 1. Frontend - Home.tsx
**File**: `frontend/src/pages/Home.tsx`

#### Added State Variables
```typescript
const [showSaveModal, setShowSaveModal] = useState(false);
const [reportFormData, setReportFormData] = useState({
  name: "",
  tags: "",
  notes: ""
});
```

#### Modified Functions

**Before** - `handleSaveReport()`:
```typescript
const reportName = prompt("Enter a name for this report:");
const tags = prompt("Enter tags (comma-separated, optional):");
const notes = prompt("Add any notes (optional):");
```

**After** - `handleSaveReport()`:
```typescript
setReportFormData({ name: "", tags: "", notes: "" });
setShowSaveModal(true);
```

#### New Function
**`handleSubmitSaveReport()`**: 
- Validates that report name is provided (required field)
- Validates that evaluationResult exists
- Processes form data and calls the API
- Closes modal and shows loading state

#### New Modal Component
Added a complete modal dialog with:
- **Report Name** field (required) - with red asterisk indicator
- **Tags** field (optional) - with helper text "Comma-separated values"
- **Notes** field (optional) - multi-line textarea
- Cancel and Save buttons
- Form validation (Save button disabled if name is empty)
- Click outside to close functionality
- Smooth animations (fade-in overlay, slide-up content)

### 2. Frontend - Home.css
**File**: `frontend/src/styling/Home.css`

#### Added Styles (~200 lines)

**Modal Structure**:
- `.modal-overlay` - Full-screen semi-transparent backdrop with fade-in animation
- `.modal-content` - White card with rounded corners, shadow, and slide-up animation
- `.modal-header` - Title and close button layout
- `.modal-close` - X button with hover effects

**Form Styling**:
- `.modal-form` - Form container with proper spacing
- `.form-group` - Each input group with label and field
- `.form-group label` - Styled labels with required/optional indicators
- `.form-group input[type="text"]` - Text inputs with focus states
- `.form-group textarea` - Multi-line notes field
- `.form-hint` - Helper text below inputs

**Button Styles**:
- `.modal-actions` - Button container (right-aligned)
- `.btn-cancel` - Gray cancel button
- `.btn-save` - Purple gradient save button with disabled state

**Responsive Design**:
- Mobile-friendly adjustments for smaller screens
- Full-width buttons on mobile
- Reduced padding and spacing

## User Experience Improvements

### Before
❌ Three sequential browser prompts
❌ No visual feedback
❌ No field validation hints
❌ Poor mobile experience
❌ Text-only, no styling

### After
✅ Single elegant modal dialog
✅ All fields visible at once
✅ Clear required/optional indicators
✅ Helper text for tags format
✅ Responsive design for all screen sizes
✅ Visual feedback (animations, focus states)
✅ Better validation (disabled save button)
✅ Click outside to cancel
✅ Professional appearance matching app design

## Validation Rules
- **Report Name**: Required - Save button disabled if empty
- **Tags**: Optional - Automatically splits by comma
- **Notes**: Optional - Multi-line text area

## Technical Details

### Modal Implementation
- Uses React state for visibility control
- Controlled form inputs
- Event propagation handling (click outside to close)
- Form submission with preventDefault
- Proper TypeScript null checks

### Animations
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

### Color Scheme
- Primary gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Required indicator: `#e74c3c` (red)
- Optional text: `#999` (gray)
- Focus state: `rgba(102, 126, 234, 0.1)` (light blue)

## Testing Checklist
- [ ] Modal opens when "Save Report" button is clicked
- [ ] Report name field is auto-focused
- [ ] Save button is disabled when name is empty
- [ ] Save button becomes enabled when name is typed
- [ ] Tags field accepts comma-separated values
- [ ] Notes field accepts multi-line text
- [ ] Cancel button closes modal without saving
- [ ] X button closes modal without saving
- [ ] Clicking overlay closes modal without saving
- [ ] Form submission saves report with all three fields
- [ ] Success message displays after saving
- [ ] Error messages display if API fails
- [ ] Modal works on mobile devices
- [ ] Modal works on tablets
- [ ] Modal works on desktop

## Files Modified
1. `frontend/src/pages/Home.tsx` - Added modal state, component, and submit handler
2. `frontend/src/styling/Home.css` - Added complete modal styling with animations

## API Endpoint Used
```
POST /api/v1/reports/save
```

**Request Body**:
```json
{
  "report_name": "string (required)",
  "query": "string",
  "context": "string",
  "llm_output": "string",
  "aggregate_metrics": { ... },
  "sentence_evaluations": [ ... ],
  "tags": ["string"],
  "notes": "string"
}
```

## Result
The save report feature now provides a modern, intuitive user experience with all three input fields (name, tags, notes) collected in a single, beautifully styled modal dialog. Only the report name is mandatory, with clear visual indicators for required vs optional fields.
