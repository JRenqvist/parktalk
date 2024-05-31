package com.example.parktalk.login;

import android.content.Intent;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.example.parktalk.R;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Token;
import com.example.parktalk.home.HomeActivity;
import com.example.parktalk.userEmail.UserEmail;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * This fragment will display the login screen of the app
 */
public class LoginFragment extends Fragment {
    private EditText edInputEmail, edPassword;
    private LoginActivity loginActivity;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        loginActivity = (LoginActivity) getActivity();

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_login, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        edInputEmail = view.findViewById(R.id.input_email);
        edPassword = view.findViewById(R.id.password);
        Button login = view.findViewById(R.id.login);
        TextView signUp = view.findViewById(R.id.signup);
        Log.i("INFO", "launches login activity");

        login.setOnClickListener(v -> {
            String email = edInputEmail.getText().toString();
            String password = edPassword.getText().toString();

            //save the email in a singleton
            UserEmail.getInstance().setEmail(email);

            //check if no empty boxes
            if (email.isEmpty() || password.isEmpty()) {
                Toast.makeText(getContext(), "Please fill in all details", Toast.LENGTH_SHORT).show();
            } else {

                // Check user credentials with backend
                APICalls connection = new APICalls(getContext());

                // Create JSON data
                JSONObject jsonObject = new JSONObject();
                try {
                    jsonObject.put("email", email);
                    jsonObject.put("password", password);
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }

                connection.sendRequest(Request.Method.POST, jsonObject, null,
                        "users/login", new APIListener() {

                            @Override
                            public void onSuccess(APIObject responseData) {
                                Log.v("AUTHORIZED", "Successfully logged in and got token");

                                Token.getInstance().setToken(responseData.getToken());

                                // Start the HomeActivity
                                startActivity(new Intent(loginActivity, HomeActivity.class));
                                Toast.makeText(getContext(), "Login success", Toast.LENGTH_SHORT).show();
                            }

                            @Override
                            public void onError(APIObject errorResponse) {
                                Log.e("DENIED", "User does not exist in database");

                                Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                            }
                        });


            }
        });
        // Navigate to sign up fragment
        signUp.setOnClickListener(v -> loginActivity.navigateToSignup());
    }
}
