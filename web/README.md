# myProgress Web Application

A React Vite-based web application for the myProgress degree audit system.

## Features

### Transcript Builder
- Build your transcript by adding programs and courses
- Load a test transcript with one click
- Add/remove programs and courses dynamically
- Form validation and error handling

### Report Viewer
- View AI-generated audit reports in a hierarchical structure
- **Fully customizable** - edit any aspect of the report:
  - Edit block names, status, credits, and types
  - Add/remove/edit notes
  - Add/remove/edit courses
  - Add/remove nested blocks
  - Expand/collapse sections
- Export reports as JSON
- Import reports from JSON files
- Visual indicators for different block types and statuses

## Getting Started

### Prerequisites
- Node.js 16+ and npm/yarn
- The FastAPI backend running on `http://localhost:8000`

### Installation

```bash
cd web
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

The production build will be in the `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
web/
├── src/
│   ├── components/
│   │   ├── TranscriptBuilder.jsx    # Transcript input form
│   │   ├── TranscriptBuilder.css
│   │   ├── ReportViewer.jsx         # Customizable report viewer
│   │   └── ReportViewer.css
│   ├── App.jsx                       # Main app component
│   ├── App.css
│   ├── main.jsx                      # Entry point
│   └── index.css                     # Global styles
├── index.html
├── package.json
├── vite.config.js                    # Vite configuration with proxy
└── README.md
```

## API Integration

The app communicates with the FastAPI backend at `http://localhost:8000`:

- `POST /audit` - Generate audit report
- `GET /health` - Health check

The Vite dev server is configured to proxy API requests to the backend.

## Customization Features

The Report Viewer is designed to be extremely flexible since AI-generated reports may need tweaking:

1. **Inline Editing**: Click on any block name to edit it
2. **Field Editing**: All fields (status, credits, block type) are editable
3. **Dynamic Content**: Add/remove notes, courses, and nested blocks
4. **Export/Import**: Save your customized reports and load them back
5. **Visual Hierarchy**: Color-coded blocks by type and level

## Notes

- The test transcript includes courses for Computer Science and Economics programs
- Failed courses (grade "F") automatically have credits set to 0
- Course codes must be numeric (validation enforced)
- The report structure is recursive and supports unlimited nesting

