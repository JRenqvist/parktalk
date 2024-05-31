import requests, base64, random

local = "http://127.0.0.1:5000"
azure = ""
url = local
token = ""
emails = [
        "anders.johnsson@example.se",
        "karin.larsson@example.se",
        "lars.pettersson@example.se",
        "eva.karlsson@example.se",
        "oskar.bengtsson@example.se",
        "anna.svensson@example.se",
        "fredrik.olsson@example.se",
        "emilia.johansson@example.se",
        "gustav.andersson@example.se",
        "sofie.lindberg@example.se",
        "mikael.nilsson@example.se",
        "hanna.holm@example.se",
        "elisabeth.wikstrom@example.se",
        "matilda.vikander@example.se",
        "jonas.gustafsson@example.se",
        "elin.kjellberg@example.se",
        "simon.rosenberg@example.se",
        "linnea.magnusson@example.se",
        "christian.forsberg@example.se",
        "sara.tollberg@example.se",
        "henrik.stromberg@example.se",
        "mia.nilsson@example.se",
        "julia.berglund@example.se",
        "robin.holmgren@example.se",
        "tilda.ekstrom@example.se",
        "isak.rydberg@example.se",
        "agnes.palmgren@example.se",
        "lucas.ostberg@example.se",
        "rebecca.falk@example.se",
        "sebastian.carlsson@example.se",
    ]

def create_users():
    """ This function creates 30 users and adds them to the database. """
    global token
    dictionary = {
        "anders_j": "anders.johnsson@example.se",
        "karin_l": "karin.larsson@example.se",
        "lars_p": "lars.pettersson@example.se",
        "eva_k": "eva.karlsson@example.se",
        "oskar_b": "oskar.bengtsson@example.se",
        "anna_s": "anna.svensson@example.se",
        "fredrik_o": "fredrik.olsson@example.se",
        "emilia_j": "emilia.johansson@example.se",
        "gustav_a": "gustav.andersson@example.se",
        "sofie_l": "sofie.lindberg@example.se",
        "mikael_n": "mikael.nilsson@example.se",
        "hanna_h": "hanna.holm@example.se",
        "elisabeth_w": "elisabeth.wikstrom@example.se",
        "matilda_v": "matilda.vikander@example.se",
        "jonas_g": "jonas.gustafsson@example.se",
        "elin_k": "elin.kjellberg@example.se",
        "simon_r": "simon.rosenberg@example.se",
        "linnea_m": "linnea.magnusson@example.se",
        "christian_f": "christian.forsberg@example.se",
        "sara_t": "sara.tollberg@example.se",
        "henrik_s": "henrik.stromberg@example.se",
        "mia_n": "mia.nilsson@example.se",
        "julia_b": "julia.berglund@example.se",
        "robin_h": "robin.holmgren@example.se",
        "tilda_e": "tilda.ekstrom@example.se",
        "isak_r": "isak.rydberg@example.se",
        "agnes_p": "agnes.palmgren@example.se",
        "lucas_o": "lucas.ostberg@example.se",
        "rebecca_f": "rebecca.falk@example.se",
        "sebastian_c": "sebastian.carlsson@example.se",
    }

    for num, (username, email) in enumerate(dictionary.items()):
        requests.post(url+"/users/create",
                      json={"username": username, 
                            "email": email,
                            "password": "pass123"})
        print("Created user number " + str(num))
    
    # Lastly, create one valid token to use for authentication
    x = requests.post(url+"/users/login",
                      json={"email": "anders.johnsson@example.se",
                            "password": "pass123"})
    token = x.json()["token"]

    print("--- Successfully created all users ---")


def create_posts():
    """ This function creates 50 posts and adds them to the database. """
    global emails

    captions = ["Vad betyder detta?",
                "Fattar inte nedersta skylten",
                "Vadå SMS???",
                "Måste jag ha någon p-skiva här?",
                "Hur länge får jag stå här om det är lördag"]

    # For now, upload same image. Might want to make it unique in the future.
    with open("testImages/7.jpg", "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    
    for num in range(50):
        email = emails[random.randint(0, 29)]
        caption = captions[random.randint(0, 4)]
        x = requests.post(url+"/posts/create",
                          json={"email": email,
                                "caption": caption,
                                "address": "Sverige, Linköping",
                                "picture": base64_image}, 
                          headers={"Authorization": "Bearer " + token})
        print("Created post number " + str(num))
    
    print("--- Successfully created all posts ---")



def create_comments():
    """ This function creates 70 comments and adds them to the database. """
    global emails

    comments = ["Du får stå där alla dagar men 9-19 vardagar och 9-17 dag före röd dag är det avgift",
                "Nedersta skylten betyder att det är parkeringsförbud jämna dagar 0-8",
                "Tror att mellersta skylten betyder att det är en miljözon och att vissa fordon får stå där",
                "Du måste inte ha någon p-skiva här. Istället måste du ha parkeringslapp från automat eller easypark elr liknande",
                ]
    
    for num in range(70):
        email = emails[random.randint(0, 29)]
        post_id = random.randint(1, 30)
        comment = comments[random.randint(0, 3)]
        x = requests.post(url+"/posts/comments/add",
                          json={"email": email,
                                "post_id": post_id,
                                "comment": comment}, 
                          headers={"Authorization": "Bearer " + token})
        print("Created comment number " + str(num))


def like_posts():
    """ This function iterates through all users and posts and likes 50% of them randomly. """
    
    for email in emails:
        for post_id in range(1, 51):
            if random.randint(0, 1) == 0:
                x = requests.post(url+"/posts/like",
                                json={"email": email,
                                        "post_id": post_id}, 
                                headers={"Authorization": "Bearer " + token})
                print("Liked post number " + str(post_id) + " by user " + str(email))


def like_comments():
    """ This function iterates through all comments and likes 50% of them randomly. """
    
    for email in emails:
        for comment_id in range(1, 71):
            if random.randint(0, 1) == 0:
                x = requests.post(url+"/posts/comments/like",
                                json={"email": email,
                                      "comment_id": comment_id}, 
                                headers={"Authorization": "Bearer " + token})
                print("Liked comment number " + str(comment_id) + " by user " + str(email))


if __name__ == '__main__':

    # Initialize the data
    create_users()
    create_posts()
    create_comments()
    
    # Like posts and comments
    like_posts()
    like_comments()
