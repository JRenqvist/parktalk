package com.example.parktalk.comments;

import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.PixelCopy;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.android.volley.Request;
import com.example.parktalk.R;
import com.example.parktalk.api.APICallback;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.Comment;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Token;
import com.example.parktalk.databinding.CommentItemBinding;
import com.example.parktalk.home.HomeActivity;
import com.example.parktalk.userEmail.UserEmail;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.List;
import java.util.Objects;

/**
 * This is the adapter used for the RecyclerView that displays the comments
 * of a post
 */
public class CommentAdapter extends RecyclerView.Adapter<CommentAdapter.CommentHolder> {

    private List<Comment> commentList;
    private final Context context;
    private APICalls connection;
    private final NavClickListener navClickListener;

    public CommentAdapter(List<Comment> commentList, Context context, NavClickListener navClickListener) {
        this.commentList = commentList;
        this.context = context;
        this.navClickListener = navClickListener;
    }

    @NonNull
    @Override
    public CommentHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        CommentItemBinding binding = CommentItemBinding.inflate(LayoutInflater.from(parent.getContext()));
        this.connection = new APICalls(parent.getContext());

        return new CommentHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull CommentHolder holder, int position) {
        Comment comment = commentList.get(position);

        holder.commentText.setText(comment.getComment_string());
        holder.commentUsername.setText(comment.getUsername());
        holder.commentUsername.setOnClickListener(v -> onUserClick(comment.getUser_email()));
        holder.commentProfilePicture.setOnClickListener(v -> onUserClick(comment.getUser_email()));
        holder.commentText.setOnClickListener(v -> onUserClick(comment.getUser_email()));
        holder.commentLikes.setText(comment.getLikes() + " likes");
        holder.commentLikeButton.setOnClickListener(v -> onCommentLikeClick(comment.getComment_id(), holder));

        // For the delete button, if the logged in user is not the owner of the comment,
        // then don't show the delete button
        String email = UserEmail.getInstance().getEmail();
        String commentId = Integer.toString(comment.getComment_id());
        userIsOwnerOfComment(email, commentId, new APICallback() {
            @Override
            public void onCallback(boolean response) {
                if (!response) {
                    // If we get in here, it means the user is NOT the owner of the comment
                    // If-statement to make sure delete button is not already removed.
                    // When a user posts a comment, we update the list and so these views will already be gone
                    if ((LinearLayout) holder.commentDeleteButton.getParent() != null) {
                        // Remove the delete button from the view
                        ((LinearLayout) holder.commentDeleteButton.getParent()).removeView(holder.commentDeleteButton);
                    }

                } else {
                    // If we get in here, it means the user IS the owner of the comment
                    // Set click listener
                    holder.commentDeleteButton.setOnClickListener(v -> onCommentDeleteClick(v, comment));
                }
            }

            @Override
            public void onError(APIObject errorResponse) {
                Log.e("NETWORK", "Could not get data: " + errorResponse.getMessage());
            }
        });

        // Set the like button status to same as backend
        checkIsCommentLiked(comment.getComment_id(),
                new APICallback() {
                    @Override
                    public void onCallback(boolean response) {
                        if (response) {
                            // If we get in here, it means the user is liking the comment
                            // Set like button
                            setLikeImage(holder);
                        } else {
                            // If we get in here, it meas the user is not liking the comment
                            // Set unlike button
                            setUnlikeImage(holder);
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get like status on comment: " + errorResponse.getMessage());
                    }
                });


    }

    private void onUserClick(String userEmail) {
        navClickListener.onUsernameClick(userEmail);
    }

    private void onCommentLikeClick(int commentId, CommentHolder holder) {
        Log.v("INFO", "Clicked like button");
        // Check if the comment is liked already
        checkIsCommentLiked(commentId, new APICallback() {
            @Override
            public void onCallback(boolean response) {
                if (response) {
                    // If we get in here, it means the user is liking the comment
                    // Since we clicked the like button, now unlike the comment
                    unlikeComment(commentId);
                    setUnlikeImage(holder);
                    // Subtract one from the like counter
                    decreaseLikeNumber(holder);
                } else {
                    // If we get in here, it means the user is not liking the comment
                    // Since we clicked the like button, now like the comment
                    likeComment(commentId);
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

    private void likeComment(int commentId) {
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("email", email);
            jsonObject.put("comment_id", commentId);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }
        connection.sendRequest(Request.Method.POST, jsonObject, token,
                "posts/comments/like",
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully liked comment in backend");
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not like comment: " + errorResponse.getMessage());
                        Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private void unlikeComment(int commentId) {
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("email", email);
            jsonObject.put("comment_id", commentId);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }
        connection.sendRequest(Request.Method.POST, jsonObject, token,
                "posts/comments/unlike",
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully unliked comment in backend");
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not like comment: " + errorResponse.getMessage());
                        Toast.makeText(context, errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private void setLikeImage(CommentHolder holder) {
        holder.commentLikeButton.setImageResource(R.drawable.ic_likedalready);
    }

    private void setUnlikeImage(CommentHolder holder) {
        holder.commentLikeButton.setImageResource(R.drawable.ic_like);
    }

    private void increaseLikeNumber(CommentHolder holder) {
        int currentLikes = getIntOfLikeCount(holder);
        currentLikes += 1;
        holder.commentLikes.setText(currentLikes + " likes");
    }

    private void decreaseLikeNumber(CommentHolder holder) {
        int currentLikes = getIntOfLikeCount(holder);
        currentLikes -= 1;
        holder.commentLikes.setText(currentLikes + " likes");
    }

    private int getIntOfLikeCount(CommentHolder holder) {
        String likeString = (String) holder.commentLikes.getText();
        StringBuilder resultString = new StringBuilder();
        // For every character in the string, if digit -> append to resultString, else break
        for (int i = 0; i < likeString.length(); i++) {
            boolean flag = Character.isDigit(likeString.charAt(i));
            if (flag) {
                resultString.append(likeString.charAt(i));
            } else {
                // Break since there will not be bat more digits in the string
                break;
            }
        }
        // Return the resulting string as an integer
        return Integer.parseInt(resultString.toString());
    }

    private void onCommentDeleteClick(View v, Comment comment) {
        Log.v("INFO", "Clicked delete button");

        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        connection.sendRequest(Request.Method.DELETE, null, token,
                "/posts/comments/delete/" + email + "/" + comment.getComment_id(),
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully deleted comment");
                        Toast.makeText(v.getContext(), responseData.getMessage(), Toast.LENGTH_SHORT).show();
                        removeItem(comment);
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not delete post: " + errorResponse.getMessage());
                        Toast.makeText(v.getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });

    }

    private void checkIsCommentLiked(int commentId, APICallback callback) {
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();
        connection.sendRequest(Request.Method.GET, null, token,
                "posts/iscommentliked/" + email + "/" + commentId,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        String alreadyLikeMessage = "User has already liked this comment";
                        String notLikeMessage = "User hasn't liked this comment";
                        if (Objects.equals(responseData.getMessage(), alreadyLikeMessage)) {
                            // If we get in here, it means the user is liking the comment
                            callback.onCallback(true);
                        } else if (Objects.equals(responseData.getMessage(), notLikeMessage)) {
                            // If we get in here, it means the user is not liking the comment
                            callback.onCallback(false);
                        } else {
                            // If we get in here, it means the comparison strings are not correct
                            Log.e("NETWORK", "Comparison strings are not equal: " + responseData.getMessage());
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

    private void userIsOwnerOfComment(String email, String commentId, APICallback callback) {
        String token = Token.getInstance().getToken();
        connection.sendRequest(Request.Method.GET, null, token,
                "/posts/comments/isuserowner/" + email + "/" + commentId,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        if (Objects.equals(responseData.getMessage(), "true")) {
                            // If we get in here, it means the user IS the owner
                            callback.onCallback(true);
                        } else if (Objects.equals(responseData.getMessage(), "false")) {
                            // If we get in here, it means the user is NOT the owner
                            callback.onCallback(false);
                        } else {
                            // If we get in here, it means the comparison strings are not equal
                            Log.e("NETWORK", "Comparison strings are not equal: " + responseData.getMessage());
                            throw new RuntimeException();
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get comment ownership status: " + errorResponse.getMessage());
                        callback.onError(errorResponse);
                    }
                });
    }

    @Override
    public int getItemCount() {
        return commentList.size();
    }

    public void setCommentList(List<Comment> commentList) {
        this.commentList = commentList;
        notifyDataSetChanged();
    }

    public void addItem(Comment comment) {
        this.commentList.add(comment);
        notifyDataSetChanged();
    }

    public void removeItem(Comment comment) {
        this.commentList.remove(comment);
        notifyDataSetChanged();
    }

    public class CommentHolder extends RecyclerView.ViewHolder{
        private TextView commentText, commentUsername, commentLikes;
        private ImageButton commentLikeButton, commentDeleteButton;
        private ImageView commentProfilePicture;
        public CommentHolder(@NonNull CommentItemBinding binding) {
            super(binding.getRoot());
            commentText = binding.commentText;
            commentLikeButton = binding.commentLikeButton;
            commentDeleteButton = binding.commentDeleteButton;
            commentUsername = binding.commentUsername;
            commentLikes = binding.commentLikes;
            commentProfilePicture = binding.commentProfilePicture;

        }
    }


}
