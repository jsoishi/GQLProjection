import pytest
import numpy as np
import dedalus.public as de
from GQLProjection import Project
import matplotlib.pyplot as plt

def test_3D_projection():
    Lx = 1
    xb = de.Fourier('x', 128, interval=(0,Lx))
    yb = de.Fourier('y', 128) # interval is (0, 2pi)
    zb = de.Chebyshev('z', 16)
    d = de.Domain([xb, yb, zb], grid_dtype=np.float64)
    f = d.new_field()
    xx,yy,zz = d.grids()

    nx_l = 2
    ny_l = 2
    nx_h = 8
    ny_h = 8
    f['g'] = ( np.sin(nx_l*2*np.pi/Lx*xx))*(np.sin(ny_l*yy)) + ( np.sin(nx_h*2*np.pi/Lx*xx))*(np.sin(ny_h*yy)) 
    low = Project(f,[8,1],'low', index=False).evaluate()
    hi = Project(f, [8,1],'high', index=False).evaluate()
    plt.subplot(131)
    plt.imshow(f['g'][:,:,0])
    plt.colorbar()
    plt.subplot(132)
    plt.imshow(low['g'][:,:,0])
    plt.colorbar()
    plt.title("low")
    plt.subplot(133)
    plt.imshow(hi['g'][:,:,0])
    plt.colorbar()
    plt.title("hi")
    plt.tight_layout()
    plt.savefig("test_3D.png", dpi=100)
    #assert (np.allclose(low['g'],f['g']) and np.allclose(hi['g'], np.zeros_like(f['g'])))
    #assert (np.allclose(low['g'],f['g']))
    assert (np.allclose(hi['g'], np.zeros_like(f['g'])))
