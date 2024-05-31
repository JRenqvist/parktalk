package com.example.parktalk.api;

/**
 * Listener functions for the API calls
 */
public interface APIListener {
    void onSuccess(APIObject responseData);
    void onError(APIObject errorResponse);
}
