import torch

def classify_item(df, model, category_embeddings, categories, device, batch_size):
    all_classes = []
    
    # Iterate over the DataFrame in batches for efficient GPU processing
    for i in range(0, len(df), batch_size):
        # Select batch of documents (food descriptions)
        batch_documents = df['Item'].iloc[i:i + batch_size].tolist()
        
        # Encode the batch of food items
        # Use encode_document for maximum performance
        batch_embeddings = model.encode_document(
            batch_documents,
            convert_to_tensor=True,
            device=device
        )
        
        # --- 4. Calculate Similarity and Assign the Best Class ---
        # Calculate cosine similarity between the batch embeddings and the category embeddings
        # The result will be a tensor of shape (Batch Size, Number of Categories)
        # The similarity calculation happens entirely on the GPU
        similarities = model.similarity(batch_embeddings, category_embeddings)
        
        # Find the index of the highest similarity score for each food item
        # dim=1 means finding the max across the categories
        best_match_indices = torch.argmax(similarities, dim=1).cpu().numpy()
        
        # Map the index back to the category name
        batch_classes = [categories[idx] for idx in best_match_indices]
        
        all_classes.extend(batch_classes)
    df['class'] = all_classes
    return df
