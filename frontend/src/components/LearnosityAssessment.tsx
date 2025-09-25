import React, { useEffect, useState, useRef } from 'react';

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
  const initializedRef = useRef(false);

  useEffect(() => {
    const initializeLearnosity = async () => {
      const maxRetries = 5;
      const retryDelay = 2000; // 2 seconds
      
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          // Fetch configuration from FastAPI backend - using new test endpoint
          const response = await fetch('http://localhost:8000/api/tests/new');
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
    if (learnosityConfig && !loading && !initializedRef.current) {
      initializedRef.current = true;

      // Check if Learnosity script is already loaded
      const existingScript = document.querySelector('script[src*="items.learnosity.com"]');

      if (existingScript) {
        // Script already exists, just initialize if LearnosityItems is available
        if (window.LearnosityItems) {
          try {
            // Clear any existing assessment first
            const assessElement = document.getElementById('learnosity_assess');
            if (assessElement) {
              assessElement.innerHTML = '';
            }
            window.LearnosityItems.init(learnosityConfig);
          } catch (err) {
            console.error('Failed to initialize Learnosity:', err);
            setError('Failed to initialize Learnosity Items API');
            initializedRef.current = false;
          }
        }
        return;
      }

      // Load Learnosity Items API script only if not already loaded
      const script = document.createElement('script');
      script.src = 'https://items.learnosity.com/?latest-lts';
      script.async = true;

      script.onload = () => {
        // Initialize Items API after script loads and DOM is ready
        if (window.LearnosityItems) {
          try {
            // Clear any existing assessment first
            const assessElement = document.getElementById('learnosity_assess');
            if (assessElement) {
              assessElement.innerHTML = '';
            }
            window.LearnosityItems.init(learnosityConfig);
          } catch (err) {
            console.error('Failed to initialize Learnosity:', err);
            setError('Failed to initialize Learnosity Items API');
            initializedRef.current = false;
          }
        } else {
          setError('Failed to load Learnosity Items API');
          initializedRef.current = false;
        }
      };

      script.onerror = () => {
        setError('Failed to load Learnosity script');
        initializedRef.current = false;
      };

      document.head.appendChild(script);

      // Cleanup function to remove script on unmount
      return () => {
        if (document.head.contains(script)) {
          document.head.removeChild(script);
        }
        initializedRef.current = false;
      };
    }
  }, [learnosityConfig, loading]);

  if (loading) {
    return <div>Creating new test... (Generating questions and connecting to backend)</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div id="learnosity_assess"></div>
  );
};

export default LearnosityAssessment;