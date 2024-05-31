package com.example.parktalk.api;

import android.content.Context;

import androidx.annotation.Nullable;

import com.android.volley.ClientError;
import com.android.volley.DefaultRetryPolicy;
import com.android.volley.RequestQueue;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.google.gson.Gson;

import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * This class handles all API calls to the backend.
 *
 * @params context  The context of what is sending the request, not null
 * @apiNote         The API always returns on the JSON format
 *                  {
 *                      status: success/fail,
 *                      message: information
 *                  }
 *                  These two will always be in included, but more data may be sent.
 *                  See backend comments for details.
 */
public class APICalls {
    private final String URL = "http://10.0.2.2:5000/";
    private final Context context;
    private RequestQueue queue;

    public APICalls(Context context) {
        this.context = context;

        // Create one queue that holds all requests
        this.queue = Volley.newRequestQueue(context);

    }

    public void sendRequest(int method, @Nullable JSONObject jsonObject,
                            @Nullable String token, String route, APIListener listener) {

        // Create string request
        StringRequest stringRequest = new StringRequest(method, URL +route,
                response -> {
                    // Create APIObject based on response data using GSON
                    Gson gson = new Gson();
                    APIObject apiObject = gson.fromJson(response, APIObject.class);

                    // Call listeners function
                    listener.onSuccess(apiObject);
                },
                volleyError -> {

                    // This if clause will determine if the error we caught was an error from
                    // our backend or some other error thrown by volley
                    if (volleyError instanceof ClientError) {
                        // If we get in here, it means it's an error on our backend
                        // Get byte array from response data
                        byte[] byteArray = volleyError.networkResponse.data;

                        // Convert byte array to APIObject using GSON
                        Gson gson = new Gson();
                        String jsonStringFromByteArray = new String(byteArray, StandardCharsets.UTF_8);
                        APIObject errorResponse = gson.fromJson(jsonStringFromByteArray, APIObject.class);

                        // Call listeners function
                        listener.onError(errorResponse);
                    } else {
                        // If we get in here, it means the error was thrown for something else.
                        volleyError.printStackTrace();

                        APIObject errorResponse = new APIObject("fail", "Network error. Please try again.");
                        listener.onError(errorResponse);

                    }
                }) {
                @Override
                public byte[] getBody() {
                    return jsonObject.toString().getBytes();
                }

                @Override
                public Map<String, String> getHeaders() {
                    Map<String, String> params = new HashMap<>();
                    params.put("Authorization", "Bearer " + token);
                    return params;
                }

                @Override
                public String getBodyContentType() {
                    return "application/json";
                }
            };
        stringRequest.setRetryPolicy(new DefaultRetryPolicy(DefaultRetryPolicy.DEFAULT_TIMEOUT_MS, 5, DefaultRetryPolicy.DEFAULT_BACKOFF_MULT));
        queue.add(stringRequest);

    }
}

