#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6
# # -*- coding: UTF-8 -*-

import re
import time
import logging
import string

import tweepy
from tweepy import OAuthHandler

import config


class StreamListener(tweepy.StreamListener):
    def __init__(self):
        self.tw = TwitterAccount()
        self.api = self.tw.get_api()

    def on_status(self, status):
        if status.in_reply_to_status_id:
            try:
                self.get_tweet(status, True)
            except AttributeError as error:
                self.get_tweet(status, False)

    def get_tweet(self, status, is_extended):
        try:
            if is_extended:
                full_text_repl_tw = status.extended_tweet.get('full_text')
                tweet = self.api.get_status(id=status.in_reply_to_status_id,
                                            tweet_mode='extended')
                tweet_text = tweet.full_text
            else:
                full_text_repl_tw = status.text
                tweet = self.api.get_status(id=status.in_reply_to_status_id)
                tweet_text = tweet.text

            if not tweet.in_reply_to_status_id:
                origin_tweet = re.sub("\n", " ", tweet_text)
                reply_tweet = re.sub("\n", " ", full_text_repl_tw)

                # Write tweets to the tweets file
                text_to_write = f'{origin_tweet} < - > {reply_tweet}\n'
                self.tw.write_to_file(text=text_to_write,
                                      file='data/all_tweets.csv')

                exclude = set(string.punctuation)
                text_without_puncts = ''.join(ch for ch in reply_tweet
                                              if ch not in exclude).lower()
                if "dont agree" in text_without_puncts or "disagree" in text_without_puncts:
                    self.tw.write_to_file(text=text_to_write,
                                          file='data/disagreed.plarity')
                    print(f"{text_to_write}\n")
                else:
                    self.tw.write_to_file(text=text_to_write,
                                          file='data/agreed.plarity')
        except tweepy.TweepError as error:
                print(error)

    def on_error(self, status_code):
        print("Got an error: ", status_code)
        if status_code == 420:
            return False


class TwitterAccount():
    def __init__(self, user="wylsacom"):
        self.user = user
        self.num_of_tweets = 10
        self.num_of_repl = 20
        self.limit = 0

    def get_api(self):
        try:
            self.consumer_key = config.consumer_key
            self.consumer_secret = config.consumer_secret
            self.access_token = config.access_token
            self.access_secret = config.access_secret

            self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            self.auth.set_access_token(self.access_token, self.access_secret)
            self.api = tweepy.API(self.auth, wait_on_rate_limit_notify=True)
        except tweepy.TweepError as exception:
            logging.exception(exception)
        return self.api

    # TODO: search some users tweets and get their ids
    # Using that ids search for tweets using 'api.get_status(id=) method'
    def get_tweets(self):
        user_tweets = self.api.user_timeline(id=self.user,
                                             count=self.num_of_tweets,
                                             pages=10)
        self.limit += len(user_tweets)

        for num, tweet in enumerate(user_tweets):
            tweet.text = re.sub("\n", " ", tweet.text)
            print(num, tweet.text)
            self.write_to_file(f"Tweet number {num}: \n")
            if self.limit >= 320:
                print("No more tweets")
                print("Sleep for 15min....")
                self.limit = 0
                time.sleep(900)
                continue
            else:
                try:
                    # replies = self.api.search(q=f"@{self.user}",
                    #                           since_id=tweet.id)
                    status = tweepy.Cursor(self.api.search,
                                           q=f"@{self.user}",
                                           since_id=tweet.id,
                                           rpp=self.num_of_repl,
                                           pages=1
                                           ).items()
                    self.limit += self.num_of_repl
                    for reply in status:
                        if reply.in_reply_to_status_id == tweet.id:
                            reply_user = str(reply.user.screen_name).strip()
                            self.write_to_file(f'"{self.user} tweeted: {tweet.text}";\n')
                            self.write_to_file(f'"{reply_user} replied: {reply.text}";\n')
                            self.write_to_file("-----------------------\n")
                            break
                            print("----------Нашел ответ!----------\n")
                            print("Ищу ответ на следующий твит\n")

                except tweepy.TweepError as error:
                    logging.exception(error)
                    time.sleep(900)
                    continue

    def write_to_file(self, text, file="data.csv"):
        file_name = f'data/{self.user}.csv'
        with open(file, 'a') as file:
            file.write(text)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--username", help="Choose the user whose tweets to download")
    # args = parser.parse_args()
    # if args.username:
    #     print(f"Searching {args.username} tweets")
        # tweeter = TwitterAccount(user=args.username)
        # twitter.get_api()
        # twitter.get_tweets()
    # else:
    #     TwitterAccount()

    twitter = TwitterAccount()
    api = twitter.get_api()
    streamListener = StreamListener()
    stream = tweepy.Stream(auth=api.auth,
                           listener=streamListener,
                           tweet_mode='extended')

    stream.filter(track=["disagree", "#disagree", "don't agree"],
                  # "agree", "#agree", "couldn't agree more"],
                  languages=["en"],
                  async=True)
