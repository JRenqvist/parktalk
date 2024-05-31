package com.example.parktalk.home;

import androidx.appcompat.app.AppCompatActivity;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.NavDirections;
import androidx.navigation.Navigation;
import androidx.navigation.fragment.NavHostFragment;

import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.LinearLayout;

import com.example.parktalk.comments.CommentsFragment;
import com.example.parktalk.comments.CommentsFragmentDirections;
import com.example.parktalk.login.LoginActivity;
import com.example.parktalk.comments.NavClickListener;
import com.example.parktalk.user.PostFragment;
import com.example.parktalk.user.PostFragmentDirections;
import com.example.parktalk.user.PostingFragment;
import com.example.parktalk.userEmail.UserEmail;
import com.example.parktalk.user.PostingFragmentDirections;
import com.example.parktalk.user.ProfileFragment;
import com.example.parktalk.R;
import com.example.parktalk.databinding.ActivityHomeBinding;
import com.example.parktalk.navDrawer.NavDrawer;
import com.example.parktalk.user.ProfileFragmentDirections;

import java.util.Objects;

import de.hdodenhof.circleimageview.CircleImageView;

/**
 * This activity is the home activity that can be reached
 * by pressing "Home" in the navigation drawer.
 * This is where both the feeds will be shown
 */
public class HomeActivity extends AppCompatActivity implements NavClickListener {
    private DrawerLayout dragLeft;
    private CircleImageView userProfileImage;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        com.example.parktalk.databinding.ActivityHomeBinding binding = ActivityHomeBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        dragLeft = findViewById(R.id.drawerLayout);
        ImageView menu = findViewById(R.id.menu);
        LinearLayout home = findViewById(R.id.home);
        LinearLayout logout = findViewById(R.id.logout);
        userProfileImage = findViewById(R.id.image_profile);
        ImageView leaderboardIcon = findViewById(R.id.leaderboardIcon);
        ImageView searchIcon = findViewById(R.id.searchButton);
        Log.i("INFO", "launches home activity");

        // Setting clickListeners on the different View objects
        NavDrawer.setImageViewClickListener(menu, dragLeft);
        NavDrawer.setLinearLayoutClickListener(home, this, HomeActivity.class);
        NavDrawer.setLinearLayoutClickListener(logout, this, LoginActivity.class);

        /* This section of the code will handle the navigation in the main part of the app
         * We will use safeargs to navigate from certain fragments to others. These are:
         *  - Navigate to ProfileFragments needs a safearg of the email to be viewed
         *  - Navigate to PostFragment needs a safearg of the post ID to be viewed
         *  - Navigate to CommentsFragment needs a safearg of the post ID that holds the comments we want to view
         * We don't need to use safeargs for the rest of the fragments.
         * Motivation (as demanded under "Tekniska lösningar - 3. Användning safeargs..." on the course homepage):
         *      Safeargs is really efficient to use when passing data between fragments.
         *      - It has type safety
         *      - Makes for cleaner and more simple code
         *      - Supports refactoring
         *      - Is compatible with Navigation
         */
        // The 3 following click listeners will be global, meaning you can see them in the entire app
        userProfileImage.setOnClickListener(v -> {
            // Check which fragment we are in and navigate accordingly
            NavHostFragment navHostFragment = (NavHostFragment) getSupportFragmentManager().findFragmentById(R.id.homeContainer);
            Fragment currentFragment = navHostFragment.getChildFragmentManager().getFragments().get(0);
            String email = UserEmail.getInstance().getEmail();

            if (currentFragment instanceof HomePageFragment) {
                // Main feed --> Profile
                navigate(HomePageFragmentDirections.actionHomePageFragmentToProfileFragment(email));
                userProfileImage.setImageResource(R.drawable.arrow_upload);
            } else if (currentFragment instanceof FollowingFeedFragment) {
                // Following feed --> Profile
                navigate(FollowingFeedFragmentDirections.actionFollowingFeedFragmentToProfileFragment(email));
                userProfileImage.setImageResource(R.drawable.arrow_upload);
            } else if (currentFragment instanceof ProfileFragment) {
                // If the user is watching their own profile, navigate to Posting
                // Else navigate to user's own profile first
                ProfileFragment profileFragment = (ProfileFragment) currentFragment;
                String currentlyViewingEmail = profileFragment.getUser_email();

                if (Objects.equals(currentlyViewingEmail, email)) {
                    // Profile --> Posting (User is view their own profile)
                    navigate(ProfileFragmentDirections.actionProfileFragmentToPostingFragment());
                    userProfileImage.setImageResource(R.drawable.arrow_back);
                } else {
                    // Profile --> Profile (User is viewing someone else's profile)
                    navigate(ProfileFragmentDirections.actionProfileFragmentSelf(email));
                    userProfileImage.setImageResource(R.drawable.arrow_upload);
                }
            } else if (currentFragment instanceof PostingFragment) {
                // Posting --> Profile
                navigate(PostingFragmentDirections.actionPostingFragmentToProfileFragment(email));
                userProfileImage.setImageResource(R.drawable.arrow_upload);
            } else if (currentFragment instanceof SearchFragment) {
                // Search --> Profile
                navigate(SearchFragmentDirections.actionSearchFragmentToProfileFragment(email));
                userProfileImage.setImageResource(R.drawable.arrow_upload);
            } else if (currentFragment instanceof LeaderboardFragment) {
                // Leaderboard --> Profile
                navigate(LeaderboardFragmentDirections.actionLeaderboardFragmentToProfileFragment(email));
                userProfileImage.setImageResource(R.drawable.arrow_upload);
            } else if (currentFragment instanceof CommentsFragment) {
                // Comments --> Profile
                navigate(CommentsFragmentDirections.actionCommentsFragmentToProfileFragment(email));
                userProfileImage.setImageResource(R.drawable.arrow_upload);
            } else if (currentFragment instanceof PostFragment) {
                // Post --> Profile
                navigate(PostFragmentDirections.actionPostFragmentToProfileFragment(email));
                userProfileImage.setImageResource(R.drawable.arrow_upload);
            }
        });
        leaderboardIcon.setOnClickListener(v -> {
            // Check which fragment we are in and navigate accordingly
            NavHostFragment navHostFragment = (NavHostFragment) getSupportFragmentManager().findFragmentById(R.id.homeContainer);
            Fragment currentFragment = navHostFragment.getChildFragmentManager().getFragments().get(0);

            if (currentFragment instanceof HomePageFragment) {
                // Main feed --> Leaderboard
                navigate(HomePageFragmentDirections.actionHomePageFragmentToLeaderboardFragment());
            } else if (currentFragment instanceof FollowingFeedFragment) {
                // Following feed --> Leaderboard
                navigate(FollowingFeedFragmentDirections.actionFollowingFeedFragmentToLeaderboardFragment());
            } else if (currentFragment instanceof SearchFragment) {
                // Search --> Leaderboard
                navigate(SearchFragmentDirections.actionSearchFragmentToLeaderboardFragment());
            } else if (currentFragment instanceof CommentsFragment) {
                // Comments --> Leaderboard
                navigate(CommentsFragmentDirections.actionCommentsFragmentToLeaderboardFragment());
            } else if (currentFragment instanceof LeaderboardFragment) {
                // Leaderboard --> Leaderboard
                navigate(LeaderboardFragmentDirections.actionLeaderboardFragmentSelf());
            } else if (currentFragment instanceof ProfileFragment) {
                // Profile --> Leaderboard
                navigate(ProfileFragmentDirections.actionProfileFragmentToLeaderboardFragment());
                userProfileImage.setImageResource(R.drawable.back6);
            } else if (currentFragment instanceof  PostingFragment) {
                // Posting --> Leaderboard
                navigate(PostingFragmentDirections.actionPostingFragmentToLeaderboardFragment());
            } else if (currentFragment instanceof PostFragment) {
                // Post --> Leaderboard
                navigate(PostFragmentDirections.actionPostFragmentToLeaderboardFragment());
            }
        });
        searchIcon.setOnClickListener(v -> {
            // Check which fragment we are in and navigate accordingly
            NavHostFragment navHostFragment = (NavHostFragment) getSupportFragmentManager().findFragmentById(R.id.homeContainer);
            Fragment currentFragment = navHostFragment.getChildFragmentManager().getFragments().get(0);

            if (currentFragment instanceof HomePageFragment) {
                // Main feed --> Search
                navigate(HomePageFragmentDirections.actionHomePageFragmentToSearchFragment());
            } else if (currentFragment instanceof FollowingFeedFragment) {
                // Following feed --> Search
                navigate(FollowingFeedFragmentDirections.actionFollowingFeedFragmentToSearchFragment());
            } else if (currentFragment instanceof CommentsFragment) {
                // Comments --> Search
                navigate(CommentsFragmentDirections.actionCommentsFragmentToSearchFragment());
            } else if (currentFragment instanceof SearchFragment) {
                // Search --> Search
                navigate(SearchFragmentDirections.actionSearchFragmentSelf());
            } else if (currentFragment instanceof LeaderboardFragment) {
                // Leaderboard --> Search
                navigate(LeaderboardFragmentDirections.actionLeaderboardFragmentToSearchFragment());
            } else if (currentFragment instanceof ProfileFragment) {
                // Profile --> Search
                navigate(ProfileFragmentDirections.actionProfileFragmentToSearchFragment());
                userProfileImage.setImageResource(R.drawable.back6);
            } else if (currentFragment instanceof PostingFragment) {
                // Posting --> Search
                navigate(PostingFragmentDirections.actionPostingFragmentToSearchFragment());
            } else if (currentFragment instanceof PostFragment) {
                // Post --> Search
                navigate(PostFragmentDirections.actionPostFragmentToSearchFragment());
            }
        });
    }

    @Override
    protected void onPause() {
        super.onPause();
        NavDrawer.closeDrawer(dragLeft);
    }

    public void navigate(NavDirections action) {
        NavController navController = Navigation.findNavController(this, R.id.homeContainer);
        navController.navigate(action);
    }

    @Override
    public void onCommentClick(int postId) {
        // Check which fragment we are in and navigate accordingly
        NavHostFragment navHostFragment = (NavHostFragment) getSupportFragmentManager().findFragmentById(R.id.homeContainer);
        Fragment currentFragment = navHostFragment.getChildFragmentManager().getFragments().get(0);

        if (currentFragment.getClass() == HomePageFragment.class) {
            navigate(HomePageFragmentDirections.actionHomePageFragmentToCommentsFragment(postId));
        } else if (currentFragment.getClass() == FollowingFeedFragment.class) {
            navigate(FollowingFeedFragmentDirections.actionFollowingFeedFragmentToCommentsFragment(postId));
        }
    }

    @Override
    public void onUsernameClick(String userEmail) {
        // Check which fragment we are in and navigate accordingly
        NavHostFragment navHostFragment = (NavHostFragment) getSupportFragmentManager().findFragmentById(R.id.homeContainer);
        Fragment currentFragment = navHostFragment.getChildFragmentManager().getFragments().get(0);
        System.out.println(userEmail);
        if (currentFragment.getClass() == HomePageFragment.class) {
            navigate(HomePageFragmentDirections.actionHomePageFragmentToProfileFragment(userEmail));
        } else if (currentFragment.getClass() == FollowingFeedFragment.class) {
            navigate(FollowingFeedFragmentDirections.actionFollowingFeedFragmentToProfileFragment(userEmail));
        } else if (currentFragment.getClass() == SearchFragment.class) {
            navigate(SearchFragmentDirections.actionSearchFragmentToProfileFragment(userEmail));
        } else if (currentFragment.getClass() == LeaderboardFragment.class) {
            navigate(LeaderboardFragmentDirections.actionLeaderboardFragmentToProfileFragment(userEmail));
        } else if (currentFragment.getClass() == CommentsFragment.class) {
            navigate(CommentsFragmentDirections.actionCommentsFragmentToProfileFragment(userEmail));
        }
    }
}