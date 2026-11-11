"""Q5: CLIP loss and classification with illustrative embeddings."""
import torch
from torch.nn import functional as F

images = F.normalize(torch.tensor([[1., 0.], [0., 1.]]), dim=-1)
texts = F.normalize(torch.tensor([[1., 0.], [0., 1.]]), dim=-1)
temperature = 0.1
logits = images @ texts.T / temperature
targets = torch.arange(2)
loss = (F.cross_entropy(logits, targets)
        + F.cross_entropy(logits.T, targets)) / 2
names = ["room", "delivery zone"]
scores = images[:1] @ texts.T / temperature
prediction = names[scores.argmax(dim=-1).item()]
assert loss.item() < 0.001
assert prediction == "room"
print("Illustrative image-text logits:", logits.tolist())
print(f"Symmetric contrastive loss: {loss.item():.8f}")
print("Predicted class:", prediction)
