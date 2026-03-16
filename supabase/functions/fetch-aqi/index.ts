import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const WAQI_API_BASE = "https://api.waqi.info";

// --------------------------------------------------
// CORS HEADERS
// --------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Max-Age": "86400",
};

// --------------------------------------------------
// TOKEN HELPER
// --------------------------------------------------

function getWaqiToken(): string {
  const token = Deno.env.get("WAQI_API_TOKEN");
  if (!token) {
    throw new Error("WAQI_API_TOKEN not configured in Supabase secrets");
  }
  return token.trim();
}

function maskToken(token: string) {
  if (token.length <= 8) return "***";
  return `${token.slice(0, 4)}...${token.slice(-4)}`;
}

// --------------------------------------------------
// SAFE JSON PARSE
// --------------------------------------------------

async function safeJson(req: Request) {
  try {
    return await req.json();
  } catch {
    return {};
  }
}

// --------------------------------------------------
// MAIN EDGE FUNCTION
// --------------------------------------------------

serve(async (req: Request) => {

  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {

    const url = new URL(req.url);

    const body = await safeJson(req);

    const action =
      body?.action ??
      url.searchParams.get("action") ??
      "getStations";

    const stationId =
      body?.stationId ??
      url.searchParams.get("stationId");

    const keyword =
      body?.keyword ??
      url.searchParams.get("keyword");

    const token = getWaqiToken();

    console.log("Using WAQI token:", maskToken(token));

    let data: any = null;

    // ======================================================
    // 1️⃣ GET ALL STATIONS
    // ======================================================

    if (action === "getStations") {

      const bounds = body?.bounds ?? {
        lat1: 28.20,
        lng1: 76.40,
        lat2: 29.30,
        lng2: 77.90,
      };

      const apiUrl =
        `${WAQI_API_BASE}/map/bounds/?latlng=` +
        `${bounds.lat1},${bounds.lng1},${bounds.lat2},${bounds.lng2}` +
        `&token=${token}`;

      console.log("Fetching stations:", apiUrl);

      const response = await fetch(apiUrl);

      if (!response.ok) {
        throw new Error(`WAQI request failed: ${response.status}`);
      }

      const result = await response.json();

      console.log("WAQI response status:", result.status);

      if (result.status !== "ok") {
        throw new Error(result.data || "WAQI API error");
      }

      data = result.data
        .filter((s: any) => s.aqi && s.aqi !== "-")
        .map((s: any) => ({
          id: s.uid?.toString() ?? s.station?.name ?? "unknown",
          name: s.station?.name ?? "Unknown Station",
          aqi: parseInt(s.aqi) || null,
          lat: s.lat,
          lng: s.lon,
          time: s.station?.time ?? null,
        }));

      console.log(`Stations fetched: ${data.length}`);
    }

    // ======================================================
    // 2️⃣ GET SINGLE STATION DETAILS
    // ======================================================

    else if (action === "getStationDetails") {

      if (!stationId) {
        throw new Error("stationId is required");
      }

      const apiUrl =
        `${WAQI_API_BASE}/feed/${stationId}/?token=${token}`;

      console.log("Fetching station:", stationId);

      const response = await fetch(apiUrl);

      if (!response.ok) {
        throw new Error(`WAQI request failed: ${response.status}`);
      }

      const result = await response.json();

      if (result.status !== "ok") {
        throw new Error(result.data || "Station not found");
      }

      const iaqi = result.data?.iaqi ?? {};

      data = {
        aqi: result.data?.aqi ?? null,

        // pollution
        pm2_5: iaqi?.pm25?.v ?? null,
        pm10: iaqi?.pm10?.v ?? null,
        no2: iaqi?.no2?.v ?? null,
        so2: iaqi?.so2?.v ?? null,
        co: iaqi?.co?.v ?? null,

        // weather
        temperature: iaqi?.t?.v ?? null,
        humidity: iaqi?.h?.v ?? null,
        pressure: iaqi?.p?.v ?? null,
        wind_speed: iaqi?.w?.v ?? null,
        wind_direction: iaqi?.wd?.v ?? null,

        city: result.data?.city ?? null,
        time: result.data?.time ?? null,
      };
    }

    // ======================================================
    // 3️⃣ SEARCH STATION
    // ======================================================

    else if (action === "searchStation") {

      if (!keyword) {
        throw new Error("keyword is required");
      }

      const apiUrl =
        `${WAQI_API_BASE}/search/?keyword=` +
        `${encodeURIComponent(keyword)}` +
        `&token=${token}`;

      const response = await fetch(apiUrl);

      if (!response.ok) {
        throw new Error(`WAQI request failed: ${response.status}`);
      }

      const result = await response.json();

      if (result.status !== "ok") {
        throw new Error(result.data || "Search failed");
      }

      data = result.data.map((s: any) => ({
        uid: s.uid,
        name: s.station?.name ?? "Unknown",
        aqi: s.aqi ?? null,
        time: s.time?.stime ?? null,
      }));
    }

    // ======================================================
    // UNKNOWN ACTION
    // ======================================================

    else {
      throw new Error(`Unknown action: ${action}`);
    }

    // ======================================================
    // SUCCESS RESPONSE
    // ======================================================

    return new Response(
      JSON.stringify({
        success: true,
        data,
      }),
      {
        status: 200,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );

  } catch (error) {

    const message =
      error instanceof Error ? error.message : "Unknown error";

    console.error("fetch-aqi error:", message);

    return new Response(
      JSON.stringify({
        success: false,
        error: message,
      }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  }
});