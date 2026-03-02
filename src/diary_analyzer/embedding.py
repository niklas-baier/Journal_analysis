import torch
from sentence_transformers import SentenceTransformer
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

        # Calculate cosine similarity between the batch embeddings and the category embeddings
        # The result will be a tensor of shape (Batch Size, Number of Categories)
        similarities = model.similarity(batch_embeddings, category_embeddings)

        # Find the index of the highest similarity score for each food item
        best_match_indices = torch.argmax(similarities, dim=1).cpu().numpy()

        # Map the index back to the category name
        batch_classes = [categories[idx] for idx in best_match_indices]

        all_classes.extend(batch_classes)
    df['class'] = all_classes
    return df

def classify_dataframe(df, classification_prompts, categories, model):
    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")
    print(df)
    model.to(device)
    print(f"Model moved to {device}")


    # --- 2. Encode the Labels/Prompts ---
    print("Encoding classification prompts...")
    category_embeddings = model.encode_document(
        classification_prompts,
        convert_to_tensor=True,
        device=device
    )
    # Shape will be (3, 768) for 3 categories
    print(f"Category embeddings shape: {category_embeddings.shape}")

    # --- Create Example DataFrame ---
    data = {
        'food': [
            "Chocolate ice cream with fudge sauce",
            "Grilled salmon with roasted asparagus",
            "Spicy black bean burger patty",
            "A piece of prime rib steak",
            "Apple pie slice"
        ]
    }

    # --- 3. Process the DataFrame in Batches ---
    BATCH_SIZE = 32 # Adjust based on your GPU memory and efficiency needs
    # Run the classification function
    df_classified = classify_item(
        df,
        model,
        category_embeddings,
        categories,
        device,
        BATCH_SIZE
    )

    print("\n--- Classified DataFrame ---")
    return df_classified
