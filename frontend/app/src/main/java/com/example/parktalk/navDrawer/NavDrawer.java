package com.example.parktalk.navDrawer;

import android.app.Activity;
import android.content.Intent;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.android.volley.Request;
import com.example.parktalk.login.LoginActivity;
import com.example.parktalk.R;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Token;

import org.json.JSONObject;

/**
 * This is a common class that handles the functionality in the navigation drawer.
 * This class is used to set the click listeners to the items in the navigation drawer.
 */
public class NavDrawer {
    public static void setLinearLayoutClickListener(LinearLayout linearLayout, AppCompatActivity currentActivity, Class nextActivity) {

        // If the ID of the LinearLayout is logout, make an API call and mark the token as expired
        if (linearLayout.getId() == R.id.logout) {
            linearLayout.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    // Mark token as expired
                    APICalls connection = new APICalls(currentActivity);

                    // Send empty JSON data
                    JSONObject jsonData = new JSONObject();
                    String token = Token.getInstance().getToken();

                    // Send call to user/logout route
                    connection.sendRequest(Request.Method.POST, jsonData, token,
                            "users/logout", new APIListener() {
                                @Override
                                public void onSuccess(APIObject responseData) {
                                    Log.v("AUTHORIZED", "Successfully marked token as expired");

                                    Toast.makeText(currentActivity,"Logout", Toast.LENGTH_SHORT).show();
                                    redirectActivity(currentActivity, LoginActivity.class);
                                }

                                @Override
                                public void onError(APIObject errorResponse) {
                                    Log.e("DENIED", "Could not dispose token: " + errorResponse.getMessage());
                                }
                            });

                }
            });

        // Else set the click listeners as normal
        } else {
            linearLayout.setOnClickListener(v -> {
                redirectActivity(currentActivity, nextActivity);
            });
        }
    }

    public static void setImageViewClickListener(ImageView imageView, DrawerLayout drawerLayout) {
        imageView.setOnClickListener(v -> {
            openDrawer(drawerLayout);
        });
    }

    public static void openDrawer(DrawerLayout drawerLayout){
        drawerLayout.openDrawer(GravityCompat.START);
    }

    public static void closeDrawer(DrawerLayout drawerLayout){
        if (drawerLayout.isDrawerOpen(GravityCompat.START)){
            drawerLayout.closeDrawer(GravityCompat.START);
        }
    }

    public static void redirectActivity(Activity activity, Class secondActivity){
        Intent intent = new Intent(activity, secondActivity);
        intent.setFlags(intent.FLAG_ACTIVITY_NEW_TASK);
        activity.startActivity(intent);
        activity.finish();
    }
}
