package com.example.parktalk.api;

import androidx.annotation.Nullable;

import java.util.ArrayList;

/**
 * The object we get from an API call
 * Using GSON to create this object
 */
public class APIObject {
    // Base return messages
    private String status, message, token, username;

    // Single user return messages
    @Nullable
    private User user;

    // Single post return messages
    @Nullable
    private Post post;

    // Single comment return messages
    @Nullable
    private Comment comment;

    // List of posts
    @Nullable
    private ArrayList<Post> posts;

    // List of users
    @Nullable
    private ArrayList<User> users;

    // List of comments
    private ArrayList<Comment> comments;

    public APIObject(String status, String message) {
        this.status = status;
        this.message = message;
    }

    public Post getPost() {
        return post;
    }

    public void setPost(Post post) {
        this.post = post;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    @Nullable public String getToken() {
        return token;
    }

    public void setToken(@Nullable String token) {
        this.token = token;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    @Nullable
    public Comment getComment() {
        return comment;
    }

    public void setComment(@Nullable Comment comment) {
        this.comment = comment;
    }

    @Nullable
    public ArrayList<Post> getPosts() {
        return posts;
    }

    public void setPosts(@Nullable ArrayList<Post> posts) {
        this.posts = posts;
    }

    @Nullable
    public ArrayList<User> getUsers() {
        return users;
    }

    public void setUsers(@Nullable ArrayList<User> users) {
        this.users = users;
    }

    public ArrayList<Comment> getComments() {
        return comments;
    }

    public void setComments(ArrayList<Comment> comments) {
        this.comments = comments;
    }

    @Nullable
    public User getUser() {
        return user;
    }

    public void setUser(@Nullable User user) {
        this.user = user;
    }
}