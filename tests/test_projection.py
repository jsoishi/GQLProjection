import pytest
import numpy as np
import dedalus.public as de
from GQLProjection import GQLProject
import matplotlib.pyplot as plt

@pytest.mark.mpi(min_size=2)
def test_3D_projection():
    Lx = 1
    xb = de.Fourier('x', 128, interval=(0,Lx))
    yb = de.Fourier('y', 128) # interval is (0, 2pi)
    zb = de.Chebyshev('z', 16)
    d = de.Domain([xb, yb, zb], grid_dtype=np.float64)
    f = d.new_field()
    xx,yy,zz = d.all_grids()

    nx_l = 2
    ny_l = 2
    nx_h = 8
    ny_h = 8
    f['g'] = ( np.sin(nx_l*2*np.pi/Lx*xx))*(np.sin(ny_l*yy)) + ( np.sin(nx_h*2*np.pi/Lx*xx))*(np.sin(ny_h*yy)) 
    low = GQLProject(f,[8,8],'low').evaluate()
    hi  = GQLProject(f, [8,8],'high').evaluate()
    assert (np.allclose(low['g'],f['g']) and np.allclose(hi['g'], np.zeros_like(f['g'])))
    
