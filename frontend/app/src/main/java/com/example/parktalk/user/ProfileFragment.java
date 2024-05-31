package com.example.parktalk.user;

import android.content.Context;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.GridView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.example.parktalk.api.User;
import com.example.parktalk.home.HomeActivity;
import com.example.parktalk.R;
import com.example.parktalk.userEmail.UserEmail;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Post;
import com.example.parktalk.api.Token;
import com.example.parktalk.api.APICallback;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Objects;

/**
 * This fragment will display the profile of a user.
 * We get the users email passed with a safe arg in the transition
 */
public class  ProfileFragment extends Fragment {
    private TextView points, numberOfPosts, followers, username;
    private Button followButton;
    private GridView gridView;
    private String user_email;
    private ArrayList<Post> posts;
    private ProfileAdapter adapter;
    private HomeActivity home;

    public ProfileFragment() {
        // Required empty public constructor
    }


    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Get argument using safeargs
        user_email = getArguments().getString("user_email");
        Log.v("INFO", "User requested profile of: " + user_email);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        home = (HomeActivity) getActivity();
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_profile, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        init(view);

        // Set click listener to following function
        followButton.setOnClickListener(v -> onFollowClick(view.getContext()));

        // Set adapter with empty arraylist of posts.
        // This arraylist will later get updated once the call to the backend is complete
        adapter = new ProfileAdapter(getContext(), new ArrayList<>());
        gridView.setAdapter(adapter);
        gridView.setOnItemClickListener((parent, view1, position, id) -> {
            // Navigate to the single post fragment
            Post clickedPost = posts.get(position);
            int post_id = clickedPost.getPost_id();
            home.navigate(ProfileFragmentDirections.actionProfileFragmentToPostFragment(post_id));
        });

        // Call the function that displays the users about info
        // like username, followers, points etc
        getAndDisplayUserData();

    }

    /* This function fetches the current data stored in the database and displays them in the app
     * We need to make two api calls: one to get the username, points etc ("about" in backend)
     * and one to get the posts of the user
     */
    private void getAndDisplayUserData() {

        // Make call to "about"
        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();

        connection.sendRequest(Request.Method.GET, null, token, "users/get/data/"+user_email,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        // On success, set all the TextViews to the data we get from the call
                        User user = responseData.getUser();
                        username.setText(user.getUsername());
                        followers.setText("Followers: " + user.getFollowers());
                        points.setText("Points: " + user.getPoints());
                        numberOfPosts.setText("Posts: " + user.getPosts_amount());

                        // If the logged in user is the user we are displaying, don't show the follow button
                        String email = UserEmail.getInstance().getEmail();
                        if (Objects.equals(email, user.getEmail())) {
                            // If we get in here, it means that the logged in user is the user we are displaying
                            // Remove follow button
                            ((LinearLayout) followButton.getParent()).removeView(followButton);
                        } else {
                            // If we get in here, it means that the logged in user is not the user we are displaying
                            // Set the profile image to

                            // Get follow status of this user and update the follow button's appearance accordingly
                            checkIsFollowing(new APICallback() {
                                @Override
                                public void onCallback(boolean response) {
                                    if (response) {
                                        // If we get in here, it means that we are already following the user
                                        // Mark the follow button as "Unfollow"
                                        followButton.setText("Unfollow");
                                        followButton.setBackgroundTintList(ContextCompat.getColorStateList(getContext(), R.color.send_button_activated));
                                    } else {
                                        // If we get in here, it means that we are not following the user
                                        // Mark the button as "Follow"
                                        followButton.setText("Follow");
                                        followButton.setBackgroundTintList(ContextCompat.getColorStateList(getContext(), R.color.redish_like_icon));
                                    }
                                }

                                @Override
                                public void onError(APIObject errorResponse) {
                                    Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                                    Log.e("NETWORK", errorResponse.getMessage());
                                }
                            });

                            Log.v("NETWORK", "Got about data");
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Toast.makeText(getContext(), "Could not get user about", Toast.LENGTH_SHORT).show();
                        Log.e("NETWORK", "Could not get user about data: " + errorResponse.getMessage());
                    }
                });

        // After sending request to get about data, send request to get the user's posts
        connection.sendRequest(Request.Method.GET, null, token, "/users/get/posts/"+user_email,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        posts = responseData.getPosts();
                        adapter.updateData(posts);

                        Log.v("NETWORK", "Got the user's posts");
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_LONG).show();
                        Log.e("NETWORK", "Could not get the user's posts: " + errorResponse.getMessage());
                    }
                });
    }

    /*
     * This function makes an api call to see if the current user using the app is following
     * the user of the profile currently being displayed.
     */
    private void checkIsFollowing(APICallback callback) {
        // Get both the emails
        String followerEmail = UserEmail.getInstance().getEmail();
        String followingEmail = user_email;

        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();

        // Send a request to the backend and call the appropriate callback function on success/error
        connection.sendRequest(Request.Method.GET, null, token,
                "/users/isfollowing/" + followerEmail + "/" + followingEmail,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        // Call the onCallback with the boolean result of comparison with "true"
                        callback.onCallback(Objects.equals(responseData.getMessage(), "true"));
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        callback.onError(errorResponse);
                    }
                });
    }

    /* This function will be called once we click the follow button in the app
     * Then call the appropriate follow/unfollow route depending on what the button says
     */
    private void onFollowClick(Context context) {

        checkIsFollowing(new APICallback() {
            @Override
            public void onCallback(boolean response) {
                if (response) {
                    // If we get into here, it means that the logged in user is following
                    // the user being displayed.
                    // Call the function to unfollow the user in the backend
                    // This function also updates the follow button's appearance to match the
                    // following status
                    unfollowUser(context);
                    // Decrease the follower amount by 1
                    decreaseFollowerNumber();

                } else {
                    // If we get into here, it means that the logged in user is not following
                    // the user being displayed.
                    // Call the function to follow the user in the backend
                    // This function also updates the follow button's appearance to match the
                    // following status
                    followUser(context);
                    // Increase follower amount by 1
                    increaseFollowerNumber();
                }
            }
            @Override
            public void onError(APIObject errorResponse) {
                Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                Log.e("NETWORK", "Could not check if user is being followed: " + errorResponse.getMessage());
            }
        });
    }

    /* This function will make an api call to follow the user in the backend
     */
    private void followUser(Context context) {
        String followerEmail = UserEmail.getInstance().getEmail();
        String followingEmail = user_email;

        APICalls connection = new APICalls(getContext());

        JSONObject jsonObject = new JSONObject();
        String token = Token.getInstance().getToken();

        try {
            jsonObject.put("following_email", followingEmail);
            jsonObject.put("follower_email", followerEmail);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }

        connection.sendRequest(Request.Method.POST, jsonObject, token, "/users/follow",
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("INFO", "Successfully followed user");
                        Toast.makeText(getContext(), responseData.getMessage(), Toast.LENGTH_SHORT).show();

                        // Set the follow button to "Unfollow" type, since we just followed the user
                        setUnfollowButton(context);
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.v("INFO", "Could not follow user: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });

    }

    /* This function will unfollow a user in the backend
     */
    private void unfollowUser(Context context) {
        String followerEmail = UserEmail.getInstance().getEmail();
        String followingEmail = user_email;

        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();

        connection.sendRequest(Request.Method.DELETE, null, token,
                "/users/unfollow/"+followingEmail+"/"+followerEmail,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("INFO", "Successfully unfollowed user");
                        Toast.makeText(getContext(), responseData.getMessage(), Toast.LENGTH_SHORT).show();

                        // Set follow button to "Follow" type, since we just unfollowed the user
                        setFollowButton(context);
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.v("INFO", "Could not follow user: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });

    }

    /* This function will increase the follower number by 1
     */
    private void increaseFollowerNumber() {
        int currentFollowers = getIntOfFollowers();
        currentFollowers += 1;
        followers.setText("Followers: " + currentFollowers);
    }

    /* This function will decrease the follower number by 1
     */
    private void decreaseFollowerNumber() {
        int currentFollowers = getIntOfFollowers();
        currentFollowers -= 1;
        followers.setText("Followers: " + currentFollowers);
    }

    /* This function will return the integer part of
     * the follower count in the profile's about area
     */
    private int getIntOfFollowers() {
        String likeString = (String) followers.getText();
        StringBuilder resultString = new StringBuilder();
        // For every character in the string, if digit -> append to resultString
        for (int i = 0; i < likeString.length(); i++) {
            boolean flag = Character.isDigit(likeString.charAt(i));
            if (flag) {
                resultString.append(likeString.charAt(i));
            }
        }
        // Return the resulting string as an integer
        return Integer.parseInt(resultString.toString());
    }

    /* This function will set the follow button to a red button with the text "Follow"
     */
    private void setFollowButton(Context context) {
        // Change the color and text of the button
        followButton.setBackgroundTintList(ContextCompat.getColorStateList(context, R.color.redish_like_icon));
        followButton.setText("Follow");
    }

    /* This function will set the follow button to a blue button with the text "Unfollow"
     */
    private void setUnfollowButton(Context context) {
        followButton.setBackgroundTintList(ContextCompat.getColorStateList(context, R.color.send_button_activated));
        followButton.setText("Unfollow");
    }

    public String getUser_email() {
        return user_email;
    }

    /* Initializing function that sets all fields
     */
    private void init(View view) {
        points = view.findViewById(R.id.points);
        numberOfPosts = view.findViewById(R.id.numberofposts);
        gridView = view.findViewById(R.id.posts);
        followers = view.findViewById(R.id.followers);
        username = view.findViewById(R.id.username);
        followButton = view.findViewById(R.id.followButton);
    }
}