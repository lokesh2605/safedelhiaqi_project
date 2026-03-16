🌫️ Safe Delhi AQI

A Real-Time Air Quality Monitoring Web Application that visualizes pollution levels across Delhi using an interactive map and live AQI data.

This project helps users understand the air quality situation in Delhi by displaying monitoring stations, pollution intensity, and detailed air metrics.

🚀 Live Demo

(After deployment you can add the link)

https://safedelhiaqi.vercel.app
📸 Project Preview

Add screenshots here later:

/screenshots/map-view.png
/screenshots/heatmap-view.png

Example:

Map View	Heatmap View

	
✨ Features

✅ Real-time AQI monitoring
✅ Interactive pollution map
✅ Heatmap visualization of pollution intensity
✅ Search for AQI monitoring stations
✅ Station-level pollution details
✅ Weather and pollutant metrics
✅ Fast API using edge functions
✅ Clean and responsive UI

🧰 Tech Stack
Frontend

React

TypeScript

Vite

Leaflet Maps

Backend

Edge functions from Supabase

Data Source

Air quality data from World Air Quality Index Project

Deployment

GitHub

Vercel

📂 Project Structure
safedelhiaqi_project
│
├── src
│   ├── components
│   ├── hooks
│   ├── pages
│   ├── integrations
│   │   └── supabase
│   └── utils
│
├── supabase
│   └── functions
│       └── fetch-aqi
│
├── public
├── package.json
├── vite.config.ts
└── README.md
⚙️ Installation
1 Clone the repository
git clone https://github.com/lokesh2605/safedelhiaqi_project.git
2 Go to project folder
cd safedelhiaqi_project
3 Install dependencies
npm install
4 Start development server
npm run dev

App will run at:

http://localhost:5173
🔑 Environment Variables

Create .env file:

VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_PUBLISHABLE_KEY=your_supabase_key

Supabase secret:

WAQI_API_TOKEN=your_waqi_api_token
📊 AQI Scale
AQI	Category	Health Impact
0-50	Good	Air quality is satisfactory
51-100	Moderate	Acceptable
101-150	Unhealthy for Sensitive Groups	Possible health risk
151-200	Unhealthy	Everyone may feel effects
201-300	Very Unhealthy	Health alert
301+	Hazardous	Emergency conditions
🔮 Future Improvements

🚀 Historical AQI analytics
🚀 Pollution prediction models
🚀 Mobile app version
🚀 User alerts for high AQI
🚀 Multi-city comparison

👨‍💻 Author

Lokesh Gadda

GitHub
https://github.com/lokesh2605

📜 License

MIT License
