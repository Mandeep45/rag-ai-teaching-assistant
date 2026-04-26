from transcript_parser import parse_transcript
from chunker import chunk_text

def process_dataset(df):
    """
    Process all videos in the dataset.
    df: pandas dataframe of the dataset
    returns: list of all chunks from all videos
    """
    all_chunks = []

    for index, row in df.iterrows():
        try:
            clean_text = parse_transcript(row['content'])
            chunks = chunk_text(clean_text, row['title'], row['video_url'])
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Error processing video {row['title']}: {e}")
            continue

    print(f"Total chunks from all videos: {len(all_chunks)}")
    return all_chunks