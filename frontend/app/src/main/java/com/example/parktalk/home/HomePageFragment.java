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
import com.example.parktalk.databinding.FragmentHomePageBinding;

import java.util.ArrayList;
import java.util.List;

/**
 * This fragment will display the main feed. The main feed is a feed of random posts posted by anyone
 * on the app
 */
public class HomePageFragment extends Fragment {
    private RecyclerView recyclerView;
    private HomePageAdapter homePageAdapter;
    private HomeActivity homeActivity;
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
        return inflater.inflate(R.layout.fragment_home_page, container, false);

    }
    @Override
    public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState){
        super.onViewCreated(view, savedInstanceState);

        init(view);

        homePageAdapter = new HomePageAdapter(new ArrayList<>(), getContext(), homeActivity);
        recyclerView.setAdapter(homePageAdapter);

        // Have to set click listener with findViewById since binding didn't work :(
        view.findViewById(R.id.feed_selector_container).findViewById(R.id.followingFeedButton).setOnClickListener(v -> onFollowingFeedClick(v));

        // Get data and send request to main feed
        connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();

        // Send request to get initial post
        connection.sendRequest(Request.Method.GET, null, token,
                "feed/get", new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully got feed post");
                        System.out.println(responseData.getPost());
                        list.add(responseData.getPost());
                        homePageAdapter.setList(list);
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                        Log.e("NETWORK", "Could not get data: " + errorResponse.getMessage());
                    }
                });

        // Add scroll listener that detects if we have scrolled to the end, if so:
        // send another request to get another post
        recyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrolled(RecyclerView recyclerView, int dx, int dy) {
                super.onScrolled(recyclerView, dx, dy);

                LinearLayoutManager layoutManager = (LinearLayoutManager) recyclerView.getLayoutManager();
                if (layoutManager != null) {
                    int lastVisibleItemPosition = layoutManager.findLastVisibleItemPosition();
                    int totalItemCount = layoutManager.getItemCount();

                    if (lastVisibleItemPosition == totalItemCount - 1) {
                        // Last item is visible
                        addPostToList(homePageAdapter);
                    }
                }
            }
        });

    }

    private void addPostToList(HomePageAdapter adapter) {
        // Make an api call to get a post and add it at the end of the recyclerview
        // Make api call

        String token = Token.getInstance().getToken();
        connection.sendRequest(Request.Method.GET, null, token,
                "feed/get",
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully got feed post");
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
                        }

                        if (!isPostAlreadyAdded) {
                            adapter.addItem(post);
                        }
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get feed post: " + errorResponse.getMessage());
                        Toast.makeText(homeActivity, "Could not get feed post. Please try again.", Toast.LENGTH_SHORT).show();
                    }
                });


    }

    private void onFollowingFeedClick(View v) {
        Log.v("INFO", "Clicked following feed");
        homeActivity.navigate(HomePageFragmentDirections.actionHomePageFragmentToFollowingFeedFragment());
    }

    // init function
    private void init(View view) {
        recyclerView = view.findViewById(R.id.postView);
        recyclerView.setHasFixedSize(true);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext());
        linearLayoutManager.setReverseLayout(true);
        linearLayoutManager.setStackFromEnd(true);
        recyclerView.setLayoutManager(linearLayoutManager);

    }
}