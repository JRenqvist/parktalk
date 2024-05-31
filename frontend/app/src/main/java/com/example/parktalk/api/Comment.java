package com.example.parktalk.api;

/**
 * This is a comment object of a post
 */
public class Comment {
    private int comment_id, post_id, likes;
    private String user_email, comment_string, username;

    public Comment(int comment_id, int post_id, int likes, String user_email, String comment_string) {
        this.comment_id = comment_id;
        this.post_id = post_id;
        this.likes = likes;
        this.user_email = user_email;
        this.comment_string = comment_string;
    }

    public int getComment_id() {
        return comment_id;
    }

    public void setComment_id(int comment_id) {
        this.comment_id = comment_id;
    }

    public int getPost_id() {
        return post_id;
    }

    public void setPost_id(int post_id) {
        this.post_id = post_id;
    }

    public int getLikes() {
        return likes;
    }

    public void setLikes(int likes) {
        this.likes = likes;
    }

    public String getUser_email() {
        return user_email;
    }

    public void setUser_email(String user_email) {
        this.user_email = user_email;
    }

    public String getComment_string() {
        return comment_string;
    }

    public void setComment_string(String comment_string) {
        this.comment_string = comment_string;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }
}
