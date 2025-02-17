import torch
import torch.nn as nn
import torch_geometric.nn as geom_nn

class GNNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(GNNModel, self).__init__()
        self.conv1 = geom_nn.GCNConv(input_dim, hidden_dim)
        self.conv2 = geom_nn.GCNConv(hidden_dim, output_dim)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x
