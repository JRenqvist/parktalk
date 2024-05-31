package com.example.parktalk.home;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.parktalk.api.User;
import com.example.parktalk.comments.NavClickListener;
import com.example.parktalk.databinding.SearchItemBinding;

import java.util.List;

/**
 * This is the adapter for the RecyclerView of users we get from searching for users
 */
public class SearchAdapter extends RecyclerView.Adapter<SearchAdapter.SearchHolder> {
    private List<User> searchResultList;
    private Context context;
    private NavClickListener navClickListener;

    public SearchAdapter(List<User> searchResultList, Context context, NavClickListener navClickListener) {
        this.searchResultList = searchResultList;
        this.context = context;
        this.navClickListener = navClickListener;
    }

    @NonNull
    @Override
    public SearchHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        SearchItemBinding binding = SearchItemBinding.inflate(LayoutInflater.from(parent.getContext()));
        return new SearchHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull SearchHolder holder, int position) {
        User user = this.searchResultList.get(position);

        holder.username.setText(user.getUsername());
        holder.username.setOnClickListener(v -> navClickListener.onUsernameClick(user.getEmail()));
        holder.profilePicture.setOnClickListener(v -> navClickListener.onUsernameClick(user.getEmail()));
    }

    @Override
    public int getItemCount() {
        return searchResultList.size();
    }

    public class SearchHolder extends RecyclerView.ViewHolder {
        private TextView username;
        private ImageView profilePicture;

        public SearchHolder(@NonNull SearchItemBinding binding) {
            super(binding.getRoot());
            this.username = binding.searchResultUsername;
            this.profilePicture = binding.searchResultProfilePicture;
        }
    }

    public void setSearchResultList(List<User> searchResultList) {
        this.searchResultList = searchResultList;
        notifyDataSetChanged();
    }
}
