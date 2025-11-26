"""
yt_data_ingest.py

Module for ingesting YouTube data from the YouTube Data API.

This module defines functions to create a YouTube API client and fetch video
metadata from channels or search queries. The data can then be stored in a
data lake or database for further analysis.

Note:
    You must supply a valid YouTube Data API key via the 'YOUTUBE_API_KEY'
    environment variable or as a function argument. Refer to Google's
    documentation for how to obtain an API key.

Example:
    python yt_data_ingest.py --channel-id UC_x5XG1OV2P6uZZ5FSM9Ttw --max-results 100
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

try:
    from googleapiclient.discovery import build
except ImportError:
    # Placeholder for googleapiclient; instruct user to install required package.
    build = None  # type: ignore

def get_youtube_client(api_key: str):
    """
    Create a YouTube API client using the provided API key.

    Args:
        api_key: A string containing your YouTube Data API key.

    Returns:
        A googleapiclient.discovery.Resource instance representing the YouTube API client.

    Raises:
        ImportError: If googleapiclient is not installed.
    """
    if build is None:
        raise ImportError(
            "googleapiclient is not installed. Install it via 'pip install google-api-python-client'."
        )
    return build("youtube", "v3", developerKey=api_key)

def fetch_channel_videos(
    client,
    channel_id: str,
    max_results: int = 50,
    page_token: Optional[str] = None,
) -> List[Dict]:
    """
    Fetch a list of videos from a YouTube channel.

    Args:
        client: A YouTube API client created via get_youtube_client.
        channel_id: The ID of the channel to fetch videos from.
        max_results: Maximum number of results to return (up to 50).
        page_token: Token for pagination; used to fetch additional pages.

    Returns:
        A list of dictionaries containing video metadata such as videoId, title, description,
        publishTime, and statistics (views, likes, comments).
    """
    request = client.search().list(
        part="id,snippet",
        channelId=channel_id,
        maxResults=max_results,
        type="video",
        pageToken=page_token,
        order="date",
    )
    response = request.execute()
    videos: List[Dict] = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append(
            {
                "video_id": video_id,
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "publish_time": snippet.get("publishedAt"),
            }
        )
    return videos

def main() -> None:
    """
    Entry point for command-line execution.

    This function reads the API key from an environment variable and retrieves
    videos for the specified channel or search query. Results are printed to stdout.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Ingest YouTube video data.")
    parser.add_argument("--channel-id", help="The YouTube channel ID to ingest from.")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum results to fetch.")
    args = parser.parse_args()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError("Please set the YOUTUBE_API_KEY environment variable.")

    client = get_youtube_client(api_key)
    if args.channel_id:
        videos = fetch_channel_videos(client, args.channel_id, max_results=args.max_results)
        for vid in videos:
            print(vid)

if __name__ == "__main__":
    main()
