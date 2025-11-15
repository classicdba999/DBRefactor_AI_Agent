# DBRefactor AI - Next.js UI

Modern, responsive web interface for the DBRefactor AI Agent framework.

## Features

- **Dashboard**: Real-time overview of agents, workflows, and migrations
- **Agent Management**: View and control all registered agents
- **Workflow Builder**: Create and monitor complex migration workflows
- **Database Discovery**: Interactive schema discovery and analysis
- **Dependency Visualization**: Visual dependency graph with ReactFlow
- **Real-time Updates**: WebSocket support for live status updates
- **Dark Mode**: Full dark mode support
- **Responsive Design**: Works seamlessly on desktop and mobile

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **Components**: Radix UI primitives
- **Charts**: Recharts
- **Graph Visualization**: ReactFlow
- **Icons**: Lucide React
- **Type Safety**: TypeScript

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- FastAPI backend running on `http://localhost:8000`

### Installation

1. **Install dependencies**:
   ```bash
   cd ui
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
# Build the application
npm run build

# Start the production server
npm run start
```

## Project Structure

```
ui/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── agents/            # Agent management
│   ├── workflows/         # Workflow management
│   ├── discovery/         # Schema discovery
│   ├── dependencies/      # Dependency visualization
│   └── layout.tsx         # Root layout
├── components/            # Reusable components
│   ├── ui/               # Base UI components
│   ├── sidebar.tsx       # Navigation sidebar
│   ├── stats-card.tsx    # Statistics card
│   └── ...
├── lib/                  # Utility functions
│   └── utils.ts         # Helper utilities
└── public/              # Static assets
```

## API Integration

The UI communicates with the FastAPI backend through:

- **REST API**: `/api/v1/*` endpoints
- **WebSocket**: `/ws` for real-time updates

### API Proxy

Next.js rewrites API requests to the backend:

```javascript
// next.config.js
{
  source: '/api/:path*',
  destination: 'http://localhost:8000/api/:path*',
}
```

## Available Pages

### Dashboard (`/`)
- Overview statistics
- Agent performance charts
- Recent activity
- Quick actions

### Agents (`/agents`)
- List all registered agents
- View agent details and capabilities
- Enable/disable agents
- Monitor agent statistics

### Workflows (`/workflows`)
- Create new workflows
- View workflow status
- Execute workflows
- Monitor progress

### Discovery (`/discovery`)
- Discover database schemas
- View object counts
- Categorize by complexity
- Export results

### Dependencies (`/dependencies`)
- Interactive dependency graph
- Migration order analysis
- Circular dependency detection
- Visual object relationships

## Configuration

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Backend URL

Update `next.config.js` if your backend runs on a different port:

```javascript
{
  source: '/api/:path*',
  destination: 'http://your-backend-url:port/api/:path*',
}
```

## Development

### Adding New Pages

1. Create a new directory in `app/`:
   ```bash
   mkdir app/your-page
   ```

2. Add `page.tsx`:
   ```typescript
   export default function YourPage() {
     return <div>Your content</div>
   }
   ```

3. Add navigation link in `components/sidebar.tsx`

### Creating Components

Use the UI component library in `components/ui/`:

```typescript
import { Card, CardHeader, CardTitle } from "@/components/ui/card"

export function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>My Card</CardTitle>
      </CardHeader>
    </Card>
  )
}
```

### Styling

Use Tailwind CSS utility classes:

```typescript
<div className="p-4 bg-blue-600 text-white rounded-lg">
  Styled content
</div>
```

## Customization

### Theme Colors

Edit `tailwind.config.ts` to customize colors:

```typescript
theme: {
  extend: {
    colors: {
      primary: "hsl(var(--primary))",
      // Add your colors
    },
  },
}
```

### Global Styles

Modify `app/globals.css` for theme variables:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  /* ... */
}
```

## Deployment

### Vercel (Recommended)

```bash
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Static Export

For static hosting:

```bash
npm run build
# Deploy the 'out' directory
```

## Troubleshooting

### API Connection Issues

1. Ensure FastAPI backend is running
2. Check `next.config.js` proxy settings
3. Verify CORS is enabled in FastAPI

### Build Errors

```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

### WebSocket Connection

Make sure WebSocket endpoint is accessible:
```javascript
ws://localhost:8000/ws
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Part of the DBRefactor AI Agent project.

## Support

For issues and questions, please open an issue on GitHub.
