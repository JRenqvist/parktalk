package com.example.parktalk.home;

import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;
import android.util.Base64;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.android.volley.Request;
import com.example.parktalk.R;
import com.example.parktalk.comments.NavClickListener;
import com.example.parktalk.userEmail.UserEmail;
import com.example.parktalk.api.APICallback;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Post;
import com.example.parktalk.api.Token;
import com.example.parktalk.databinding.PostItemBinding;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/**
 * The main adapter for both feeds. Organizes and sets data on each object in the
 * RecyclerView that will display posts
 */
public class HomePageAdapter extends RecyclerView.Adapter<HomePageAdapter.HomeHolder> {
    private List<Post> list;
    private final Context context;
    private final NavClickListener navClickListener;
    private final Set<String> deleteButtonVisibleIds;

    public HomePageAdapter(List<Post> list, Context context, NavClickListener navClickListener) {
        this.context = context;
        this.list = list;
        this.navClickListener = navClickListener;
        this.deleteButtonVisibleIds = new HashSet<>();
    }

    @NonNull
    @Override
    public HomeHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        PostItemBinding binding = PostItemBinding.inflate(LayoutInflater.from(parent.getContext()));
        return new HomeHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull HomeHolder holder, int position) {
        Post post = list.get(position);

        // Check if location is null, then set standard string
        if (post.getAddress().isEmpty()) {
            post.setAddress("Location turned off");
        }

        // Set the data of what is displayed in app to data from Post variable
        holder.likeCount.setText(post.getLikes() + " likes");
        holder.comments.setText("View all " + post.getAmount_of_comments() + " comments");
        holder.comments.setOnClickListener(v -> onCommentButtonClick(post.getPost_id()));
        holder.location.setText(post.getAddress());
        holder.caption.setText(post.getCaption());
        holder.username.setText(post.getUsername());
        holder.username.setOnClickListener(v -> onUsernameClick(v, post.getUser_email()));
        holder.like.setOnClickListener(v -> onLikeButtonClick(post.getPost_id(), holder));
        holder.comment.setOnClickListener(v -> onCommentButtonClick(post.getPost_id()));

        // Convert the image Base64 -> Bitmap and display the bitmap
        Bitmap imageBitmap = base64ToBitmap(post.getImg());
        holder.postImage.setImageBitmap(imageBitmap);

        // Call function to check like status on post
        // and set image of like button accordingly
        checkIsPostLiked(post.getPost_id(), new APICallback() {
            @Override
            public void onCallback(boolean response) {
                if (response) {
                    // If we get in here, it means the user is liking the post
                    setLikeImage(holder);
                } else {
                    // If we get in here, it means the user is not liking the post
                    setUnlikeImage(holder);
                }
            }

            @Override
            public void onError(APIObject errorResponse) {
                Log.e("NETWORK", "Could not get like status: " + errorResponse.getMessage());
                Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });

        // Call function to check ownership of post
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
                            holder.deletePost.setVisibility(View.GONE);
                            deleteButtonVisibleIds.remove(postId);

                        } else {
                            holder.deletePost.setVisibility(View.VISIBLE);
                            deleteButtonVisibleIds.add(postId);
                            holder.deletePost.setOnClickListener(v -> onPostDeleteClick(v, postId));
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {

                    }
                });
    }


    /* This function is called when the user clicks the like button
     */
    private void onLikeButtonClick(int postId, HomeHolder holder) {
        checkIsPostLiked(postId, new APICallback() {
            @Override
            public void onCallback(boolean response) {
                if (response) {
                    // If we get in here, it means the user is already liking the post in the backend,
                    // so now we need to unlike the post.
                    // Call functions to unlike the post in the backend and set the image to unliked version
                    unlikePost(postId);
                    setUnlikeImage(holder);
                    // Subtract one from the like counter
                    decreaseLikeNumber(holder);
                } else {
                    // If we get in here, it means the user is not liking the post in the backend,
                    // so now we need to like the post.
                    // Call functions to like the post in backend and set the image to liked version
                    likePost(postId);
                    setLikeImage(holder);
                    // Add one to the like counter
                    increaseLikeNumber(holder);
                }
            }

            @Override
            public void onError(APIObject errorResponse) {
                Log.e("NETWORK", "Could not get liked data: " + errorResponse.getMessage());
                Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    /* This function is called when a user clicks the username in a post
     * This will redirect the user to the posting user's profile page
     */
    private void onUsernameClick(View v, String userEmail) {
        navClickListener.onUsernameClick(userEmail);
    }

    /* This function is called when the user click the comment button
     * This will redirect the user to the comments of that post
     */
    private void onCommentButtonClick(int postId) {
        Log.v("INFO", "Clicked the comments button");
        navClickListener.onCommentClick(postId);
    }
    private Bitmap base64ToBitmap(String img) {
        // Decode the base64 string into bitmap
        byte[] decodedBytes = Base64.decode(img, Base64.DEFAULT);
        return BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
    }

    private void checkIsPostLiked(int postId, APICallback callback) {

        // Get the current users email and token
        String email = UserEmail.getInstance().getEmail();
        String token = Token.getInstance().getToken();

        APICalls connection = new APICalls(context);
        connection.sendRequest(Request.Method.GET, null, token,
                "/posts/ispostliked/" + email + "/" + postId,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        // Check if the user has liked image in database, and call callback function accordingly
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
    private void likePost(int postId) {
        APICalls connection = new APICalls(context);
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("email", email);
            jsonObject.put("post_id", postId);
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
                        Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    /* This function sends a request to unlike the post in the backend
     */
    private void unlikePost(int postId) {
        APICalls connection = new APICalls(context);
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("email", email);
            jsonObject.put("post_id", postId);
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
                        Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    /* This function will set the image of the like button to the "unlike" version
     */
    private void setUnlikeImage(HomeHolder holder) {
        holder.like.setImageResource(R.drawable.ic_like);
    }

    /* This function will set the image of the like button to the "like" version
     */
    private void setLikeImage(HomeHolder holder) {
        holder.like.setImageResource(R.drawable.ic_likedalready);
    }

    /* This function will increase the like count by 1
     */
    private void increaseLikeNumber(HomeHolder holder) {
        int currentLikes = getIntOfLikeCount(holder);
        currentLikes += 1;
        holder.likeCount.setText(currentLikes + " likes");
    }

    /* This function will decrease the like count by 1
     */
    private void decreaseLikeNumber(HomeHolder holder) {
        int currentLikes = getIntOfLikeCount(holder);
        currentLikes -= 1;
        holder.likeCount.setText(currentLikes + " likes");
    }

    /* This function will return the integer part of the like-string of the post
     */
    private int getIntOfLikeCount(HomeHolder holder) {
        String likeString = (String) holder.likeCount.getText();
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

    private void userIsOwnerOfPost(String email, String postId, APICallback callback) {
        String token = Token.getInstance().getToken();
        APICalls connection = new APICalls(context);

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

    private void onPostDeleteClick(View v, String postId) {
        Log.v("INFO", "Clicked delete button");
        APICalls connection = new APICalls(context);

        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        connection.sendRequest(Request.Method.DELETE, null, token,
                "/posts/delete/" + email + "/" + postId,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully deleted post");
                        Toast.makeText(context, responseData.getMessage(), Toast.LENGTH_SHORT).show();
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not delete post: " + errorResponse.getMessage());
                        Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    @Override
    public int getItemCount() {
        return list.size();
    }

    public void setList(List<Post> list) {
        this.list = list;
        if (context instanceof Activity) {
            ((Activity) context).runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    notifyDataSetChanged();
                }
            });
        } else {
            new Handler(Looper.getMainLooper()).post(new Runnable() {
                @Override
                public void run() {
                    notifyDataSetChanged();
                }
            });
        }
    }

    public void addItem(Post post) {
        // This function adds an item to the list
        list.add(post);
        notifyItemInserted(list.size() - 1);
    }

    public List<Post> getList() {
        return list;
    }

    static class HomeHolder extends RecyclerView.ViewHolder {
        private TextView location, likeCount, caption, comments, username;
        private ImageView postImage;
        private ImageButton like, comment, deletePost;

        public HomeHolder(@NonNull PostItemBinding binding) {
            super(binding.getRoot());
            location = binding.location;
            likeCount = binding.likeCount;
            caption = binding.caption;
            comments = binding.comments;
            postImage = binding.postImage;
            like = binding.like;
            comment = binding.comment;
            deletePost = binding.deletePost;
            username = binding.postUsername;
        }
    }

}
