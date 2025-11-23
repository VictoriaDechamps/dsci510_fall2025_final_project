# src/analysis_spotify.py
# some analyses on music data
# plots are saved to the results folder

from pathlib import Path
import collections
import calendar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.config import (data_folder,results_folder,spotify_kworb_kaggle1_filename,spotify_green,text_color,bg_color,audio_feature_columns)

def apply_spotify_style(ax):
    fig = ax.get_figure()
    if fig is not None:
        fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.title.set_color(text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)

def pick_column(data, possible_names):
    for name in possible_names:
        if name in data.columns:
            return name
    return None

def make_folder(folder_path):
    folder_path.mkdir(parents=True, exist_ok=True)

def pick_streams_column(data):
    return pick_column(data, ["kworb_daily_streams", "Daily [streams]", "kworb_streams", "Streams"])

def load_data():
    data_dir = data_folder
    results_dir = results_folder
    make_folder(results_dir)

    input_csv = data_dir / spotify_kworb_kaggle1_filename

    if not input_csv.exists():
        print("ERROR:", input_csv, "not found.")
        return None, data_dir, results_dir

    data = pd.read_csv(input_csv)

    if "popularity" in data.columns:
        data["popularity"] = pd.to_numeric(data["popularity"], errors="coerce")
    if "popularity_spotify" in data.columns:
        data["popularity_spotify"] = pd.to_numeric(data["popularity_spotify"], errors="coerce")

    for column_name in ["kworb_daily_streams", "Daily [streams]", "kworb_streams", "Streams"]:
        if column_name in data.columns:
            data[column_name] = pd.to_numeric(data[column_name], errors="coerce")

    for duration_column in ["duration_ms_spotify", "duration_ms"]:
        if duration_column in data.columns:
            data[duration_column] = pd.to_numeric(data[duration_column], errors="coerce")

    if "artist_followers" in data.columns:
        data["artist_followers"] = pd.to_numeric(data["artist_followers"], errors="coerce")
    if "artist_popularity" in data.columns:
        data["artist_popularity"] = pd.to_numeric(data["artist_popularity"], errors="coerce")

    return data, data_dir, results_dir

def audio_features_vs_streams(data, results_dir):
    streams_column = pick_column(data, ["kworb_streams", "Streams"])
    if streams_column is None:
        streams_column = pick_streams_column(data)
    if streams_column is None:
        print("streams column missing.")
        return

    audio_columns = [c for c in audio_feature_columns if c in data.columns]
    columns_to_use = audio_columns + [streams_column]

    small_data = data[columns_to_use].dropna()
    if small_data.empty:
        print("no rows with both audio features and streams")
        return

    correlation_series = small_data.corr(numeric_only=True)[streams_column].sort_values(ascending=False)

# bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    correlation_series.drop(streams_column, errors="ignore").plot(
        kind="bar",
        color=spotify_green,
        ax=ax,)
    ax.set_title("Correlation of Audio Features with Total Streams")
    ax.set_xlabel("Feature")
    ax.set_ylabel("Correlation with Total Streams")
    apply_spotify_style(ax)
    plt.tight_layout()
    output_bar = results_dir / "audio_features_vs_total_streams_bar.png"
    plt.savefig(output_bar)
    plt.close(fig)
    print("Saved plot →", output_bar)

# pairplot

    pairplot_columns = audio_columns + [streams_column]
    graph = sns.pairplot(
        small_data,
        vars=pairplot_columns,
        plot_kws={"alpha": 0.5, "color": spotify_green},
        diag_kws={"color": spotify_green})
    for row_axes in graph.axes:
        for ax in row_axes:
            if ax is not None:
                apply_spotify_style(ax)
    plt.tight_layout()
    output_pair = results_dir / "audio_features_pairplot_streams.png"
    plt.savefig(output_pair)
    plt.close()
    print("Saved pairplot →", output_pair)


# release month vs streams
def release_month_vs_streams(data, results_dir):
    streams_column = pick_streams_column(data)
    if "release_date" not in data.columns or streams_column is None:
        print("needed columns missing.")
        return

    temp_data = data.copy()
    temp_data["release_date_parsed"] = pd.to_datetime(temp_data["release_date"], errors="coerce")
    temp_data["release_month"] = temp_data["release_date_parsed"].dt.month

    month_and_streams = temp_data[["release_month", streams_column]].dropna()
    if month_and_streams.empty:
        print("No valid release_month/streams data")
        return

    month_average = month_and_streams.groupby("release_month")[streams_column].mean()
    month_indexes = list(range(1, 13))
    month_average = month_average.reindex(month_indexes)
    month_names = [calendar.month_abbr[m] for m in month_indexes]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(month_names, month_average.values, color=spotify_green)
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Streams")
    ax.set_title("Average Streams by Release Month")
    ax.set_ylim(bottom=6e5)
    apply_spotify_style(ax)
    plt.tight_layout()
    output_bar = results_dir / "release_month_vs_streams_bar.png"
    plt.savefig(output_bar)
    plt.close(fig)
    print("Saved plot →", output_bar)

# total words vs streams

def total_words_vs_streams(data, results_dir):
    streams_column = pick_streams_column(data)
    if "lyrics" not in data.columns or streams_column is None:
        print("columns missing.")
        return
    def total_word_count(text):
        if pd.isna(text):
            return np.nan
        text = str(text)
        text = text.replace("’", "'")
        pieces = text.lower().split()
        cleaned_words = [w.strip(".,!?\"'()[]{}:;") for w in pieces]
        cleaned_words = [w for w in cleaned_words if w]
        return len(cleaned_words)
    data_copy = data.copy()
    data_copy["total_words"] = data_copy["lyrics"].apply(total_word_count)
    words_and_streams = data_copy[["total_words", streams_column]].dropna()
    if words_and_streams.empty:
        print("No data for total words vs streams")
        return

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=words_and_streams,
        x="total_words",
        y=streams_column,
        scatter_kws={"alpha": 0.5, "color": spotify_green},
        line_kws={"color": "grey"},
        ax=ax)
    ax.set_xlabel("Total Words in Lyrics")
    ax.set_ylabel("Streams")
    ax.set_title("Total Lyrics Word Count vs Streams")
    apply_spotify_style(ax)
    plt.tight_layout()
    output_path = results_dir / "total_words_vs_streams.png"
    plt.savefig(output_path)
    plt.close(fig)
    print("Saved plot →", output_path)

# most common words in top songs

def most_common_high_stream_words(data, results_dir, top_n=20):
    streams_column = pick_streams_column(data)
    if "lyrics" not in data.columns or streams_column is None:
        print("columns missing")
        return
    data_copy = data.copy()
    if data_copy[streams_column].isna().all():
        print("No streams values for lyrics word analysis")
        return
    top_streams_cutoff = data_copy[streams_column].quantile(0.75)
    top_songs_data = data_copy[data_copy[streams_column] >= top_streams_cutoff]
    all_words = []
    for lyrics_text in top_songs_data["lyrics"].dropna():
        lyrics_text = str(lyrics_text)
        lyrics_text = lyrics_text.replace("’", "'")
        pieces = lyrics_text.lower().split()
        cleaned_tokens = [w.strip(".,!?\"'()[]{}:;") for w in pieces]
        cleaned_tokens = [w for w in cleaned_tokens if w]
        all_words.extend(cleaned_tokens)

# words to ginore
    stopwords = {
        "the", "and", "a", "to", "of", "in", "it", "is", "i", "you","on", "for", "that", "me", "my", "your", "with", "this", "be",
        "at", "we", "so", "but", "not", "no", "do", "are", "all","la", "oh", "yeah", "ya", "na", "ooh", "ah", "uh",
        "when", "just", "know", "what", "now", "youre", "yours","dont", "let", "its", "never", "cause", "because", "was",
        "can", "cant", "nah", "like", "out", "come", "been", "get","too", "used", "im", "i'm", "i’m", "ive", "i've", "want", "wanna",
        "you're", "youre", "it's", "its", "feel", "say", "one", "down","got", "back", "thats", "that's", "hey", "take", "see", "doin",
        "baby", "girl", "boy", "woah", "whoa", "mmm", "i'll", "I'll",
        "way", "give", "have", "here", "every", "her", "need", "how","make", "they", "only", "where", "we're", "from", "could",
        "away", "said", "gonna", "won't", "will", "why", "more", "bad","tell", "our", "keep", "then", "still", "think", "into", "good",
        "day", "would", "were", "side", "some", "right", "something",
        "look", "ever", "ain't", "knew", "maybe", "even", "stop","there", "gotta", "nothing", "turn", "had", "through", "over",
        "around", "hard", "play", "much","don't","can't","let's","things"}
    filtered_words = [w for w in all_words if w not in stopwords and len(w) > 2]
    word_counter = collections.Counter(filtered_words)
    most_common_list = word_counter.most_common(top_n)
    if not most_common_list:
        print("No words found after filtering")
        return
    words, counts = zip(*most_common_list)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(words, counts, color=spotify_green)
    ax.set_xticklabels(words, rotation=45, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("Most Common Words in High-Stream Songs")
    apply_spotify_style(ax)
    plt.tight_layout()
    output_path = results_dir / "top_words_in_high_stream_songs.png"
    plt.savefig(output_path)
    plt.close(fig)
    print("Saved plot →", output_path)

# audio profiles- top & bottom 10%
def audio_profiles_top_vs_bottom(data, results_dir):
    streams_column = pick_streams_column(data)
    if streams_column is None:
        print("streams column missing")
        return
    audio_columns = [c for c in audio_feature_columns if c in data.columns]
    if not audio_columns:
        print("No audio feature columns")
        return
    cleaned_data = data.dropna(subset=audio_columns + [streams_column])
    if cleaned_data.empty:
        print("No rows with both audio features and streams")
        return
    top_streams_cutoff = cleaned_data[streams_column].quantile(0.90)
    bottom_streams_cutoff = cleaned_data[streams_column].quantile(0.10)
    top_songs = cleaned_data[cleaned_data[streams_column] >= top_streams_cutoff]
    bottom_songs = cleaned_data[cleaned_data[streams_column] <= bottom_streams_cutoff]
    top_means = top_songs[audio_columns].mean()
    bottom_means = bottom_songs[audio_columns].mean()
    for feature_name in audio_columns:
        fig, ax = plt.subplots(figsize=(5, 4))
        values = [top_means[feature_name], bottom_means[feature_name]]
        labels = ["Top 10%", "Bottom 10%"]
        ax.bar(labels, values, color=spotify_green)
        ax.set_ylabel("Average " + feature_name)
        ax.set_title(f"{feature_name.capitalize()}: Top vs Bottom (by Streams)")
        apply_spotify_style(ax)
        plt.tight_layout()
        output_feature_plot = results_dir / f"top_vs_bottom_{feature_name}_streams.png"
        plt.savefig(output_feature_plot)
        plt.close(fig)
        print("Saved feature comparison plot →", output_feature_plot)

# tempo distribution
def tempo_distribution(data, results_dir):
    if "tempo" not in data.columns:
        print("tempo column missing")
        return
    tempo_values = data["tempo"].dropna()
    if tempo_values.empty:
        print("No tempo data available")
        return
    min_tempo = tempo_values.min()
    max_tempo = tempo_values.max()
    start_value = 5 * np.floor(min_tempo / 5.0)
    end_value = 5 * np.ceil(max_tempo / 5.0)
    tempo_bins = np.arange(start_value, end_value + 5, 5)
    tempo_buckets = pd.cut(tempo_values, bins=tempo_bins, include_lowest=True)
    bucket_counts = tempo_buckets.value_counts().sort_index()
    x_labels = [f"{int(interval.left)}-{int(interval.right)}" for interval in bucket_counts.index]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x_labels, bucket_counts.values, color=spotify_green)
    ax.set_xlabel("Tempo (BPM, 5-BPM ranges)")
    ax.set_ylabel("Number of Songs")
    ax.set_title("Distribution of Song Tempos")
    ax.tick_params(axis="x", rotation=90)
    apply_spotify_style(ax)
    plt.tight_layout()
    output_path = results_dir / "tempo_distribution.png"
    plt.savefig(output_path)
    plt.close(fig)
    print("Saved plot →", output_path)

# song duration vs streams
def duration_vs_streams(data, results_dir):
    streams_column = pick_streams_column(data)
    duration_column = pick_column(data, ["duration_ms_spotify", "duration_ms"])
    if duration_column is None or streams_column is None:
        print("duration or streams missing")
        return
    duration_and_streams = data[[duration_column, streams_column]].dropna()
    if duration_and_streams.empty:
        print("No data for duration vs streams")
        return
    duration_and_streams = duration_and_streams.copy()
    duration_and_streams["duration_minutes"] = duration_and_streams[duration_column] / 60000.0
    max_minutes = duration_and_streams["duration_minutes"].max()
    top_minute = np.ceil(max_minutes)
    minute_bins = np.arange(0, top_minute + 1, 1.0)
    minute_labels = [f"{int(minute_bins[i])}-{int(minute_bins[i + 1])}" for i in range(len(minute_bins) - 1)]
    duration_and_streams["duration_bin"] = pd.cut(
        duration_and_streams["duration_minutes"],
        bins=minute_bins,
        labels=minute_labels,
        include_lowest=True)
    avg_streams_by_bin = duration_and_streams.groupby("duration_bin")[streams_column].mean().dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(avg_streams_by_bin.index.astype(str), avg_streams_by_bin.values, color=spotify_green)
    ax.set_xlabel("Song Duration (minutes)")
    ax.set_ylabel("Average Streams")
    ax.set_title("Average Streams by Song Duration Range")
    ax.tick_params(axis="x", rotation=90)
    apply_spotify_style(ax)
    plt.tight_layout()
    output_path = results_dir / "duration_vs_streams_one_minute_bars.png"
    plt.savefig(output_path)
    plt.close(fig)
    print("Saved plot →", output_path)

# correlation heatmap

def correlation_heatmap(data, results_dir):
    streams_column = pick_streams_column(data)
    if streams_column is None:
        print("streams column missing")
        return
    selected_columns = [streams_column]
    extra_columns = ["artist_followers","artist_popularity","duration_ms_spotify","duration_ms","popularity","popularity_spotify",] + audio_feature_columns
    for column_name in extra_columns:
        if column_name in data.columns and column_name not in selected_columns:
            selected_columns.append(column_name)
    small_data = data[selected_columns].dropna()
    if small_data.empty:
        print("No numeric data for heatmap")
        return
    correlation_matrix = small_data.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap=sns.light_palette(spotify_green, as_cmap=True),
        square=True,
        ax=ax,)
    ax.set_title("Correlation Heatmap: Streams, Audio Features, Artist Stats")
    apply_spotify_style(ax)
    plt.tight_layout()
    output_path = results_dir / "correlation_heatmap.png"
    plt.savefig(output_path)
    plt.close(fig)
    print("Saved heatmap →", output_path)

# pie chart

def explicit_pie_chart(data, results_dir):
    if "explicit" not in data.columns:
        print("explicit column missing")
        return
    explicit_counts = data["explicit"].value_counts(dropna=False)
    labels = []
    sizes = []
    for flag_value, count in explicit_counts.items():
        if pd.isna(flag_value):
            labels.append("Unknown")
        elif bool(flag_value):
            labels.append("Explicit")
        else:
            labels.append("Non-Explicit")
        sizes.append(count)
    if not sizes:
        print("No data for explicit pie chart.")
        return
    colors = []
    for label in labels:
        if label == "Explicit":
            colors.append(spotify_green)
        else:
            colors.append("lightgrey")
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"color": text_color})
    ax.set_title("Explicit vs Non-Explicit Songs", color=text_color)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    plt.tight_layout()
    output_path = results_dir / "explicit_pie_chart.png"
    plt.savefig(output_path)
    plt.close(fig)
    print("Saved pie chart →", output_path)

def load_data_youtube():
    root_folder = Path(__file__).resolve().parents[1]
    data_dir = root_folder / "data"
    results_dir = root_folder / "results"
    make_folder(results_dir)
    input_csv = data_dir / "spotify_kworb_kaggle1_kaggle2.csv"
    if not input_csv.exists():
        print("ERROR:", input_csv, "not found")
        return None, data_dir, results_dir
    data = pd.read_csv(input_csv)
    return data, data_dir, results_dir

def spotify_vs_youtube_streams(data, results_dir):
    data.columns = data.columns.str.strip()
    if "kworb_streams" not in data.columns:
        print("Column 'kworb_streams' not found.")
        return
    if "Total Views" not in data.columns:
        print("Column 'Total Views' not found.")
        print("Columns available:", list(data.columns))
        return
    data["Total Views"] = (
        data["Total Views"]
        .astype(str)
        .str.replace(",", "", regex=False))
    data["Total Views"] = pd.to_numeric(data["Total Views"], errors="coerce")
    data["kworb_streams"] = pd.to_numeric(data["kworb_streams"], errors="coerce")
    clean = data[["kworb_streams", "Total Views"]].dropna()
    if clean.empty:
        print("No valid Spotify & YouTube rows")
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(clean["kworb_streams"], clean["Total Views"],
               color=spotify_green)
    ax.set_xlabel("Spotify Streams (Kworb)")
    ax.set_ylabel("YouTube Total Views")
    ax.set_title("Spotify Streams vs YouTube Views")

    apply_spotify_style(ax)
    plt.tight_layout()

    out_path = results_dir / "spotify_vs_youtube_streams.png"
    plt.savefig(out_path)
    plt.close(fig)
    print("Saved plot →", out_path)

def main():

    data, data_dir, results_dir = load_data()
    if data is None:
        return
    audio_features_vs_streams(data, results_dir)
    release_month_vs_streams(data, results_dir)
    total_words_vs_streams(data, results_dir)
    most_common_high_stream_words(data, results_dir)
    audio_profiles_top_vs_bottom(data, results_dir)
    tempo_distribution(data, results_dir)
    duration_vs_streams(data, results_dir)
    correlation_heatmap(data, results_dir)
    explicit_pie_chart(data, results_dir)
    yt_data, yt_data_dir, yt_results_dir = load_data_youtube()
    if yt_data is not None:
        spotify_vs_youtube_streams(yt_data, results_dir)
    print("Analysis complete :)")
    print("Plots in:", results_dir)


if __name__ == "__main__":
    main()
