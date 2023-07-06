import requests


def get_discourse_post_raw_content(discourse_config, headers):
    url = (
        f"{discourse_config['endpoint']}/posts/{discourse_config['input_post_id']}.json"
    )

    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code == 200:
        post_data = response.json()
        print(post_data)
        raw_content = post_data["raw"]
        print(raw_content)
        return raw_content

    return None
