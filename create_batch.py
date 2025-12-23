from pathlib import Path

from google import genai
from google.genai import types


def main():
    genai_client = genai.Client(
        vertexai=True,
        project="kingu-family-photos",
        location="global",
    )

    photos_dir = Path("photos")

    for dir_path in photos_dir.iterdir():
        if not dir_path.is_dir():
            continue

        requests_file = dir_path / "requests.jsonl"
        if not requests_file.exists():
            print(f"Skipping: {dir_path.name} (requests.jsonl not found)")
            continue

        dir_name = dir_path.name
        result_uri = f"gs://add_keywords_with_gemini.kingu.dev/photos/{dir_name}/"

        batch_job = genai_client.batches.create(
            model="gemini-3-flash-preview",
            src=types.BatchJobSource(
                format="jsonl",
                gcs_uri=[
                    f"gs://add_keywords_with_gemini.kingu.dev/photos/{dir_name}/requests.jsonl"
                ],
            ),
            config=types.CreateBatchJobConfig(
                display_name=f"Add Keywords Batch - {dir_name}",
                dest=types.BatchJobDestination(
                    format="jsonl",
                    gcs_uri=result_uri,
                ),
            ),
        )
        print(f"Created batch job: {batch_job.name} ({dir_name})")


if __name__ == "__main__":
    main()
