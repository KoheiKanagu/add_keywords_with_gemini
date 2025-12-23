import glob
import json
import os

import photoscript
import tqdm


def main():
    keywords_dict = {}

    prediction_files = glob.glob("photos/**/predictions.jsonl", recursive=True)

    for file_path in tqdm.tqdm(prediction_files):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)

                    file_uri = data["request"]["contents"][0]["parts"][0]["fileData"][
                        "fileUri"
                    ]

                    filename = os.path.basename(file_uri)
                    uuid_key, _ = os.path.splitext(filename)

                    text_content = data["response"]["candidates"][0]["content"][
                        "parts"
                    ][0]["text"]

                    try:
                        response_json = json.loads(text_content)
                    except json.JSONDecodeError:
                        # Fallback: try to strip markdown code blocks if present
                        if text_content.startswith("```json"):
                            text_content = text_content.replace("```json", "").replace(
                                "```", ""
                            )
                        elif text_content.startswith("```"):
                            text_content = text_content.replace("```", "")
                        response_json = json.loads(text_content)

                    keywords = response_json.get("keywords", [])

                    keywords_dict[uuid_key] = keywords

                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    print(f"Error processing line in {file_path}: {e}")
                    continue

    for uuid_key, keywords in tqdm.tqdm(keywords_dict.items()):
        photo = photoscript.Photo(uuid=uuid_key)
        photo.keywords = photo.keywords + keywords


if __name__ == "__main__":
    main()
