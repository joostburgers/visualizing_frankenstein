# Frankenstein Analysis - Streamlined Workflow
# This optimized version:
# 1. Runs sentiment analysis only once on all paragraphs
# 2. Uses manual location data (skips geoparsing)
# 3. Saves all results as parquet files for easy loading
# 4. Makes the presentation notebook independent

import pandas as pd
import numpy as np
import re
import os
import glob
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from tqdm import tqdm
from typing import Dict, Any
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

print("🚀 Starting optimized Frankenstein analysis workflow...")
print("=" * 60)

# Step 1: Load and process text files
print("📚 Step 1: Loading and processing text files...")

data_folder = "data"
txt_files = glob.glob(os.path.join(data_folder, "*.txt"))

print(f"Found {len(txt_files)} text files:")
for file in txt_files:
    print(f"  - {file}")

# Read all text files into a DataFrame
data_rows = []
for file_path in txt_files:
    filename = os.path.basename(file_path)
    if filename.startswith('frankenstein_') and filename.endswith('.txt'):
        text_section = filename[len('frankenstein_'):-len('.txt')]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            data_rows.append({
                'text_section': text_section,
                'full_text': full_text
            })
            print(f"✅ Read {filename} - {len(full_text)} characters")
            
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

frankenstein_df = pd.DataFrame(data_rows)

# Step 2: Extract chapters and letters
print("\n📖 Step 2: Extracting chapters and letters...")

def extract_chapters_and_letters_final(text_section, full_text):
    """Extract chapters/letters with special handling for closing_letters"""
    chapters_letters = []
    
    if text_section == 'closing_letters':
        chapters_letters.append({
            'text_section': text_section,
            'chapter_letter': 'CLOSING LETTERS',
            'full_text': full_text.strip()
        })
        return chapters_letters
    
    # Extract chapters and letters
    chapter_pattern = r'(CHAPTER\s+[IVX\d]+\.?)'
    chapter_matches = list(re.finditer(chapter_pattern, full_text, flags=re.IGNORECASE))
    
    letter_pattern = r'(LETTER\s+[IVX\d]+\.?)'
    letter_matches = list(re.finditer(letter_pattern, full_text, flags=re.IGNORECASE))
    
    # Filter embedded letters
    filtered_letter_matches = []
    for letter_match in letter_matches:
        is_embedded = False
        for i, chapter_match in enumerate(chapter_matches):
            chapter_start = chapter_match.start()
            chapter_end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(full_text)
            
            if chapter_start < letter_match.start() < chapter_end:
                is_embedded = True
                break
        
        if not is_embedded:
            filtered_letter_matches.append(letter_match)
    
    # Process all sections
    all_matches = chapter_matches + filtered_letter_matches
    all_matches.sort(key=lambda x: x.start())
    
    for i, match in enumerate(all_matches):
        title = match.group(1).replace('.', '').strip().upper()
        start_pos = match.end()
        
        if i + 1 < len(all_matches):
            end_pos = all_matches[i + 1].start()
        else:
            end_pos = len(full_text)
        
        content = full_text[start_pos:end_pos].strip()
        
        if len(content) > 100:
            chapters_letters.append({
                'text_section': text_section,
                'chapter_letter': title,
                'full_text': content
            })
    
    return chapters_letters

# Extract chapters and letters
unnested_data_final = []
for _, row in frankenstein_df.iterrows():
    extracted = extract_chapters_and_letters_final(row['text_section'], row['full_text'])
    unnested_data_final.extend(extracted)

frankenstein_final_df = pd.DataFrame(unnested_data_final)
print(f"✅ Extracted {len(frankenstein_final_df)} chapters/letters")

# Step 3: Split into paragraphs
print("\n📝 Step 3: Splitting into paragraphs...")

def split_into_paragraphs(text_section, chapter_letter, full_text):
    """Split the full text of a chapter/letter into individual paragraphs"""
    paragraphs = []
    
    paragraph_splits = re.split(r'\n\s*\n', full_text)
    
    for i, paragraph in enumerate(paragraph_splits):
        paragraph = paragraph.strip()
        paragraph = re.sub(r'\s+', ' ', paragraph)
        
        if len(paragraph) > 10:
            paragraphs.append({
                'text_section': text_section,
                'chapter_letter': chapter_letter,
                'paragraph_number': i + 1,
                'paragraph_text': paragraph
            })
    
    return paragraphs

# Process paragraphs
paragraph_data = []
for _, row in frankenstein_final_df.iterrows():
    paragraphs = split_into_paragraphs(
        row['text_section'], 
        row['chapter_letter'], 
        row['full_text']
    )
    paragraph_data.extend(paragraphs)

frankenstein_paragraphs_df = pd.DataFrame(paragraph_data)
print(f"✅ Created {len(frankenstein_paragraphs_df)} paragraphs")

# Step 4: Load manual location data
print("\n🗺️ Step 4: Loading manual location data...")

try:
    frankenstein_manual_locations = pd.read_csv("frankenstein_paragraphs_geoparsed_and_located.csv")
    print(f"✅ Loaded manual locations: {len(frankenstein_manual_locations)} paragraphs")
except FileNotFoundError:
    print("❌ Manual locations file not found: frankenstein_paragraphs_geoparsed_and_located.csv")
    print("Please ensure this file exists in the current directory")
    exit()

# Step 5: Initialize RoBERTa model for sentiment analysis (ONE TIME ONLY)
print("\n🤖 Step 5: Loading RoBERTa sentiment model...")

MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    print("✅ RoBERTa model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

def polarity_scores_roberta(text: str) -> Dict[str, float]:
    """Calculate RoBERTa sentiment scores for a given text"""
    encoded_text = tokenizer.encode_plus(
        text, 
        max_length=512, 
        truncation=True, 
        return_tensors='pt'
    )
    
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    
    return {
        'roberta_neg': scores[0],
        'roberta_neu': scores[1], 
        'roberta_pos': scores[2],
        'roberta_compound': (scores[2] - scores[0]) * (1 - scores[1])
    }

# Step 6: Run sentiment analysis ONCE on all paragraphs
print("\n💭 Step 6: Running sentiment analysis on all paragraphs...")
print("This is the only time sentiment analysis runs - efficient approach!")

def add_sentiment_scores(text):
    """Add sentiment scores with error handling"""
    try:
        return polarity_scores_roberta(text)
    except Exception as e:
        return {'roberta_neg': None, 'roberta_neu': None, 'roberta_pos': None, 'roberta_compound': None}

# Apply sentiment analysis with progress bar
tqdm.pandas(desc="Analyzing sentiment")
sentiment_scores = frankenstein_paragraphs_df['paragraph_text'].progress_apply(add_sentiment_scores)

# Convert to DataFrame and merge
sentiment_df = pd.DataFrame(sentiment_scores.tolist())
frankenstein_all_with_sentiment = pd.concat([frankenstein_paragraphs_df.reset_index(drop=True), sentiment_df], axis=1)

print(f"✅ Sentiment analysis complete for all {len(frankenstein_all_with_sentiment)} paragraphs")

# Step 7: Character analysis using existing sentiment data
print("\n🎭 Step 7: Analyzing character sentiment...")

principal_characters = {
    'Victor': ['Victor', 'Frankenstein'],
    'Elizabeth': ['Elizabeth'],
    'Henry': ['Henry', 'Clerval'],
    'Justine': ['Justine'],
    'Felix': ['Felix'],
    'Agatha': ['Agatha'],
    'Monster': ['monster', 'creature', 'fiend', 'daemon'],
    'William': ['William'],
    'Ernest': ['Ernest'],
    'Father': ['Alphonse', 'father', 'my father', 'his father'],
    'Mother': ['Caroline', 'mother', 'my mother', 'his mother']
}

def contains_character(text, character_variants):
    """Check if text contains any variant of a character name"""
    text_lower = text.lower()
    return any(variant.lower() in text_lower for variant in character_variants)

character_sentiment_data = []

for character_name, variants in principal_characters.items():
    character_paragraphs = frankenstein_all_with_sentiment[
        frankenstein_all_with_sentiment['paragraph_text'].apply(
            lambda x: contains_character(x, variants)
        )
    ].copy()
    
    if len(character_paragraphs) > 0:
        avg_sentiment = character_paragraphs['roberta_compound'].mean()
        total_paragraphs = len(character_paragraphs)
        total_words = character_paragraphs['paragraph_text'].str.split().str.len().sum()
        
        positive_count = sum(character_paragraphs['roberta_compound'] > 0.1)
        negative_count = sum(character_paragraphs['roberta_compound'] < -0.1)
        neutral_count = total_paragraphs - positive_count - negative_count
        
        most_positive_idx = character_paragraphs['roberta_compound'].idxmax()
        most_negative_idx = character_paragraphs['roberta_compound'].idxmin()
        
        character_sentiment_data.append({
            'Character': character_name,
            'Total_Mentions': total_paragraphs,
            'Total_Words': total_words,
            'Avg_Sentiment': avg_sentiment,
            'Positive_Mentions': positive_count,
            'Negative_Mentions': negative_count,
            'Neutral_Mentions': neutral_count,
            'Most_Positive_Score': character_paragraphs.loc[most_positive_idx, 'roberta_compound'],
            'Most_Negative_Score': character_paragraphs.loc[most_negative_idx, 'roberta_compound'],
            'Most_Positive_Text': character_paragraphs.loc[most_positive_idx, 'paragraph_text'][:150] + "...",
            'Most_Negative_Text': character_paragraphs.loc[most_negative_idx, 'paragraph_text'][:150] + "..."
        })

character_sentiment_df = pd.DataFrame(character_sentiment_data)
character_sentiment_df = character_sentiment_df.sort_values('Avg_Sentiment', ascending=False)

print(f"✅ Character analysis complete for {len(character_sentiment_df)} characters")

# Step 8: Location sentiment analysis using existing data
print("\n🌍 Step 8: Analyzing location sentiment...")

# Merge with manual locations to get coordinates
coords_columns = list(frankenstein_manual_locations.columns[-2:])
lat_col = coords_columns[0]
lon_col = coords_columns[1]

# Create a mapping from paragraph info to location info
location_mapping = frankenstein_manual_locations[
    ['text_section', 'chapter_letter', 'paragraph_number', 'curated_name', lat_col, lon_col]
].dropna(subset=[lat_col, lon_col])

# Merge with sentiment data
frankenstein_locations_with_sentiment = frankenstein_all_with_sentiment.merge(
    location_mapping,
    on=['text_section', 'chapter_letter', 'paragraph_number'],
    how='inner'
)

# Calculate word counts
frankenstein_locations_with_sentiment['word_count'] = frankenstein_locations_with_sentiment['paragraph_text'].str.split().str.len()
total_narrative_words = frankenstein_all_with_sentiment['paragraph_text'].str.split().str.len().sum()

# Aggregate by location
location_sentiment_summary = frankenstein_locations_with_sentiment.groupby(['curated_name', lat_col, lon_col]).agg({
    'word_count': 'sum',
    'roberta_compound': 'mean',
    'roberta_pos': 'mean',
    'roberta_neg': 'mean',
    'roberta_neu': 'mean',
    'paragraph_text': 'count'
}).reset_index()

location_sentiment_summary = location_sentiment_summary.rename(columns={
    'word_count': 'total_words',
    'paragraph_text': 'paragraph_count',
    'roberta_compound': 'avg_sentiment'
})

location_sentiment_summary['narrative_percent'] = (location_sentiment_summary['total_words'] / total_narrative_words * 100).round(2)

def categorize_sentiment(score):
    if score > 0.1:
        return "Positive"
    elif score < -0.1:
        return "Negative"
    else:
        return "Neutral"

location_sentiment_summary['sentiment_category'] = location_sentiment_summary['avg_sentiment'].apply(categorize_sentiment)

print(f"✅ Location sentiment analysis complete for {len(location_sentiment_summary)} locations")

# Step 9: Save all results as parquet files
print("\n💾 Step 9: Saving results as parquet files...")

# Save main datasets
frankenstein_all_with_sentiment.to_parquet("frankenstein_all_paragraphs_with_sentiment.parquet", index=False)
frankenstein_all_with_sentiment.to_csv("frankenstein_all_with_sentiment.csv", index=False)


character_sentiment_df.to_parquet("frankenstein_character_sentiment.parquet", index=False)
location_sentiment_summary.to_parquet("frankenstein_location_sentiment.parquet", index=False)
frankenstein_manual_locations.to_parquet("frankenstein_manual_locations.parquet", index=False)

print("✅ Saved parquet files:")
print("  - frankenstein_all_paragraphs_with_sentiment.parquet")
print("  - frankenstein_character_sentiment.parquet")  
print("  - frankenstein_location_sentiment.parquet")
print("  - frankenstein_manual_locations.parquet")

print("\n🎉 OPTIMIZED ANALYSIS COMPLETE!")
print("=" * 60)
print("📊 Summary:")
print(f"  - Total paragraphs: {len(frankenstein_all_with_sentiment)}")
print(f"  - Characters analyzed: {len(character_sentiment_df)}")
print(f"  - Locations analyzed: {len(location_sentiment_summary)}")
print(f"  - Sentiment analysis: Run ONCE efficiently")
print(f"  - Geoparsing: Skipped (used manual data)")
print(f"  - Storage: Parquet files for fast loading")
print("\n🚀 Ready for presentation notebook!")