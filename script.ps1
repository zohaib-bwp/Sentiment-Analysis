$body = @{ text = "I love this movie" } | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:5000/predict `
  -Method POST `
  -Headers @{ "X-API-KEY" = "testkey" } `
  -Body $body `
  -ContentType "application/json"
