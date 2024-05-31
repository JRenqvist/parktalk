package com.example.parktalk.api;

/**
 * This is a post object in the app
 */
public class Post {
    private int post_id, likes, amount_of_comments;
    private String user_email, caption, address, img, username;

    public Post(int post_id,
                int likes,
                int amount_of_comments,
                String user_email,
                String caption,
                String address,
                String img,
                String username) {
        this.post_id = post_id;
        this.likes = likes;
        this.amount_of_comments = amount_of_comments;
        this.user_email = user_email;
        this.caption = caption;
        this.address = address;
        this.img = img;
        this.username = username;
    }

    public int getAmount_of_comments() {
        return amount_of_comments;
    }

    public void setAmount_of_comments(int amount_of_comments) {
        this.amount_of_comments = amount_of_comments;
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

    public String getCaption() {
        return caption;
    }

    public void setCaption(String caption) {
        this.caption = caption;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getImg() {
        return img;
    }

    public void setImg(String img) {
        this.img = img;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }
}
