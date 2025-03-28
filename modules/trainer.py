import torch
import gc
import matplotlib.pyplot as plt


class Trainer():
  def __init__(self, net):
    self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    self.net = net


  def _train_epoch(self, trainloader, optimizer, loss_fn, 
                   retitrain = False):
    
    loss_basket = 0
    n_batches = len(trainloader)

    for i, data in enumerate(trainloader):
      batch, labels = data
      batch, labels = batch.to(self.device), labels.to(self.device)

      self.net.train()
      out = self.net(batch)
      loss = loss_fn(out, labels)
      optimizer.zero_grad()
      loss.backward()

      optimizer.step()

      loss_basket += loss

    return loss_basket/n_batches


  def _valid_epoch(self, validloader, optimizer, loss_fn):

    n_batches = len(validloader)
    v_loss_basket = 0
    v_accuracy_basket = 0

    self.net.eval()

    # Possible fix for running out of memory!
    # with torch.no_grad():
    for v_batch, v_labels in validloader:

      v_batch, v_labels = v_batch.to(self.device), v_labels.to(self.device)
      out = self.net(v_batch)

      v_loss_basket += loss_fn(out, v_labels)
      v_accuracy_basket += (out.argmax(axis=1)==v_labels).sum()/len(v_labels)

    return v_loss_basket/n_batches, v_accuracy_basket/n_batches




  def train(self, trainloader, validloader, optimizer, loss_fn,
            epochs, retitrain = False, plotting = False):
    
    losses = []
    v_losses = []
    v_accs = []

    for t in range(epochs):
      
      # train epoch
      gc.collect()
      loss = self._train_epoch(trainloader, optimizer, loss_fn,
                               retitrain = retitrain)
      # valid epoch
      gc.collect()
      vloss, vacc = self._valid_epoch(validloader, optimizer, loss_fn)

      # gather the data for plotting
      losses.append(loss.cpu().detach().numpy())
      v_losses.append(vloss.cpu().detach().numpy())
      v_accs.append(vacc.cpu().detach().numpy())

      completed = (t*100)//epochs
      print(f"Training {completed}%: \t loss {loss:.5f}\t v_loss {vloss:.5f},\t v_acc {vacc:.5f}")


    if plotting: 
      x = range(len(losses))

      fig = plt.figure(figsize=(10,5))
      fig.add_subplot(1,2,1)
      plt.plot(x,losses, label="Training loss")
      plt.plot(x,v_losses, label="Validation loss")
      plt.xlabel("Epochs")
      plt.legend()
      fig.add_subplot(1,2,2)
      plt.plot(x,v_accs, label="Validation accuracy")
      plt.xlabel("Epochs")
      plt.legend()
      plt.show()

    print("Training complete.")
    