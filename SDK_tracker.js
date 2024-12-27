(
  function () {
  // Avoid reinitializing if the SDK is already defined
  if (window.TrackerSDK) {
    console.warn('TrackerSDK is already loaded.');
    return;
  }


  class TrackerSDK {
    static endpoint = 'http://127.0.0.1:8000/history'; // Default endpoint

    static init(endpoint = null) {
      if (TrackerSDK.initialized) {
        console.warn('TrackerSDK is already initialized.');
        return;
      }

      TrackerSDK.endpoint = endpoint || TrackerSDK.endpoint;
      TrackerSDK.initialized = true;

      // Track page visit on initialization
      TrackerSDK.trackVisit();
    }

    static async getUserIp() {
      return await fetch("http://127.0.0.1:8000/get-user-ip")
        .then((response) => response.json())
        .then((data) => data.ip) // Return just the IP address
        .catch((error) => {
          console.error("Error fetching IP address:", error);
          return null; // Return null if there's an error
        });
    }

    static async trackVisit() {
      const IP = await this.getUserIp().then((IP) => IP)
      const visitData = {
        url: window.location.href,
        ip_address: IP,
        timestamp: new Date().toISOString(),
      };
      console.log(visitData)
      TrackerSDK.sendData(visitData);
    }

    static async sendData(data) {
      console.log('Sending data:', data);
      fetch(TrackerSDK.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      })
        .then((response) => {
          if (!response.ok) {
            console.error('Failed to send tracking data:', response.statusText);
          }
        })
        .catch((error) => {
          console.error('Error sending tracking data:', error);
        });
    }
  }

  // Attach the TrackerSDK to the global `window` object
  window.TrackerSDK = TrackerSDK;
})();
