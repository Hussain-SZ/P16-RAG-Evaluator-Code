# Save & View Evaluation Reports Feature

## Overview
This feature allows users to save their RAG evaluation results for later viewing, creating a persistent history of evaluations.

## Features Added

### Backend
1. **New Database Model**: `SavedEvaluationReport` - stores complete evaluation data
2. **New Repository**: `EvaluationReportRepository` - handles database operations
3. **New API Endpoints**:
   - `POST /api/v1/reports/save` - Save an evaluation report
   - `GET /api/v1/reports/my-reports` - List all user's reports
   - `GET /api/v1/reports/report/{id}` - Get full report details
   - `PATCH /api/v1/reports/report/{id}` - Update report metadata
   - `DELETE /api/v1/reports/report/{id}` - Delete a report
   - `GET /api/v1/reports/stats` - Get report statistics

### Frontend
1. **New Page**: `MyReports.tsx` - View and manage saved reports
2. **Updated Home Page**: Added "Save Report" button and "My Reports" navigation
3. **New Styles**: `MyReports.css` - Responsive design for reports page

## How to Use

### 1. Run an Evaluation
- Go to the Dashboard (`/home`)
- Enter query, context, and LLM answer
- Click "Evaluate RAG Response"
- View the results

### 2. Save the Report
- After evaluation completes, click **"💾 Save Report"** button
- Enter a report name (e.g., "ML Query Test - Nov 2024")
- Optionally add tags (comma-separated, e.g., "machine-learning, test")
- Optionally add notes
- Click OK to save

### 3. View Saved Reports
- Click **"📚 My Reports"** button in the top navigation
- Browse your saved reports in the left panel
- Click any report to view full details in the right panel

### 4. Manage Reports
- **View Details**: Click on a report to see complete evaluation
- **Delete**: Click the "🗑️ Delete" button in the report details
- **Filter**: Use tags to organize and find reports

## API Documentation

### Save Report
```http
POST /api/v1/reports/save
Authorization: Bearer <token>
Content-Type: application/json

{
  "report_name": "My Evaluation",
  "query": "What is ML?",
  "context": "...",
  "llm_output": "...",
  "aggregate_metrics": {...},
  "sentence_evaluations": [...],
  "tags": ["ml", "test"],
  "notes": "Good results"
}
```

### List Reports
```http
GET /api/v1/reports/my-reports?limit=50&skip=0&tags=ml,test
Authorization: Bearer <token>
```

### Get Report Details
```http
GET /api/v1/reports/report/{report_id}
Authorization: Bearer <token>
```

### Delete Report
```http
DELETE /api/v1/reports/report/{report_id}
Authorization: Bearer <token>
```

## Database Schema

```python
{
  "_id": ObjectId,
  "user_id": str,
  "report_name": str,
  "query": str,
  "context": str,
  "llm_output": str,
  "aggregate_metrics": {
    "faithfulness_rate": float,
    "hallucination_rate": float,
    "inferred_rate": float,
    "extrapolated_rate": float,
    "total_sentences": int,
    ...
  },
  "sentence_evaluations": [
    {
      "sentence_number": int,
      "sentence_text": str,
      "classification": str,
      "justification": str,
      "supporting_chunk": str
    }
  ],
  "tags": [str],
  "notes": str,
  "created_at": datetime
}
```

## Security

- All endpoints require authentication
- Users can only access their own reports
- Reports are associated with user_id
- Ownership is verified before view/update/delete operations

## UI Features

### Reports List
- Shows report name, date, and key metrics
- Color-coded metric badges (faithfulness, hallucination)
- Tag display for easy categorization
- Click to view full details

### Report Details
- Complete evaluation results
- Original inputs (query, context, answer)
- Aggregate metrics with color coding
- Sentence-by-sentence analysis
- Collapsible sections for better organization

## Testing

### Backend
```bash
# Test save report
curl -X POST http://localhost:8000/api/v1/reports/save \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"report_name": "Test", ...}'

# Test list reports
curl http://localhost:8000/api/v1/reports/my-reports \
  -H "Authorization: Bearer <token>"
```

### Frontend
1. Login to the application
2. Run an evaluation
3. Save the report with a name
4. Navigate to "My Reports"
5. Verify report appears in list
6. Click report to view details
7. Test delete functionality

## Future Enhancements

Possible additions:
- Export reports to PDF/CSV
- Share reports with other users
- Compare multiple reports side-by-side
- Advanced filtering and search
- Report analytics and trends
- Batch operations on reports
- Report templates

## Troubleshooting

### "Database not available" error
- Ensure MongoDB is running
- Check DATABASE connection in .env
- Verify db_manager is connected

### "Unauthorized" error
- Ensure user is logged in
- Check token is valid and not expired
- Verify Authorization header is included

### Reports not saving
- Check browser console for errors
- Verify all required fields are present
- Check backend logs for detailed errors

## Files Modified/Created

### Backend
- `backend/app/models/evaluation_report.py` (NEW)
- `backend/app/schemas/evaluation_reports.py` (NEW)
- `backend/app/database/evaluation_report_repository.py` (NEW)
- `backend/app/routes/evaluation_reports.py` (NEW)
- `backend/app/api/api.py` (MODIFIED - added reports router)

### Frontend
- `frontend/src/pages/MyReports.tsx` (NEW)
- `frontend/src/styling/MyReports.css` (NEW)
- `frontend/src/pages/Home.tsx` (MODIFIED - added save functionality)
- `frontend/src/styling/Home.css` (MODIFIED - added save button styles)
- `frontend/src/App.tsx` (MODIFIED - added /my-reports route)
