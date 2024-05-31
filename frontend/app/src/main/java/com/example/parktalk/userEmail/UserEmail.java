package com.example.parktalk.userEmail;

/**
 * This class will store the email of the user when they log in.
 * This is to keep track of who is currently using the app, so we can post, delete etc accordingly
 */
public class UserEmail {
    private final static UserEmail instance = new UserEmail();
    private String email = null;

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
    public static UserEmail getInstance(){return instance;}
}
