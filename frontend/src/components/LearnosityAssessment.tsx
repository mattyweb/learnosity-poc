import React, { useEffect, useState } from 'react';

interface LearnosityConfig {
  security: any;
  request: any;
}

declare global {
  interface Window {
    LearnosityItems: any;
  }
}

const LearnosityAssessment: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [learnosityConfig, setLearnosityConfig] = useState<LearnosityConfig | null>(null);

  useEffect(() => {
    const initializeLearnosity = async () => {
      const maxRetries = 5;
      const retryDelay = 2000; // 2 seconds
      
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          // Fetch configuration from FastAPI backend
          const response = await fetch('http://localhost:8000/api/items');
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: Failed to fetch Learnosity configuration`);
          }
          
          const data: LearnosityConfig = await response.json();
          
          // Store the config and stop loading so DOM renders
          setLearnosityConfig(data);
          setLoading(false);
          
          // If we get here, success! Break out of retry loop
          break;
          
        } catch (err) {
          console.log(`Attempt ${attempt} failed:`, err instanceof Error ? err.message : 'Unknown error');
          
          if (attempt === maxRetries) {
            setError(`Failed to connect to backend after ${maxRetries} attempts. Make sure the FastAPI server is running on port 8000.`);
            setLoading(false);
            return;
          }
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
      }
    };

    initializeLearnosity();
  }, []);

  // Second useEffect to initialize Learnosity after DOM is ready
  useEffect(() => {
    if (learnosityConfig && !loading) {
      // Load Learnosity Items API script
      const script = document.createElement('script');
      script.src = 'https://items.learnosity.com/?latest-lts';
      script.async = true;
      
      script.onload = () => {
        // Initialize Items API after script loads and DOM is ready
        if (window.LearnosityItems) {
          window.LearnosityItems.init(learnosityConfig);
        } else {
          setError('Failed to load Learnosity Items API');
        }
      };
      
      script.onerror = () => {
        setError('Failed to load Learnosity script');
      };
      
      document.head.appendChild(script);
      
      // Cleanup function to remove script on unmount
      return () => {
        if (document.head.contains(script)) {
          document.head.removeChild(script);
        }
      };
    }
  }, [learnosityConfig, loading]);

  if (loading) {
    return <div>Loading assessment... (Connecting to backend)</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div id="learnosity_assess"></div>
  );
};

export default LearnosityAssessment;