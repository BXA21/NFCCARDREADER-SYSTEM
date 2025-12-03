# NFC Attendance System - Frontend

Modern React frontend for the NFC Attendance System built with TypeScript, Vite, and Tailwind CSS.

## Features

- 🔐 JWT-based authentication with auto-refresh
- 📱 Responsive, mobile-first design
- 🎨 Beautiful UI with Tailwind CSS
- 📊 Real-time attendance dashboard
- 👥 Employee management (Phase 7)
- 📈 Reports and analytics (Phase 9)
- ♿ Accessible components

## Tech Stack

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Form Validation**: React Hook Form + Zod
- **Icons**: Lucide React
- **Charts**: Recharts

## Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

## Installation

1. **Install dependencies**

```bash
cd frontend
npm install
```

2. **Configure environment**

```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (default points to localhost:8000)
```

3. **Start development server**

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

## Available Scripts

```bash
# Development
npm run dev          # Start dev server with hot reload

# Production
npm run build        # Build for production
npm run preview      # Preview production build locally

# Code Quality
npm run lint         # Run ESLint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable components
│   │   ├── layout/        # Layout components (Sidebar, Header)
│   │   └── ProtectedRoute.tsx
│   ├── contexts/          # React contexts
│   │   └── AuthContext.tsx
│   ├── pages/             # Page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── EmployeesPage.tsx
│   │   └── AttendancePage.tsx
│   ├── lib/               # Utilities and configuration
│   │   ├── axios.ts       # Axios instance with interceptors
│   │   └── utils.ts       # Helper functions
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── config/            # Configuration
│   │   └── api.ts         # API endpoints
│   ├── App.tsx            # Main App component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── index.html             # HTML template
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite config
├── tailwind.config.js     # Tailwind config
└── README.md              # This file
```

## Authentication

The app uses JWT-based authentication:

1. **Login**: User enters credentials on `/login`
2. **Token Storage**: Access and refresh tokens stored in localStorage
3. **Auto-Refresh**: Axios interceptor automatically refreshes expired tokens
4. **Protected Routes**: All dashboard routes require authentication
5. **Logout**: Clears tokens and redirects to login

### Default Credentials

```
Username: admin
Password: Admin@123
```

## API Integration

### Axios Configuration

The app uses a custom Axios instance (`src/lib/axios.ts`) with:
- Base URL configuration
- Authorization header injection
- Automatic token refresh on 401 errors
- Request/response interceptors

### Example API Call

```typescript
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'

const response = await axiosInstance.get(API_ENDPOINTS.EMPLOYEES)
const employees = response.data
```

### React Query Integration

All API calls use React Query for:
- Automatic caching
- Background refetching
- Loading/error states
- Optimistic updates

```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['employees'],
  queryFn: async () => {
    const response = await axiosInstance.get(API_ENDPOINTS.EMPLOYEES)
    return response.data
  }
})
```

## Routing

The app uses React Router v6 with nested routes:

```
/login                  → Login page (public)
/                       → Dashboard layout (protected)
  ├─ /dashboard         → Dashboard page
  ├─ /employees         → Employees management
  ├─ /attendance        → Attendance records
  ├─ /corrections       → Correction requests
  ├─ /shifts            → Shift management
  ├─ /reports           → Reports
  └─ /export            → Export data
```

## Styling

### Tailwind CSS

The app uses Tailwind CSS for styling with custom configuration:

**Colors:**
- Primary: Blue (#2563eb)
- Success: Green (#16a34a)
- Warning: Orange (#d97706)
- Danger: Red (#dc2626)

**Custom Components:**
```css
.btn          /* Base button styles */
.btn-primary  /* Primary button */
.btn-danger   /* Danger button */
.input        /* Form input */
.card         /* Card container */
.badge        /* Status badge */
```

### Example Usage

```tsx
<button className="btn btn-primary">
  Click Me
</button>

<input className="input" placeholder="Enter text" />

<div className="card">
  <h3>Card Title</h3>
  <p>Card content</p>
</div>

<span className="badge badge-success">Active</span>
```

## Building for Production

```bash
# Build the app
npm run build

# Preview the build
npm run preview
```

The build output will be in the `dist/` directory.

### Deployment

The built app can be deployed to any static hosting service:

- **Vercel**: `vercel deploy`
- **Netlify**: Drag and drop `dist/` folder
- **AWS S3**: Upload `dist/` folder
- **Nginx**: Serve `dist/` folder

Make sure to configure the API base URL for production in `.env`:

```bash
VITE_API_BASE_URL=https://api.yourcompany.com/api/v1
```

## Development Phases

### ✅ Phase 6: Foundation (Current)
- [x] React + TypeScript setup
- [x] Authentication flow
- [x] Dashboard layout
- [x] Basic pages
- [x] API integration

### 🔄 Phase 7: Employee Management (Next)
- [ ] Employee list with search/filter
- [ ] Create/edit employee form
- [ ] Card issuance modal
- [ ] Employee detail view

### 🔄 Phase 8: Corrections
- [ ] Submit correction request
- [ ] Approval workflow for supervisors

### 🔄 Phase 9: Reports & Export
- [ ] Attendance reports
- [ ] CSV export
- [ ] Charts and analytics

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Follow the existing code style
2. Use TypeScript strict mode
3. Write meaningful component names
4. Add comments for complex logic
5. Test on multiple screen sizes

## Troubleshooting

### API Connection Error

**Problem**: Cannot connect to backend API

**Solution**:
- Check backend is running on http://localhost:8000
- Verify CORS is configured in backend
- Check `.env` file has correct API URL

### Build Fails

**Problem**: `npm run build` fails

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear vite cache
rm -rf node_modules/.vite
```

### Login Not Working

**Problem**: Login fails with 401 error

**Solution**:
- Verify backend is running
- Check default credentials: admin / Admin@123
- Check browser console for errors
- Verify API endpoint is correct

## Support

For issues or questions, refer to:
- Backend API documentation: http://localhost:8000/docs
- Main project README
- System administrator

## License

Proprietary - Internal use only



