import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM

class MixtureOfExperts(nn.Module):
    def __init__(self, expert_configs, gating_input_dim=768):
        super(MixtureOfExperts, self).__init__()
        # Initialize experts from given Hugging Face model names
        self.experts = nn.ModuleDict({
            name: AutoModelForCausalLM.from_pretrained(model_name)
            for name, model_name in expert_configs.items()
        })
        self.gating_network = nn.Linear(gating_input_dim, len(self.experts))
    
    def forward(self, input_ids, attention_mask=None):
        # For demonstration, we assume input_ids can be cast to float for gating.
        gating_logits = self.gating_network(input_ids.float())
        expert_weights = torch.softmax(gating_logits, dim=-1)
        outputs = [
            expert_weights[:, i].unsqueeze(-1) * self.experts[expert](input_ids, attention_mask=attention_mask).logits
            for i, expert in enumerate(self.experts)
        ]
        return sum(outputs)
