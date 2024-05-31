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
import com.example.parktalk.api.Token;
import com.example.parktalk.api.User;
import com.example.parktalk.databinding.FragmentLeaderboardBinding;

import java.util.ArrayList;
import java.util.List;

/**
 * This fragment will display a list of the 10 users with the highest points in the app
 */
public class LeaderboardFragment extends Fragment {

    private FragmentLeaderboardBinding binding;
    private RecyclerView recyclerView;
    private LeaderboardAdapter adapter;
    private HomeActivity homeActivity;
    private List<User> list;


    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = FragmentLeaderboardBinding.inflate(getLayoutInflater());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        homeActivity = (HomeActivity) getActivity();
        Log.i("INFO", "Launched leaderboard fragment");

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_leaderboard, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState) {
        init(view);

        LeaderboardAdapter adapter = new LeaderboardAdapter(getContext(), new ArrayList<>(), homeActivity);
        recyclerView.setAdapter(adapter);

        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();

        connection.sendRequest(Request.Method.GET, null, token,
                "/users/get/leaderboard", new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        list = responseData.getUsers();
                        adapter.setLeaderboardList(list);
                        Log.i("NETWORK", "Successfully got leaderboard data");
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Toast.makeText(getContext(), "Could not get data", Toast.LENGTH_SHORT).show();
                        Log.e("NETWORK", "Could not get data: " + errorResponse.getMessage());
                    }
                });



    }

    private void init(View view) {
        recyclerView = view.findViewById(R.id.leaderboard);
        recyclerView.setHasFixedSize(true);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext());
        linearLayoutManager.setReverseLayout(true);
        linearLayoutManager.setStackFromEnd(true);
        recyclerView.setLayoutManager(linearLayoutManager);
    }
}