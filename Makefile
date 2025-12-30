export:
	uv run export.py

create-batch:
	uv run create_batch.py

upload:
	gcloud storage rsync --recursive photos "gs://add_keywords_with_gemini.kingu.dev/photos/"

download:
	gcloud storage rsync --recursive "gs://add_keywords_with_gemini.kingu.dev/photos/" photos/

add-keywords:
	uv run add_keywords.py
