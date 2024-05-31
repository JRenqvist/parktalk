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
import android.widget.EditText;
import android.widget.Toast;

import com.android.volley.Request;
import com.example.parktalk.R;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Token;
import com.example.parktalk.databinding.FragmentSearchBinding;

import java.util.ArrayList;

/**
 * This fragment will display a search bar where the user can search for other users by their username
 */
public class SearchFragment extends Fragment {
    private HomeActivity homeActivity;
    private RecyclerView searchResultRecyclerView;
    private SearchAdapter adapter;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        Log.i("INFO", "Launched search fragment");
        homeActivity = (HomeActivity) getActivity();

        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_search, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState) {
        init(view);

        adapter = new SearchAdapter(new ArrayList<>(), getContext(), homeActivity);
        searchResultRecyclerView.setAdapter(adapter);

        view.findViewById(R.id.searchIcon).setOnClickListener(v -> onExecuteSearch(view));
        view.findViewById(R.id.searchText).setOnClickListener(v -> onExecuteSearch(view));
    }

    private void onExecuteSearch(View v) {
        Log.v("INFO", "Clicked search");
        APICalls connection = new APICalls(getContext());
        String token = Token.getInstance().getToken();
        EditText input = (EditText) v.findViewById(R.id.searchBar);
        String query = input.getText().toString();
        System.out.println(query);

        connection.sendRequest(Request.Method.GET, null, token,
                "/users/search/" + query,
                new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("NETWORK", "Successfully got search data");
                        adapter.setSearchResultList(responseData.getUsers());
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("NETWORK", "Could not get search data: " + errorResponse.getMessage());
                        Toast.makeText(getContext(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
    }

    private void init(View view) {
        searchResultRecyclerView = view.findViewById(R.id.searchResults);
        searchResultRecyclerView.setHasFixedSize(true);
        LinearLayoutManager linearLayoutManager = new LinearLayoutManager(getContext());
        linearLayoutManager.setReverseLayout(true);
        linearLayoutManager.setStackFromEnd(true);
        searchResultRecyclerView.setLayoutManager(linearLayoutManager);
    }

}