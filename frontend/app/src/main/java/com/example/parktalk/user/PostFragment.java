package com.example.parktalk.user;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.util.Base64;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.example.parktalk.R;
import com.example.parktalk.home.HomeActivity;
import com.example.parktalk.userEmail.UserEmail;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Post;
import com.example.parktalk.api.Token;
import com.example.parktalk.api.APICallback;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Objects;

/**
 * This fragment will display a single post
 */
public class PostFragment extends Fragment {

    private TextView location, likeCount, comments, caption, username;
    private ImageButton like, comment, deletePost;
    private ImageView post_image;
    private int argument_post_id;
    private HomeActivity home;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        argument_post_id = getArguments().getInt("post_id");
        Log.v("INFO", "User requested post id: " + argument_post_id);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        home = (HomeActivity) getActivity();
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_post, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        init(view);

        // Make an api call to fetch the post data
        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();

        connection.sendRequest(Request.Method.GET, null, token,
                "posts/get/" + argument_post_id,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {

                        // Assign all variables to data we got from api call
                        Post post = responseData.getPost();
                        location.setText(post.getAddress());
                        likeCount.setText(post.getLikes() + " likes");
                        comments.setText("View all " + post.getAmount_of_comments() + " comments");
                        caption.setText(post.getCaption());
                        username.setText(post.getUsername());
                        username.setOnClickListener(v -> clickedUsername(v, post.getUser_email()));
                        like.setOnClickListener(v -> clickedLike(v));
                        comment.setOnClickListener(v -> clickedComments(v));
                        post_image.setImageBitmap(base64ToBitmap(post.getImg()));

                        // Call function to check like status on post
                        // and set image of like button accordingly
                        checkIsLiked(new APICallback() {
                            @Override
                            public void onCallback(boolean response) {
                                if (response) {
                                    // If we get in here, it means the user is liking the post
                                    setLikeImage();
                                } else {
                                    // If we get in here, it means the user is not liking the post
                                    setUnlikeImage();
                                }
                            }

                            @Override
                            public void onError(APIObject errorResponse) {
                                Log.e("NETWORK", "Could not get like status: " + errorResponse.getMessage());
                                Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                            }
                        });

                        // Call function to check ownership status on post
                        // If user is not owner, then hide the delete button
                        String email = UserEmail.getInstance().getEmail();
                        String postId = Integer.toString(post.getPost_id());
                        userIsOwnerOfPost(email, postId,
                                new APICallback() {
                                    @Override
                                    public void onCallback(boolean response) {
                                        if (!response) {
                                            // If we get in here, it means the user is NOT the owner of the post
                                            // Remove the delete button from the view
                                            ((RelativeLayout) deletePost.getParent()).removeView(deletePost);
                                        } else {
                                            // If we get in here, it means the user IS the owner of the post
                                            // Set click listener
                                            deletePost.setOnClickListener(v -> onPostDeleteClick(v));
                                        }
                                    }

                                    @Override
                                    public void onError(APIObject errorResponse) {

                                    }
                                });


                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get posts: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });

    }

    /* This function is called when a user clicks the username in the post
     * This will redirect the user to the posting user's profile page
     */
    private void clickedUsername(View v, String userEmail) {
        home.navigate(PostFragmentDirections.actionPostFragmentToProfileFragment(userEmail));
    }

    /* This function is called when a user clicks the like button
     * Check with backend to see if post is liked by user or not
     * Then send appropriate like/unlike request
     */
    private void clickedLike(View v) {

        // First, check if
        checkIsLiked(new APICallback() {
            @Override
            public void onCallback(boolean response) {
                if (response) {
                    // If we get into here, it means the user has already liked the post before
                    // so we need to mark it as unliked
                    // Make api call to unlike in backend
                    unlikePost();
                    // Update image to "unlike" version
                    setUnlikeImage();
                    // Subtract one from the like counter
                    decreaseLikeNumber();
                } else {
                    // If we get into here, it means the user has not liked the post before
                    // so we need to mark it as liked
                    // Make api call the like in backend
                    likePost();
                    // Update image to "like" version
                    setLikeImage();
                    // Add one to the like counter
                    increaseLikeNumber();
                }
            }

            @Override
            public void onError(APIObject errorResponse) {
                Log.e("NETWORK", "Could not get liked data: " + errorResponse.getMessage());
                Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void checkIsLiked(APICallback callback) {
        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();


        connection.sendRequest(Request.Method.GET, null, token,
                "/posts/ispostliked/" + email + "/" + argument_post_id,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        String alreadyLikeMessage = "User has already liked this post";
                        String notLikeMessage = "User hasn't liked this post";
                        if (responseData.getMessage().equals(alreadyLikeMessage)) {
                            callback.onCallback(true);
                        } else if (responseData.getMessage().equals(notLikeMessage)) {
                            callback.onCallback(false);
                        } else {
                            Log.e("ERROR", "Comparison strings are not equal to the response data");
                            throw new RuntimeException();
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get response data: " + errorResponse.getMessage());
                        callback.onError(errorResponse);
                    }
                });
    }

    /* This function sends a request to like the post in the backend
     */
    private void likePost() {
        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("email", email);
            jsonObject.put("post_id", argument_post_id);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }

        connection.sendRequest(Request.Method.POST, jsonObject, token,
                "/posts/like",
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully liked post in backend");
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not like post: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    /* This function sends a request to unlike the post in the backend
     */
    private void unlikePost() {
        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("email", email);
            jsonObject.put("post_id", argument_post_id);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }

        connection.sendRequest(Request.Method.POST, jsonObject, token,
                "/posts/unlike",
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully unliked post in backend");
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not unlike post: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    /* This function will set the image of the like button to the "unlike" version
     */
    private void setUnlikeImage() {
        like.setImageResource(R.drawable.ic_like);
    }

    /* This function will set the image of the like button to the "like" version
     */
    private void setLikeImage() {
        like.setImageResource(R.drawable.ic_likedalready);
    }

    private void increaseLikeNumber() {
        int currentLikes = getIntOfLikeCount();
        currentLikes += 1;
        likeCount.setText(currentLikes + " likes");
    }

    private void decreaseLikeNumber() {
        int currentLikes = getIntOfLikeCount();
        currentLikes -= 1;
        likeCount.setText(currentLikes + " likes");
    }

    /* This function will return the integer part of the like-string of the post
     */
    private int getIntOfLikeCount() {
        String likeString = (String) likeCount.getText();
        StringBuilder resultString = new StringBuilder();
        // For every character in the string, if digit -> append to resultString, else break
        for (int i = 0; i < likeString.length(); i++) {
            boolean flag = Character.isDigit(likeString.charAt(i));
            if (flag) {
                resultString.append(likeString.charAt(i));
            } else {
                // Break since there will not be any more digits in the string
                break;
            }
        }
        // Return the resulting string as an integer
        return Integer.parseInt(resultString.toString());
    }

    private void clickedComments(View v) {
        Log.v("INFO", "Clicked the comments button");
        home.navigate(PostFragmentDirections.actionPostFragmentToCommentsFragment(argument_post_id));
    }

    private Bitmap base64ToBitmap(String img) {
        // Decode the base64 string into bitmap
        byte[] decodedBytes = Base64.decode(img, Base64.DEFAULT);
        return BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
    }

    private void onPostDeleteClick(View v) {
        Log.v("INFO", "Clicked delete button");
        APICalls connection = new APICalls(getContext());

        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();
        String postId = Integer.toString(argument_post_id);

        connection.sendRequest(Request.Method.DELETE, null, token,
                "/posts/delete/" + email + "/" + postId,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully deleted post");
                        Toast.makeText(getContext(), responseData.getMessage(), Toast.LENGTH_SHORT).show();
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not delete post: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private void userIsOwnerOfPost(String email, String postId, APICallback callback) {
        String token = Token.getInstance().getToken();
        APICalls connection = new APICalls(getContext());

        connection.sendRequest(Request.Method.GET, null, token,
                "/posts/isuserowner/" + email + "/" + postId,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        if (Objects.equals(responseData.getMessage(), "true")) {
                            // If we get in here, it means the user IS the owner of the post
                            callback.onCallback(true);
                        } else if (Objects.equals(responseData.getMessage(), "false")) {
                            // If we get in here, it means the user is NOT the owner of the post
                            callback.onCallback(false);
                        } else {
                            Log.e("NETWORK", "Comparison strings are not equal: " + responseData.getMessage());
                            throw new RuntimeException();
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get post ownership status: " + errorResponse.getMessage());
                        callback.onError(errorResponse);
                    }
                });
    }

    /* Initializing function of fields
     */
    private void init(View view) {
        location = view.findViewById(R.id.location);
        post_image = view.findViewById(R.id.post_image);
        like = view.findViewById(R.id.like);
        comment = view.findViewById(R.id.comment);
        likeCount = view.findViewById(R.id.likeCount);
        caption = view.findViewById(R.id.caption);
        comments = view.findViewById(R.id.comments);
        deletePost = view.findViewById(R.id.deletePost);
        username = view.findViewById(R.id.postUsername);

    }
}