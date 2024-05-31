package com.example.parktalk.api;

/**
 * This is a user in the app
 */
public class User {
    private String email;
    private String username;
    private int points;
    private int posts_amount;
    private int followers;

    public User(String email,
                String username,
                int points,
                int posts_amount,
                int amountOfFollowers) {
        this.email = email;
        this.username = username;
        this.points = points;
        this.posts_amount = posts_amount;
        this.followers = amountOfFollowers;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public int getPoints() {
        return points;
    }

    public void setPoints(int points) {
        this.points = points;
    }

    public int getPosts_amount() {
        return posts_amount;
    }

    public void setPosts_amount(int posts_amount) {
        this.posts_amount = posts_amount;
    }

    public int getFollowers() {
        return followers;
    }

    public void setFollowers(int followers) {
        this.followers = followers;
    }
}
