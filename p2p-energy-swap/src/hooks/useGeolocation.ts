// src/hooks/useGeolocation.ts
import { useEffect, useState, useCallback } from 'react';

type Coords = { lat: number; lon: number };
type GeoState = {
  coords: Coords | null;
  city: string | null;
  permission: 'prompt' | 'granted' | 'denied' | 'unknown';
  loading: boolean;
  error: string | null;
  refresh: () => void;
};

const STORAGE_KEY = 'geo';

function loadCached(): { coords: Coords | null; city: string | null } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { coords: null, city: null };
    const parsed = JSON.parse(raw);
    return { coords: parsed.coords ?? null, city: parsed.city ?? null };
  } catch {
    return { coords: null, city: null };
  }
}

function saveCached(data: { coords: Coords | null; city: string | null }) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {}
}

async function reverseGeocode(lat: number, lon: number): Promise<string | null> {
  try {
    // Use Open-Meteo reverse geocoding (no API key)
    const url = new URL('https://geocoding-api.open-meteo.com/v1/reverse');
    url.searchParams.set('latitude', String(lat));
    url.searchParams.set('longitude', String(lon));
    url.searchParams.set('count', '1');
    url.searchParams.set('language', 'en');
    url.searchParams.set('format', 'json');
    const resp = await fetch(url.toString());
    if (!resp.ok) return null;
    const data = await resp.json();
    const first = data?.results?.[0];
    if (!first) return null;
    // Prefer name + country code
    const city = [first.name, first.admin1]?.filter(Boolean).join(', ') || first.name;
    return city || null;
  } catch {
    return null;
  }
}

export function useGeolocation(): GeoState {
  const cached = loadCached();
  const [coords, setCoords] = useState<Coords | null>(cached.coords);
  const [city, setCity] = useState<string | null>(cached.city);
  const [permission, setPermission] = useState<GeoState['permission']>('unknown');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    if (!('geolocation' in navigator)) {
      setError('Geolocation not supported');
      setPermission('denied');
      return;
    }
    setLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = Number(pos.coords.latitude.toFixed(5));
        const lon = Number(pos.coords.longitude.toFixed(5));
        setCoords({ lat, lon });
        // Best-effort reverse geocode if no cached city
        let label = city;
        if (!label) {
          label = await reverseGeocode(lat, lon);
          setCity(label);
        }
        saveCached({ coords: { lat, lon }, city: label ?? null });
        setPermission('granted');
        setLoading(false);
      },
      (err) => {
        setError(err.message || 'Failed to get location');
        setPermission(err.code === err.PERMISSION_DENIED ? 'denied' : 'prompt');
        setLoading(false);
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 60_000 }
    );
  }, [city]);

  useEffect(() => {
    // Try to read permission status where supported
    let cancelled = false;
    if ('permissions' in navigator && (navigator as any).permissions?.query) {
      (navigator as any).permissions
        .query({ name: 'geolocation' as any })
        .then((res: any) => {
          if (cancelled) return;
          setPermission((res.state as any) || 'unknown');
        })
        .catch(() => {});
    }
    return () => {
      cancelled = true;
    };
  }, []);

  // If nothing cached, attempt a lazy fetch on mount (non-blocking)
  useEffect(() => {
    if (!coords) {
      // Don't auto-prompt; wait until a page asks for it, but try a low-friction check
      // Here we no-op by default. Call refresh() explicitly in pages.
    }
  }, [coords]);

  return { coords, city, permission, loading, error, refresh };
}

export default useGeolocation;
