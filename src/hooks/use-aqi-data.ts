import { useState, useEffect, useCallback, useRef } from "react";
import { supabase } from "@/integrations/supabase/client";
import { StationData } from "@/types/aqi";
import { DELHI_STATIONS, getZone, formatAQI } from "@/lib/aqi-utils";

interface UseAQIDataOptions {
  refreshInterval?: number;
}

export function useAQIData(options: UseAQIDataOptions = {}) {
  const { refreshInterval = 300000 } = options;

  const [stations, setStations] = useState<StationData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isUsingLiveData, setIsUsingLiveData] = useState(false);

  const lastStoredRef = useRef<number>(0);

  const generateMockData = useCallback((): StationData[] => {
    return DELHI_STATIONS.map((station) => {
      const baseAQI = 80 + Math.floor(Math.random() * 220);

      return {
        id: station.id,
        name: station.name,
        aqi: baseAQI,
        lat: station.lat,
        lng: station.lng,
        zone: getZone(baseAQI),
        pollutants: {
          pm25: 30 + Math.floor(Math.random() * 200),
          pm10: 50 + Math.floor(Math.random() * 250),
          no2: 10 + Math.floor(Math.random() * 80),
          so2: 5 + Math.floor(Math.random() * 40),
          co: 2 + Math.floor(Math.random() * 15),
          o3: 20 + Math.floor(Math.random() * 60),
        },
        dominentPol: "pm25",
        time: new Date().toISOString(),
      };
    });
  }, []);

  const fetchAllStations = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const { data, error: fnError } = await supabase.functions.invoke(
        "fetch-aqi",
        {
          body: { action: "getStations" },
        }
      );

      console.log("SUPABASE RESPONSE:", data);
      console.log("SUPABASE ERROR:", fnError);

      if (fnError) {
        throw fnError;
      }

      if (!data || !data.success) {
        throw new Error(data?.error || "Failed to fetch AQI data");
      }

      const liveStations: StationData[] = data.data.map((s: any) => {
        const aqi = formatAQI(s.aqi);

        return {
          id: s.id,
          name: s.name,
          aqi,
          lat: s.lat,
          lng: s.lng,
          zone: getZone(aqi),
          time: s.time,
        };
      });

      if (liveStations.length > 0) {
        setStations(liveStations);
        setIsUsingLiveData(true);
        console.log("Loaded live AQI stations:", liveStations.length);
      } else {
        throw new Error("No stations returned from API");
      }

      setLastUpdated(new Date());
    } catch (err) {
      console.warn("Live AQI failed — using mock data", err);

      const mockStations = generateMockData();

      setStations(mockStations);
      setIsUsingLiveData(false);
      setLastUpdated(new Date());

      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  }, [generateMockData]);

  useEffect(() => {
    fetchAllStations();

    const interval = setInterval(fetchAllStations, refreshInterval);

    return () => clearInterval(interval);
  }, [fetchAllStations, refreshInterval]);

  const refresh = useCallback(() => {
    fetchAllStations();
  }, [fetchAllStations]);

  return {
    stations,
    isLoading,
    error,
    lastUpdated,
    refresh,
    isUsingLiveData,
  };
}