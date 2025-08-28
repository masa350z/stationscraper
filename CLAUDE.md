# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Philosophy

This is a development/prototype project where **simplicity, maintainability, and readability are the highest priorities**. Follow the YAGNI (You Aren't Gonna Need It) principle:

- Keep code simple and straightforward
- Avoid unnecessary features or complex abstractions
- Don't implement sophisticated error handling unless specifically needed
- Prioritize clarity over performance optimizations
- Use basic, well-understood patterns and libraries

**コードの説明やコメントは日本語で記述してください。**

## Development Commands

### Main Data Processing Pipeline
```bash
# Run the complete data pipeline (scraping, API calls, merging)
cd src
python main.py

# Manual dependency installation (python-dotenv not in requirements.txt)
pip install python-dotenv
```

### Web Application
```bash
# Run the web visualization app with Docker
cd mapapp
docker-compose up

# Access the web app at http://localhost:5000
```

## Architecture Overview

This is a dual-component system for analyzing Tokyo area station data:

### 1. Data Pipeline (`src/`)
- **Entry Point**: `src/main.py` orchestrates the entire pipeline
- **Scrapers**: `src/scrapers/` - Web scraping for station lists (TravelTowns) and rent prices (SUUMO)
- **API Integrations**: `src/apis/` - Ekispert API for route times, Google Maps API for geocoding
- **Data Processing**: `src/pipeline/` - Merging, filtering, and analysis of collected data
- **Configuration**: `src/config.py` - Environment variables and project constants

### 2. Web Visualization (`mapapp/`)
- **Backend**: Flask server (`server.py`) with PostgreSQL database
- **Frontend**: Leaflet.js-based map interface
- **Database**: PostgreSQL with station data (coordinates, prices, commute times)
- **Deployment**: Docker Compose setup with auto-initialization

## Data Flow

1. **Collection**: TravelTowns scraper → station master data
2. **Enrichment**: SUUMO scraper → rent prices by station
3. **Analysis**: Ekispert API → commute times to target stations
4. **Geocoding**: Google Maps API → coordinates for each station
5. **Storage**: CSV files in `data/output/` with different views (merged, price_info, route_info)
6. **Visualization**: Web app loads processed data into PostgreSQL for interactive filtering

## Key Configuration

### Environment Variables Required
```
EKISPERT_KEY=your_ekispert_api_key
GOOGLE_MAPS_KEY=your_google_maps_api_key
```

### Critical Missing Constants
The `src/config.py` file is missing these constants that `src/pipeline/analysis.py` expects:
- `MAX_TRANS_DEFAULT`
- `MAX_TIME_DEFAULT` 
- `MAX_PRICE_DEFAULT`

### Target Stations
Currently configured to analyze commute times to stations defined in `WALK_MINUTES` dict in `src/config.py`.

## Data Structure

### CSV Output Files
- `data/station_address.csv`: Station master (line, station)
- `data/station_price/station_price_{room_type}.csv`: Rent prices by station
- `data/output/price_info/price_by_station_{room_type}.csv`: Merged station + price data
- `data/output/route_info/route_info_{target_station}.csv`: Commute time analysis
- `data/output/merged/merged_with_coordinates.csv`: Final dataset with geocoding

### Database Schema (Web App)
```sql
CREATE TABLE stations (
    id SERIAL PRIMARY KEY,
    line TEXT,
    station TEXT,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    price DOUBLE PRECISION,
    commute_time INT
);
```

## Important Notes

- The main pipeline skips API calls if output files already exist
- `src/apis/analysis.py` and `src/apis/visualization.py` are empty placeholder files
- Web app expects a `stations.csv` file in `mapapp/` directory for database initialization
- All scraping includes rate limiting (`SCRAPING_SLEEP_SEC`) and retry logic