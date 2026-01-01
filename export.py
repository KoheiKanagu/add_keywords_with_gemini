import datetime
import json
import pathlib
import subprocess

from osxphotos import PhotosDB, QueryOptions


def main():
    db = PhotosDB()
    photos = db.query(options=QueryOptions(selected=True))

    if not photos:
        print("No selected photos found.")
        return

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    now_dir = pathlib.Path("photos") / now
    now_dir.mkdir(exist_ok=True)

    with open("prompts.txt", "r") as f:
        prompts = f.read().strip()

    requests = []

    for photo in photos:
        if photo.ismovie:
            print(f"Skipping movie: {photo.filename}")
            continue

        webp_path = now_dir / f"{photo.uuid}.webp"
        cmd = [
            "cwebp",
            "-metadata",
            "exif",
            "-resize",
            "2000",
            "0",
            "-q",
            "80",
            "-quiet",
            photo.path,
            "-o",
            str(webp_path),
        ]
        subprocess.run(cmd, check=True)
        print(f"Created WebP file: {webp_path}")

        request = {
            "request": {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "fileData": {
                                    "fileUri": f"gs://add_keywords_with_gemini.kingu.dev/{now_dir}/{webp_path.name}",
                                    "mimeType": "image/webp",
                                }
                            },
                        ],
                    }
                ],
                "systemInstruction": {
                    "role": "system",
                    "parts": [{"text": prompts}],
                },
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseSchema": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "写真に関連するキーワードのリスト",
                            },
                        },
                    },
                },
            }
        }
        requests.append(request)

    with open(f"photos/{now}/requests.jsonl", "w") as f:
        for req in requests:
            f.write(json.dumps(req, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()  # type: ignore
