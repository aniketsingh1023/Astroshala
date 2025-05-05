// utils/apiHelper.ts

/**
 * Helper function for making API calls with proper error handling
 */
export async function apiCall<T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<T> {
    try {
      // Ensure headers are set
      const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      };
  
      // Make the request
      const response = await fetch(url, {
        ...options,
        headers,
      });
  
      // Check if response is JSON
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        console.error("Non-JSON response:", text);
        throw new Error("Server returned non-JSON response");
      }
  
      // Parse the JSON response
      const data = await response.json();
  
      // Handle server errors
      if (!response.ok) {
        throw new Error(data.error || `API error: ${response.status}`);
      }
  
      return data as T;
    } catch (error) {
      // Log and rethrow
      console.error("API call failed:", error);
      throw error;
    }
  }
  
  /**
   * Helper function for authenticated API calls
   */
  export async function authApiCall<T>(
    url: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('Authentication required');
    }
    
    // Add auth header
    const headers = {
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    };
    
    return apiCall<T>(url, {
      ...options,
      headers,
    });
  }