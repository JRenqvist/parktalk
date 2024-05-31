package com.example.parktalk.api;

/**
 * A token object created to keep track of tokens users get when logging in
 */
public class Token {
    private final static Token instance = new Token();
    private String token = null;

    public Token() {}

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public static Token getInstance() {
        return instance;
    }
}
