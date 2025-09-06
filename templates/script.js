function fetchData() {
      fetch('/data')
        .then(response => response.json())
        .then(data => {
          // Update raw values
          document.getElementById('soilRaw').innerText = data.soil;
          document.getElementById('smokeRaw').innerText = data.smoke;
          document.getElementById('ldrRaw').innerText = data.ldr;
          document.getElementById('flameRaw').innerText = data.flame;

          // Soil logic
          const soilStatus = document.getElementById('soilStatus');
          if (data.soil > 700) {
            soilStatus.innerText = "🚱 No signs of flood";
            soilStatus.className = "status-box status-green";
          } else if (data.soil > 400) {
            soilStatus.innerText = "💧 Moisture detected";
            soilStatus.className = "status-box status-yellow";
          } else {
            soilStatus.innerText = "🌊 Water level rising";
            soilStatus.className = "status-box status-red";
          }

          // Smoke logic
          const smokeStatus = document.getElementById('smokeStatus');
          if (data.smoke > 200) {
            smokeStatus.innerText = "⚠️ Smoke or Gas Detected!";
            smokeStatus.className = "status-box status-red";
          } else {
            smokeStatus.innerText = "✅ Air is Clean";
            smokeStatus.className = "status-box status-green";
          }

          // LDR logic
          const ldrStatus = document.getElementById('ldrStatus');
          if (data.ldr < 300) {
            ldrStatus.innerText = "🌞 Bright Light,Full Power";
            ldrStatus.className = "status-box status-green";
          } else if (data.ldr < 700) {
            ldrStatus.innerText = "🌤 Medium Light,Unstable Power";
            ldrStatus.className = "status-box status-yellow";
          } else {
            ldrStatus.innerText = "🌑 It's Dark,No Power";
            ldrStatus.className = "status-box status-red";
          }

          // Flame logic
          const flameStatus = document.getElementById('flameStatus');
          if (data.flame == 0) {
            flameStatus.innerText = "🔥 Flame Detected!";
            flameStatus.className = "status-box status-red";
          } else {
            flameStatus.innerText = "✅ No Flame";
            flameStatus.className = "status-box status-green";
          }
        });
    }

    setInterval(fetchData, 900);
