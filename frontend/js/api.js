async function requestSolution(topic, equation) {
 const response = await fetch("/api/calculate",{
     method: "POST",
     headers: {
         "Constent-Type": "application/json"
     },
     body: JSON.stringify({
         topic,
         equation
     })
 });
 const data = await response.json();
 if (!response.ok) {
     throw new Error(
         typeof data.detail === "string"
         ? data.detail
             : "The calculation could not be completed"
     );
 }
 return data;
}