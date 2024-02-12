import numpy as np
import dedalus.core.basis as basis
import dedalus.core.coords as coords
from dedalus.core.field import Operand
from dedalus.core.operators import SpectralOperator, SpectralOperator1D
from dedalus.tools.dispatch import MultiClass

class GQLProject(SpectralOperator, metaclass=MultiClass):
    """
    Projection operator for generalized quasilinear approximation

    Parameters
    ----------
    operand : Operand object
    coord : Space object
    cutoff : int
    
    """
    name = 'project'
    
    @classmethod
    def _preprocess_args(cls, operand, coord, cutoff, subspace, out=None):
        if isinstance(coord, coords.Coordinate):
            pass
        elif isinstance(coord, str):
            coord = operand.domain.get_coord(coord)
        else:
            raise ValueError("coord must be Coordinate or str")
        return (operand, coord, cutoff, subspace), {'out': out}

    @classmethod
    def _check_args(cls, operand, coord, cutoff, subspace, out=None):
        # Dispatch by operand basis and subaxis
        if isinstance(operand, Operand):
            basis = operand.domain.get_basis(coord)
            subaxis = basis.coordsystem.coords.index(coord)
            if isinstance(basis, cls.input_basis_type) and cls.basis_subaxis == subaxis:
                return True
        return False

    def __init__(self, operand, coord, cutoff, subspace, out=None):
        """
        cutoff gives mode index, not wavenumber. must be an integer
        """
        super().__init__(operand, out=out)
        self.cutoff = cutoff
        self.subspace = subspace
        # SpectralOperator requirements
        self.coord = coord
        self.input_basis = operand.domain.get_basis(coord)
        self.output_basis = self._output_basis(self.input_basis)
        self.first_axis = self.input_basis.first_axis
        self.last_axis = self.input_basis.last_axis
        # LinearOperator requirements
        self.operand = operand
        # FutureField requirements
        self.domain = operand.domain.substitute_basis(self.input_basis, self.output_basis)
        self.tensorsig = operand.tensorsig
        self.dtype = operand.dtype

        # local_coeff = self.domain.all_elements()
        # low_mask = np.ones(self.domain.local_coeff_shape, dtype='bool')

        # for i in range(self.dim):
        #     inter = self.domain.bases[i].interval
        #     L = inter[1] - inter[0]
        #     local_mode_num = (L*local_coeff[i]/(2*np.pi)).astype(int)
        #     low_mask &= (np.abs(local_mode_num) <= cutoff_mode[i])
        if self.subspace == 'high' or self.subspace == 'h':
            self.subspace = 'h'
        elif self.subspace == 'low' or self.subspace == 'l':
            self.subspace = 'l'
        else:
            raise ValueError("Subspace must be high/h or low/l, not {}".format(subspace))

    def __repr__(self):
        if self.subspace == 'h':
            inequality = '>'
        else:
            inequality = '<='
        return '{}({}, c_{}{}{})'.format(self.name, repr(self.operand), self.coord.name, inequality, self.cutoff)

    def __str__(self):
        if self.subspace == 'h':
            inequality = '>'
        else:
            inequality = '<='
        return '{}({}, c_{}{}{})'.format(self.name, str(self.operand), self.coord.name, inequality, self.cutoff)
        

    def subspace_matrix(self, layout):
        """Build matrix operating on global subspace data."""
        return self._subspace_matrix(layout, self.input_basis, self.output_basis, self.first_axis, self.cutoff, self.subspace)

class GQLProjectRealFourier(GQLProject, SpectralOperator1D):
    input_basis_type = basis.RealFourier
    basis_subaxis = 0
    subaxis_dependence = [True]
    subaxis_coupling = [False]

    @staticmethod
    def _output_basis(input_basis):
        return input_basis

    @staticmethod
    def _group_matrix(group, input_basis, output_basis, cutoff, subspace):
        # for RealFourier, mode numbers are always positive, so no need for abs()...
        if subspace == 'h':
            if group > cutoff:
                return np.eye(2)
        elif subspace == 'l':
            if group <= cutoff:
                return np.eye(2)
        else:
            raise ValueError(f"subspace should be 'h' or 'l', not {subspace}")
        return np.zeros(shape=(2,2))
