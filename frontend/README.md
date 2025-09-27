# TEMPO Air Quality Frontend

A modern, responsive frontend for the TEMPO Air Quality App built with Next.js 14, React, and TailwindCSS.

## 🚀 Features

- **Real-time Dashboard**: Live air quality monitoring with interactive components
- **Forecast Visualization**: 24-hour AQI predictions with trend analysis
- **Interactive Maps**: Leaflet.js integration for geographic data visualization
- **Health Alerts**: Personalized recommendations and alert system
- **Responsive Design**: Mobile-first approach with TailwindCSS
- **Smooth Animations**: Framer Motion for enhanced user experience

## 🛠️ Tech Stack

- **Next.js 14** with App Router
- **React 18** with TypeScript
- **TailwindCSS** for styling
- **ShadCN/UI** for component library
- **Recharts** for data visualization
- **Leaflet.js** for maps
- **Framer Motion** for animations
- **Axios** for API calls

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Dashboard page
│   ├── forecast/          # Forecast page
│   ├── alerts/            # Alerts page
│   └── about/             # About page
├── components/            # React components
│   ├── ui/               # ShadCN UI components
│   ├── Navbar.tsx        # Navigation component
│   ├── AQICard.tsx       # AQI display card
│   ├── WeatherCard.tsx   # Weather display card
│   ├── ForecastChart.tsx # Forecast visualization
│   ├── MapView.tsx       # Interactive map
│   └── AlertBox.tsx      # Alert notifications
├── lib/                  # Utilities and API client
│   ├── utils.ts          # Utility functions
│   └── api.ts            # API client
├── styles/               # Additional styles
└── public/               # Static assets
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 🎨 Components

### AQICard
Displays current air quality information with:
- AQI value and category
- Pollutant breakdown (PM2.5, PM10, NO₂, O₃)
- Color-coded health indicators
- Data source information

### WeatherCard
Shows current weather conditions:
- Temperature and conditions
- Humidity and wind speed
- Atmospheric pressure
- Visibility

### ForecastChart
Interactive forecast visualization:
- 24-hour AQI predictions
- Trend analysis
- Custom tooltips
- Responsive design

### MapView
Geographic data visualization:
- Interactive Leaflet map
- AQI markers with popups
- Color-coded legend
- Real-time updates

### AlertBox
Notification system:
- Severity-based styling
- Health recommendations
- Dismissible alerts
- Smooth animations

## 🎯 Pages

### Dashboard (`/`)
- Main air quality overview
- Current conditions
- Weather integration
- Interactive map
- Health recommendations

### Forecast (`/forecast`)
- 24-hour AQI predictions
- Pollutant selection
- Trend analysis
- Model information

### Alerts (`/alerts`)
- Real-time notifications
- Alert management
- Health recommendations
- Customizable preferences

### About (`/about`)
- Project information
- Technology stack
- Data sources
- AQI scale explanation

## 🎨 Styling

The app uses TailwindCSS with custom configurations:

- **Color System**: AQI-specific color palette
- **Typography**: Inter font family
- **Spacing**: Consistent spacing scale
- **Animations**: Framer Motion integration
- **Responsive**: Mobile-first design

## 🔧 API Integration

The frontend communicates with the backend through:

- **RESTful API**: FastAPI backend
- **Real-time Updates**: Polling mechanism
- **Error Handling**: Graceful fallbacks
- **Loading States**: User feedback

## 📱 Responsive Design

- **Mobile**: Optimized for mobile devices
- **Tablet**: Enhanced tablet experience
- **Desktop**: Full-featured desktop interface
- **Accessibility**: WCAG compliant

## 🚀 Deployment

### Vercel (Recommended)

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

### Manual Build

```bash
npm run build
npm start
```

## 🧪 Testing

```bash
# Run tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 📦 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

## 🔧 Configuration

### TailwindCSS
Custom configuration in `tailwind.config.js`:
- AQI color palette
- Custom animations
- Responsive breakpoints

### Next.js
Configuration in `next.config.js`:
- Image domains
- Environment variables
- API rewrites

## 🎯 Performance

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Webpack bundle analyzer
- **Lazy Loading**: Component-level lazy loading

## 🐛 Troubleshooting

### Common Issues

1. **API Connection**: Check `NEXT_PUBLIC_API_URL`
2. **Build Errors**: Clear `.next` folder
3. **Dependencies**: Delete `node_modules` and reinstall
4. **TypeScript**: Check type definitions

### Debug Mode

```bash
DEBUG=* npm run dev
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Built with ❤️ for the NASA Space Challenge**
