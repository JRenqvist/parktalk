package com.example.parktalk.user;

import static android.app.Activity.RESULT_OK;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.drawable.BitmapDrawable;
import android.location.Geocoder;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;

import android.provider.MediaStore;
import android.util.Base64;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import com.android.volley.Request;
import com.example.parktalk.home.HomeActivity;
import com.example.parktalk.userEmail.UserEmail;
import com.example.parktalk.api.APICalls;
import com.example.parktalk.api.APIListener;
import com.example.parktalk.api.APIObject;
import com.example.parktalk.api.Token;
import com.example.parktalk.databinding.FragmentPostingBinding;
import com.google.firebase.crashlytics.buildtools.reloc.org.apache.commons.io.output.ByteArrayOutputStream;

import org.json.JSONException;
import org.json.JSONObject;


import java.util.Locale;

/**
 * This fragment will display a posting screen where a user can upload a post
 */
public class PostingFragment extends Fragment {
    private final int REQUEST_CODE = 22;
    private FragmentPostingBinding binding;
    private LocationManager locationManager;
    private LocationListener locationListener;
    private String currentAddress;
    private HomeActivity home;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = FragmentPostingBinding.inflate(getLayoutInflater());
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {

        if (requestCode == REQUEST_CODE && resultCode == RESULT_OK) {
            // Convert the photo to a bitmap
            Bitmap photo = (Bitmap) data.getExtras().get("data");

            // Set the ImageView to the bitmap photo
            binding.imageToPost.setImageBitmap(photo);
            System.out.println("Inside onActivityresult: " + currentAddress);

            // Set the address text
            binding.postAdress.setText(currentAddress);

        }
        else {
            Toast.makeText(getActivity(), "Not able to take picture", Toast.LENGTH_SHORT).show();
            super.onActivityResult(requestCode, resultCode, data);
        }
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        home = (HomeActivity) getActivity();

        setupGPSAndCamera();
        Log.v("INFO", "Current address: " + currentAddress);

        //post the image
        binding.postIMG.setOnClickListener(v -> createPost());

        binding.CancelPost.setOnClickListener(v -> home.navigate(PostingFragmentDirections.actionPostingFragmentToProfileFragment(UserEmail.getInstance().getEmail())));
        // Camera
        binding.takePicture.setOnClickListener(v -> {
            Intent cametaIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            startActivityForResult(cametaIntent, REQUEST_CODE);
        });

        return binding.getRoot();
    }
    public void createPost(){
        // Check user credentials with backend
        APICalls connection = new APICalls(getActivity());

        // Create JSON data
        JSONObject jsonObject = new JSONObject();

        String email = UserEmail.getInstance().getEmail();
        String caption = binding.caption.getText().toString();
        String address = binding.postAdress.getText().toString();

        // Convert a imageView into base64
        BitmapDrawable bitmapDrawable = (BitmapDrawable) binding.imageToPost.getDrawable();

        // If the image we get is null, immediately stop
        if (bitmapDrawable == null) {
            Toast.makeText(getActivity(), "No image attached", Toast.LENGTH_SHORT).show();
            return;
        }

        String picture = getStringImage(bitmapDrawable.getBitmap());
        try {
            jsonObject.put("email", email);
            jsonObject.put("caption", caption);
            jsonObject.put("picture", picture);
            jsonObject.put("address", address);

        } catch (JSONException e) {
            throw new RuntimeException(e);
        }

        connection.sendRequest(Request.Method.POST, jsonObject, Token.getInstance().getToken(),
                "posts/create", new APIListener() {
                    @Override
                    public void onSuccess(APIObject responseData) {
                        Log.v("AUTHORIZED", "Successfully posted");

                        Toast.makeText(getActivity(), "Post success", Toast.LENGTH_SHORT).show();
                        home.navigate(PostingFragmentDirections.actionPostingFragmentToProfileFragment(UserEmail.getInstance().getEmail()));
                    }

                    @Override
                    public void onError(APIObject errorResponse) {
                        Log.e("DENIED", "fail to post");

                        Toast.makeText(getActivity(), errorResponse.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });

    }

    @SuppressLint("MissingPermission")
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        Log.v("INFO", "Gets into onRequest function");
        if(requestCode == REQUEST_CODE){
            if(grantResults.length>0 && grantResults[0] == PackageManager.PERMISSION_GRANTED){
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,0,10,
                        locationListener);
            }
            else{ Toast.makeText(getActivity(), "Location permission is denied, please allow the permission",
                    Toast.LENGTH_SHORT).show();
            }
        }
    }

    public String getStringImage(Bitmap bm){
        ByteArrayOutputStream ba=new ByteArrayOutputStream(  );
        bm.compress( Bitmap.CompressFormat.PNG,90,ba );
        byte[] by=ba.toByteArray();
        String encod= Base64.encodeToString( by,Base64.DEFAULT );
        return encod;
    }

    private void setupGPSAndCamera() {
        // Gps

        locationManager = (LocationManager) getActivity().getSystemService(Context.LOCATION_SERVICE);
        locationListener = location -> {
            Geocoder geocoder = new Geocoder(getActivity(), Locale.getDefault());
            geocoder.getFromLocation(location.getLatitude(), location.getLongitude(), 1,
                    addresses -> {
                        String country = addresses.get(0).getCountryName();
                        String city = addresses.get(0).getLocality();
                        String address = country + ", " + city;
                        Log.v("Address" , "Current address is " + address);
                        currentAddress = address;
                    });};

        if(ContextCompat.checkSelfPermission(
                getActivity(), android.Manifest.permission.ACCESS_FINE_LOCATION)!= PackageManager.PERMISSION_GRANTED) {
            Log.v("INFO", "GPS location not allowed");
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION},22);
        }
        else {
            Log.v("INFO", "GPS location already allowed");
            locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,0,10,
                    locationListener);
        }


    }

}