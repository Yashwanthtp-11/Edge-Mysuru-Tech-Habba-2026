import { useEffect, useState } from "react";
import ImageUpload from "./components/ImageUpload.jsx";

const modules = [
  {
    title: "Weather",
    detail: "Forecast-based guidance is coming soon.",
    accent: "sun",
  },
  {
    title: "Government Schemes",
    detail: "Official scheme information will appear here.",
    accent: "leaf",
  },
  {
    title: "AI Assistant",
    detail: "Ask farming questions in your preferred language.",
    accent: "chat",
  },
  {
    title: "Voice Assistant",
    detail: "Voice support is being prepared for the next phase.",
    accent: "voice",
  },
];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const DEMO_LOCATION = { lat: 12.2958, lon: 76.6394 };

function WeatherCard() {
  const [weather, setWeather] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    fetch(
      `${API_BASE_URL}/api/weather/current?lat=${DEMO_LOCATION.lat}&lon=${DEMO_LOCATION.lon}`,
      { signal: controller.signal },
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error("Weather request failed");
        }
        return response.json();
      })
      .then(setWeather)
      .catch((requestError) => {
        if (requestError.name !== "AbortError") {
          setError(true);
        }
      });

    return () => controller.abort();
  }, []);

  if (error) {
    return (
      <article className="module-card weather-card weather-error">
        <div className="module-icon" aria-hidden="true">*</div>
        <div>
          <h2>Weather</h2>
          <p>Unable to fetch weather. Please try again.</p>
        </div>
      </article>
    );
  }

  if (!weather) {
    return (
      <article className="module-card weather-card">
        <div className="module-icon" aria-hidden="true">*</div>
        <div>
          <h2>Weather</h2>
          <p>Fetching weather...</p>
        </div>
      </article>
    );
  }

  const advisory = weather.agricultural_advisory?.messages?.[0];
  const location = weather.location?.name || "Mysuru, Karnataka";

  return (
    <article className="module-card weather-card">
      <div className="module-icon" aria-hidden="true">*</div>
      <div>
        <h2>{location}</h2>
        <p className="weather-temperature">{weather.temperature_c}°C</p>
        <p>{weather.description || weather.condition}</p>
        <dl className="weather-details">
          <div><dt>Humidity</dt><dd>{weather.humidity_percent}%</dd></div>
          <div><dt>Wind</dt><dd>{weather.wind_speed_mps} m/s</dd></div>
          {weather.rain_probability !== null && (
            <div><dt>Rain</dt><dd>{weather.rain_probability}%</dd></div>
          )}
        </dl>
        {advisory && <p className="weather-advisory">{advisory}</p>}
      </div>
      <span className="module-state">OpenWeather</span>
    </article>
  );
}

function NotificationsCard() {
  const [notifications, setNotifications] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/notifications/latest?limit=3`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Notification request failed");
        }
        return response.json();
      })
      .then((data) => setNotifications(data.notifications || []))
      .catch(() => setError(true));
  }, []);

  return (
    <section className="updates-section" aria-labelledby="updates-title">
      <div className="updates-heading">
        <p className="eyebrow">Latest government updates detected from official sources</p>
        <h2 id="updates-title">Relevant government updates</h2>
      </div>
      {error && <p className="updates-message">Unable to fetch government updates. Please try again.</p>}
      {!error && notifications === null && <p className="updates-message">Fetching government updates...</p>}
      {!error && notifications?.length === 0 && <p className="updates-message">No government updates are currently available.</p>}
      <div className="updates-grid">
        {notifications?.map((notification) => (
          <article className="update-card" key={notification.id}>
            <div className="update-card-topline">
              <span>{notification.category}</span>
              {notification.is_new && <strong>NEW</strong>}
            </div>
            <h3>{notification.title}</h3>
            {notification.summary && <p>{notification.summary}</p>}
            <p className="update-source">{notification.source_name}</p>
            <a href={notification.official_url} target="_blank" rel="noreferrer">
              Official source
            </a>
          </article>
        ))}
      </div>
    </section>
  );
}

function App() {
  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="KrishiVaani home">
          <span className="brand-mark">K</span>
          <span>KrishiVaani</span>
        </a>
        <span className="status-pill">Foundation ready</span>
      </header>

      <section className="intro" aria-labelledby="page-title">
        <p className="eyebrow">Farmer assistance platform</p>
        <h1 id="page-title">Clearer decisions for every field.</h1>
        <p className="lede">
          AI-powered assistance for farmers, shaped around trusted information
          and practical next steps.
        </p>
        <div className="language-control" aria-label="Language options">
          <span>Language</span>
          <button type="button" className="language-option active">
            English
          </button>
          <button type="button" className="language-option" disabled>
            Kannada
          </button>
        </div>
      </section>

      <section className="module-grid" aria-label="KrishiVaani modules">
        {modules.map((module) => (
          module.title === "Weather" ? <WeatherCard key={module.title} /> : <article className={`module-card ${module.accent}`} key={module.title}>
            <div className="module-icon" aria-hidden="true">
              {module.accent === "sun" && "*"}
              {module.accent === "leaf" && "+"}
              {module.accent === "chat" && "..."}
              {module.accent === "voice" && "))"}
            </div>
            <div>
              <h2>{module.title}</h2>
              <p>{module.detail}</p>
            </div>
            <span className="module-state">Coming soon</span>
          </article>
        ))}
      </section>

      <NotificationsCard />

      <section aria-labelledby="diagnosis-title">
        <div className="updates-heading">
          <p className="eyebrow">Evidence-backed plant health guidance</p>
          <h2 id="diagnosis-title">Diagnose a leaf</h2>
        </div>
        <ImageUpload />
      </section>

      <footer>
        <span>Built for farmers, with care.</span>
        <span className="footer-dot" aria-hidden="true" />
        <span>Trusted data will power the next steps.</span>
      </footer>
    </main>
  );
}

export default App;