export async function predictAQI(data:any) {

  console.log("CALLING ML API", data);

  const res = await fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });

  const result = await res.json();

  console.log("ML RESPONSE", result);

  return result;
}