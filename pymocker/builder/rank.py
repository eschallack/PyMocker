from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')

def rank(options:list[str],target:str):
    if not options:
        return []
    query_embeddings = model.encode(options, convert_to_tensor=True)
    target_embedding = model.encode(target, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embeddings, target_embedding)
    return sorted(
        zip(options, cos_scores.tolist()),
        key=lambda x: x[1][0],
        reverse=True
    )
    