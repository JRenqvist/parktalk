package com.example.parktalk.home;

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
import com.example.parktalk.R;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Post;
import com.example.parktalk.api.Token;
import com.example.parktalk.databinding.FragmentFollowingFeedBinding;
import com.example.parktalk.userEmail.UserEmail;

import java.util.ArrayList;
import java.util.List;

/**
 * This fragment will display the following feed. The following feed will be a feed with posts
 * from the people the current user is following
 */
public class FollowingFeedFragment extends Fragment {
    private HomeActivity homeActivity;
    private HomePageAdapter adapter;
    private RecyclerView recyclerView;
    private List<Post> list = new ArrayList<>();
    private APICalls connection;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        homeActivity = (HomeActivity) getActivity();
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_following_feed, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        init(view);

        adapter = new HomePageAdapter(new ArrayList<>(), getContext(), homeActivity);
        recyclerView.setAdapter(adapter);

        // Have to set click listener with findViewById since binding didn't work :(
        view.findViewById(R.id.feed_selector_container).findViewById(R.id.mainFeedButton).setOnClickListener(v -> onMainFeedClick(v));

        // Get data and send request to get following feed
        connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();

        connection.sendRequest(Request.Method.GET, null, token,
                "/feed/get/following/" + email,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully got following post");
                        list.add(responseData.getPost());
                        adapter.setList(list);
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get data: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });

        recyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrolled(@NonNull RecyclerView recyclerView, int dx, int dy) {
                super.onScrolled(recyclerView, dx, dy);

                LinearLayoutManager layoutManager = (LinearLayoutManager) recyclerView.getLayoutManager();
                if (layoutManager != null) {
                    int lastVisibleItemPosition = layoutManager.findLastVisibleItemPosition();
                    int totalItemCount = layoutManager.getItemCount();

                    if (lastVisibleItemPosition == totalItemCount - 1) {
                        // Last item is visible
                        addPostToList(adapter);
                    }
                }
            }
        });

    }

    private void addPostToList(HomePageAdapter adapter) {
        // Make an api call to get a post and add it at the end of the recyclerview
        // Make api call

        String token = Token.getInstance().getToken();
        String email = UserEmail.getInstance().getEmail();
        connection.sendRequest(Request.Method.GET, null, token,
                "feed/get/following/" + email,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully got following post");
                        Post post = responseData.getPost();

                        // Check if we have already added the post to the recyclerview before
                        boolean isPostAlreadyAdded = false;
                        for (Post existingPost : adapter.getList()) {
                            if (existingPost.getPost_id() == post.getPost_id()) {
                                // If we get in here, it means the post is already in the recyclerview
                                // so don't add it
                                isPostAlreadyAdded = true;
                                break;
                            }
                            Log.d("DEBUG", "existing post: " + existingPost.getPost_id());

                        }
                        Log.d("DEBUG", "fetched post: " + post.getPost_id());
                        Log.d("DEBUG", "isPostAlreadyAdded: " + isPostAlreadyAdded);
                        if (!isPostAlreadyAdded) {
                            adapter.addItem(post);
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get feed post: " + errorResponse.getMessage());
                    }
                });
            }


    /* This function will be called when the user clicks the main feed button
     */
    private void onMainFeedClick(View v) {
        Log.v("INFO", "Clicked main feed");
        homeActivity.navigate(FollowingFeedFragmentDirections.actionFollowingFeedFragmentToHomePageFragment());
    }

    private void init(View view) {
        recyclerView = view.findViewById(R.id.followingFeed);
        recyclerView.setHasFixedSize(true);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext());
        linearLayoutManager.setReverseLayout(true);
        linearLayoutManager.setStackFromEnd(true);
        recyclerView.setLayoutManager(linearLayoutManager);
    }

}