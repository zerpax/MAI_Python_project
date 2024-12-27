import React, { useState, useEffect } from "react";

const ScammersList = () => {
  const [scammers, setScammers] = useState([]); // State for scammers
  const [error, setError] = useState("");      // State for error messages
  const [loading, setLoading] = useState(true); // State for loading spinner

  const fetchScammers = async () => {
    try {
      // Retrieve the JWT token from localStorage (or wherever you store it)
      const token = localStorage.getItem('token');

      if (!token) {
        setError("You are not authorized. Please log in.");
        setLoading(false);
        return;
      }

      const response = await fetch("http://127.0.0.1:8000/scammers/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, // Include the JWT token
        },
      });

      if (!response.ok) {
        // Handle HTTP errors
        const { detail } = await response.json();
        setError(`Error: ${detail}`);
        setLoading(false);
        return;
      }

      const data = await response.json(); // Parse JSON response
      setScammers(data);
    } catch (err) {
      setError("Failed to fetch scammers. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScammers();
  }, []);

  if (loading) {
    return <div>Loading...</div>; // Loading state
  }

  if (error) {
    return <div className="error">{error}</div>; // Display error messages
  }

  return (
    <div>
      <h1>Scammers List</h1>
      <ul>
        {scammers.map((scammer, index) => (
          <li key={index}>{scammer.ip_address}</li>
        ))}
      </ul>
    </div>
  );
};

export default ScammersList;
