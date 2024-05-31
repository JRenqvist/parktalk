package com.example.parktalk.user;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Base64;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.GridView;
import android.widget.ImageView;

import com.example.parktalk.R;
import com.example.parktalk.api.Post;

import java.util.List;

/**
 * This is the adapter for the GridView that will show the posts made by the currently viewed user
 */
public class ProfileAdapter extends BaseAdapter {

    private Context context;
    private List<Post> posts;

    public ProfileAdapter(Context context, List<Post> posts) {
        this.context = context;
        this.posts = posts;
    }

    @Override
    public int getCount() {
        return posts.size();
    }

    @Override
    public Object getItem(int position) {
        return posts.get(position);
    }

    @Override
    public long getItemId(int position) {
        return position;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        if (convertView == null) {
            convertView = LayoutInflater.from(context).inflate(R.layout.profile_post_item, parent, false);
        }

        ImageView imageView = convertView.findViewById(R.id.profile_post_image);

        // Decode the base64 string into bitmap
        String base64String = posts.get(position).getImg();
        byte[] decodedBytes = Base64.decode(base64String, Base64.DEFAULT);
        Bitmap bitmap = BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);

        // Set the Bitmap to the ImageView
        imageView.setImageBitmap(bitmap);

        return convertView;
    }

    public void updateData(List<Post> posts) {
        this.posts = posts;
        notifyDataSetChanged();
    }

}
