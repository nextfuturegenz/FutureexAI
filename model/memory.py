import torch
import torch.nn as nn

class ConversationMemory(nn.Module):
    def __init__(self, input_size=768, hidden_size=512):
        super(ConversationMemory, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.hidden_state = None

    def forward(self, input_embedding):
        # Assume input_embedding has shape [sequence_length, feature_dim]
        output, self.hidden_state = self.lstm(input_embedding.unsqueeze(0), self.hidden_state)
        return output
