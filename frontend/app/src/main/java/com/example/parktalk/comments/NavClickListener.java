package com.example.parktalk.comments;

/**
 * This interface is used when we want to navigate to a user's profile from clicking a username
 * in the comments or the author of the post
 * Or if we want to go to the comment section of a given post
 */
public interface NavClickListener {
    void onCommentClick(int postId);
    void onUsernameClick(String userEmail);
}
