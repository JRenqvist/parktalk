package com.example.parktalk.home;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.parktalk.api.User;
import com.example.parktalk.comments.NavClickListener;
import com.example.parktalk.databinding.LeaderboardItemBinding;

import java.util.List;

/**
 * This is the adapter of the leaderboard's RecyclerView
 */
public class LeaderboardAdapter extends RecyclerView.Adapter<LeaderboardAdapter.LeaderboardHolder> {

    private List<User> leaderboardList;
    private Context context;
    private NavClickListener navClickListener;

    public LeaderboardAdapter(Context context, List<User> leaderboardList, NavClickListener navClickListener) {
        this.context = context;
        this.leaderboardList = leaderboardList;
        this.navClickListener = navClickListener;
    }

    @NonNull
    @Override
    public LeaderboardHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LeaderboardItemBinding binding = LeaderboardItemBinding.inflate(LayoutInflater.from(parent.getContext()));
        return new LeaderboardHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull LeaderboardHolder holder, int position) {
        User user = this.leaderboardList.get(position);

        // Convert points to string from integer
        // and add what position the user has
        String name = position+1 + ". " + user.getUsername();
        String points = "Points: " + user.getPoints();
        holder.leaderboardName.setText(name);
        holder.leaderboardPoints.setText(points);

        // If the user clicks on the name or points, send them to the person's profile
        holder.leaderboardName.setOnClickListener(v -> navClickListener.onUsernameClick(user.getEmail()));
        holder.leaderboardPoints.setOnClickListener(v -> navClickListener.onUsernameClick(user.getEmail()));
    }

    @Override
    public int getItemCount() {
        return leaderboardList.size();
    }

    public class LeaderboardHolder extends RecyclerView.ViewHolder {
        private TextView leaderboardName;
        private TextView leaderboardPoints;
        public LeaderboardHolder(@NonNull LeaderboardItemBinding binding) {
            super(binding.getRoot());
            leaderboardName = binding.leaderboardName;
            leaderboardPoints = binding.leaderboardPoints;
        }
    }

    public void setLeaderboardList(List<User> leaderboardList) {
        this.leaderboardList = leaderboardList;
        notifyDataSetChanged();
    }
}
