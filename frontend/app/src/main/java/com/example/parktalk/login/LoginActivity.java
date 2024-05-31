package com.example.parktalk.login;

import androidx.appcompat.app.AppCompatActivity;
import androidx.navigation.NavController;
import androidx.navigation.NavDirections;
import androidx.navigation.Navigation;

import android.os.Bundle;

import com.example.parktalk.R;

/**
 * This activity is the login page
 * This is what the user first sees when they start the app
 */
public class LoginActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
    }

    public void navigateToSignup() {
        NavDirections action = LoginFragmentDirections.actionLoginFragmentToSignupFragment();
        NavController navController = Navigation.findNavController(this, R.id.loginContainer);
        navController.navigate(action);
    }

    public void navigateToLogin() {
        NavDirections action = SignupFragmentDirections.actionSignupFragmentToLoginFragment();
        NavController navController = Navigation.findNavController(this, R.id.loginContainer);
        navController.navigate(action);
    }

}