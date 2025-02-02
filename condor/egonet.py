# Get egonet of a user and write it into a Gephi file
# The egonet is made of all its neighbours and the edges between neighbours (followers or followees)
# author: Alberto Lumbreras
###########################################################################
import argparse
import csv
import os
import time
import tweepy
import yaml
from tweepy import TweepError
from xml.sax.saxutils import escape
from utils.utils import screen_names, api_neighbours_ids, fetch_neighbours, make_adjacency_matrix
from config import PATHS

# Read keys from file that contains
# CONSUMER_KEY: 6it3IkPFI4RNIGhIci1w
# CONSUMER_SECRET: zGUE1bTucHcNn5IxFNyBP8dN2EvbrMtij5xuWHqcW0
with open('config.yml', 'r') as f:
    doc = yaml.load(f, Loader=yaml.FullLoader)
    CONSUMER_KEY = doc["CONSUMER_KEY"]
    CONSUMER_SECRET = doc["CONSUMER_SECRET"]

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_delay=60)


def ego_neighbourhood(ego_screenname, direction = "in", force = False):
    """ Get the neighbours of ego and the neighbours of its neighbours
        Store everyting in files
    """
    ego = api.get_user(ego_screenname).id
    neighbours = api_neighbours_ids(ego, api, direction= direction)
    # Include self in generated graph
    neighbours.append(ego)

    # Fetch neighbours of each ego neighbour
    for i, userid in enumerate(neighbours):
        print("Processed:" + str(i) + "/" + str(len(neighbours)))
        print("User: ", str(userid))
        n = fetch_neighbours(userid, api, direction = direction, force = force)
        print("neighbours: ", n)

    # Fetch screen names
    screen_names(neighbours, api)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", required=True, help="Screen name of twitter user")
    parser.add_argument("-f", "--function", required=True, help="Function to execute",
                        choices=['followers', 'followees', 'followers_graph', 'followees_graph'])
    parser.add_argument("--force", type=bool, required=False, help="Forces re-fetching of users")

    args = vars(parser.parse_args())
    user = args['user']
    function = args['function']
    force = args['force']

    while(True): 
        try:
            if function == 'followers':
                ego_neighbourhood(user, direction = "in", force = force)
            if function == 'followees':
                ego_neighbourhood(user, direction = "out", force = force)
            break
        except TweepError as e:
            print(e)
            time.sleep(60)

    if function == 'followers_graph':
        # Set up users to include in the graph (ego and neighbours)
        ego = api.get_user(user).id   
        with open(os.path.join(PATHS['in'], str(ego)), 'r') as f:
            ego_neighbours = [int(id) for line in csv.reader(f) for id in line]
        make_adjacency_matrix(ego_neighbours, direction = "in", file= user + '_in.csv')

    if function == 'followees_graph':    
        #graph_ego(screen_name, direction = "out")
        # Set up users to include in the graph (ego and neighbours)
        ego = api.get_user(user).id
        with open(os.path.join(PATHS['out'], str(ego)), 'r') as f:
            ego_neighbours = [int(id) for line in csv.reader(f) for id in line]
        make_adjacency_matrix(ego_neighbours, direction = "out", file= user + '_out.csv')
