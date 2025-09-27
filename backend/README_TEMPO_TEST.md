# NASA TEMPO Data Test Instructions

## Setup
1. **Get NASA EarthData Account** (Free):
   - Go to: https://urs.earthdata.nasa.gov/
   - Click "Register for a profile"  
   - Create your account and verify email

2. **Add Your Credentials**:
   - Edit the `.env` file in the backend directory
   - Replace these lines:
     ```
     EARTHDATA_USERNAME=your_earthdata_username_here
     EARTHDATA_PASSWORD=your_earthdata_password_here
     ```
   - With your actual credentials:
     ```
     EARTHDATA_USERNAME=your_actual_username
     EARTHDATA_PASSWORD=your_actual_password
     ```

## Run Tests

### Simple Test (Recommended first):
```bash
cd backend
python test_tempo_simple.py
```
This will:
- ✅ Test your NASA EarthData login
- ✅ Show available TEMPO satellite collections  
- ✅ Search for recent TEMPO data over New York
- ✅ Verify data access permissions

### Comprehensive Test:
```bash
cd backend  
python test_earthdata_tempo.py
```
This will:
- ✅ Test authentication
- ✅ Search TEMPO collections
- ✅ Find recent satellite data for 5 North American cities
- ✅ Test data download capabilities
- ✅ Show complete TEMPO data structure

## What You'll See

### If Successful ✅:
- Authentication confirmation
- List of available TEMPO products (NO2, O3, HCHO)
- Recent satellite data for North American cities
- Download URLs for actual NASA data files

### If Failed ❌:
- Clear error messages about what went wrong
- Instructions to fix common issues
- Verification that credentials are correct

## TEMPO Data Coverage
- **Geographic**: North America only (US, Canada, Mexico)  
- **Temporal**: Hourly during daylight
- **Pollutants**: NO2, O3, HCHO from space
- **Resolution**: ~2.1 km x 4.4 km pixels

## Next Steps
Once tests pass, the backend will use real NASA TEMPO data instead of mock data for North American cities!