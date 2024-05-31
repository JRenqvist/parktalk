package com.example.parktalk.comments;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import com.android.volley.Request;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Comment;
import com.example.parktalk.api.Token;
import com.example.parktalk.databinding.FragmentCommentsBinding;
import com.example.parktalk.home.HomeActivity;
import com.example.parktalk.userEmail.UserEmail;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

/**
 * This Fragment will display the comments of a given post
 * @params  postId - A safearg with the id of the post we want to view
 */
public class CommentsFragment extends Fragment {

    private FragmentCommentsBinding binding;
    private RecyclerView commentsRecyclerView;
    private List<Comment> commentList;
    private int argumentPostId;
    private HomeActivity homeActivity;
    private CommentAdapter commentAdapter;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        argumentPostId = getArguments().getInt("postId");
        Log.v("INFO", "Now viewing comments on post with id: " + argumentPostId);


    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        homeActivity = (HomeActivity) getActivity();

        // Inflate the layout for this fragment
        binding = FragmentCommentsBinding.inflate(inflater, container, false);
        return binding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState){
        super.onViewCreated(view, savedInstanceState);

        init();

        commentAdapter = new CommentAdapter(new ArrayList<>(), getContext(), homeActivity);
        commentsRecyclerView.setAdapter(commentAdapter);

        binding.post.setOnClickListener(v -> onPostCommentClick());

        // Make API call to get updated list of comments
        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();

        connection.sendRequest(Request.Method.GET, null, token,
                "/posts/comments/get/" + argumentPostId,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully got comments");
                        commentList = responseData.getComments();
                        commentAdapter.setCommentList(commentList);
                    }

                    @Override
                    public void onError(APIObject errorResponse) {

                    }
                });

    }

    private void onPostCommentClick() {
        Log.v("INFO", "User wants to post a comment");

        String commentText = binding.addComment.getText().toString();
        String email = UserEmail.getInstance().getEmail();
        String token = Token.getInstance().getToken();

        JSONObject jsonObject = new JSONObject();

        try {
            jsonObject.put("email", email);
            jsonObject.put("post_id", argumentPostId);
            jsonObject.put("comment", commentText);
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }

        APICalls connection = new APICalls(getContext());
        connection.sendRequest(Request.Method.POST, jsonObject, token,
                "posts/comments/add",
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("INFO", "Successfully posted comment");
                        Toast.makeText(getContext(), responseData.getMessage(), Toast.LENGTH_SHORT).show();

                        Comment comment = responseData.getComment();
                        addCommentToView(comment);

                        // Set the text to nothing after posting comment
                        binding.addComment.setText("");
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.v("INFO", "Could not post comment: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });

    }

    private void addCommentToView(Comment comment) {
        // Adds a comment to the view
        commentAdapter.addItem(comment);
    }

    private void init() {
        commentsRecyclerView = binding.commentsrecyclerview;
        commentsRecyclerView.setHasFixedSize(true);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext());
        linearLayoutManager.setReverseLayout(true);
        linearLayoutManager.setStackFromEnd(true);
        commentsRecyclerView.setLayoutManager(linearLayoutManager);

    }
}
