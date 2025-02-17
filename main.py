import torch
from transformers import AutoTokenizer
from models.rag import RAGRetriever
from models.moe import MixtureOfExperts
from models.memory import ConversationMemory
from models.gnn import GNNModel
from models.hybrid import HybridModel
from utils.config import EXPERT_CONFIGS, KNOWLEDGE_DATA
import networkx as nx

def create_knowledge_graph():
    # Create a simple knowledge graph using networkx
    G = nx.Graph()
    G.add_edges_from([
        ("AI", "Machine Learning"),
        ("Machine Learning", "Deep Learning"),
        ("AI", "Neural Networks"),
        ("Elon Musk", "Tesla"),
        ("Elon Musk", "SpaceX")
    ])
    # Convert to edge_index (PyTorch Geometric format)
    edge_index = torch.tensor(list(G.edges), dtype=torch.long).t().contiguous()
    # Create node features (random for demonstration)
    x = torch.rand((len(G.nodes), 16))
    return x, edge_index

def main():
    # Initialize the tokenizer
    model_name = "mistralai/Mistral-7B-Instruct-v0.1"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Initialize modules
    rag_retriever = RAGRetriever(KNOWLEDGE_DATA)
    moe_model = MixtureOfExperts(EXPERT_CONFIGS)
    memory_model = ConversationMemory()
    x, edge_index = create_knowledge_graph()
    gnn_model = GNNModel(input_dim=16, hidden_dim=32, output_dim=16)
    
    # Build the hybrid model
    hybrid_model = HybridModel(rag_retriever, moe_model, memory_model, gnn_model, tokenizer)
    
    # Example inference
    user_input = "Tell me about artificial intelligence."
    response = hybrid_model.generate_response(user_input, x, edge_index)
    print("Response:", response)

if __name__ == "__main__":
    main()
