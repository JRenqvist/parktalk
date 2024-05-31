package com.example.parktalk.login;

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

import org.json.JSONException;
import org.json.JSONObject;

/**
 * This fragment will display the signup screen of the app
 */
public class SignupFragment extends Fragment {
    private EditText edUsername, edPassword, edEmail, edConfirmPassword;
    private LoginActivity loginActivity;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        loginActivity = (LoginActivity) getActivity();

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_signup, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        edUsername = view.findViewById(R.id.input_email);
        edPassword = view.findViewById(R.id.password);
        edEmail = view.findViewById(R.id.email);
        edConfirmPassword = view.findViewById(R.id.confirmpassword);
        Button register = view.findViewById(R.id.login);
        TextView existAccount = view.findViewById(R.id.existingUser);

        existAccount.setOnClickListener(v -> loginActivity.navigateToLogin());

        register.setOnClickListener(v -> {
            String username = edUsername.getText().toString();
            String email = edEmail.getText().toString();
            String password = edPassword.getText().toString();
            String confirm = edConfirmPassword.getText().toString();

            //check no empty boxes
            if(username.isEmpty() || password.isEmpty() || email.isEmpty() || confirm.isEmpty()){
                Toast.makeText(getContext(), "Please fill in all details", Toast.LENGTH_SHORT).show();
            }
            else{
                //check if the password is solid
                if(password.compareTo(confirm)==0){
                    if(isSolid(password)){

                        // Make API call
                        APICalls connection = new APICalls(loginActivity);

                        // Create JSON data
                        JSONObject jsonObject = new JSONObject();
                        try {
                            jsonObject.put("username", username);
                            jsonObject.put("email", email);
                            jsonObject.put("password", password);
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }

                        connection.sendRequest(Request.Method.POST, jsonObject, null,
                                "users/create", new APIListener() {
                                    @Override
                                    public void onSuccess(APIObject responseData) {
                                        Log.v("AUTHORIZED", "Successfully registered user");

                                        Toast.makeText(getContext(), responseData.getMessage(), Toast.LENGTH_SHORT).show();
                                        // Navigate to login fragment
                                        loginActivity.navigateToLogin();
                                    }

                                    @Override
                                    public void onError(APIObject errorResponse) {
                                        Log.e("DENIED", "Could not create user");

                                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                                    }
                                });
                    }
                    else {Toast.makeText(getContext(), "Password must contain at least 8 characters, having letter and digit",
                            Toast.LENGTH_SHORT).show();}
                }
                //check if both passwords are identical
                else{Toast.makeText(getContext(), "Passwords didn't match", Toast.LENGTH_SHORT).show();}
            }
        });

    }
    public static boolean isSolid(String password){
        int flag1=0,flag2=0;
        if (password.length()<8){return false;}
        else {
            for (int i=0; i<password.length();i++){
                if(Character.isLetter(password.charAt(i))){flag1=1;}
                if (Character.isDigit(password.charAt(i))){flag2=1;}
            }
            if(flag1==1 && flag2==1){return true;}

            return false;
        }
    }

}