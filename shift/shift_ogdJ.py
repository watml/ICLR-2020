import torch
from torch import optim
from torch import tensor
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from model import *

################################################# data preprocessing #############################################

X = np.load("one_gaussian.npy")
X = torch.tensor(X)
dim = 2
sample_size = 128 * 128 * 16

# initialization, fix the same initialization
v = np.ones(dim)
np.random.seed(12)
phi = torch.tensor(v + np.random.randn(dim) * 0.1, requires_grad=True) 
np.random.seed(24)
theta = torch.tensor(np.random.randn(dim) * 0.1, requires_grad=True)

################################################# parameters #############################################
alpha = 0.2
beta1 = 0.1
beta2 = 0.0

# the problem is a min-max optimization: min_phi max_theta E_v[s(theta.x)] - E_0[s(theta.(z + phi))]

# for storing x^{t-1}, y^{t-1}
oldtheta = torch.zeros(dim)
oldtheta.requires_grad_()
oldphi = torch.zeros(dim)
oldphi.requires_grad_()

################################################# start training #################################################

# total number of epochs to train
num_epochs = 32
bs = 128 * 16   # batch size
n_bs = 128      # number of batches
Z = torch.randn(bs, dim)
Phi = np.zeros((num_epochs * n_bs // 4, dim))

for epoch in range(num_epochs):
    for _ in range(n_bs):        # for each batch
        # train the discriminator
        if theta.grad is not None:
            theta.grad.zero_()
        if phi.grad is not None:
            phi.grad.zero_()
        if oldtheta.grad is not None:
            oldtheta.grad.zero_()
        if oldphi.grad is not None:
            oldphi.grad.zero_()
        x = X[(bs * _) : (bs * (_ + 1))].float()
       
        # compute nabla_x f(x^t, y^t)
        d = dis(theta, x) - dis(theta, gen(phi.float(), Z))
        d.backward()
        # compute nabla_x f(x^{t-1}, y^{t-1})
        d = dis(oldtheta, x) - dis(oldtheta, gen(oldphi.float(), Z))
        d.backward()
        theta_tmp = theta.float() + alpha * theta.grad.float() - beta1 * oldtheta.grad.float()
        phi_tmp = phi.float() - alpha * phi.grad.float()  + beta2 * oldphi.grad.float()

        # rename oldtheta and oldphi
        oldtheta, oldphi = theta.detach(), phi.detach()
        oldtheta.requires_grad_()
        oldphi.requires_grad_()

        # rename theta and phi
        theta, phi = theta_tmp.detach(), phi_tmp.detach()
        theta.requires_grad_()
        phi.requires_grad_()
        
        if _ % 4 == 0:
            print("epoch: ", epoch, "batch: ", _, "phi: ", phi)
            Phi[(epoch * n_bs + _) // 4] = phi.detach().numpy()

np.save("ogdJ_alpha_" + str(alpha) + "_beta1_" + str(beta1) + "_beta2_" + str(beta2), Phi)
