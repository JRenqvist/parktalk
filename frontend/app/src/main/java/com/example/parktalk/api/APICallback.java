package com.example.parktalk.api;

/**
 * This interface is a callback to wait for response from boolean routes in backend like /posts/ispostliked etc.
 * This makes it easier to set the image of e.g the like button to "liked" or "unliked"
 */
public interface APICallback {
    void onCallback(boolean response);
    void onError(APIObject errorResponse);
}
