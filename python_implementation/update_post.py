import requests


def check_response(response):
    if response.status_code == 200:
        return "Post updated successfully!"
    else:
        return "Failed to update post. " + response.json()


def update_discourse_post(topic, discourse_config, headers):
    # Build the request URL and headers
    url = f"{discourse_config['endpoint']}/posts/{topic.postid}.json"
    print(topic.topicid, topic.postid)
    print()
    # Build the request payload
    payload = {
        "post[raw]": str(topic.raw_text),
    }
    # Send the PUT request to update the post
    response = requests.put(url, headers=headers, data=payload)
    return check_response(response)


def update_discourse_topic_tags(topic, discourse_config, headers):
    # Build the request URL and headers
    url = f"{discourse_config['endpoint']}/t/{topic.topicid}.json"

    # Build the request payload
    payload = {"tags": ["toc", "synched-from-github"]}
    # Send the PUT request to update the post
    response = requests.put(url, headers=headers, json=payload)
    return check_response(response)
