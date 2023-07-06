from update_post import update_discourse_post, update_discourse_topic_tags
from get_postids_and_urls import get_discourse_post_raw_content
import requests
import yaml
import os


def get_config():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    api_config = os.path.join(script_directory, "ignore/api_keys.yaml")
    # Load YAML data from file
    with open(api_config) as file:
        yaml_data = yaml.safe_load(file)

    # Find the "discourse" entry in the YAML data
    discourse_config = next(
        entry for entry in yaml_data if entry["domain"] == "discourse"
    )

    print_config(discourse_config)
    return discourse_config


def get_post_id_of_topic(topic_id, discourse_config, headers):
    # API endpoint and headers
    api_endpoint = f"{discourse_config['endpoint']}/t/{topic_id}.json"

    # Make API request
    response = requests.get(api_endpoint, headers=headers)
    response_json = response.json()

    # Extract the ID of the first post
    first_post_id = response_json["post_stream"]["posts"][0]["id"]

    return first_post_id


class Topic:
    def __init__(self, topicid, url, raw_url):
        self.topicid = topicid
        self.postid = ""
        self.url = url
        self.raw_url = raw_url
        self.raw_text = ""

    def set_raw_text(self):
        print(self.raw_url)
        response = requests.get(self.raw_url)
        if response.status_code == 200:
            additional_text = "This post is automatically synchronized with {}".format(
                self.url
            )
            self.raw_text = "{}\n{}".format(additional_text, response.text)


def convert_github_url(url):
    raw_url = url.replace("github.com", "raw.githubusercontent.com")
    raw_url = raw_url.replace("/blob/", "/")
    return raw_url


def extract_topics(table_of_urls_and_topic_ids, discourse_config, headers):
    lines = table_of_urls_and_topic_ids.split("\n")
    topics = []

    for line in lines:
        parts = line.strip().split("|")
        if len(parts) == 2:
            topicid = parts[0].strip()
            url = parts[1].strip()
            raw_url = convert_github_url(url)
            topic = Topic(topicid, url, raw_url)
            topic.postid = get_post_id_of_topic(
                topic.topicid, discourse_config, headers
            )
            topic.set_raw_text()
            topics.append(topic)

    return topics


def print_config(discourse_config):
    print("Configuration Variables:")
    print(f"API KEY: {discourse_config['key']}")
    print(f"API ENDPOINT: {discourse_config['endpoint']}")
    print(f"INPUT POST ID: {discourse_config['input_post_id']}")


def print_topic(topic):
    print("PostID:", topic.topicid)
    print("URL:", topic.raw_url)
    print(
        "Raw URL Text:", topic.raw_text[:100]
    )  # Print first 100 characters of raw text
    print()


def get_topics(discourse_config, headers):
    return extract_topics(
        get_discourse_post_raw_content(discourse_config, headers),
        discourse_config,
        headers,
    )


def construct_headers(discourse_config):
    headers = {
        "Api-Key": discourse_config["key"],
        "Api-Username": discourse_config["name"],
    }
    return headers


if __name__ == "__main__":
    discourse_config = get_config()
    headers = construct_headers(discourse_config)

    topics = get_topics(discourse_config, headers)

    for topic in topics:
        print(update_discourse_post(topic, discourse_config, headers))
        print(update_discourse_topic_tags(topic, discourse_config, headers))
